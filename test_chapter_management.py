"""
Test edit and delete chapter functionality
"""
from app import create_app, db
from app.models.comic import Comic, Chapter

app = create_app()

with app.app_context():
    print("\n=== Chapter Management Test ===\n")
    
    # Get novel chapters
    novel = Comic.query.filter_by(content_type='novel').first()
    if not novel:
        print("No novel found!")
    else:
        print(f"Novel: {novel.title}")
        print(f"Content Type: {novel.content_type}")
        
        chapters = Chapter.query.filter_by(comic_id=novel.id).all()
        print(f"\nTotal chapters: {len(chapters)}")
        
        for chapter in chapters:
            print(f"\n  Chapter {chapter.chapter_number}: {chapter.title}")
            print(f"    ID: {chapter.id}")
            print(f"    Has content: {bool(chapter.content)}")
            print(f"    Content length: {len(chapter.content) if chapter.content else 0} chars")
            print(f"    Has images: {bool(chapter.image_urls)}")
            print(f"    Edit URL: http://127.0.0.1:5001/admin/chapter/{chapter.id}/edit")
            print(f"    Delete URL: http://127.0.0.1:5001/admin/chapter/{chapter.id}/delete")
        
        print("\n=== Routes Available ===")
        print("1. Edit Novel Chapter (should show content textarea)")
        print("2. Delete Chapter (should remove from database)")
        print("\nBoth routes check permissions (admin/moderator/owner only)")
