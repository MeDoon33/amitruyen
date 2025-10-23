from app import db
from datetime import datetime

class Chapter(db.Model):
    __tablename__ = 'chapters'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    chapter_number = db.Column(db.Integer, nullable=False)
    comic_id = db.Column(db.Integer, db.ForeignKey('comics.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    comic = db.relationship('Comic', backref=db.backref('chapters', lazy=True))

    def __repr__(self):
        return f'<Chapter {self.chapter_number}: {self.title}>'