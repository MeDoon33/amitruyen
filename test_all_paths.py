#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test hiển thị danh hiệu cho các loại tu luyện và logo
"""

from app import create_app, db
from app.models.user import User, RankTitle

def test_all_rank_paths():
    app = create_app()
    with app.app_context():
        print("🎯 Testing All Rank Path Displays")
        print("=" * 60)
        
        # Tạo test users cho từng path
        test_users = []
        paths = ['tu_tien', 'ma_vuong', 'vuong_gia']
        
        for path in paths:
            # Tạo hoặc lấy test user
            username = f"test_{path}"
            user = User.query.filter_by(username=username).first()
            
            if not user:
                user = User(
                    username=username,
                    email=f"{username}@test.com", 
                    rank_type=path,
                    level=1,
                    points=0
                )
                user.set_password('password123')
                db.session.add(user)
                print(f"✅ Created test user: {username}")
            else:
                user.rank_type = path
                print(f"♻️  Updated existing user: {username}")
            
            test_users.append(user)
        
        db.session.commit()
        
        # Test hiển thị cho từng path ở các level khác nhau
        test_levels = [1, 3, 5, 7, 10]
        
        for user in test_users:
            print(f"\n🔥 {user.get_rank_type_display()} Path - User: {user.username}")
            print("-" * 50)
            
            for level in test_levels:
                user.level = level
                user.points = level * 100
                
                rank_title = user.get_rank_title()
                css_class = user.get_rank_title_css_class()
                logo_url = user.get_rank_logo()
                display_with_logo = user.get_display_name_with_logo_and_title()
                username_with_logo = user.get_username_with_logo()
                
                print(f"  📊 Level {level}:")
                print(f"    🏆 Title: {rank_title}")
                print(f"    🎨 CSS: {css_class}")
                print(f"    🖼️  Logo: {logo_url if logo_url else 'No logo'}")
                print(f"    📝 Full Display: {display_with_logo}")
                print(f"    👤 Username + Logo: {username_with_logo}")
                print()
        
        # Test rank titles trong database
        print("\n📋 Available Rank Titles in Database:")
        print("=" * 60)
        
        for path in ['Tu Tiên', 'Ma Vương', 'Vương Giả']:
            titles = RankTitle.query.filter_by(rank_type=path).order_by(RankTitle.level).all()
            print(f"\n🎭 {path} Path:")
            if titles:
                for title in titles:
                    print(f"  Level {title.level}: {title.title}")
            else:
                print(f"  ❌ No titles found for {path}")
        
        # Test CSS classes cho từng rank type
        print(f"\n🎨 CSS Classes Test:")
        print("=" * 60)
        
        for user in test_users:
            user.level = 5  # Test level 5 cho tất cả
            css_class = user.get_rank_title_css_class()
            rank_type_display = user.get_rank_type_display()
            
            print(f"  {rank_type_display}: {css_class}")
        
        db.session.rollback()  # Reset changes
        
        print(f"\n✅ Test completed successfully!")
        return True

if __name__ == '__main__':
    test_all_rank_paths()