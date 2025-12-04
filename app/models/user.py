from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db 

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # Increase length to safely store modern hash algorithms (scrypt, pbkdf2, argon2)
    password_hash = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    # role: admin, moderator, uploader, reader
    role = db.Column(db.String(20), default='reader', nullable=False)  # 'admin', 'moderator', 'uploader', 'reader'
    avatar_url = db.Column(db.Text, nullable=True)  # URL to avatar image
    display_name = db.Column(db.String(100), nullable=True)  # Display name for comments
    
    # Ban system
    is_banned = db.Column(db.Boolean, default=False)  # Có bị cấm không
    ban_until = db.Column(db.DateTime, nullable=True)  # Cấm đến khi nào (None = vĩnh viễn)
    ban_reason = db.Column(db.Text, nullable=True)  # Lý do cấm
    banned_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Admin/Mod cấm
    banned_at = db.Column(db.DateTime, nullable=True)  # Thời gian bị cấm
    
    # User progression system
    points = db.Column(db.Integer, default=0)  # Điểm người dùng
    level = db.Column(db.Integer, default=1)  # Cấp độ
    rank_type = db.Column(db.String(50), default='tu_tien')  # Loại cấp bậc: tu_tien, ma_vuong, vuong_gia
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_currently_banned(self):
        """Check if user is currently banned"""
        if not self.is_banned:
            return False
        
        # If ban_until is None, it's a permanent ban
        if self.ban_until is None:
            return True
        
        # Check if ban period has expired
        if datetime.utcnow() > self.ban_until:
            # Automatically unban if time has passed
            self.is_banned = False
            self.ban_until = None
            db.session.commit()
            return False
        
        return True
    
    def get_ban_info(self):
        """Get ban information for display"""
        if not self.is_currently_banned():
            return None
        
        info = {
            'is_permanent': self.ban_until is None,
            'ban_until': self.ban_until,
            'reason': self.ban_reason or 'Không có lý do',
            'banned_at': self.banned_at
        }
        
        if not info['is_permanent'] and self.ban_until:
            remaining = self.ban_until - datetime.utcnow()
            days = remaining.days
            hours = remaining.seconds // 3600
            info['remaining_days'] = days
            info['remaining_hours'] = hours
        
        return info

    def is_admin(self):
        return self.role == 'admin'

    def is_moderator(self):
        return self.role == 'moderator' or self.role == 'admin'

    def is_uploader(self):
        return self.role == 'uploader' or self.role == 'moderator' or self.role == 'admin'

    def is_reader(self):
        return self.role in ['reader', 'uploader', 'moderator', 'admin']

    def get_role_display(self):
        if self.role == 'admin':
            return 'Admin'
        elif self.role == 'moderator':
            return 'Kiểm duyệt'
        elif self.role == 'uploader':
            return 'Người đăng truyện'
        else:
            return 'Đọc giả'
    
    def get_display_name(self):
        """Get display name for comments, fallback to username"""
        return self.display_name if self.display_name else self.username
    
    def get_display_name_with_title(self):
        """Get display name with rank title for comments and profile"""
        base_name = self.get_display_name()
        if not self._is_rank_titles_enabled():
            return f"{base_name}"
        rank_title = self.get_rank_title()
        return f"{base_name} 【{rank_title}】"
    
    def get_display_name_with_styled_title(self):
        """Get display name with styled rank title and logo after title for HTML rendering"""
        base_name = self.get_display_name()
        if not self._is_rank_titles_enabled():
            return f'<span class="user-display-with-logo"><span class="username">{base_name}</span></span>'
        rank_title = self.get_rank_title()
        css_class = self.get_rank_title_css_class()
        logo = self.get_rank_logo()
        logo_html = f'<img src="{logo}" alt="Rank Logo" class="rank-logo-small">' if logo else ''
        return f'<span class="user-display-with-logo"><span class="username">{base_name}</span> <span class="{css_class}">{rank_title}</span> {logo_html}</span>'
    
    def get_avatar_url(self):
        """Get avatar URL with fallback to default avatar"""
        if self.avatar_url:
            return self.avatar_url
        # Default avatar - white circle with duck emoji
        return "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100' viewBox='0 0 100 100'%3e%3ccircle cx='50' cy='50' r='50' fill='%23f8f9fa' stroke='%23dee2e6' stroke-width='2'/%3e%3ctext x='50' y='50' font-size='40' text-anchor='middle' dominant-baseline='central'%3e🦆%3c/text%3e%3c/svg%3e"
    
    # Progression system methods
    def add_points(self, points_to_add):
        """Add points and check for level up"""
        self.points += points_to_add
        # Optimized: iterative instead of recursive to avoid stack overflow
        while self.points >= self.get_required_points_for_level(self.level + 1):
            self.level += 1
    
    @staticmethod
    def get_required_points_for_level(level):
        """Calculate required points for a specific level"""
        # Formula: (level - 1) * 100 + (level - 1) * 50
        # Level 1: 0, Level 2: 150, Level 3: 350, Level 4: 600, etc.
        if level <= 1:
            return 0
        return (level - 1) * 100 + ((level - 1) * (level - 2) // 2) * 50
    
    def _is_rank_titles_enabled(self):
        """Centralized check for rank titles feature flag"""
        from flask import current_app
        return current_app and current_app.config.get('RANK_TITLES_ENABLED', True)
    
    def get_rank_title(self):
        """Get current rank title based on level and rank type"""
        if not self._is_rank_titles_enabled():
            return ''
        return RankTitle.get_title_for_level(self.rank_type, self.level)
    
    def get_rank_title_css_class(self):
        """Get CSS class for rank title gradient based on level"""
        if not self._is_rank_titles_enabled():
            return ''
        # Primary class based on level (color progression)
        level_class = f"level-{min(self.level, 10)}"
        base_class = f"rank-title {level_class}"
        
        # Add animation effects based on level
        if self.level >= 9:
            base_class += " legendary"  # Level 9-10: Đỏ với hiệu ứng đặc biệt
        elif self.level >= 7:
            base_class += " high-level animated"  # Level 7-8: Vàng với glow
        elif self.level >= 5:
            base_class += " animated"  # Level 5-6: Tím với animation
        elif self.level >= 3:
            base_class += " animated"  # Level 3-4: Xanh nước biển với animation
        
        # Add legacy rank type class for additional styling if needed
        rank_type_classes = {
            'Tu Tiên': 'tu-tien-type',
            'tu_tien': 'tu-tien-type',
            'Ma Vương': 'ma-vuong-type',
            'ma_vuong': 'ma-vuong-type',
            'Vương Giả': 'vuong-gia-type',
            'vuong_gia': 'vuong-gia-type'
        }
        
        if self.rank_type in rank_type_classes:
            base_class += f" {rank_type_classes[self.rank_type]}"
            
        return base_class
    
    def get_progress_to_next_level(self):
        """Get progress percentage to next level"""
        current_level_points = self.get_required_points_for_level(self.level)
        next_level_points = self.get_required_points_for_level(self.level + 1)
        
        if next_level_points == current_level_points:
            return 100
            
        progress = ((self.points - current_level_points) / (next_level_points - current_level_points)) * 100
        return min(100, max(0, progress))
    
    def get_rank_type_display(self):
        """Get display name for rank type"""
        rank_types = {
            'tu_tien': 'Tu Tiên',
            'ma_vuong': 'Ma Vương', 
            'vuong_gia': 'Vương Giả'
        }
        return rank_types.get(self.rank_type, 'Tu Tiên')
    
    def get_rank_logo(self):
        """Get logo URL for rank type and level"""
        if not self._is_rank_titles_enabled():
            return None
        if self.rank_type in ['vuong_gia', 'Vương Giả']:
            # Honor of Kings tier logos cho Vương Giả path
            logo_mapping = {
                1: 'https://vuonggiavinhdieu.net/wp-content/uploads/2025/08/TIER-BRONZE-HONOR-OF-KINGS-150x150.webp',
                2: 'https://vuonggiavinhdieu.net/wp-content/uploads/2025/08/TIER-SILVER-HONOR-OF-KINGS-150x150.webp',
                3: 'https://vuonggiavinhdieu.net/wp-content/uploads/2025/08/TIER-GOLD-HONOR-OF-KINGS-150x150.webp',
                4: 'https://vuonggiavinhdieu.net/wp-content/uploads/2025/08/TIER-PLATINUM-HONOR-OF-KINGS-150x150.webp',
                5: 'https://vuonggiavinhdieu.net/wp-content/uploads/2025/08/TIER-DIAMOND-HONOR-OF-KINGS-150x150.webp',
                6: 'https://vuonggiavinhdieu.net/wp-content/uploads/2025/08/TIER-MASTER-HONOR-OF-KINGS-150x150.webp',
            }
            return logo_mapping.get(self.level, 'https://vuonggiavinhdieu.net/wp-content/uploads/2025/08/TIER-MASTER-2-HONOR-OF-KINGS-150x150.webp' if self.level >= 7 else None)
        return None


class UserBadge(db.Model):
    """User earned badges/achievements"""
    __tablename__ = 'user_badges'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('user_badges', lazy=True))
    badge = db.relationship('Badge', backref=db.backref('user_badges', lazy=True))
    
    __table_args__ = (db.UniqueConstraint('user_id', 'badge_id', name='unique_user_badge'),)


class Badge(db.Model):
    """Available badges/achievements"""
    __tablename__ = 'badges'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))  # Emoji or icon class
    category = db.Column(db.String(50))  # reading, commenting, uploading, etc.
    requirement_type = db.Column(db.String(50))  # points, comments, uploads, reads
    requirement_value = db.Column(db.Integer)  # Threshold value
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class RankTitle(db.Model):
    """Rank titles for different progression paths"""
    __tablename__ = 'rank_titles'
    
    id = db.Column(db.Integer, primary_key=True)
    rank_type = db.Column(db.String(50), nullable=False)  # tu_tien, ma_vuong, vuong_gia
    level = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(7), default='#000000')  # Hex color for display
    
    __table_args__ = (db.UniqueConstraint('rank_type', 'level', name='unique_rank_level'),)
    
    @staticmethod
    def get_title_for_level(rank_type, level):
        """Get title for specific rank type and level"""
        # Map lowercase rank types to display names
        rank_type_mapping = {
            'tu_tien': 'Tu Tiên',
            'ma_vuong': 'Ma Vương',
            'vuong_gia': 'Vương Giả'
        }
        
        # Convert to display name if needed
        display_rank_type = rank_type_mapping.get(rank_type, rank_type)
        
        title_obj = RankTitle.query.filter_by(rank_type=display_rank_type, level=level).first()
        if title_obj:
            return title_obj.title
        
        # For levels higher than available in database, use highest available title
        if display_rank_type == 'Vương Giả' and level > 10:
            highest_title = RankTitle.query.filter_by(rank_type=display_rank_type).order_by(RankTitle.level.desc()).first()
            if highest_title:
                return highest_title.title
        
        return f"Cấp {level}"


class UserActivity(db.Model):
    """Track user activities for point calculation"""
    __tablename__ = 'user_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # read_chapter, comment, rating, daily_login, etc.
    points_earned = db.Column(db.Integer, default=0)
    reference_id = db.Column(db.Integer)  # ID of comic, chapter, comment, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('activities', lazy=True))