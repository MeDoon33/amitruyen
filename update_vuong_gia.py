#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Update Pháp Sư path to Vương Giả path with new ranks
"""

from app import create_app, db
from app.models.user import RankTitle, User

def update_to_vuong_gia():
    app = create_app()
    with app.app_context():
        print("🔄 Updating Pháp Sư to Vương Giả...")
        
        # Xóa các rank titles cũ của Pháp Sư
        old_phap_su_titles = RankTitle.query.filter_by(rank_type='Pháp Sư').all()
        for title in old_phap_su_titles:
            db.session.delete(title)
        print(f"✅ Deleted {len(old_phap_su_titles)} old Pháp Sư titles")
        
        # Thêm rank titles mới cho Vương Giả
        vuong_gia_titles = [
            (1, 'Thanh Đồng'),  # Xanh lá
            (2, 'Bạch Ngân'),   # Xanh nước biển  
            (3, 'Hoàng Kim'),   # Vàng
            (4, 'Bạch Kim'),    # Xanh ngọc
            (5, 'Kim Cương'),   # Tím
            (6, 'Chí Tôn'),     # Vàng kim
            (7, 'Vương Giả'),   # Vàng trắng
            (8, 'Vương Giả'),   # Vàng trắng
            (9, 'Vương Giả'),   # Vàng trắng
            (10, 'Vương Giả'),  # Vàng trắng
        ]
        
        for level, title in vuong_gia_titles:
            rank_title = RankTitle(
                rank_type='Vương Giả',
                level=level,
                title=title
            )
            db.session.add(rank_title)
        
        # Cập nhật users hiện có từ Pháp Sư sang Vương Giả
        phap_su_users = User.query.filter_by(rank_type='Pháp Sư').all()
        for user in phap_su_users:
            user.rank_type = 'Vương Giả'
            print(f"   Updated user {user.username} to Vương Giả")
        
        # Cập nhật users có rank_type 'phap_su' (lowercase)
        phap_su_users_lower = User.query.filter_by(rank_type='phap_su').all()
        for user in phap_su_users_lower:
            user.rank_type = 'vuong_gia'
            print(f"   Updated user {user.username} to vuong_gia")
        
        try:
            db.session.commit()
            print("✅ Successfully updated to Vương Giả path!")
            
            # Hiển thị rank titles mới
            print("\n📋 New Vương Giả rank titles:")
            new_titles = RankTitle.query.filter_by(rank_type='Vương Giả').order_by(RankTitle.level).all()
            for title in new_titles:
                print(f"   Level {title.level}: {title.title}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()

if __name__ == '__main__':
    update_to_vuong_gia()