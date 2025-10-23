from app import create_app, db
from app.models.user import User

def create_admin():
    app = create_app()
    with app.app_context():
        username = 'admin'
        email = 'admin@gmail.com'
        password = 'admin123'  # Change this after first login!
        if User.query.filter_by(username=username).first():
            print('Admin user already exists.')
            return
        admin = User(username=username, email=email, role='admin')
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        print('Admin user created! Username: admin, Password: admin123')

if __name__ == '__main__':
    create_admin()
