#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Upgrade Admin User to Hóa Thần Level
"""

from app import create_app, db
from app.models.user import User

def upgrade_admin_to_hoa_than():
    app = create_app()
    with app.app_context():
        # Find admin user
        admin = User.query.filter_by(username='admin').first()
        
        if not admin:
            print("❌ Admin user not found!")
            return
        
        print(f"📊 BEFORE UPGRADE:")
        print(f"   Username: {admin.username}")
        print(f"   Display Name: {admin.get_display_name()}")
        print(f"   Current Level: {admin.level}")
        print(f"   Current Rank: {admin.get_rank_title()}")
        print(f"   Current Points: {admin.points}")
        print(f"   CSS Class: {admin.get_rank_title_css_class()}")
        
        # Upgrade to level 5 (Hóa Thần)
        admin.level = 5
        admin.points = admin.get_required_points_for_level(5)
        
        try:
            db.session.commit()
            print(f"\n✅ UPGRADE SUCCESSFUL!")
            print(f"   New Level: {admin.level}")
            print(f"   New Rank: {admin.get_rank_title()}")
            print(f"   New Points: {admin.points}")
            print(f"   New CSS Class: {admin.get_rank_title_css_class()}")
            print(f"   Styled Display: {admin.get_display_name_with_styled_title()}")
        except Exception as e:
            print(f"❌ Error upgrading: {e}")
            db.session.rollback()

if __name__ == '__main__':
    upgrade_admin_to_hoa_than()