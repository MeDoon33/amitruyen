from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from app.models.comic import Comic
from app.models.user import User
from app import db
from datetime import datetime, timedelta
from sqlalchemy import func

main = Blueprint('main', __name__)

@main.route('/')
def homepage():
    """Main homepage - redirect to comic homepage by default"""
    return redirect(url_for('main.comic_homepage'))

@main.route('/comics-home')
def comic_homepage():
    """Homepage dedicated to comics (truyện tranh)"""
    # Filter for comics only (using content_type field)
    comics_query = Comic.query.filter(
        (Comic.content_type == 'comic') | (Comic.content_type == None)
    )
    
    latest_comics = comics_query.order_by(Comic.updated_at.desc()).limit(12).all()
    popular_comics = comics_query.order_by(Comic.views.desc()).limit(5).all()
    ranking_comics = comics_query.order_by(Comic.views.desc()).limit(10).all()
    
    return render_template('comic_homepage.html', 
                         latest_comics=latest_comics, 
                         popular_comics=popular_comics,
                         ranking_comics=ranking_comics,
                         page_type='comics')

@main.route('/novels-home')
def novel_homepage():
    """Homepage dedicated to novels (truyện chữ)"""
    # Filter for novels only (using content_type field)
    novels_query = Comic.query.filter(Comic.content_type == 'novel')
    
    latest_novels = novels_query.order_by(Comic.updated_at.desc()).limit(12).all()
    popular_novels = novels_query.order_by(Comic.views.desc()).limit(5).all()
    ranking_novels = novels_query.order_by(Comic.views.desc()).limit(10).all()
    
    return render_template('novel_homepage.html', 
                         latest_novels=latest_novels, 
                         popular_novels=popular_novels,
                         ranking_novels=ranking_novels,
                         page_type='novels')

@main.route('/api/ranking/<period>')
def get_ranking_data(period):
    """
    API endpoint để lấy dữ liệu xếp hạng theo khoảng thời gian
    period: 'thang', 'tuan', 'ngay'
    """
    try:
        now = datetime.utcnow()
        
        if period == 'ngay':
            # Lấy comics được cập nhật trong 24h qua, sắp xếp theo views
            date_filter = now - timedelta(days=1)
            comics = Comic.query.filter(
                Comic.updated_at >= date_filter
            ).order_by(Comic.views.desc()).limit(10).all()
            
        elif period == 'tuan':
            # Lấy comics được cập nhật trong 7 ngày qua, sắp xếp theo views
            date_filter = now - timedelta(days=7)
            comics = Comic.query.filter(
                Comic.updated_at >= date_filter
            ).order_by(Comic.views.desc()).limit(10).all()
            
        elif period == 'thang':
            # Lấy comics được cập nhật trong 30 ngày qua, sắp xếp theo views
            date_filter = now - timedelta(days=30)
            comics = Comic.query.filter(
                Comic.updated_at >= date_filter
            ).order_by(Comic.views.desc()).limit(10).all()
            
        else:
            return jsonify({'error': 'Invalid period'}), 400
            
        # Format dữ liệu để trả về
        ranking_data = []
        for idx, comic in enumerate(comics, 1):
            ranking_data.append({
                'rank': idx,
                'id': comic.id,
                'title': comic.title,
                'author': comic.author,
                'cover_image': comic.cover_image,
                'views': comic.views,
                'chapters_count': len(comic.chapters) if comic.chapters else 0,
                'updated_at': comic.updated_at.strftime('%Y-%m-%d %H:%M:%S') if comic.updated_at else None
            })
            
        return jsonify({
            'success': True,
            'period': period,
            'data': ranking_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Profile page (after login)
from flask_login import login_required, current_user
from app.models.comic import Follow, Comic

@main.route('/profile')
@login_required
def profile():
    # Lấy các truyện đang theo dõi
    followed_comics = db.session.query(Comic).join(Follow).filter(Follow.user_id == current_user.id).order_by(Follow.created_at.desc()).all()
    return render_template('auth/profile.html', user=current_user, followed_comics=followed_comics)

@main.route('/demo/level-colors')
def demo_level_colors():
    # Lấy một số user mẫu để demo
    sample_users = User.query.limit(5).all()
    return render_template('demo_level_colors.html', sample_users=sample_users)

@main.route('/test/gradient')
def test_gradient():
    # Test gradient clip functionality
    sample_users = User.query.limit(3).all()
    return render_template('test_gradient.html', sample_users=sample_users)

@main.route('/demo/gradient-titles')
def demo_gradient_titles():
    """Demo trang hiển thị gradient titles"""
    # Lấy một số user mẫu
    sample_users = User.query.limit(5).all()
    return render_template('demo_gradient_titles.html', sample_users=sample_users)

@main.route('/test/leaderboard-design')
def test_leaderboard_design():
    """Test page for leaderboard design"""
    return render_template('test_leaderboard_design.html')

@main.route('/ranking/comics')
def comic_ranking():
    """Comic ranking page"""
    return render_template('comic_ranking.html')

@main.route('/api/comic-ranking')
def get_comic_ranking():
    """API endpoint for comic ranking"""
    try:
        period = request.args.get('period', 'all')  # all, month, week, day
        content_type = request.args.get('type', 'all')  # all, comics, novels
        
        # Base query
        comics_query = Comic.query
        
        # Filter by content type
        if content_type == 'comics':
            # Filter for comics only
            comics_query = comics_query.filter(
                (Comic.content_type == 'comic') | (Comic.content_type == None)
            )
        elif content_type == 'novels':
            # Filter for novels only
            comics_query = comics_query.filter(Comic.content_type == 'novel')
        
        # Filter by time period
        if period != 'all':
            now = datetime.utcnow()
            if period == 'day':
                date_filter = now - timedelta(days=1)
            elif period == 'week':
                date_filter = now - timedelta(days=7)
            elif period == 'month':
                date_filter = now - timedelta(days=30)
            
            comics_query = comics_query.filter(Comic.updated_at >= date_filter)
        
        # Order by views (descending) and limit to top 20
        comics = comics_query.order_by(Comic.views.desc()).limit(20).all()
        
        # Format data
        comics_data = []
        for comic in comics:
            comics_data.append({
                'id': comic.id,
                'title': comic.title,
                'author': comic.author,
                'cover_image': comic.cover_image,
                'views': comic.views or 0,
                'likes': 0,  # Placeholder for likes
                'chapters_count': len(comic.chapters) if comic.chapters else 0,
                'status': 'Đang tiến hành',  # Default status
                'genre': comic.genre,
                'updated_at': comic.updated_at.strftime('%Y-%m-%d') if comic.updated_at else None
            })
        
        return jsonify({
            'success': True,
            'comics': comics_data,
            'period': period,
            'type': content_type,
            'total': len(comics_data)
        })
        
    except Exception as e:
        print(f"Error in comic ranking API: {e}")  # Debug print
        return jsonify({'success': False, 'error': str(e)}), 500

