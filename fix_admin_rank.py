#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fix admin user rank type to vuong_gia
"""

from app import create_app, db
from app.models.user import User

def fix_admin_rank_type():
    app = create_app()
    with app.app_context():
        admin = User.query.filter_by(role='admin').first()
        
        if admin:
            print(f"👑 Admin user: {admin.username}")
            print(f"📊 Current rank_type: {admin.rank_type}")
            print(f"📊 Current level: {admin.level}")
            print(f"💎 Current points: {admin.points}")
            
            # Update to vuong_gia
            admin.rank_type = 'vuong_gia'
            
            db.session.commit()
            
            print(f"✅ Updated admin rank_type to: {admin.rank_type}")
            print(f"🏆 Current title: {admin.get_rank_title()}")
            print(f"🎨 CSS class: {admin.get_rank_title_css_class()}")
            print(f"🖼️  Logo: {admin.get_rank_logo()}")
        else:
            print("❌ No admin user found")

if __name__ == '__main__':
    fix_admin_rank_type()