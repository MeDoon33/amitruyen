from app import create_app, db
from sqlalchemy import text
from app.models.user import User

app = create_app()
with app.app_context():
    print("=== KIỂM TRA BẢNG USERS ===\n")
    
    # 1. Cấu trúc bảng
    print("1. CẤU TRÚC BẢNG:")
    print("-" * 80)
    print(f"{'Tên cột':<15} | {'Kiểu dữ liệu':<20} | {'NULL':<5} | {'Key':<5} | {'Default':<15}")
    print("-" * 80)
    
    result = db.session.execute(text('DESCRIBE users'))
    for row in result:
        print(f"{row[0]:<15} | {row[1]:<20} | {row[2]:<5} | {row[3]:<5} | {str(row[4]) if row[4] else 'None':<15}")
    
    # 2. Số lượng users
    print(f"\n2. SỐ LƯỢNG USERS:")
    print("-" * 30)
    user_count = db.session.execute(text('SELECT COUNT(*) as count FROM users')).fetchone()
    print(f"Tổng số users: {user_count[0]}")
    
    # 3. Thông tin users
    print(f"\n3. DANH SÁCH USERS:")
    print("-" * 100)
    print(f"{'ID':<3} | {'Username':<15} | {'Email':<25} | {'Role':<10} | {'Level':<5} | {'Points':<7} | {'Rank Type':<10}")
    print("-" * 100)
    
    users = User.query.all()
    for user in users:
        print(f"{user.id:<3} | {user.username:<15} | {user.email:<25} | {user.role:<10} | {user.level:<5} | {user.points:<7} | {user.rank_type:<10}")
    
    # 4. Users có progression data
    print(f"\n4. PROGRESSION DATA:")
    print("-" * 70)
    print(f"{'Username':<15} | {'Level':<5} | {'Points':<7} | {'Rank Title':<15} | {'Progress %':<10}")
    print("-" * 70)
    
    for user in users:
        progress = user.get_progress_to_next_level()
        rank_title = user.get_rank_title()
        print(f"{user.username:<15} | {user.level:<5} | {user.points:<7} | {rank_title:<15} | {progress:.1f}%")
    
    # 5. User activities count
    print(f"\n5. HOẠT ĐỘNG USERS:")
    print("-" * 50)
    activities_count = db.session.execute(text('SELECT COUNT(*) FROM user_activities')).fetchone()
    print(f"Tổng số hoạt động: {activities_count[0]}")
    
    # Activities by user
    if activities_count[0] > 0:
        print(f"\n{'Username':<15} | {'Số hoạt động':<15}")
        print("-" * 32)
        activity_counts = db.session.execute(text('''
            SELECT u.username, COUNT(ua.id) as activity_count 
            FROM users u 
            LEFT JOIN user_activities ua ON u.id = ua.user_id 
            GROUP BY u.id, u.username
            ORDER BY activity_count DESC
        ''')).fetchall()
        
        for row in activity_counts:
            print(f"{row[0]:<15} | {row[1]:<15}")
    
    # 6. Badge counts
    print(f"\n6. BADGES:")
    print("-" * 40)
    badge_count = db.session.execute(text('SELECT COUNT(*) FROM user_badges')).fetchone()
    print(f"Tổng số badges đã nhận: {badge_count[0]}")
    
    if badge_count[0] > 0:
        print(f"\n{'Username':<15} | {'Số badges':<10}")
        print("-" * 27)
        badge_counts = db.session.execute(text('''
            SELECT u.username, COUNT(ub.id) as badge_count 
            FROM users u 
            LEFT JOIN user_badges ub ON u.id = ub.user_id 
            GROUP BY u.id, u.username
            ORDER BY badge_count DESC
        ''')).fetchall()
        
        for row in badge_counts:
            print(f"{row[0]:<15} | {row[1]:<10}")

print("\n=== HOÀN THÀNH KIỂM TRA ===")