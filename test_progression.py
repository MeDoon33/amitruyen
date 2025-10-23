"""
Test script for the user progression system
"""

from app import create_app, db
from app.models.user import User
from app.services.progression import ProgressionService

def test_progression_system():
    app = create_app()
    
    with app.app_context():
        # Find a test user (or create one)
        test_user = User.query.filter_by(username='admin').first()
        
        if not test_user:
            print("Creating test user...")
            test_user = User(
                username='testuser',
                email='test@example.com'
            )
            test_user.set_password('password')
            db.session.add(test_user)
            db.session.commit()
        
        print(f"Testing with user: {test_user.username}")
        print(f"Initial level: {test_user.level}")
        print(f"Initial points: {test_user.points}")
        print(f"Initial rank: {test_user.get_rank_title()}")
        
        # Test point awarding
        print("\n=== Testing Point Awarding ===")
        
        # Award points for reading
        result = ProgressionService.award_points(test_user.id, 'read_chapter', 1)
        print(f"Read chapter result: {result}")
        
        # Award points for commenting
        result = ProgressionService.award_points(test_user.id, 'comment', 1)
        print(f"Comment result: {result}")
        
        # Award points for rating
        result = ProgressionService.award_points(test_user.id, 'rating', 1)
        print(f"Rating result: {result}")
        
        # Award points for daily login
        result = ProgressionService.award_points(test_user.id, 'daily_login')
        print(f"Daily login result: {result}")
        
        # Refresh user data
        db.session.refresh(test_user)
        
        print(f"\nFinal level: {test_user.level}")
        print(f"Final points: {test_user.points}")
        print(f"Final rank: {test_user.get_rank_title()}")
        print(f"Progress to next level: {test_user.get_progress_to_next_level():.1f}%")
        
        # Test stats
        print("\n=== Testing Stats ===")
        stats = ProgressionService.get_user_stats(test_user.id)
        if stats:
            print(f"Total reads: {stats['total_reads']}")
            print(f"Total comments: {stats['total_comments']}")
            print(f"Total ratings: {stats['total_ratings']}")
            print(f"Badge count: {stats['badge_count']}")
        
        print("\n=== Test Completed ===")

if __name__ == '__main__':
    test_progression_system()