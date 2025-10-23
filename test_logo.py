#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import create_app
from app.models.user import User

def test_vuong_gia_logo():
    app = create_app()
    with app.app_context():
        # Test với user Vương Giả
        vuong_gia_user = User.query.filter_by(username='test_vuong_gia').first()
        if vuong_gia_user:
            print("🏆 Testing Vương Giả Logo Features:")
            print(f"   Username: {vuong_gia_user.username}")
            print(f"   Rank Type: {vuong_gia_user.rank_type}")
            print(f"   Level: {vuong_gia_user.level}")
            print(f"   Logo URL: {vuong_gia_user.get_rank_logo()}")
            print(f"   Display with Logo: {vuong_gia_user.get_display_name_with_logo_and_title()}")
        
        # Test với admin user nếu đã chuyển sang Vương Giả
        admin_user = User.query.filter_by(role='admin').first()
        if admin_user and admin_user.rank_type == 'vuong_gia':
            print(f"\n👑 Testing Admin Vương Giả:")
            print(f"   Username: {admin_user.username}")
            print(f"   Logo URL: {admin_user.get_rank_logo()}")
            print(f"   Display: {admin_user.get_display_name_with_logo_and_title()}")

if __name__ == '__main__':
    test_vuong_gia_logo()