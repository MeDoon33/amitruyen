from app import create_app, db
from app.models.user import User, UserActivity
from app.models.comic import UserReadHistory
from app.services.progression import ProgressionService

app = create_app()
with app.app_context():
    # Kiểm tra user admin
    user = User.query.filter_by(username='admin').first()
    print(f'=== THÔNG TIN USER ===')
    print(f'Username: {user.username}')
    print(f'Level: {user.level}')
    print(f'Points: {user.points}')
    print(f'Rank: {user.get_rank_title()}')
    
    # Kiểm tra các hoạt động gần đây
    print(f'\n=== HOẠT ĐỘNG GẦN ĐÂY ===')
    activities = UserActivity.query.filter_by(user_id=user.id).order_by(UserActivity.created_at.desc()).limit(10).all()
    for activity in activities:
        print(f'{activity.created_at}: {activity.activity_type} - {activity.points_earned} điểm')
    
    # Kiểm tra lịch sử đọc
    print(f'\n=== LỊCH SỬ ĐỌC ===')
    read_history = UserReadHistory.query.filter_by(user_id=user.id).order_by(UserReadHistory.created_at.desc()).limit(5).all()
    for history in read_history:
        print(f'{history.created_at}: Comic {history.comic_id}, Chapter {history.chapter_id}')
    
    # Test thủ công award points
    print(f'\n=== TEST THÊM ĐIỂM ===')
    result = ProgressionService.award_points(user.id, 'read_chapter', 999)
    print(f'Kết quả: {result}')
    
    # Kiểm tra lại points
    db.session.refresh(user)
    print(f'Points sau test: {user.points}')