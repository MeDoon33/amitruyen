from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models.comic import Comic, Chapter
from app.routes import admin

@admin.route('/comic/<int:comic_id>/add_chapter', methods=['GET', 'POST'])
@login_required
def add_chapter(comic_id):
    comic = Comic.query.get_or_404(comic_id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        chapter_number = len(comic.chapters) + 1
        
        chapter = Chapter(
            title=title,
            content=content,
            chapter_number=chapter_number,
            comic_id=comic_id
        )
        
        db.session.add(chapter)
        db.session.commit()
        
        flash('Chapter added successfully!', 'success')
        return redirect(url_for('comic.view', id=comic_id))
        
    return render_template('admin/add_chapter.html', comic=comic)

@admin.route('/comic/<int:comic_id>/chapter/<int:chapter_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_chapter(comic_id, chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    comic = Comic.query.get_or_404(comic_id)
    
    if request.method == 'POST':
        chapter.title = request.form.get('title')
        chapter.content = request.form.get('content')
        
        db.session.commit()
        flash('Chapter updated successfully!', 'success')
        return redirect(url_for('comic.view', id=comic_id))
        
    return render_template('admin/edit_chapter.html', chapter=chapter, comic=comic)