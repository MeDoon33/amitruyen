from datetime import datetime, timedelta
from app import db
from app.models.user import User, UserActivity, UserBadge, Badge


class ProgressionService:
    """Service to handle user progression logic"""
    
    # Point values for different activities
    POINT_VALUES = {
        'read_chapter': 5,
        'comment': 10, 
        'rating': 15,
        'daily_login': 10,
        'upload_comic': 50,
        'first_time_activity': 20,  # Bonus for first time doing an activity
    }
    
    @staticmethod
    def award_points(user_id, activity_type, reference_id=None):
        """Award points for user activity"""
        # Feature flag: short-circuit if progression disabled
        from flask import current_app
        if not current_app.config.get('PROGRESSION_ENABLED', True):
            return {
                'points_earned': 0,
                'total_points': None,
                'level_up': False,
                'new_level': None,
                'rank_title': ''
            }
        user = User.query.get(user_id)
        if not user:
            return False
            
        points = ProgressionService.POINT_VALUES.get(activity_type, 0)
        
        # Check for daily limits to prevent spam
        if not ProgressionService._can_earn_points(user_id, activity_type, reference_id):
            return False
            
        # Check for first-time bonus
        if ProgressionService._is_first_time_activity(user_id, activity_type):
            points += ProgressionService.POINT_VALUES.get('first_time_activity', 0)
        
        # Create activity record
        activity = UserActivity(
            user_id=user_id,
            activity_type=activity_type,
            points_earned=points,
            reference_id=reference_id
        )
        db.session.add(activity)
        
        # Add points to user and check for level up
        old_level = user.level
        user.add_points(points)
        
        # Check for new badges
        ProgressionService._check_badges(user)
        
        db.session.commit()
        
        # Return level up info
        return {
            'points_earned': points,
            'total_points': user.points,
            'level_up': user.level > old_level,
            'new_level': user.level,
            'rank_title': user.get_rank_title()
        }
    
    @staticmethod
    def _can_earn_points(user_id, activity_type, reference_id=None):
        """Check if user can earn points for this activity (daily limits)"""
        today = datetime.utcnow().date()
        
        # Daily login - once per day
        if activity_type == 'daily_login':
            existing = UserActivity.query.filter(
                UserActivity.user_id == user_id,
                UserActivity.activity_type == 'daily_login',
                db.func.date(UserActivity.created_at) == today
            ).first()
            return existing is None
        
        # Reading - max 200 chapters per day for points
        elif activity_type == 'read_chapter':
            today_reads = UserActivity.query.filter(
                UserActivity.user_id == user_id,
                UserActivity.activity_type == 'read_chapter',
                db.func.date(UserActivity.created_at) == today
            ).count()
            return today_reads < 200
        
        # Comments - max 5 per day for points  
        elif activity_type == 'comment':
            today_comments = UserActivity.query.filter(
                UserActivity.user_id == user_id,
                UserActivity.activity_type == 'comment',
                db.func.date(UserActivity.created_at) == today
            ).count()
            return today_comments < 5
        
        # Ratings - once per comic
        elif activity_type == 'rating' and reference_id:
            existing = UserActivity.query.filter(
                UserActivity.user_id == user_id,
                UserActivity.activity_type == 'rating',
                UserActivity.reference_id == reference_id
            ).first()
            return existing is None
        
        return True
    
    @staticmethod
    def _is_first_time_activity(user_id, activity_type):
        """Check if this is user's first time doing this activity"""
        existing = UserActivity.query.filter(
            UserActivity.user_id == user_id,
            UserActivity.activity_type == activity_type
        ).first()
        return existing is None
    
    @staticmethod
    def _check_badges(user):
        """Check and award new badges to user - Optimized version"""
        # Get badge IDs user already has
        user_badge_ids = {ub.badge_id for ub in user.user_badges}  # Use set for O(1) lookup
        
        # Get available badges in one query with proper filtering
        available_badges = Badge.query.filter(
            Badge.is_active == True,
            ~Badge.id.in_(user_badge_ids)
        ).all()
        
        if not available_badges:
            return
        
        # Pre-calculate activity counts to avoid repeated queries
        activity_counts = {}
        for activity_type in ['comment', 'read_chapter']:
            activity_counts[activity_type] = UserActivity.query.filter(
                UserActivity.user_id == user.id,
                UserActivity.activity_type == activity_type
            ).count()
        
        # Check each badge
        new_badges = []
        for badge in available_badges:
            if badge.requirement_type == 'points' and user.points >= badge.requirement_value:
                new_badges.append(UserBadge(user_id=user.id, badge_id=badge.id))
            elif badge.requirement_type == 'level' and user.level >= badge.requirement_value:
                new_badges.append(UserBadge(user_id=user.id, badge_id=badge.id))
            elif badge.requirement_type == 'comments' and activity_counts.get('comment', 0) >= badge.requirement_value:
                new_badges.append(UserBadge(user_id=user.id, badge_id=badge.id))
            elif badge.requirement_type == 'reads' and activity_counts.get('read_chapter', 0) >= badge.requirement_value:
                new_badges.append(UserBadge(user_id=user.id, badge_id=badge.id))
        
        # Bulk insert new badges
        if new_badges:
            db.session.bulk_save_objects(new_badges)
    
    @staticmethod
    def get_user_stats(user_id):
        """Get comprehensive user progression stats"""
        user = User.query.get(user_id)
        if not user:
            return None
            
        # Activity counts
        total_reads = UserActivity.query.filter(
            UserActivity.user_id == user_id,
            UserActivity.activity_type == 'read_chapter'
        ).count()
        
        total_comments = UserActivity.query.filter(
            UserActivity.user_id == user_id,
            UserActivity.activity_type == 'comment'
        ).count()
        
        total_ratings = UserActivity.query.filter(
            UserActivity.user_id == user_id,
            UserActivity.activity_type == 'rating'
        ).count()
        
        # Badge count
        badge_count = len(user.user_badges)
        
        return {
            'user': user,
            'points': user.points,
            'level': user.level,
            'rank_title': user.get_rank_title(),
            'rank_type_display': user.get_rank_type_display(),
            'progress_to_next': user.get_progress_to_next_level(),
            'total_reads': total_reads,
            'total_comments': total_comments,
            'total_ratings': total_ratings,
            'badge_count': badge_count,
            'badges': user.user_badges
        }