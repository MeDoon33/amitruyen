#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test Vương Giả rank system
"""

from app import create_app, db
from app.models.user import User, RankTitle

def test_vuong_gia_system():
    app = create_app()
    with app.app_context():
        print("🎯 Testing Vương Giả Rank System")
        print("=" * 50)
        
        # Test 1: Verify rank titles
        print("\n📋 Vương Giả Rank Titles:")
        vuong_gia_titles = RankTitle.query.filter_by(rank_type='Vương Giả').order_by(RankTitle.level).all()
        
        expected_titles = {
            1: 'Thanh Đồng',   # Xanh lá
            2: 'Bạch Ngân',    # Xanh nước biển
            3: 'Hoàng Kim',    # Vàng
            4: 'Bạch Kim',     # Xanh ngọc
            5: 'Kim Cương',    # Tím
            6: 'Chí Tôn',      # Vàng kim
            7: 'Vương Giả',    # Vàng trắng
            8: 'Vương Giả',    # Vàng trắng
            9: 'Vương Giả',    # Vàng trắng
            10: 'Vương Giả',   # Vàng trắng
        }
        
        success = True
        for title in vuong_gia_titles:
            expected = expected_titles.get(title.level, 'Unknown')
            status = "✅" if title.title == expected else "❌"
            print(f"   {status} Level {title.level}: {title.title} (Expected: {expected})")
            if title.title != expected:
                success = False
        
        # Test 2: Create test user with Vương Giả rank
        print(f"\n👤 Testing User Creation with Vương Giả rank:")
        
        # Check if test user exists
        test_user = User.query.filter_by(username='test_vuong_gia').first()
        if not test_user:
            test_user = User(
                username='test_vuong_gia',
                email='test@vuonggia.com',
                rank_type='vuong_gia',
                level=1,
                points=0
            )
            test_user.set_password('password123')
            db.session.add(test_user)
            db.session.commit()
            print("   ✅ Created test user")
        else:
            print("   ℹ️ Test user already exists")
        
        # Test 3: Test rank progression through levels
        print(f"\n⭐ Testing Rank Progression:")
        levels_to_test = [1, 3, 5, 7, 10]
        
        for level in levels_to_test:
            test_user.level = level
            test_user.points = level * 100  # Simple point calculation
            
            rank_title = test_user.get_rank_title()
            css_class = test_user.get_rank_title_css_class()
            display_name = test_user.get_display_name_with_styled_title()
            
            print(f"   Level {level}:")
            print(f"     🏆 Title: {rank_title}")
            print(f"     🎨 CSS Class: {css_class}")
            print(f"     📝 Display: {display_name}")
            print()
        
        # Test 4: Color mapping verification
        print(f"📊 Color Mapping Verification:")
        color_map = {
            1: "Xanh lá (level-1)",
            2: "Xanh nước biển (level-2)", 
            3: "Vàng (level-3)",
            4: "Xanh ngọc (level-4)",
            5: "Tím (level-5)",
            6: "Vàng kim (level-6)",
            7: "Vàng trắng (level-7)",
            8: "Vàng trắng (level-8)",
            9: "Vàng trắng (level-9)",
            10: "Vàng trắng (level-10)",
        }
        
        for level, color_desc in color_map.items():
            test_user.level = level
            css_class = test_user.get_rank_title_css_class()
            expected_level_class = f"level-{level}"
            has_level_class = expected_level_class in css_class
            status = "✅" if has_level_class else "❌"
            print(f"   {status} Level {level}: {color_desc} -> {css_class}")
        
        db.session.rollback()  # Reset test user changes
        
        print(f"\n🎉 Vương Giả system test completed!")
        return success

if __name__ == '__main__':
    test_vuong_gia_system()