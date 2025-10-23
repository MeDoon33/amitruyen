#!/usr/bin/env python3
"""
Test progression service award_points method
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.services.progression import ProgressionService
from app.models.user import User

def test_progression_service():
    """Test ProgressionService.award_points method"""
    app = create_app()
    
    with app.app_context():
        print("=== TEST PROGRESSION SERVICE ===")
        
        # Test với user admin
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print(f"User: {admin.username} - Level {admin.level} - Points {admin.points}")
            
            # Test award_points method
            result = ProgressionService.award_points(admin.id, 'upload_comic', reference_id=999)
            
            if result:
                print("✅ Award points thành công!")
                print(f"Points earned: {result['points_earned']}")
                print(f"Total points: {result['total_points']}")
                print(f"Level up: {result['level_up']}")
                print(f"New level: {result['new_level']}")
            else:
                print("❌ Award points thất bại!")
        else:
            print("Không tìm thấy admin user!")

if __name__ == '__main__':
    test_progression_service()