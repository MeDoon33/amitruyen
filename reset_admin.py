from app import create_app, db
from app.models.user import User

def reset_admin_password():
    app = create_app()
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print('No admin user found!')
            return
        admin.set_password('admin1234')
        db.session.commit()
        print('Admin password reset to: admin1234')

if __name__ == '__main__':
    reset_admin_password()
