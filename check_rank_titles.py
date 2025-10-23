#!/usr/bin/env python3
"""
Check rank titles for Vương Giả in database
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.user import RankTitle

def check_rank_titles():
    """Check available rank titles for Vương Giả"""
    app = create_app()
    
    with app.app_context():
        print("=== KIỂM TRA RANK TITLES VƯƠNG GIẢ ===")
        
        vuong_gia_titles = RankTitle.query.filter_by(rank_type='Vương Giả').order_by(RankTitle.level).all()
        
        if vuong_gia_titles:
            print("Rank titles có sẵn:")
            for title in vuong_gia_titles:
                print(f"Level {title.level}: {title.title}")
            
            max_level = max([t.level for t in vuong_gia_titles])
            print(f"\nMax level có title: {max_level}")
            
            # Kiểm tra title cho level 16
            level_16_title = RankTitle.query.filter_by(rank_type='Vương Giả', level=16).first()
            print(f"Title cho level 16: {level_16_title.title if level_16_title else 'KHÔNG CÓ'}")
            
        else:
            print("Không có rank titles nào cho Vương Giả!")

if __name__ == '__main__':
    check_rank_titles()