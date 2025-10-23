
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from ..models.comic import Comic
from ..models.user import User
from ..decorators import admin_required
from ..services.progression import ProgressionService
from .. import db

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/comic/<int:comic_id>/delete', methods=['POST'])
@login_required
def delete_comic(comic_id):
    comic = Comic.query.get_or_404(comic_id)
    # Cho phép moderator (bao gồm admin) hoặc uploader chủ sở hữu xóa
    if not (current_user.is_moderator() or (comic.uploader_id == current_user.id and current_user.role == 'uploader')):
        flash('Bạn không có quyền xóa truyện này.', 'danger')
        return redirect(url_for('comic.view_comic', comic_id=comic.id))
    try:
        db.session.delete(comic)
        db.session.commit()
        flash('Đã xóa truyện thành công!', 'success')
        return redirect(url_for('comic.get_comics'))
    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi khi xóa truyện: {str(e)}', 'danger')
        return redirect(url_for('comic.view_comic', comic_id=comic.id))


# Admin: Manage users and set roles (only username 'admin' can set roles)
@admin.route('/users', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_users():
    if request.method == 'POST':
        if current_user.username != 'admin':
            flash('Only the super admin can change roles.', 'danger')
            return redirect(url_for('admin.manage_users'))
        user_id = request.form.get('user_id')
        new_role = request.form.get('role')
        user = User.query.get(user_id)
        if user:
            user.role = new_role
            db.session.commit()
            flash(f"Updated role for {user.username} to {new_role}", 'success')
        return redirect(url_for('admin.manage_users'))
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)

from ..decorators import uploader_required

@admin.route('/upload', methods=['GET', 'POST'])
@login_required
@uploader_required
def upload_comic():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        description = request.form.get('description')
        cover_image = request.form.get('cover_image')
        genre = request.form.get('genre')
        content_type = request.form.get('content_type', 'comic')
        status = request.form.get('status', 'ongoing')
        tags = request.form.get('tags')
        
        if not title:
            flash('Title is required!', 'danger')
            return redirect(url_for('admin.upload_comic'))
        
        # Kiểm tra trùng lặp truyện (cùng title và author)
        title_normalized = title.strip().lower()
        author_normalized = author.strip().lower() if author else None
        
        existing_comic = Comic.query.filter(
            db.func.lower(Comic.title) == title_normalized
        ).all()
        
        # Nếu có truyện cùng tên, kiểm tra thêm tác giả
        duplicate_found = False
        similar_comics = []
        
        for comic in existing_comic:
            comic_author_normalized = comic.author.lower() if comic.author else None
            if comic_author_normalized == author_normalized:
                # Trùng hoàn toàn
                flash(f'❌ Truyện "{title}" của tác giả "{author or "Không rõ"}" đã tồn tại! '
                      f'<a href="{url_for("comic.view_comic", comic_id=comic.id)}" target="_blank" class="btn btn-sm btn-outline-primary ms-2">Xem truyện</a>', 'danger')
                duplicate_found = True
                break
            else:
                # Cùng tên nhưng khác tác giả
                similar_comics.append(comic)
        
        if duplicate_found:
            return redirect(url_for('admin.upload_comic'))
        
        # Cảnh báo về truyện cùng tên nhưng khác tác giả
        if similar_comics:
            similar_list = ', '.join([f'"{c.title}" ({c.author or "Không rõ"})' for c in similar_comics[:3]])
            flash(f'⚠️ Phát hiện truyện cùng tên: {similar_list}. Vui lòng kiểm tra kỹ để tránh trùng lặp!', 'warning')
        
        try:
            comic = Comic(
                title=title,
                author=author,
                description=description,
                cover_image=cover_image,
                content_type=content_type,
                genre=genre,
                status=status,
                tags=tags,
                uploader_id=current_user.id
            )
            db.session.add(comic)
            db.session.commit()
            
            # Cộng điểm progression cho việc upload comic
            progression_result = ProgressionService.award_points(current_user.id, 'upload_comic', reference_id=comic.id)
            
            success_msg = f'Comic "{title}" created successfully!'
            if progression_result:
                success_msg += f' +{progression_result["points_earned"]} điểm kinh nghiệm'
                if progression_result['level_up']:
                    success_msg += f' 🎉 Lên cấp {progression_result["new_level"]}!'
            
            flash(success_msg, 'success')
            return redirect(url_for('comic.view_comic', comic_id=comic.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating comic: {str(e)}', 'danger')
            return redirect(url_for('admin.upload_comic'))
    
    return render_template('admin/upload_comic.html')

@admin.route('/check-duplicate', methods=['POST'])
@login_required 
@uploader_required
def check_duplicate():
    """API endpoint to check for duplicate comics"""
    data = request.get_json()
    title = data.get('title', '').strip()
    author = data.get('author', '').strip()
    
    if len(title) < 3:
        return jsonify({'duplicates': [], 'exact_duplicate': False})
    
    title_normalized = title.lower()
    author_normalized = author.lower() if author else None
    
    # Find comics with similar titles
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
    
    return jsonify({
        'duplicates': duplicates,
        'exact_duplicate': exact_duplicate
    })

@admin.route('/comic/<int:comic_id>/add_chapter', methods=['GET', 'POST'])
@login_required
def add_chapter(comic_id):
    from ..models.comic import Chapter
    import json, hashlib
    
    comic = Comic.query.get_or_404(comic_id)
    # Quyền: moderator (bao gồm admin) có thể thêm chapter bất kỳ; uploader chỉ thêm vào truyện của mình
    if not (current_user.is_moderator() or (comic.uploader_id == current_user.id and current_user.is_uploader())):
        flash('Bạn không có quyền thêm chương cho truyện này.', 'danger')
        return redirect(url_for('comic.view_comic', comic_id=comic_id))
    
    if request.method == 'POST':
        chapter_number = request.form.get('chapter_number')
        title = request.form.get('title')
        # Normalize and basic validations
        if not chapter_number:
            flash('Số chương là bắt buộc!', 'danger')
            return redirect(url_for('admin.add_chapter', comic_id=comic_id))
        try:
            chapter_number_float = float(chapter_number)
        except ValueError:
            flash('Số chương không hợp lệ!', 'danger')
            return redirect(url_for('admin.add_chapter', comic_id=comic_id))

        # Duplicate chapter number check
        existing_same_number = Chapter.query.filter_by(comic_id=comic_id, chapter_number=chapter_number_float).first()
        if existing_same_number:
            flash(f'❌ Chương {chapter_number} đã tồn tại (ID: {existing_same_number.id}).', 'danger')
            return redirect(url_for('admin.add_chapter', comic_id=comic_id))

        if comic.content_type == 'novel':
            content = request.form.get('content')
            if not content:
                flash('Nội dung chương là bắt buộc cho truyện chữ!', 'danger')
                return redirect(url_for('admin.add_chapter', comic_id=comic_id))
            content_trimmed = content.strip()
            content_hash = hashlib.sha256(content_trimmed.encode('utf-8')).hexdigest()

            # Optimized: Use DB index instead of loading all chapters - future enhancement: add content_hash column
            # For now: only check last 50 chapters (most likely duplicates are recent)
            potential_duplicate = None
            recent_chapters = Chapter.query.filter_by(comic_id=comic_id).order_by(Chapter.chapter_number.desc()).limit(50).all()
            for ch in recent_chapters:
                if ch.content and hashlib.sha256(ch.content.strip().encode('utf-8')).hexdigest() == content_hash:
                    potential_duplicate = ch
                    break

            if potential_duplicate:
                flash(f'⚠️ Nội dung trùng với chương {potential_duplicate.chapter_number} (ID: {potential_duplicate.id}).', 'warning')

            try:
                chapter = Chapter(
                    comic_id=comic_id,
                    chapter_number=chapter_number_float,
                    title=title,
                    content=content_trimmed,
                    image_urls=None
                )
                db.session.add(chapter)
                db.session.commit()
                msg = f'Đã thêm chương {chapter_number} thành công!'
                if potential_duplicate:
                    msg += ' (Cảnh báo trùng)'
                flash(msg, 'success')
                return redirect(url_for('comic.view_comic', comic_id=comic_id))
            except Exception as e:
                db.session.rollback()
                flash(f'Lỗi khi thêm chương: {str(e)}', 'danger')
                return redirect(url_for('admin.add_chapter', comic_id=comic_id))
        else:
            image_urls_text = request.form.get('image_urls')
            if not image_urls_text:
                flash('Danh sách ảnh là bắt buộc cho truyện tranh!', 'danger')
                return redirect(url_for('admin.add_chapter', comic_id=comic_id))
            image_urls = [u.strip() for u in image_urls_text.split('\n') if u.strip()]
            img_hash = hashlib.sha256('\n'.join(image_urls).encode('utf-8')).hexdigest()
            
            # Optimized: check last 50 chapters only
            potential_img_duplicate = None
            recent_chapters = Chapter.query.filter_by(comic_id=comic_id).order_by(Chapter.chapter_number.desc()).limit(50).all()
            for ch in recent_chapters:
                if ch.image_urls:
                    try:
                        existing_list = json.loads(ch.image_urls)
                        existing_hash = hashlib.sha256('\n'.join(existing_list).encode('utf-8')).hexdigest()
                        if existing_hash == img_hash:
                            potential_img_duplicate = ch
                            break
                    except Exception:
                        continue
                        
            if potential_img_duplicate:
                flash(f'⚠️ Bộ ảnh trùng với chương {potential_img_duplicate.chapter_number} (ID: {potential_img_duplicate.id}).', 'warning')
            try:
                chapter = Chapter(
                    comic_id=comic_id,
                    chapter_number=chapter_number_float,
                    title=title,
                    image_urls=json.dumps(image_urls)
                )
                db.session.add(chapter)
                db.session.commit()
                msg = f'Chapter {chapter_number} added successfully!'
                if potential_img_duplicate:
                    msg += ' (Cảnh báo trùng)'
                flash(msg, 'success')
                return redirect(url_for('comic.view_comic', comic_id=comic_id))
            except Exception as e:
                db.session.rollback()
                flash(f'Error adding chapter: {str(e)}', 'danger')
                return redirect(url_for('admin.add_chapter', comic_id=comic_id))
    
    # Chọn template phù hợp dựa vào content_type
    if comic.content_type == 'novel':
        return render_template('admin/add_novel_chapter.html', comic=comic)
    else:
        return render_template('admin/add_chapter.html', comic=comic)

@admin.route('/comic/<int:comic_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_comic(comic_id):
    comic = Comic.query.get_or_404(comic_id)
    # Cho phép moderator (bao gồm admin) hoặc uploader chủ sở hữu
    if not (current_user.is_moderator() or comic.uploader_id == current_user.id):
        flash('Bạn không có quyền sửa truyện này.', 'danger')
        return redirect(url_for('comic.view_comic', comic_id=comic.id))
    if request.method == 'POST':
        comic.title = request.form.get('title')
        comic.author = request.form.get('author')
        comic.description = request.form.get('description')
        comic.cover_image = request.form.get('cover_image')
        # update content_type if provided
        content_type = request.form.get('content_type')
        if content_type:
            comic.content_type = content_type
        comic.genre = request.form.get('genre')
        comic.status = request.form.get('status', 'ongoing')
        comic.tags = request.form.get('tags')
        db.session.commit()
        flash('Comic updated successfully!', 'success')
        return redirect(url_for('comic.view_comic', comic_id=comic.id))
    return render_template('admin/edit_comic.html', comic=comic)

@admin.route('/chapter/<int:chapter_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_chapter(chapter_id):
    from ..models.comic import Chapter
    import json
    chapter = Chapter.query.get_or_404(chapter_id)
    comic = Comic.query.get_or_404(chapter.comic_id)
    # Cho phép moderator (bao gồm admin) hoặc uploader chủ sở hữu
    if not (current_user.is_moderator() or comic.uploader_id == current_user.id):
        flash('Bạn không có quyền sửa chương truyện này.', 'danger')
        return redirect(url_for('comic.read_chapter', comic_id=comic.id, chapter_number=chapter.chapter_number))
    
    if request.method == 'POST':
        chapter.chapter_number = float(request.form.get('chapter_number'))
        chapter.title = request.form.get('title')
        
        # Kiểm tra xem đây là truyện chữ hay truyện tranh
        if comic.content_type == 'novel':
            # Truyện chữ - cập nhật content
            content = request.form.get('content')
            if not content:
                flash('Nội dung chương là bắt buộc!', 'danger')
                return redirect(url_for('admin.edit_chapter', chapter_id=chapter_id))
            
            chapter.content = content.strip()
            chapter.image_urls = None
        else:
            # Truyện tranh - cập nhật image URLs
            image_urls_text = request.form.get('image_urls')
            if not image_urls_text:
                flash('Image URLs are required!', 'danger')
                return redirect(url_for('admin.edit_chapter', chapter_id=chapter_id))
            
            image_urls = [url.strip() for url in image_urls_text.split('\n') if url.strip()]
            chapter.image_urls = json.dumps(image_urls)
        
        db.session.commit()
        flash('Đã cập nhật chương thành công!' if comic.content_type == 'novel' else 'Chapter updated successfully!', 'success')
        return redirect(url_for('comic.view_comic', comic_id=comic.id))
    
    # GET request - hiển thị form
    if comic.content_type == 'novel':
        return render_template('admin/edit_novel_chapter.html', chapter=chapter, comic=comic)
    else:
        image_urls = '\n'.join(json.loads(chapter.image_urls)) if chapter.image_urls else ''
        return render_template('admin/edit_chapter.html', chapter=chapter, comic=comic, image_urls=image_urls)

@admin.route('/chapter/<int:chapter_id>/delete', methods=['POST', 'GET'])
@login_required
def delete_chapter(chapter_id):
    from ..models.comic import Chapter, UserReadHistory, Comment
    # Lấy chapter và comic
    chapter = Chapter.query.get_or_404(chapter_id)
    comic = Comic.query.get_or_404(chapter.comic_id)

    # Kiểm tra quyền: moderator/admin hoặc uploader sở hữu truyện
    if not (current_user.is_moderator() or comic.uploader_id == current_user.id):
        flash('Bạn không có quyền xóa chương truyện này.', 'danger')
        return redirect(url_for('comic.view_comic', comic_id=comic.id))

    try:
        chapter_number = chapter.chapter_number
        chapter_title = chapter.title or f"Chương {chapter_number}"

        # Xóa lịch sử đọc liên quan (UserReadHistory phụ thuộc chapter_id)
        histories_deleted = UserReadHistory.query.filter_by(chapter_id=chapter.id).delete(synchronize_session=False)

        # (Tuỳ chọn) Nếu có comment gắn với chapter (hiện tại comment chỉ gắn comic, bỏ qua)
        # Nếu sau này comment gắn với chapter, thêm xử lý ở đây.

        # Xóa chapter
        db.session.delete(chapter)
        db.session.commit()

        flash(f'Đã xóa "{chapter_title}" thành công! (Đã xóa {histories_deleted} lịch sử đọc)', 'success')
    except Exception as e:
        db.session.rollback()
        # Gợi ý sửa lỗi khóa ngoại nếu vẫn còn ràng buộc khác
        msg = ('Lỗi khi xóa chương: ' + str(e) +
               ' — Nếu tiếp tục gặp lỗi khóa ngoại, cần thêm cascade="all, delete" cho quan hệ hoặc dùng ON DELETE CASCADE trong migration.')
        flash(msg, 'danger')

    return redirect(url_for('comic.view_comic', comic_id=comic.id))

@admin.route('/comic/<int:comic_id>/scan-duplicate-chapters', methods=['GET'])
@login_required
def scan_duplicate_chapters(comic_id):
    """Scan chapters of a comic for duplicates (chapter number, content hash or image set hash).
    Returns JSON report. Applicable for both truyện tranh and truyện chữ."""
    from ..models.comic import Chapter
    import json, hashlib
    comic = Comic.query.get_or_404(comic_id)
    # Permission: allow moderator/admin or uploader owner
    if not (current_user.is_moderator() or comic.uploader_id == current_user.id):
        return jsonify({'error': 'Không có quyền'}), 403

    chapters = Chapter.query.filter_by(comic_id=comic_id).order_by(Chapter.chapter_number).all()
    number_map = {}
    content_hash_map = {}
    image_hash_map = {}

    for ch in chapters:
        # Chapter number duplicates
        number_map.setdefault(ch.chapter_number, []).append(ch.id)
        # Content hash (only novels with content)
        if ch.content:
            h = hashlib.sha256(ch.content.strip().encode('utf-8')).hexdigest()
            content_hash_map.setdefault(h, []).append({'id': ch.id, 'num': ch.chapter_number})
        # Image set hash (only comics with image_urls)
        if ch.image_urls:
            try:
                imgs = json.loads(ch.image_urls)
            except Exception:
                imgs = []
            h_img = hashlib.sha256('\n'.join(imgs).encode('utf-8')).hexdigest()
            image_hash_map.setdefault(h_img, []).append({'id': ch.id, 'num': ch.chapter_number})

    duplicate_numbers = {k: v for k, v in number_map.items() if len(v) > 1}
    duplicate_contents = [v for v in content_hash_map.values() if len(v) > 1]
    duplicate_images = [v for v in image_hash_map.values() if len(v) > 1]

    return jsonify({
        'comic_id': comic_id,
        'title': comic.title,
        'duplicate_chapter_numbers': duplicate_numbers,
        'duplicate_novel_contents': duplicate_contents,
        'duplicate_image_sets': duplicate_images,
        'total_chapters': len(chapters)
    })
