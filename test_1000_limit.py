from app import create_app, db
from app.models.user import User, UserActivity
from app.services.progression import ProgressionService
from datetime import datetime

app = create_app()
with app.app_context():
    user = User.query.filter_by(username='admin').first()
    
    # Kiểm tra số lượng chapter đọc hôm nay
    today = datetime.now().date()
    today_reads = UserActivity.query.filter(
        UserActivity.user_id == user.id,
        UserActivity.activity_type == 'read_chapter',
        db.func.date(UserActivity.created_at) == today
    ).count()
    
    print(f'=== GIỚI HẠN MỚI ===')
    print(f'Số chương đã đọc hôm nay: {today_reads}')
    print(f'Giới hạn mới: 200 chương/ngày')
    print(f'Còn lại: {200 - today_reads} chương')
    
    # Test có thể nhận điểm không
    can_earn = ProgressionService._can_earn_points(user.id, 'read_chapter', 9999)
    print(f'Có thể nhận điểm đọc: {can_earn}')
    
    # Test thực tế
    print(f'\n=== TEST ĐỌC CHƯƠNG ===')
    old_points = user.points
    result = ProgressionService.award_points(user.id, 'read_chapter', 9999)
    print(f'Kết quả: {result}')
    
    db.session.refresh(user)
    print(f'Points: {old_points} → {user.points} (+{user.points - old_points})')
    print(f'Progress: {user.get_progress_to_next_level():.1f}%')
    
    print(f'\n✅ Bây giờ bạn có thể đọc thoải mái {200 - today_reads - 1} chương nữa hôm nay!')