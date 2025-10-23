from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    """
    Decorator to require admin role for a route.
    Usage: @admin_required above route function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_admin():
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.homepage'))
        return f(*args, **kwargs)
    return decorated_function

def moderator_required(f):
    """
    Decorator to require moderator or admin role for a route.
    Usage: @moderator_required above route function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_moderator():
            flash('Bạn không có quyền kiểm duyệt.', 'danger')
            return redirect(url_for('main.homepage'))
        return f(*args, **kwargs)
    return decorated_function

def uploader_required(f):
    """
    Decorator to require uploader, moderator, or admin role for a route.
    Usage: @uploader_required above route function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_uploader():
            flash('Bạn không có quyền đăng truyện.', 'danger')
            return redirect(url_for('main.homepage'))
        return f(*args, **kwargs)
    return decorated_function

def reader_required(f):
    """
    Decorator to require any logged-in user (reader, uploader, moderator, admin).
    Usage: @reader_required above route function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_reader():
            flash('Bạn không có quyền đọc truyện.', 'danger')
            return redirect(url_for('main.homepage'))
        return f(*args, **kwargs)
    return decorated_function
