from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def reset_database():
    with app.app_context():
        try:
            from sqlalchemy import text
            
            # Drop all tables
            db.session.execute(text('DROP TABLE IF EXISTS user_read_history'))
            db.session.execute(text('DROP TABLE IF EXISTS chapters'))
            db.session.execute(text('DROP TABLE IF EXISTS chapter'))
            db.session.execute(text('DROP TABLE IF EXISTS comics'))
            db.session.execute(text('DROP TABLE IF EXISTS comic'))
            db.session.execute(text('DROP TABLE IF EXISTS users'))
            db.session.execute(text('DROP TABLE IF EXISTS user'))
            db.session.commit()
            print("All tables dropped successfully!")
            
            # Import models by adding app directory to Python path
            import sys
            sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
            from app.models.comic import Comic, Chapter, UserReadHistory
            from app.models.user import User
            
            # Create tables
            db.create_all()
            print("Tables recreated successfully!")
            
            # Verify tables
            result = db.session.execute(text('SHOW TABLES'))
            tables = [row[0] for row in result]
            print("Current tables:", tables)
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    reset_database()