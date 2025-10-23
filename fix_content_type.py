"""
Script to fix content_type for existing comics/novels in database
This will set content_type based on genre/tags if not already set
"""
from app import create_app, db
from app.models.comic import Comic

app = create_app()

with app.app_context():
    print("\n=== Fixing content_type for existing records ===\n")
    
    # Find records that might be novels but don't have content_type='novel'
    potential_novels = Comic.query.filter(
        (Comic.content_type != 'novel') | (Comic.content_type == None)
    ).filter(
        (Comic.genre.ilike('%novel%')) |
        (Comic.genre.ilike('%tiểu thuyết%')) |
        (Comic.tags.ilike('%novel%')) |
        (Comic.tags.ilike('%tiểu thuyết%'))
    ).all()
    
    if potential_novels:
        print(f"Found {len(potential_novels)} potential novels without correct content_type:")
        for item in potential_novels:
            print(f"\n  ID: {item.id}")
            print(f"  Title: {item.title}")
            print(f"  Current content_type: {item.content_type}")
            print(f"  Genre: {item.genre}")
            print(f"  Tags: {item.tags}")
            
            # Ask for confirmation
            update = input(f"  Update this to content_type='novel'? (y/n): ").strip().lower()
            if update == 'y':
                item.content_type = 'novel'
                print(f"  ✓ Updated to 'novel'")
        
        # Save changes
        db.session.commit()
        print("\n✓ Changes saved to database")
    else:
        print("No potential novels found that need updating.")
    
    # Set content_type='comic' for all None records
    none_records = Comic.query.filter(Comic.content_type == None).all()
    if none_records:
        print(f"\n\nFound {len(none_records)} records with content_type=None")
        update_all = input("Update all to content_type='comic'? (y/n): ").strip().lower()
        if update_all == 'y':
            for item in none_records:
                item.content_type = 'comic'
                print(f"  ✓ Updated '{item.title}' to 'comic'")
            db.session.commit()
            print("\n✓ All None records updated to 'comic'")
    
    print("\n=== Final Statistics ===")
    comics_count = Comic.query.filter(Comic.content_type == 'comic').count()
    novels_count = Comic.query.filter(Comic.content_type == 'novel').count()
    none_count = Comic.query.filter(Comic.content_type == None).count()
    
    print(f"Comics: {comics_count}")
    print(f"Novels: {novels_count}")
    print(f"None: {none_count}")
