from app import db
from app.models.user import RankTitle, Badge


def seed_rank_titles():
    """Seed rank titles for different progression paths"""
    
    # Tu Tiên (Cultivation) path
    tu_tien_titles = [
        (1, "Luyện Khí", "#8B4513"),  # Brown
        (2, "Trúc Cơ", "#A0522D"), 
        (3, "Kim Đan", "#DAA520"),   # Goldenrod
        (4, "Nguyên Anh", "#FF8C00"), # Dark Orange
        (5, "Hóa Thần", "#FF6347"),  # Tomato
        (6, "Luyện Hư", "#9370DB"),  # Medium Purple
        (7, "Hợp Thể", "#8A2BE2"),   # Blue Violet
        (8, "Đại Thừa", "#4B0082"),  # Indigo
        (9, "Độ Kiếp", "#800080"),   # Purple
        (10, "Tiên Nhân", "#FFD700"), # Gold
    ]
    
    # Ma Vương (Demon Lord) path
    ma_vuong_titles = [
        (1, "Ma Đồ", "#2F2F2F"),     # Dark Gray
        (2, "Ma Binh", "#8B0000"),   # Dark Red
        (3, "Ma Tướng", "#A0522D"),  # Saddle Brown
        (4, "Ma Vương", "#8B0000"),  # Dark Red
        (5, "Ma Đế", "#8B008B"),     # Dark Magenta
        (6, "Ma Tôn", "#4B0082"),    # Indigo
        (7, "Ma Thần", "#800080"),   # Purple
        (8, "Ma Hoàng", "#9400D3"),  # Violet
        (9, "Ma Chúa", "#8A2BE2"),   # Blue Violet
        (10, "Ma Giới Chủ", "#000000"), # Black
    ]
    
    # Vương Giả (Royal) path - replaced Pháp Sư
    vuong_gia_titles = [
        (1, "Thanh Đồng", "#22c55e"),    # Green
        (2, "Bạch Ngân", "#06b6d4"),     # Blue
        (3, "Hoàng Kim", "#fbbf24"),     # Yellow
        (4, "Bạch Kim", "#14b8a6"),      # Teal
        (5, "Kim Cương", "#a855f7"),     # Purple
        (6, "Chí Tôn", "#d97706"),       # Gold
        (7, "Vương Giả", "#fef3c7"),     # Light Golden
        (8, "Vương Giả", "#fef3c7"),     # Light Golden
        (9, "Vương Giả", "#fef3c7"),     # Light Golden
        (10, "Vương Giả", "#fef3c7"),    # Light Golden
    ]
    
    # Clear existing data
    RankTitle.query.delete()
    
    # Insert Tu Tiên titles
    for level, title, color in tu_tien_titles:
        rank_title = RankTitle(
            rank_type='tu_tien',
            level=level,
            title=title,
            color=color
        )
        db.session.add(rank_title)
    
    # Insert Ma Vương titles
    for level, title, color in ma_vuong_titles:
        rank_title = RankTitle(
            rank_type='ma_vuong',
            level=level,
            title=title,
            color=color
        )
        db.session.add(rank_title)
    
    # Insert Vương Giả titles
    for level, title, color in vuong_gia_titles:
        rank_title = RankTitle(
            rank_type='vuong_gia',
            level=level,
            title=title,
            color=color
        )
        db.session.add(rank_title)


def seed_badges():
    """Seed initial badges/achievements"""
    
    badges_data = [
        # Reading badges
        {
            'name': 'Người Đọc Mới',
            'description': 'Đọc chương đầu tiên',
            'icon': '📖',
            'category': 'reading',
            'requirement_type': 'reads',
            'requirement_value': 1
        },
        {
            'name': 'Nghiện Đọc',
            'description': 'Đọc 100 chương',
            'icon': '📚',
            'category': 'reading',
            'requirement_type': 'reads',
            'requirement_value': 100
        },
        {
            'name': 'Thư Khố',
            'description': 'Đọc 500 chương',
            'icon': '📜',
            'category': 'reading',
            'requirement_type': 'reads',
            'requirement_value': 500
        },
        
        # Commenting badges
        {
            'name': 'Người Bình Luận',
            'description': 'Viết bình luận đầu tiên',
            'icon': '💬',
            'category': 'commenting',
            'requirement_type': 'comments',
            'requirement_value': 1
        },
        {
            'name': 'Talkative',
            'description': 'Viết 50 bình luận',
            'icon': '🗨️',
            'category': 'commenting',
            'requirement_type': 'comments',
            'requirement_value': 50
        },
        
        # Level badges
        {
            'name': 'Tân Binh',
            'description': 'Đạt cấp độ 2',
            'icon': '⭐',
            'category': 'progression',
            'requirement_type': 'level',
            'requirement_value': 2
        },
        {
            'name': 'Cao Thủ',
            'description': 'Đạt cấp độ 5',
            'icon': '🌟',
            'category': 'progression',
            'requirement_type': 'level',
            'requirement_value': 5
        },
        {
            'name': 'Chuyên Gia',
            'description': 'Đạt cấp độ 10',
            'icon': '✨',
            'category': 'progression',
            'requirement_type': 'level',
            'requirement_value': 10
        },
        
        # Points badges
        {
            'name': 'Tích Cực',
            'description': 'Đạt 1000 điểm',
            'icon': '🔥',
            'category': 'activity',
            'requirement_type': 'points',
            'requirement_value': 1000
        },
        {
            'name': 'Siêu Tích Cực',
            'description': 'Đạt 5000 điểm',
            'icon': '🚀',
            'category': 'activity',
            'requirement_type': 'points',
            'requirement_value': 5000
        },
    ]
    
    # Clear existing badges
    Badge.query.delete()
    
    # Insert badges
    for badge_data in badges_data:
        badge = Badge(**badge_data)
        db.session.add(badge)


def seed_all():
    """Seed all progression data"""
    print("Seeding rank titles...")
    seed_rank_titles()
    
    print("Seeding badges...")
    seed_badges()
    
    db.session.commit()
    print("All progression data seeded successfully!")


if __name__ == '__main__':
    from app import create_app
    
    app = create_app()
    with app.app_context():
        seed_all()