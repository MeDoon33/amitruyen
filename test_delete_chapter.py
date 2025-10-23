"""Test deletion of a chapter with dependent UserReadHistory rows"""
from app import create_app, db
from app.models.comic import Comic, Chapter, UserReadHistory
from flask import current_app

app = create_app()

with app.app_context():
    # Pick a novel chapter (first one)
    chapter = Chapter.query.filter(Chapter.content.isnot(None)).first()
    if not chapter:
        print("No novel chapter found to test.")
    else:
        comic = Comic.query.get(chapter.comic_id)
        print(f"Testing deletion for Chapter ID={chapter.id}, Number={chapter.chapter_number}, Comic='{comic.title}'")
        # Simulate read histories (if none exist)
        existing = UserReadHistory.query.filter_by(chapter_id=chapter.id).count()
        if existing == 0:
            # Need a user id; assume 1 exists
            user_id = 1
            history = UserReadHistory(user_id=user_id, comic_id=comic.id, chapter_id=chapter.id)
            db.session.add(history)
            db.session.commit()
            print("Added one simulated UserReadHistory.")
        before_hist = UserReadHistory.query.filter_by(chapter_id=chapter.id).count()
        print(f"Histories before delete: {before_hist}")
        
        # Perform deletion logic manually (similar to route)
        histories_deleted = UserReadHistory.query.filter_by(chapter_id=chapter.id).delete(synchronize_session=False)
        db.session.delete(chapter)
        db.session.commit()
        after_hist = UserReadHistory.query.filter_by(chapter_id=chapter.id).count()
        still_exists = Chapter.query.get(chapter.id)
        print(f"Histories deleted: {histories_deleted}")
        print(f"Histories remaining: {after_hist}")
        print(f"Chapter exists after delete? {'YES' if still_exists else 'NO'}")
