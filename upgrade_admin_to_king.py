#!/usr/bin/env python3
"""
Script để nâng cấp Admin lên cấp độ Vương Giả (Level 7)
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User

def upgrade_admin_to_king():
    """Nâng cấp admin lên Vương Giả (Level 7)"""
    app = create_app()
    
    with app.app_context():
        # Tìm user admin
        admin_user = User.query.filter_by(username='admin').first()
        
        if not admin_user:
            print("❌ Không tìm thấy user admin!")
            return
        
        print("=== THÔNG TIN TRƯỚC KHI NÂNG CẤP ===")
        print(f"Username: {admin_user.username}")
        print(f"Display Name: {admin_user.display_name}")
        print(f"Current Level: {admin_user.level}")
        print(f"Current Rank Type: {admin_user.rank_type}")
        
        current_rank = admin_user.get_rank_title()
        if current_rank:
            print(f"Current Rank Title: {current_rank.title if hasattr(current_rank, 'title') else str(current_rank)}")
        
        current_logo = admin_user.get_rank_logo()
        print(f"Current Logo: {current_logo}")
        
        # Nâng cấp lên Level 7 (Vương Giả)
        admin_user.level = 7
        admin_user.points = 7000  # Đặt điểm phù hợp với level 7
        
        # Commit changes
        db.session.commit()
        
        print("\n=== THÔNG TIN SAU KHI NÂNG CẤP ===")
        print(f"New Level: {admin_user.level}")
        print(f"New Points: {admin_user.points}")
        
        new_rank = admin_user.get_rank_title()
        if new_rank:
            print(f"New Rank Title: {new_rank.title if hasattr(new_rank, 'title') else str(new_rank)}")
        
        new_logo = admin_user.get_rank_logo()
        print(f"New Logo: {new_logo}")
        
        # Kiểm tra display methods
        print(f"\nDisplay with styled title: {admin_user.get_display_name_with_styled_title()}")
        
        print("\n✅ Admin đã được nâng cấp lên Vương Giả!")

if __name__ == '__main__':
    upgrade_admin_to_king()