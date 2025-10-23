#!/usr/bin/env python3
"""
Test complete duplicate detection system
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.comic import Comic

def test_complete_system():
    """Test complete duplicate detection system"""
    app = create_app()
    
    with app.app_context():
        print("=== TEST COMPLETE DUPLICATE SYSTEM ===")
        
        # Test cases
        test_cases = [
            {"title": "Solo Leveling", "author": "Jang Sung Lak", "expected": "DUPLICATE"},
            {"title": "Solo Leveling", "author": "Different Author", "expected": "SIMILAR"},
            {"title": "New Unique Comic", "author": "New Author", "expected": "SAFE"},
        ]
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n--- Test Case {i} ---")
            title = case["title"]
            author = case["author"]
            expected = case["expected"]
            
            print(f"Input: '{title}' by '{author}'")
            print(f"Expected: {expected}")
            
            # Simulate the duplicate check logic
            title_normalized = title.strip().lower()
            author_normalized = author.strip().lower() if author else None
            
            from app import db
            existing_comics = Comic.query.filter(
                db.func.lower(Comic.title) == title_normalized
            ).all()
            
            duplicates = []
            exact_duplicate = False
            
            for comic in existing_comics:
                comic_author_normalized = comic.author.lower() if comic.author else None
                
                if comic_author_normalized == author_normalized:
                    exact_duplicate = True
                
                duplicates.append({
                    'id': comic.id,
                    'title': comic.title,
                    'author': comic.author,
                    'exact_match': comic_author_normalized == author_normalized
                })
            
            # Determine result
            if exact_duplicate:
                result = "DUPLICATE"
            elif duplicates:
                result = "SIMILAR"
            else:
                result = "SAFE"
            
            print(f"Result: {result}")
            print(f"Found {len(duplicates)} similar comics")
            
            if duplicates:
                for dup in duplicates:
                    match_type = "EXACT" if dup['exact_match'] else "SIMILAR"
                    print(f"  - [{match_type}] {dup['title']} by {dup['author']} (ID: {dup['id']})")
            
            # Check if result matches expected
            status = "✅ PASS" if result == expected else "❌ FAIL"
            print(f"Status: {status}")

if __name__ == '__main__':
    test_complete_system()