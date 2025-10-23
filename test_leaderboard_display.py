#!/usr/bin/env python3
"""
Test leaderboard display with rank titles and logos
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.user import User

def test_leaderboard_display():
    """Test leaderboard API response format"""
    app = create_app()
    
    with app.app_context():
        print("=== TEST LEADERBOARD DISPLAY ===")
        
        # Get top 5 users by points
        top_users = User.query.order_by(User.points.desc(), User.level.desc()).limit(5).all()
        
        print("Top 5 users leaderboard:")
        for i, user in enumerate(top_users, 1):
            print(f"\n#{i} {user.username}")
            print(f"   Display Name: {user.get_display_name()}")
            print(f"   With Title: {user.get_display_name_with_title()}")
            print(f"   With Styled Title: {user.get_display_name_with_styled_title()}")
            print(f"   Level: {user.level}")
            print(f"   Points: {user.points}")
            print(f"   Rank Type: {user.get_rank_type_display()}")
            
            rank_title = user.get_rank_title()
            print(f"   Rank Title: {rank_title}")
            
            logo_url = user.get_rank_logo()
            if logo_url:
                print(f"   Logo: {'✅ Has logo' if logo_url else '❌ No logo'}")
        
        print("\n=== EXPECTED OUTPUT ===")
        print("Leaderboard sẽ hiển thị:")
        print("- Username với styled title (gradient + logo)")  
        print("- Level, rank type và points")
        print("- Logo Honor of Kings cho Vương Giả path")

if __name__ == '__main__':
    test_leaderboard_display()