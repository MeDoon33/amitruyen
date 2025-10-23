import os
import sys
sys.path.append('.')

from dotenv import load_dotenv
load_dotenv()

from app import create_app, db

app = create_app()

print("Starting test...")
print("DATABASE_URL:", os.getenv('DATABASE_URL'))

try:
    with app.app_context():
        # Simple query to test connection
        result = db.session.execute(db.text('SELECT 1 as test'))
        print("✓ Database connection successful!")
        print("Test result:", result.fetchone())
except Exception as e:
    print("✗ Database connection failed:", e)