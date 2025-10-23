#!/usr/bin/env python3
"""
Test script để kiểm tra logo mới cho Vương Giả
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.user import User

def test_new_logo():
    """Test logo mới cho Vương Giả"""
    app = create_app()
    
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        
        if admin:
            print("=== KIỂM TRA LOGO MỚI ===")
            print(f"Level: {admin.level}")
            print(f"New Logo URL: {admin.get_rank_logo()}")
            
            expected = 'https://vuonggiavinhdieu.net/wp-content/uploads/2025/08/TIER-MASTER-2-HONOR-OF-KINGS-150x150.webp'
            print(f"Expected URL: {expected}")
            print(f"Match: {admin.get_rank_logo() == expected}")
            
            print(f"\nDisplay: {admin.get_display_name_with_styled_title()}")
        else:
            print("Không tìm thấy admin user!")

if __name__ == '__main__':
    test_new_logo()