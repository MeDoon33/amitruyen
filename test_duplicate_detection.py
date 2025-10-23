#!/usr/bin/env python3
"""
Test duplicate comic detection
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.comic import Comic

def test_duplicate_detection():
    """Test duplicate comic detection logic"""
    app = create_app()
    
    with app.app_context():
        print("=== TEST DUPLICATE DETECTION ===")
        
        # Lấy danh sách comics hiện có
        comics = Comic.query.all()
        print(f"Total comics in database: {len(comics)}")
        
        if comics:
            print("\nComics hiện có:")
            for comic in comics[:5]:  # Hiển thị 5 truyện đầu
                print(f"- '{comic.title}' by {comic.author or 'Unknown'} (ID: {comic.id})")
        
        # Test case: Kiểm tra trùng lặp với Solo Leveling
        test_title = "Solo Leveling"
        test_author = "Jang Sung Lak"
        
        print(f"\n=== TEST CASE ===")
        print(f"Kiểm tra: '{test_title}' by '{test_author}'")
        
        title_normalized = test_title.strip().lower()
        author_normalized = test_author.strip().lower() if test_author else None
        
        from app import db
        existing_comic = Comic.query.filter(
            db.func.lower(Comic.title) == title_normalized
        ).all()
        
        print(f"Tìm thấy {len(existing_comic)} truyện cùng tên")
        
        duplicate_found = False
        similar_comics = []
        
        for comic in existing_comic:
            comic_author_normalized = comic.author.lower() if comic.author else None
            print(f"- Comparing with: '{comic.title}' by '{comic.author}' (normalized: '{comic_author_normalized}')")
            
            if comic_author_normalized == author_normalized:
                print(f"✅ DUPLICATE FOUND: {comic.title} (ID: {comic.id})")
                duplicate_found = True
                break
            else:
                similar_comics.append(comic)
                print(f"⚠️ Same title, different author: {comic.author}")
        
        if not duplicate_found and similar_comics:
            similar_list = ', '.join([f'"{c.title}" ({c.author or "Không rõ"})' for c in similar_comics[:3]])
            print(f"⚠️ Similar comics found: {similar_list}")
        
        if not duplicate_found and not similar_comics:
            print("✅ No duplicates found - safe to upload!")

if __name__ == '__main__':
    test_duplicate_detection()