#!/usr/bin/env python3
"""
Script to initialize database on Railway/Render
Run this after first deployment: python init_production.py
"""

from app import create_app, db
from app.models.user import User, RankTitle
from werkzeug.security import generate_password_hash

def init_production_db():
    app = create_app()
    
    with app.app_context():
        print("🚀 Creating database tables...")
        db.create_all()
        print("✅ Tables created!")
        
        # Check if admin exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("👤 Creating admin user...")
            admin = User(
                username='admin',
                email='admin@amitruyen.id.vn',
                password=generate_password_hash('admin123'),  # CHANGE THIS!
                role='admin',
                level=1,
                points=0,
                rank_type='tu_tien'
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created! (username: admin, password: admin123)")
            print("⚠️  REMEMBER TO CHANGE PASSWORD AFTER LOGIN!")
        else:
            print("ℹ️  Admin user already exists")
        
        # Seed rank titles if not exist
        rank_count = RankTitle.query.count()
        if rank_count == 0:
            print("📊 Seeding rank titles...")
            from seed_rank_titles_only import seed_rank_titles
            seed_rank_titles()
            print("✅ Rank titles seeded!")
        else:
            print(f"ℹ️  Rank titles already exist ({rank_count} titles)")
        
        print("\n🎉 Production database initialized successfully!")
        print("🌐 Your website is ready at: https://amitruyen.id.vn")

if __name__ == '__main__':
    init_production_db()
