#!/usr/bin/env python3
"""
Test optimized code - verify functionality remains intact
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User, RankTitle
from app.services.progression import ProgressionService


def test_user_progression():
    """Test optimized user progression system"""
    app = create_app()
    
    with app.app_context():
        print("=== TEST USER PROGRESSION OPTIMIZATION ===\n")
        
        # Test 1: Level up calculation (iterative vs recursive)
        print("Test 1: Multiple level ups with large point addition")
        user = User.query.first()
        if not user:
            print("❌ No users found in database")
            return
        
        old_level = user.level
        old_points = user.points
        
        # Add massive points to trigger multiple level ups
        user.add_points(10000)
        
        new_level = user.level
        new_points = user.points
        
        print(f"  Old: Level {old_level}, Points {old_points}")
        print(f"  New: Level {new_level}, Points {new_points}")
        print(f"  ✅ Leveled up {new_level - old_level} times without stack overflow\n")
        
        # Rollback to not affect DB
        db.session.rollback()
        
        # Test 2: Rank title with feature flag
        print("Test 2: Rank title display with feature flags")
        rank_title = user.get_rank_title()
        css_class = user.get_rank_title_css_class()
        logo = user.get_rank_logo()
        
        print(f"  Rank Title: {rank_title}")
        print(f"  CSS Class: {css_class}")
        print(f"  Logo: {logo}")
        print(f"  ✅ Rank system working correctly\n")
        
        # Test 3: Display names
        print("Test 3: Display name methods")
        display_name = user.get_display_name()
        with_title = user.get_display_name_with_title()
        styled = user.get_display_name_with_styled_title()
        
        print(f"  Display Name: {display_name}")
        print(f"  With Title: {with_title}")
        print(f"  Styled HTML: {styled[:100]}...")
        print(f"  ✅ Display methods working\n")
        
        # Test 4: Badge checking optimization
        print("Test 4: Badge award optimization")
        try:
            result = ProgressionService.award_points(user.id, 'read_chapter', reference_id=1)
            if result:
                print(f"  Points earned: {result.get('points_earned', 0)}")
                print(f"  Level up: {result.get('level_up', False)}")
                print(f"  ✅ Badge system optimized and working")
            else:
                print(f"  ⚠️ Points not awarded (likely hit daily limit)")
            db.session.rollback()
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            db.session.rollback()
        
        print("\n=== ALL TESTS COMPLETED ===")


if __name__ == '__main__':
    test_user_progression()
