#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test Gradient Titles Display
Kiểm tra hiển thị gradient cho danh hiệu
"""

from app import create_app, db
from app.models.user import User

def test_gradient_titles():
    app = create_app()
    with app.app_context():
        # Test với các user khác nhau
        users = User.query.limit(5).all()
        
        print("🎨 TEST GRADIENT TITLES")
        print("=" * 60)
        
        for user in users:
            print(f"\n👤 User: {user.username}")
            print(f"   Rank Type: {user.rank_type}")
            print(f"   Level: {user.level}")
            print(f"   Rank Title: {user.get_rank_title()}")
            print(f"   CSS Class: {user.get_rank_title_css_class()}")
            print(f"   Normal Display: {user.get_display_name_with_title()}")
            print(f"   Styled Display: {user.get_display_name_with_styled_title()}")
            print("-" * 40)
        
        # Test với từng rank type
        print("\n🌈 CSS CLASSES BY RANK TYPE:")
        rank_types = ['Tu Tiên', 'Ma Vương', 'Pháp Sư']
        for rank_type in rank_types:
            user = User.query.filter_by(rank_type=rank_type).first()
            if user:
                print(f"   {rank_type}: {user.get_rank_title_css_class()}")
        
        # Test với level cao
        print("\n⭐ HIGH LEVEL EFFECTS:")
        for level in [1, 3, 6, 8, 10]:
            test_user = User.query.first()
            if test_user:
                original_level = test_user.level
                test_user.level = level
                print(f"   Level {level}: {test_user.get_rank_title_css_class()}")
                test_user.level = original_level

if __name__ == '__main__':
    test_gradient_titles()