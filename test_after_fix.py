from app import create_app, db
from app.models.user import User
from app.services.progression import ProgressionService

app = create_app()
with app.app_context():
    user = User.query.filter_by(username='admin').first()
    print(f'Trước test: {user.points} điểm')
    
    # Test đọc chương mới
    result = ProgressionService.award_points(user.id, 'read_chapter', 1001)
    print(f'Kết quả đọc chương: {result}')
    
    db.session.refresh(user)
    print(f'Sau test: {user.points} điểm')
    print(f'Progress to next level: {user.get_progress_to_next_level():.1f}%')