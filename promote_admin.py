"""
Script to promote a user to admin role
Usage: python promote_admin.py <username>
"""
import sys
from app import create_app, db
from app.models.user import User

def promote_to_admin(username):
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"Error: User '{username}' not found.")
            return False
        
        if user.role == 'admin':
            print(f"User '{username}' is already an admin.")
            return True
        
        user.role = 'admin'
        db.session.commit()
        print(f"Success: User '{username}' has been promoted to admin.")
        return True

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python promote_admin.py <username>")
        sys.exit(1)
    
    username = sys.argv[1]
    success = promote_to_admin(username)
    sys.exit(0 if success else 1)
