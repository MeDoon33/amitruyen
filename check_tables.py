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

def check_tables():
    with app.app_context():
        try:
            from sqlalchemy import text
            # Get list of tables
            result = db.session.execute(text('SHOW TABLES'))
            tables = [row[0] for row in result]
            
            if not tables:
                print("No tables found in database. Creating tables...")
                # Import models
                from app.models.comic import Comic, Chapter, UserReadHistory
                from app.models.user import User
                
                # Create tables
                db.create_all()
                print("Tables created successfully!")
            else:
                print("Existing tables:", tables)
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    check_tables()