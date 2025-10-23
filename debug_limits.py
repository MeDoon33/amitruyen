from app import create_app, db
from app.models.user import User, UserActivity
from app.services.progression import ProgressionService
from datetime import datetime

app = create_app()
with app.app_context():
    user = User.query.filter_by(username='admin').first()
    
    # Kiểm tra số lượng chapter đọc hôm nay
    today = datetime.utcnow().date()
    today_reads = UserActivity.query.filter(
        UserActivity.user_id == user.id,
        UserActivity.activity_type == 'read_chapter',
        db.func.date(UserActivity.created_at) == today
    ).count()
    
    print(f'=== THỐNG KÊ HOẠT ĐỘNG HÔM NAY ===')
    print(f'Số chương đã đọc hôm nay: {today_reads}')
    print(f'Giới hạn đọc: 10 chương/ngày')
    print(f'Còn lại: {max(0, 10 - today_reads)} chương')
    
    # Kiểm tra logic _can_earn_points
    can_earn = ProgressionService._can_earn_points(user.id, 'read_chapter', 999)
    print(f'Có thể nhận điểm đọc: {can_earn}')
    
    # Thử với activity khác
    can_comment = ProgressionService._can_earn_points(user.id, 'comment', 999)
    print(f'Có thể nhận điểm comment: {can_comment}')
    
    # Thử test với comment
    print(f'\n=== TEST COMMENT ===')
    result = ProgressionService.award_points(user.id, 'comment', 999)
    print(f'Kết quả comment: {result}')
    
    # Kiểm tra tất cả activities hôm nay
    print(f'\n=== TẤT CẢ ACTIVITIES HÔM NAY ===')
    today_activities = UserActivity.query.filter(
        UserActivity.user_id == user.id,
        db.func.date(UserActivity.created_at) == today
    ).all()
    
    activity_counts = {}
    for activity in today_activities:
        if activity.activity_type not in activity_counts:
            activity_counts[activity.activity_type] = 0
        activity_counts[activity.activity_type] += 1
    
    for activity_type, count in activity_counts.items():
        print(f'{activity_type}: {count}')