#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Seed only rank titles for Tu Tiên and Ma Vương paths
"""

from app import create_app, db
from app.models.user import RankTitle

def seed_missing_rank_titles():
    app = create_app()
    with app.app_context():
        print("🌱 Seeding missing rank titles...")
        
        # Tu Tiên (Cultivation) path
        tu_tien_titles = [
            (1, "Luyện Khí"),     # Xanh lá
            (2, "Trúc Cơ"),       # Xanh nước biển  
            (3, "Kim Đan"),       # Vàng
            (4, "Nguyên Anh"),    # Xanh ngọc
            (5, "Hóa Thần"),      # Tím
            (6, "Luyện Hư"),      # Vàng kim
            (7, "Hợp Thể"),       # Vàng trắng
            (8, "Đại Thừa"),      # Vàng trắng
            (9, "Chân Tiên"),     # Vàng trắng
            (10, "Kim Tiên"),     # Vàng trắng
        ]
        
        # Ma Vương (Demon Lord) path
        ma_vuong_titles = [
            (1, "Ma Đồ"),         # Xanh lá
            (2, "Ma Binh"),       # Xanh nước biển
            (3, "Ma Tướng"),      # Vàng
            (4, "Ma Vương"),      # Xanh ngọc
            (5, "Ma Hoàng"),      # Tím
            (6, "Ma Đế"),         # Vàng kim
            (7, "Ma Tôn"),        # Vàng trắng
            (8, "Ma Thần"),       # Vàng trắng
            (9, "Ma Chúa"),       # Vàng trắng
            (10, "Ma Tổ"),        # Vàng trắng
        ]
        
        # Xóa titles cũ nếu có
        RankTitle.query.filter_by(rank_type='Tu Tiên').delete()
        RankTitle.query.filter_by(rank_type='Ma Vương').delete()
        print("✅ Cleared existing Tu Tiên and Ma Vương titles")
        
        # Insert Tu Tiên titles
        for level, title in tu_tien_titles:
            rank_title = RankTitle(
                rank_type='Tu Tiên',
                level=level,
                title=title,
                color='#22c55e'  # Default color
            )
            db.session.add(rank_title)
        
        # Insert Ma Vương titles
        for level, title in ma_vuong_titles:
            rank_title = RankTitle(
                rank_type='Ma Vương',
                level=level,
                title=title,
                color='#ef4444'  # Default color
            )
            db.session.add(rank_title)
        
        try:
            db.session.commit()
            print("✅ Successfully seeded Tu Tiên and Ma Vương titles!")
            
            # Verify
            tu_tien_count = RankTitle.query.filter_by(rank_type='Tu Tiên').count()
            ma_vuong_count = RankTitle.query.filter_by(rank_type='Ma Vương').count()
            vuong_gia_count = RankTitle.query.filter_by(rank_type='Vương Giả').count()
            
            print(f"📊 Rank titles count:")
            print(f"  Tu Tiên: {tu_tien_count}")
            print(f"  Ma Vương: {ma_vuong_count}")
            print(f"  Vương Giả: {vuong_gia_count}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()

if __name__ == '__main__':
    seed_missing_rank_titles()