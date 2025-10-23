"""
Test adding a novel chapter
"""
from app import create_app, db
from app.models.comic import Comic, Chapter

app = create_app()

with app.app_context():
    # Get the novel
    novel = Comic.query.filter_by(content_type='novel').first()
    
    if not novel:
        print("No novel found!")
    else:
        print(f"\nNovel: {novel.title}")
        print(f"Content Type: {novel.content_type}")
        print(f"Current chapters: {len(novel.chapters)}")
        
        # Add a test chapter
        test_content = """
Chương này là chương test để kiểm tra tính năng truyện chữ.

Đây là đoạn văn thứ hai. Nội dung truyện chữ sẽ được hiển thị theo định dạng văn bản, với các đoạn văn được phân cách rõ ràng.

Mỗi đoạn văn sẽ có khoảng cách phù hợp để người đọc dễ theo dõi.

Hệ thống hỗ trợ nhiều đoạn văn, giúp truyện chữ trở nên dễ đọc và chuyên nghiệp hơn.

Đây là đoạn kết của chương test.
        """.strip()
        
        # Check if test chapter already exists
        existing = Chapter.query.filter_by(
            comic_id=novel.id,
            chapter_number=1
        ).first()
        
        if existing:
            print(f"\nChapter 1 already exists!")
            print(f"Title: {existing.title}")
            print(f"Content length: {len(existing.content) if existing.content else 0} characters")
        else:
            new_chapter = Chapter(
                comic_id=novel.id,
                chapter_number=1,
                title="Chương Test - Khởi Đầu",
                content=test_content,
                image_urls=None
            )
            
            db.session.add(new_chapter)
            db.session.commit()
            
            print(f"\n✓ Added test chapter successfully!")
            print(f"Chapter Number: {new_chapter.chapter_number}")
            print(f"Title: {new_chapter.title}")
            print(f"Content length: {len(new_chapter.content)} characters")
            print(f"\nRead at: http://127.0.0.1:5001/comic/{novel.id}/chapter/{new_chapter.chapter_number}")
