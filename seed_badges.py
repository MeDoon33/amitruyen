"""
Script to seed initial badges/achievements into the database
"""
from app import create_app, db
from app.models.user import Badge

def seed_badges():
    app = create_app()
    with app.app_context():
        # Check if badges already exist
        existing_count = Badge.query.count()
        if existing_count > 0:
            print(f"Database already has {existing_count} badges. Skipping seed.")
            return
        
        badges = [
            # Reading badges
            Badge(
                name='Người Đọc Mới',
                description='Đọc chương đầu tiên',
                icon='📖',
                category='reading',
                requirement_type='reads',
                requirement_value=1
            ),
            Badge(
                name='Nghiện Đọc',
                description='Đọc 100 chương',
                icon='📚',
                category='reading',
                requirement_type='reads',
                requirement_value=100
            ),
            Badge(
                name='Thư Khố',
                description='Đọc 500 chương',
                icon='📕',
                category='reading',
                requirement_type='reads',
                requirement_value=500
            ),
            
            # Commenting badges
            Badge(
                name='Người Bình Luận',
                description='Viết 50 bình luận',
                icon='💬',
                category='commenting',
                requirement_type='comments',
                requirement_value=50
            ),
            Badge(
                name='Talkative',
                description='Viết 50 bình luận',
                icon='💭',
                category='commenting',
                requirement_type='comments',
                requirement_value=50
            ),
            Badge(
                name='Tán Binh',
                description='Đạt cấp độ 2',
                icon='⭐',
                category='social',
                requirement_type='level',
                requirement_value=2
            ),
            
            # Level-based badges
            Badge(
                name='Cao Thủ',
                description='Đạt cấp độ 5',
                icon='🌟',
                category='social',
                requirement_type='level',
                requirement_value=5
            ),
            Badge(
                name='Chuyên Gia',
                description='Đạt cấp độ 10',
                icon='✨',
                category='special',
                requirement_type='level',
                requirement_value=10
            ),
            
            # Point-based badges
            Badge(
                name='Tích Cực',
                description='Đạt 1000 điểm',
                icon='🔥',
                category='social',
                requirement_type='points',
                requirement_value=1000
            ),
            Badge(
                name='Siêu Tích Cực',
                description='Đạt 5000 điểm',
                icon='💎',
                category='special',
                requirement_type='points',
                requirement_value=5000
            ),
            
            # Special badges
            Badge(
                name='Người Tiên Phong',
                description='Là một trong 100 thành viên đầu tiên',
                icon='🎖️',
                category='special',
                requirement_type='early_adopter',
                requirement_value=100
            ),
        ]
        
        try:
            for badge in badges:
                db.session.add(badge)
            db.session.commit()
            print(f"Successfully seeded {len(badges)} badges into database!")
            
            # Print all badges
            print("\nAvailable badges:")
            for badge in badges:
                print(f"  {badge.icon} {badge.name} - {badge.description}")
                
        except Exception as e:
            db.session.rollback()
            print(f"Error seeding badges: {e}")

if __name__ == '__main__':
    seed_badges()
