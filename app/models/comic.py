from datetime import datetime
from app import db

class Comic(db.Model):
    __tablename__ = 'comics'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    uploader_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Người đăng truyện
    author = db.Column(db.String(100))
    description = db.Column(db.Text)
    # Allow long external image URLs (was String(500))
    cover_image = db.Column(db.Text)
    genre = db.Column(db.String(100))
    # content_type: distinguish between comics (truyện tranh) and novels (truyện chữ)
    # values: 'comic' (truyện tranh) or 'novel' (truyện chữ)
    content_type = db.Column(db.String(20), default='comic')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    chapters = db.relationship('app.models.comic.Chapter', backref='comic', lazy=True, cascade='all, delete-orphan')
    views = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='ongoing')  # ongoing, completed, hiatus
    rating = db.Column(db.Float, default=0.0)
    rating_count = db.Column(db.Integer, default=0)  # Số lượt đánh giá để tính trung bình
    follow_count = db.Column(db.Integer, default=0)  # Số người theo dõi
    tags = db.Column(db.String(500))  # Store as comma-separated values
    
    # Relationship với User (người đăng)
    uploader = db.relationship('User', backref=db.backref('uploaded_comics', lazy=True), foreign_keys=[uploader_id])

class Chapter(db.Model):
    __tablename__ = 'chapters'
    
    id = db.Column(db.Integer, primary_key=True)
    comic_id = db.Column(db.Integer, db.ForeignKey('comics.id'), nullable=False)
    chapter_number = db.Column(db.Float, nullable=False)  # Using float for chapters like 1.5
    title = db.Column(db.String(200))
    content = db.Column(db.Text)  # For novel chapters
    image_urls = db.Column(db.Text)  # Store as JSON string for comic chapters
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    views = db.Column(db.Integer, default=0)
    
class UserReadHistory(db.Model):
    __tablename__ = 'user_read_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comic_id = db.Column(db.Integer, db.ForeignKey('comics.id'), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('read_history', lazy=True))
    comic = db.relationship('Comic')
    chapter = db.relationship('app.models.comic.Chapter')

class UserRating(db.Model):
    __tablename__ = 'user_rating'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comic_id = db.Column(db.Integer, db.ForeignKey('comics.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint: mỗi user chỉ được vote 1 lần cho mỗi comic
    __table_args__ = (db.UniqueConstraint('user_id', 'comic_id', name='unique_user_comic_rating'),)
    
    user = db.relationship('User', backref=db.backref('ratings', lazy=True))
    comic = db.relationship('Comic', backref=db.backref('user_ratings', lazy=True))

class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comic_id = db.Column(db.Integer, db.ForeignKey('comics.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_hidden = db.Column(db.Boolean, default=False, nullable=False)  # For soft delete/hide by moderator
    
    # Reply functionality (nested comments)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)  # NULL = top-level comment
    
    # Like/Dislike counts
    likes_count = db.Column(db.Integer, default=0, nullable=False)
    dislikes_count = db.Column(db.Integer, default=0, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('comments', lazy=True))
    comic = db.relationship('Comic', backref=db.backref('comments', lazy=True, order_by='Comment.created_at.desc()'))
    
    # Self-referential relationship for replies
    replies = db.relationship('Comment', 
                              backref=db.backref('parent', remote_side=[id]),
                              lazy='dynamic',
                              order_by='Comment.created_at.asc()')
    
    def get_replies(self):
        """Get all non-hidden replies to this comment"""
        return self.replies.filter_by(is_hidden=False).all()
    
    def get_all_replies(self):
        """Get all replies including hidden ones (for admins)"""
        return self.replies.all()


class CommentReaction(db.Model):
    """Track user likes/dislikes on comments"""
    __tablename__ = 'comment_reactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=False)
    reaction_type = db.Column(db.String(10), nullable=False)  # 'like' or 'dislike'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint: mỗi user chỉ được react 1 lần cho mỗi comment
    __table_args__ = (db.UniqueConstraint('user_id', 'comment_id', name='unique_user_comment_reaction'),)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('comment_reactions', lazy=True))
    comment = db.relationship('Comment', backref=db.backref('reactions', lazy=True))

class Follow(db.Model):
    __tablename__ = 'follows'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comic_id = db.Column(db.Integer, db.ForeignKey('comics.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint: mỗi user chỉ được follow 1 lần cho mỗi comic
    __table_args__ = (db.UniqueConstraint('user_id', 'comic_id', name='unique_user_comic_follow'),)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('follows', lazy=True))
    comic = db.relationship('Comic', backref=db.backref('followers', lazy=True))