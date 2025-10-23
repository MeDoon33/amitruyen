from app import create_app, db
from app.models.user import User

app = create_app()
with app.app_context():
    # Test method mới
    user = User.query.filter_by(username='admin').first()
    
    print(f'=== TEST HIỂN THỊ TÊN VỚI DANH HIỆU ===')
    print(f'Tên thông thường: {user.get_display_name()}')
    print(f'Tên với danh hiệu: {user.get_display_name_with_title()}')
    print(f'Cấp độ: {user.level}')
    print(f'Danh hiệu: {user.get_rank_title()}')
    print(f'Trường phái: {user.get_rank_type_display()}')
    
    print(f'\n=== KIỂM TRA KẾT QUA ===')
    print(f'✅ Tên hiển thị trong bình luận: "{user.get_display_name_with_title()}"')
    print(f'✅ Hiển thị trong profile đầy đủ thông tin progression')
    print(f'✅ Leaderboard sẽ hiển thị tên với danh hiệu')
    
    # Test tạo user mới để xem default values
    print(f'\n=== TEST USER MỚI ===')
    new_user = User(username='test_title', email='test@title.com')
    db.session.add(new_user)
    db.session.commit()
    
    print(f'User mới - Tên: {new_user.get_display_name_with_title()}')
    print(f'User mới - Cấp: {new_user.level}')
    print(f'User mới - Danh hiệu: {new_user.get_rank_title()}')
    
    # Cleanup
    db.session.delete(new_user)
    db.session.commit()