from flask import Blueprint, request, jsonify, render_template, current_app, flash, redirect, url_for
from flask_login import current_user, login_required
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.comic import Comic, Chapter, UserReadHistory, UserRating, Comment, Follow
from app.schemas.comic import ComicCreate, ChapterCreate
from app.services.progression import ProgressionService
from app import db
import json

comic = Blueprint('comic', __name__)

@comic.route('/<int:comic_id>/rate', methods=['POST'])
@login_required
def rate_comic(comic_id):
    comic = Comic.query.get_or_404(comic_id)
    try:
        rating = int(request.form.get('rating'))
        if rating < 1 or rating > 5:
            flash('Điểm đánh giá không hợp lệ.', 'danger')
            return redirect(url_for('comic.view_comic', comic_id=comic.id))
        
        # Kiểm tra xem user đã vote chưa
        existing_rating = UserRating.query.filter_by(
            user_id=current_user.id,
            comic_id=comic_id
        ).first()
        
        if existing_rating:
            # User đã vote rồi, cập nhật vote cũ
            old_rating = existing_rating.rating
            existing_rating.rating = rating
            
            # Cập nhật lại rating trung bình
            if comic.rating is None:
                comic.rating = 0.0
            if comic.rating_count is None or comic.rating_count == 0:
                comic.rating_count = 1
                comic.rating = float(rating)
            else:
                # Trừ điểm cũ, cộng điểm mới
                total = comic.rating * comic.rating_count - old_rating + rating
                comic.rating = total / comic.rating_count
            
            flash('Đánh giá của bạn đã được cập nhật!', 'success')
        else:
            # User chưa vote, tạo vote mới
            new_rating = UserRating(
                user_id=current_user.id,
                comic_id=comic_id,
                rating=rating
            )
            db.session.add(new_rating)
            
            # Award points for rating
            progression_result = ProgressionService.award_points(
                current_user.id, 
                'rating', 
                comic_id
            )
            
            # Cập nhật rating trung bình
            if comic.rating is None:
                comic.rating = 0.0
            if comic.rating_count is None:
                comic.rating_count = 0
            total = comic.rating * comic.rating_count
            comic.rating_count += 1
            comic.rating = (total + rating) / comic.rating_count
            
            # Show level up message if applicable
            if progression_result and progression_result['level_up']:
                flash(f'Cảm ơn bạn đã đánh giá! 🎉 Bạn đã lên cấp {progression_result["new_level"]} - {progression_result["rank_title"]}!', 'success')
            else:
                flash('Cảm ơn bạn đã đánh giá!', 'success')
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi khi gửi đánh giá: {str(e)}', 'danger')
    return redirect(url_for('comic.view_comic', comic_id=comic.id))
# ...existing code...

@comic.route('/', methods=['GET'])
def get_comics():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    genre = request.args.get('genre')
    status = request.args.get('status')
    search = request.args.get('search')  # tìm theo tiêu đề hoặc tác giả
    tag = request.args.get('tag')  # tìm theo tag đơn lẻ
    
    query = Comic.query
    
    if genre:
        query = query.filter(Comic.genre == genre)
    if status:
        query = query.filter(Comic.status == status)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Comic.title.ilike(search_term)) |
            (Comic.author.ilike(search_term)) |
            (Comic.genre.ilike(search_term)) |
            (Comic.description.ilike(search_term))
        )
    if tag:
        tag_term = f"%{tag}%"
        query = query.filter(Comic.tags.ilike(tag_term))
        
    comics = query.order_by(Comic.updated_at.desc()).paginate(page=page, per_page=per_page)
    
    return render_template('comic/list.html', comics=comics, genre=genre, status=status, search=search, tag=tag)

@comic.route('/novels', methods=['GET'])
def get_novels():
    """Route for novels (truyện chữ) - filter by content_type"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    search = request.args.get('search')
    status = request.args.get('status')
    
    # Filter for novels using content_type field
    query = Comic.query.filter(Comic.content_type == 'novel')
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Comic.title.ilike(search_term)) |
            (Comic.author.ilike(search_term)) |
            (Comic.description.ilike(search_term))
        )
    
    if status:
        query = query.filter(Comic.status == status)
    
    novels = query.order_by(Comic.updated_at.desc()).paginate(page=page, per_page=per_page)
    
    return render_template('comic/novels.html', novels=novels, search=search, status=status)

@comic.route('/api/search', methods=['GET'])
def search_comics_api():
    """
    API endpoint cho tìm kiếm nâng cao
    Params:
    - q: từ khóa tìm kiếm chung
    - title: tìm theo tên truyện
    - author: tìm theo tác giả  
    - genre: tìm theo thể loại
    - limit: số kết quả trả về (mặc định 10)
    """
    try:
        # Lấy parameters
        general_query = request.args.get('q', '').strip()
        title_query = request.args.get('title', '').strip()
        author_query = request.args.get('author', '').strip()
        genre_query = request.args.get('genre', '').strip()
        limit = min(int(request.args.get('limit', 10)), 50)  # giới hạn tối đa 50
        
        # Base query
        query = Comic.query
        
        # Filters
        filters = []
        
        if general_query:
            general_term = f"%{general_query}%"
            filters.append(
                (Comic.title.ilike(general_term)) |
                (Comic.author.ilike(general_term)) |
                (Comic.genre.ilike(general_term)) |
                (Comic.description.ilike(general_term))
            )
            
        if title_query:
            title_term = f"%{title_query}%"
            filters.append(Comic.title.ilike(title_term))
            
        if author_query:
            author_term = f"%{author_query}%"
            filters.append(Comic.author.ilike(author_term))
            
        if genre_query:
            genre_term = f"%{genre_query}%"
            filters.append(Comic.genre.ilike(genre_term))
            
        # Apply filters
        if filters:
            from sqlalchemy import and_
            query = query.filter(and_(*filters))
        
        # Execute query
        comics = query.order_by(Comic.views.desc(), Comic.updated_at.desc()).limit(limit).all()
        
        # Format response
        results = []
        for comic in comics:
            results.append({
                'id': comic.id,
                'title': comic.title,
                'author': comic.author,
                'genre': comic.genre,
                'description': comic.description[:200] + '...' if comic.description and len(comic.description) > 200 else comic.description,
                'cover_image': comic.cover_image,
                'views': comic.views,
                'rating': comic.rating,
                'status': comic.status,
                'chapters_count': len(comic.chapters) if comic.chapters else 0,
                'updated_at': comic.updated_at.strftime('%Y-%m-%d %H:%M:%S') if comic.updated_at else None
            })
            
        return jsonify({
            'success': True,
            'query': {
                'general': general_query,
                'title': title_query,
                'author': author_query,
                'genre': genre_query
            },
            'total': len(results),
            'data': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@comic.route('/<int:comic_id>', methods=['GET'])
def view_comic(comic_id):
    comic = Comic.query.get_or_404(comic_id)
    comic.views += 1
    db.session.commit()
    
    chapters = Chapter.query.filter_by(comic_id=comic_id).order_by(Chapter.chapter_number.asc()).all()
    # earliest is first element when ordered ascending
    earliest_chapter = chapters[0] if chapters else None
    latest_chapter = chapters[-1] if chapters else None

    # Resume reading (last chapter read by current user if any)
    resume_chapter = None
    if current_user.is_authenticated and chapters:
        last_history = UserReadHistory.query.filter_by(
            user_id=current_user.id,
            comic_id=comic_id
        ).order_by(UserReadHistory.created_at.desc()).first()
        if last_history:
            resume_chapter = Chapter.query.get(last_history.chapter_id)
    
    # Lấy rating của user hiện tại nếu đã đăng nhập
    user_rating = None
    is_following = False
    if current_user.is_authenticated:
        user_rating_obj = UserRating.query.filter_by(
            user_id=current_user.id,
            comic_id=comic_id
        ).first()
        if user_rating_obj:
            user_rating = user_rating_obj.rating
            
        # Kiểm tra xem user có đang follow comic này không
        follow_obj = Follow.query.filter_by(
            user_id=current_user.id,
            comic_id=comic_id
        ).first()
        is_following = follow_obj is not None
    
    # Lấy comments cho comic này
    comments = Comment.query.filter_by(comic_id=comic_id).order_by(Comment.created_at.desc()).all()
    
    return render_template('comic/view.html',
                           comic=comic,
                           chapters=chapters,
                           earliest_chapter=earliest_chapter,
                           latest_chapter=latest_chapter,
                           resume_chapter=resume_chapter,
                           user_rating=user_rating,
                           comments=comments,
                           is_following=is_following)

@comic.route('/<int:comic_id>/chapter/<float:chapter_number>')
def read_chapter(comic_id, chapter_number):
    from flask_login import current_user
    
    comic = Comic.query.get_or_404(comic_id)
    chapter = Chapter.query.filter_by(comic_id=comic_id, chapter_number=chapter_number).first_or_404()
    
    # Increment view count
    chapter.views += 1
    
    # Update read history for logged-in users
    if current_user.is_authenticated:
        history = UserReadHistory.query.filter_by(
            user_id=current_user.id,
            comic_id=comic_id,
            chapter_id=chapter.id
        ).first()
        
        if history:
            # Update the timestamp by updating created_at
            history.created_at = db.func.now()
        else:
            history = UserReadHistory(
                user_id=current_user.id,
                comic_id=comic_id,
                chapter_id=chapter.id
            )
            db.session.add(history)
            
            # Award points for reading a new chapter
            progression_result = ProgressionService.award_points(
                current_user.id, 
                'read_chapter', 
                chapter.id
            )
    
    db.session.commit()
    
    # Get next and previous chapters
    next_chapter = Chapter.query.filter(
        Chapter.comic_id == comic_id,
        Chapter.chapter_number > chapter_number
    ).order_by(Chapter.chapter_number.asc()).first()
    
    prev_chapter = Chapter.query.filter(
        Chapter.comic_id == comic_id,
        Chapter.chapter_number < chapter_number
    ).order_by(Chapter.chapter_number.desc()).first()
    
    # Parse image URLs from JSON string if it's a comic
    image_urls = json.loads(chapter.image_urls) if chapter.image_urls else []
    
    # Use different template based on content type
    if comic.content_type == 'novel':
        template = 'comic/read_novel.html'
    else:
        template = 'comic/read.html'
    
    return render_template(template,
                         comic=comic,
                         chapter=chapter,
                         images=image_urls,
                         next_chapter=next_chapter,
                         prev_chapter=prev_chapter)

# API endpoints for admin/upload functionality
@comic.route('/', methods=['POST'])
@jwt_required()
def create_comic():
    try:
        data = ComicCreate(**request.get_json())
        comic = Comic(**data.model_dump())
        
        db.session.add(comic)
        db.session.commit()
        
        return jsonify({'message': 'Comic created successfully', 'id': comic.id}), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@comic.route('/<int:comic_id>/chapter', methods=['POST'])
@jwt_required()
def add_chapter(comic_id):
    try:
        data = ChapterCreate(**request.get_json())
        chapter = Chapter(
            comic_id=comic_id,
            chapter_number=data.chapter_number,
            title=data.title,
            image_urls=data.image_urls
        )
        
        db.session.add(chapter)
        db.session.commit()
        
        return jsonify({'message': 'Chapter added successfully', 'id': chapter.id}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@comic.route('/<int:comic_id>/comment', methods=['POST'])
@login_required
def add_comment(comic_id):
    comic = Comic.query.get_or_404(comic_id)
    content = request.form.get('content')
    
    if not content or not content.strip():
        flash('Bình luận không được để trống.', 'danger')
        return redirect(url_for('comic.view_comic', comic_id=comic_id))
    
    try:
        comment = Comment(
            user_id=current_user.id,
            comic_id=comic_id,
            content=content.strip()
        )
        db.session.add(comment)
        db.session.commit()
        
        # Award points for commenting
        progression_result = ProgressionService.award_points(
            current_user.id, 
            'comment', 
            comment.id
        )
        
        # Show level up message if applicable
        if progression_result and progression_result['level_up']:
            flash(f'Bình luận đã được đăng thành công! 🎉 Bạn đã lên cấp {progression_result["new_level"]} - {progression_result["rank_title"]}!', 'success')
        else:
            flash('Bình luận đã được đăng thành công!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi khi đăng bình luận: {str(e)}', 'danger')
    
    return redirect(url_for('comic.view_comic', comic_id=comic_id))

@comic.route('/<int:comic_id>/follow', methods=['POST'])
@login_required
def toggle_follow(comic_id):
    comic = Comic.query.get_or_404(comic_id)
    
    # Kiểm tra xem user đã follow chưa
    existing_follow = Follow.query.filter_by(
        user_id=current_user.id,
        comic_id=comic_id
    ).first()
    
    try:
        if existing_follow:
            # Nếu đã follow thì unfollow
            db.session.delete(existing_follow)
            comic.follow_count = max(0, comic.follow_count - 1)
            flash('Đã bỏ theo dõi truyện!', 'info')
        else:
            # Nếu chưa follow thì follow
            new_follow = Follow(
                user_id=current_user.id,
                comic_id=comic_id
            )
            db.session.add(new_follow)
            comic.follow_count = comic.follow_count + 1
            flash('Đã theo dõi truyện!', 'success')
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi khi cập nhật theo dõi: {str(e)}', 'danger')
    
    return redirect(url_for('comic.view_comic', comic_id=comic_id))