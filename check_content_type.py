"""
Script to check and display comics/novels by content_type
"""
from app import create_app, db
from app.models.comic import Comic

app = create_app()

with app.app_context():
    print("\n=== Checking content_type in database ===\n")
    
    # Get all comics
    all_comics = Comic.query.all()
    print(f"Total comics in database: {len(all_comics)}")
    
    # Group by content_type
    comics = Comic.query.filter(
        (Comic.content_type == 'comic') | (Comic.content_type == None)
    ).all()
    novels = Comic.query.filter(Comic.content_type == 'novel').all()
    
    print(f"\nComics (content_type='comic' or None): {len(comics)}")
    for comic in comics:
        print(f"  - ID: {comic.id}, Title: {comic.title}, Type: {comic.content_type}, Genre: {comic.genre}")
    
    print(f"\nNovels (content_type='novel'): {len(novels)}")
    for novel in novels:
        print(f"  - ID: {novel.id}, Title: {novel.title}, Type: {novel.content_type}, Genre: {novel.genre}")
    
    # Check for records with None content_type
    none_type = Comic.query.filter(Comic.content_type == None).all()
    if none_type:
        print(f"\n⚠️  Comics with content_type=None: {len(none_type)}")
        print("These will be treated as comics by default.")
        for item in none_type:
            print(f"  - ID: {item.id}, Title: {item.title}, Genre: {item.genre}")
