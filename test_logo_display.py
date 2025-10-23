#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test logo display methods
"""

from app import create_app
from app.models.user import User

def test_logo_display():
    app = create_app()
    with app.app_context():
        admin = User.query.filter_by(role='admin').first()
        
        print(f"👑 Admin user: {admin.username}")
        print(f"📊 Rank type: {admin.rank_type}")
        print(f"📊 Level: {admin.level}")
        print(f"🏆 Rank title: {admin.get_rank_title()}")
        print(f"🖼️  Logo URL: {admin.get_rank_logo()}")
        print(f"🎨 CSS class: {admin.get_rank_title_css_class()}")
        print()
        print("📝 Display methods:")
        print("1. get_display_name():", admin.get_display_name())
        print("2. get_display_name_with_styled_title():")
        print("  ", admin.get_display_name_with_styled_title())
        print("3. get_display_name_with_logo_and_title():")
        print("  ", admin.get_display_name_with_logo_and_title())
        print("4. get_username_with_logo():")
        print("  ", admin.get_username_with_logo())

if __name__ == '__main__':
    test_logo_display()