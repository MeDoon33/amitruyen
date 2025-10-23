"""
Delete test chapter programmatically
"""
from app import create_app, db
from app.models.comic import Chapter

app = create_app()

with app.app_context():
    # Find and delete the test chapter
    test_chapter = Chapter.query.get(13)
    
    if test_chapter:
        print(f"\nFound test chapter:")
        print(f"  ID: {test_chapter.id}")
        print(f"  Number: {test_chapter.chapter_number}")
        print(f"  Title: {test_chapter.title}")
        print(f"  Content: {test_chapter.content[:100]}...")
        
        confirm = input("\nDelete this chapter? (y/n): ").strip().lower()
        
        if confirm == 'y':
            db.session.delete(test_chapter)
            db.session.commit()
            print("\n✓ Chapter deleted successfully!")
            
            # Verify
            remaining = Chapter.query.filter_by(comic_id=11).count()
            print(f"Remaining chapters for comic 11: {remaining}")
        else:
            print("\nCancelled")
    else:
        print("Test chapter not found (already deleted?)")
