#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import create_app, db
from app.models.user import User

def check_admin_user():
    app = create_app()
    with app.app_context():
        admin = User.query.filter_by(role='admin').first()
        if admin:
            print(f"👑 Admin user: {admin.username}")
            print(f"📊 Current rank: {admin.rank_type} - Level {admin.level}")
            print(f"🏆 Title: {admin.get_rank_title()}")
            print(f"💎 Points: {admin.points}")
            print(f"🎨 CSS Class: {admin.get_rank_title_css_class()}")
            print(f"📝 Display: {admin.get_display_name_with_styled_title()}")
            
            # Option to change to Vương Giả
            if admin.rank_type != 'vuong_gia':
                print(f"\n💡 Want to change to Vương Giả? (y/n): ", end="")
                choice = input()
                if choice.lower() == 'y':
                    admin.rank_type = 'vuong_gia'
                    db.session.commit()
                    print(f"✅ Changed admin to Vương Giả!")
                    print(f"🏆 New title: {admin.get_rank_title()}")
        else:
            print("❌ No admin user found")

if __name__ == '__main__':
    check_admin_user()