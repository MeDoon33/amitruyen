from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from ..models.comic import Comic
from ..models.user import User
from ..decorators import admin_required
from ..services.progression import ProgressionService
from .. import db
from ..utils.image_upload import upload_to_imgbb, is_valid_image, get_file_size_mb

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
        
        # Xử lý upload ảnh bìa
        final_cover_image = None
        
        # Kiểm tra xem có file upload không
        if 'cover_file' in request.files:
            cover_file = request.files['cover_file']
            
            if cover_file and cover_file.filename:
                # Validate file
                if not is_valid_image(cover_file):
                    flash('❌ Định dạng file không hợp lệ! Chỉ chấp nhận: PNG, JPG, JPEG, GIF, WEBP', 'danger')
                    return redirect(url_for('admin.upload_comic'))
                
                # Check file size (max 10MB)
                if get_file_size_mb(cover_file) > 10:
                    flash('❌ Kích thước file quá lớn! Tối đa 10MB', 'danger')
                    return redirect(url_for('admin.upload_comic'))
                
                # Upload to ImgBB
                flash('⏳ Đang upload ảnh lên cloud...', 'info')
                final_cover_image = upload_to_imgbb(cover_file)
                
                if not final_cover_image:
                    flash('❌ Upload ảnh thất bại! Vui lòng thử lại hoặc sử dụng URL', 'danger')
                    return redirect(url_for('admin.upload_comic'))
        
        # Nếu không upload file, dùng URL từ input
        if not final_cover_image:
            final_cover_image = cover_image  # URL từ form input
        
        try:
            comic = Comic(
                title=title,
                author=author,
                description=description,
                cover_image=final_cover_image,  # URL từ ImgBB hoặc input URL
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
            
            success_msg = f'✅ Truyện "{title}" đã được tạo thành công!'
            if progression_result:
                success_msg += f' +{progression_result["points_earned"]} điểm kinh nghiệm'
                if progression_result['level_up']:
                    success_msg += f' 🎉 Lên cấp {progression_result["new_level"]}!'
            
            flash(success_msg, 'success')
            return redirect(url_for('comic.view_comic', comic_id=comic.id))
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Lỗi tạo truyện: {str(e)}', 'danger')
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
            # Check for file upload first
            image_urls = []
            if 'chapter_images' in request.files:
                files = request.files.getlist('chapter_images')
                if files and files[0].filename:  # Check if files were actually uploaded
                    from ..utils.image_upload import upload_to_imgbb, is_valid_image, get_file_size_mb
                    
                    for file in files:
                        if not is_valid_image(file):
                            flash(f'❌ File không hợp lệ: {file.filename}', 'danger')
                            return redirect(url_for('admin.add_chapter', comic_id=comic_id))
                        
                        if get_file_size_mb(file) > 10:
                            flash(f'❌ File quá lớn (>10MB): {file.filename}', 'danger')
                            return redirect(url_for('admin.add_chapter', comic_id=comic_id))
                        
                        # Upload to ImgBB
                        img_url = upload_to_imgbb(file)
                        if img_url:
                            image_urls.append(img_url)
                        else:
                            flash(f'❌ Không thể upload: {file.filename}', 'danger')
                            return redirect(url_for('admin.add_chapter', comic_id=comic_id))
                    
                    if image_urls:
                        flash(f'✅ Đã upload {len(image_urls)} ảnh lên ImgBB!', 'success')
            
            # Fallback to URL input if no files uploaded
            if not image_urls:
                image_urls_text = request.form.get('image_urls')
                if not image_urls_text:
                    flash('Vui lòng chọn ảnh để upload hoặc nhập URL!', 'danger')
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

@admin.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    if current_user.username != 'admin':
        flash('Only the super admin can delete users.', 'danger')
        return redirect(url_for('admin.manage_users'))
    user = User.query.get_or_404(user_id)
    if user.username == 'admin':
        flash('Không thể xóa Super Admin.', 'danger')
        return redirect(url_for('admin.manage_users'))
    try:
        db.session.delete(user)
        db.session.commit()
        flash(f'Đã xóa người dùng {user.username}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi khi xóa: {str(e)}', 'danger')
    return redirect(url_for('admin.manage_users'))


@admin.route('/my-comics')
@login_required
@uploader_required
def my_comics():
    """Trang quản lý truyện của uploader"""
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    # Admin có thể xem truyện của uploader cụ thể
    uploader_id = request.args.get('uploader_id', type=int)
    if uploader_id and current_user.is_admin():
        target_user_id = uploader_id
        target_user = User.query.get_or_404(uploader_id)
    else:
        target_user_id = current_user.id
        target_user = current_user
    
    # Lấy truyện của user
    pagination = Comic.query.filter_by(uploader_id=target_user_id)\
        .order_by(Comic.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    comics = pagination.items
    
    # Thống kê
    total_comics = Comic.query.filter_by(uploader_id=target_user_id).count()
    total_views = db.session.query(db.func.sum(Comic.views))\
        .filter(Comic.uploader_id == target_user_id).scalar() or 0
    total_follows = db.session.query(db.func.sum(Comic.follow_count))\
        .filter(Comic.uploader_id == target_user_id).scalar() or 0
    
    # Tính tổng số chapters
    from ..models.comic import Chapter
    total_chapters = db.session.query(db.func.count(Chapter.id))\
        .join(Comic)\
        .filter(Comic.uploader_id == target_user_id).scalar() or 0
    
    stats = {
        'total_comics': total_comics,
        'total_views': total_views,
        'total_follows': total_follows,
        'total_chapters': total_chapters
    }
    
    return render_template('admin/my_comics.html', 
                         comics=comics, 
                         pagination=pagination,
                         stats=stats,
                         target_user=target_user,
                         viewing_other=(uploader_id is not None and current_user.is_admin()))


@admin.route('/uploaders')
@login_required
@admin_required
def list_uploaders():
    """Danh sách tất cả uploader và số lượng truyện của họ (Admin only)"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Query users có role uploader hoặc đã upload truyện
    from sqlalchemy import func
    
    # Lấy users có truyện
    uploaders_with_comics = db.session.query(
        User,
        func.count(Comic.id).label('comic_count'),
        func.sum(Comic.views).label('total_views'),
        func.sum(Comic.follow_count).label('total_follows')
    ).outerjoin(Comic, User.id == Comic.uploader_id)\
     .group_by(User.id)\
     .having(func.count(Comic.id) > 0)\
     .order_by(func.count(Comic.id).desc())\
     .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/uploaders.html', 
                         uploaders=uploaders_with_comics)


@admin.route('/users/<int:user_id>/ban', methods=['POST'])
@login_required
@admin_required
def ban_user(user_id):
    """Ban a user for a specified duration or permanently"""
    if current_user.id == user_id:
        flash('Bạn không thể tự cấm chính mình!', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent banning other admins
    if user.is_admin() and current_user.username != 'admin':
        flash('Chỉ super admin mới có thể cấm admin khác!', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    ban_duration = request.form.get('ban_duration')  # 'hours', 'days', 'weeks', 'permanent'
    ban_value = request.form.get('ban_value', type=int)
    ban_reason = request.form.get('ban_reason', '').strip()
    
    user.is_banned = True
    user.banned_by = current_user.id
    user.banned_at = datetime.utcnow()
    user.ban_reason = ban_reason if ban_reason else 'Vi phạm quy định'
    
    if ban_duration == 'permanent':
        user.ban_until = None
        flash(f'Đã cấm vĩnh viễn tài khoản {user.username}!', 'success')
    else:
        if not ban_value or ban_value <= 0:
            flash('Vui lòng nhập thời gian cấm hợp lệ!', 'danger')
            return redirect(url_for('admin.manage_users'))
        
        if ban_duration == 'hours':
            user.ban_until = datetime.utcnow() + timedelta(hours=ban_value)
            duration_text = f'{ban_value} giờ'
        elif ban_duration == 'days':
            user.ban_until = datetime.utcnow() + timedelta(days=ban_value)
            duration_text = f'{ban_value} ngày'
        elif ban_duration == 'weeks':
            user.ban_until = datetime.utcnow() + timedelta(weeks=ban_value)
            duration_text = f'{ban_value} tuần'
        else:
            flash('Thời gian cấm không hợp lệ!', 'danger')
            return redirect(url_for('admin.manage_users'))
        
        flash(f'Đã cấm tài khoản {user.username} trong {duration_text}!', 'success')
    
    db.session.commit()
    return redirect(url_for('admin.manage_users'))


@admin.route('/users/<int:user_id>/unban', methods=['POST'])
@login_required
@admin_required
def unban_user(user_id):
    """Unban a user"""
    user = User.query.get_or_404(user_id)
    
    if not user.is_banned:
        flash(f'Tài khoản {user.username} không bị cấm!', 'info')
        return redirect(url_for('admin.manage_users'))
    
    user.is_banned = False
    user.ban_until = None
    user.ban_reason = None
    
    db.session.commit()
    flash(f'Đã gỡ cấm tài khoản {user.username}!', 'success')
    return redirect(url_for('admin.manage_users'))
