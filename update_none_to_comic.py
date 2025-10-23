"""
Simple script to set all None content_type to 'comic'
"""
from app import create_app, db
from app.models.comic import Comic

app = create_app()

with app.app_context():
    print("\n=== Updating None content_type to 'comic' ===\n")
    
    none_records = Comic.query.filter(Comic.content_type == None).all()
    
    if none_records:
        print(f"Found {len(none_records)} records with content_type=None\n")
        for item in none_records:
            print(f"Updating: ID {item.id} - {item.title}")
            item.content_type = 'comic'
        
        db.session.commit()
        print(f"\n✓ Successfully updated {len(none_records)} records to content_type='comic'")
    else:
        print("No records with content_type=None found.")
    
    print("\n=== Final Statistics ===")
    comics_count = Comic.query.filter(Comic.content_type == 'comic').count()
    novels_count = Comic.query.filter(Comic.content_type == 'novel').count()
    none_count = Comic.query.filter(Comic.content_type == None).count()
    
    print(f"Comics (content_type='comic'): {comics_count}")
    print(f"Novels (content_type='novel'): {novels_count}")
    print(f"None: {none_count}")
