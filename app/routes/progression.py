from flask import Blueprint, request, jsonify, current_app, render_template
from flask_login import login_required, current_user
from app import db
from app.models.user import User, UserBadge, Badge, RankTitle, UserActivity
from app.services.progression import ProgressionService

progression_bp = Blueprint('progression', __name__)

@progression_bp.route('/stats')
@login_required
def stats_page():
    """Display user progression stats page"""
    if not current_app.config.get('PROGRESSION_ENABLED', True):
        # Render placeholder page with message
        return render_template('progression/stats.html', progression_disabled=True)
    return render_template('progression/stats.html')

@progression_bp.route('/api/user/stats')
@login_required
def get_user_stats():
    """Get current user's progression stats"""
    try:
        if not current_app.config.get('PROGRESSION_ENABLED', True):
            return jsonify({'success': False, 'disabled': True, 'message': 'Chức năng đang phát triển'}), 503
        stats = ProgressionService.get_user_stats(current_user.id)
        if not stats:
            return jsonify({'error': 'User not found'}), 404
            
        return jsonify({
            'success': True,
            'stats': {
                'points': stats['points'],
                'level': stats['level'],
                'rank_title': stats['rank_title'],
                'rank_type_display': stats['rank_type_display'],
                'progress_to_next': stats['progress_to_next'],
                'total_reads': stats['total_reads'],
                'total_comments': stats['total_comments'],
                'total_ratings': stats['total_ratings'],
                'badge_count': stats['badge_count']
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error getting user stats: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@progression_bp.route('/api/user/badges')
@login_required
def get_user_badges():
    """Get current user's earned badges"""
    try:
        if not current_app.config.get('BADGES_ENABLED', True):
            return jsonify({'success': False, 'disabled': True, 'message': 'Huy hiệu đang phát triển'}), 503
        user_badges = UserBadge.query.filter_by(user_id=current_user.id).all()
        badges_data = []
        
        for user_badge in user_badges:
            badges_data.append({
                'id': user_badge.badge.id,
                'name': user_badge.badge.name,
                'description': user_badge.badge.description,
                'icon': user_badge.badge.icon,
                'category': user_badge.badge.category,
                'earned_at': user_badge.earned_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'badges': badges_data
        })
    except Exception as e:
        current_app.logger.error(f"Error getting user badges: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@progression_bp.route('/api/user/change-rank-type', methods=['POST'])
@login_required
def change_rank_type():
    """Change user's rank type/progression path"""
    try:
        if not current_app.config.get('RANK_TITLES_ENABLED', True):
            return jsonify({'success': False, 'disabled': True, 'message': 'Thay đổi đường thăng cấp đang phát triển'}), 503
        data = request.get_json()
        new_rank_type = data.get('rank_type')
        
        if new_rank_type not in ['tu_tien', 'ma_vuong', 'vuong_gia']:
            return jsonify({'error': 'Invalid rank type'}), 400
        
        current_user.rank_type = new_rank_type
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Rank type changed successfully',
            'new_rank_title': current_user.get_rank_title(),
            'rank_type_display': current_user.get_rank_type_display()
        })
    except Exception as e:
        current_app.logger.error(f"Error changing rank type: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@progression_bp.route('/api/badges/available')
@login_required
def get_available_badges():
    """Get all available badges and their requirements"""
    try:
        if not current_app.config.get('BADGES_ENABLED', True):
            return jsonify({'success': False, 'disabled': True, 'message': 'Danh sách huy hiệu đang phát triển'}), 503
        badges = Badge.query.filter_by(is_active=True).all()
        user_badge_ids = [ub.badge_id for ub in current_user.user_badges]
        
        badges_data = []
        for badge in badges:
            badges_data.append({
                'id': badge.id,
                'name': badge.name,
                'description': badge.description,
                'icon': badge.icon,
                'category': badge.category,
                'requirement_type': badge.requirement_type,
                'requirement_value': badge.requirement_value,
                'is_earned': badge.id in user_badge_ids
            })
        
        return jsonify({
            'success': True,
            'badges': badges_data
        })
    except Exception as e:
        current_app.logger.error(f"Error getting available badges: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@progression_bp.route('/api/rank-titles')
def get_rank_titles():
    """Get all rank titles for each progression path"""
    try:
        if not current_app.config.get('RANK_TITLES_ENABLED', True):
            return jsonify({'success': False, 'disabled': True, 'message': 'Danh hiệu đang phát triển'}), 503
        rank_titles = RankTitle.query.order_by(RankTitle.rank_type, RankTitle.level).all()
        
        titles_by_type = {}
        for title in rank_titles:
            if title.rank_type not in titles_by_type:
                titles_by_type[title.rank_type] = []
            
            titles_by_type[title.rank_type].append({
                'level': title.level,
                'title': title.title,
                'color': title.color
            })
        
        return jsonify({
            'success': True,
            'rank_titles': titles_by_type
        })
    except Exception as e:
        current_app.logger.error(f"Error getting rank titles: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@progression_bp.route('/api/user/activities')
@login_required
def get_user_activities():
    """Get user's recent activities"""
    try:
        if not current_app.config.get('PROGRESSION_ENABLED', True):
            return jsonify({'success': False, 'disabled': True, 'message': 'Hoạt động đang phát triển'}), 503
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        activities = UserActivity.query.filter_by(user_id=current_user.id)\
            .order_by(UserActivity.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        activities_data = []
        for activity in activities.items:
            activities_data.append({
                'activity_type': activity.activity_type,
                'points_earned': activity.points_earned,
                'reference_id': activity.reference_id,
                'created_at': activity.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'activities': activities_data,
            'pagination': {
                'page': page,
                'pages': activities.pages,
                'per_page': per_page,
                'total': activities.total
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error getting user activities: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@progression_bp.route('/api/leaderboard')
def get_leaderboard():
    """Get top users by points with optional content type and time period filtering"""
    try:
        if not current_app.config.get('PROGRESSION_ENABLED', True):
            return jsonify({'success': False, 'disabled': True, 'message': 'Bảng xếp hạng đang phát triển'}), 503
        page = request.args.get('page', 1, type=int)
        per_page = 50
        content_type = request.args.get('content_type', 'comics')  # all, comics, novels
        period = request.args.get('period', 'month')  # month, week, day
        
        # Base query for users
        users_query = User.query.order_by(User.points.desc(), User.level.desc())
        
        # Apply content type filtering if needed
        if content_type == 'comics':
            # For now, show users who have activity with comics (simplified)
            # This can be enhanced to filter by actual comic interactions
            users_query = users_query.filter(User.points > 0)  # Placeholder filter
        elif content_type == 'novels':
            # For now, show users who have activity with novels (simplified)  
            # This can be enhanced to filter by actual novel interactions
            users_query = users_query.filter(User.points > 0)  # Placeholder filter
        
        # Note: Time period filtering would require tracking user activity by date
        # For now, we'll return top users regardless of time period
        # This can be enhanced with UserActivity table to filter by period
        
        users = users_query.paginate(page=page, per_page=per_page, error_out=False)
        
        leaderboard_data = []
        for i, user in enumerate(users.items):
            leaderboard_data.append({
                'rank': (page - 1) * per_page + i + 1,
                'username': user.username,
                'display_name': user.get_display_name_with_styled_title(),
                'points': user.points,
                'level': user.level,
                'rank_title': user.get_rank_title(),
                'rank_type_display': user.get_rank_type_display(),
                'avatar_url': user.get_avatar_url()
            })
        
        return jsonify({
            'success': True,
            'leaderboard': leaderboard_data,
            'content_type': content_type,
            'period': period,
            'pagination': {
                'page': page,
                'pages': users.pages,
                'per_page': per_page,
                'total': users.total
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error getting leaderboard: {e}")
        return jsonify({'error': 'Internal server error'}), 500