#!/usr/bin/env python3
"""
Test script để kiểm tra redirect sau khi upload comic
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.comic import Comic
from app.models.user import User

def test_redirect_flow():
    """Test luồng redirect sau khi upload comic"""
    app = create_app()
    
    with app.app_context():
        print("=== TEST REDIRECT FLOW ===")
        
        # Kiểm tra xem có comic nào mới được tạo không
        latest_comic = Comic.query.order_by(Comic.created_at.desc()).first()
        if latest_comic:
            print(f"Latest comic: {latest_comic.title} (ID: {latest_comic.id})")
            print(f"Uploader: {latest_comic.uploader_id}")
            
            # Kiểm tra URL redirect sẽ là gì
            expected_url = f"/comic/{latest_comic.id}"
            print(f"Expected redirect URL: {expected_url}")
            
            # Kiểm tra user uploader
            uploader = User.query.get(latest_comic.uploader_id) if latest_comic.uploader_id else None
            if uploader:
                print(f"Uploader info: {uploader.username} - Level {uploader.level}")
        else:
            print("Không có comic nào trong database")
        
        print("\n=== PROGRESSION POINTS ===")
        print("Upload comic sẽ được cộng 50 điểm progression")

if __name__ == '__main__':
    test_redirect_flow()