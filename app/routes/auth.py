from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.services.progression import ProgressionService
from app import db
from sqlalchemy.exc import IntegrityError
import os
from werkzeug.utils import secure_filename

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    # Registration page and form handler
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        rank_type = request.form.get('rank_type', 'Tu Tiên')  # Default to Tu Tiên

        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('auth.register'))

        # Validate rank_type
        valid_ranks = ['Tu Tiên', 'Ma Vương', 'Pháp Sư']
        if rank_type not in valid_ranks:
            rank_type = 'Tu Tiên'

        try:
            user = User(username=username, email=email, rank_type=rank_type)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash(f'Chào mừng {username} gia nhập con đường {rank_type}!', 'success')
            return redirect(url_for('auth.login'))
        except IntegrityError:
            db.session.rollback()
            flash('Tên đăng nhập hoặc email đã tồn tại.', 'danger')
            return redirect(url_for('auth.register'))
    return render_template('auth/register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            # Check if user is banned
            if user.is_currently_banned():
                ban_info = user.get_ban_info()
                if ban_info['is_permanent']:
                    flash(f'Tài khoản của bạn đã bị cấm vĩnh viễn. Lý do: {ban_info["reason"]}', 'danger')
                else:
                    flash(f'Tài khoản của bạn bị cấm đến {ban_info["ban_until"].strftime("%d/%m/%Y %H:%M")}. Lý do: {ban_info["reason"]}', 'danger')
                return redirect(url_for('auth.login'))
            
            login_user(user)
            
            # Award daily login points
            progression_result = ProgressionService.award_points(
                user.id, 
                'daily_login'
            )
            
            # Show welcome message with level info if leveled up
            if progression_result and progression_result['level_up']:
                flash(f'Chào mừng trở lại! 🎉 Bạn đã lên cấp {progression_result["new_level"]} - {progression_result["rank_title"]}!', 'success')
            else:
                flash('Đăng nhập thành công!', 'success')
            
            return redirect(url_for('main.homepage'))
        flash('Invalid username or password.', 'danger')
        return redirect(url_for('auth.login'))
    return render_template('auth/login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.homepage'))

@auth.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not all([current_password, new_password, confirm_password]):
        flash('All fields are required.', 'danger')
        return redirect(url_for('main.profile'))
    
    if not current_user.check_password(current_password):
        flash('Current password is incorrect.', 'danger')
        return redirect(url_for('main.profile'))
    
    if new_password != confirm_password:
        flash('New passwords do not match.', 'danger')
        return redirect(url_for('main.profile'))
    
    if len(new_password) < 6:
        flash('Password must be at least 6 characters long.', 'danger')
        return redirect(url_for('main.profile'))
    
    current_user.set_password(new_password)
    db.session.commit()
    flash('Password changed successfully!', 'success')
    return redirect(url_for('main.profile'))

@auth.route('/update-avatar', methods=['POST'])
@login_required
def update_avatar():
    """Update user avatar URL"""
    avatar_url = request.form.get('avatar_url')
    
    if not avatar_url:
        flash('Please provide an avatar URL.', 'danger')
        return redirect(url_for('main.profile'))
    
    # Validate URL format (basic check)
    if not (avatar_url.startswith('http://') or avatar_url.startswith('https://')):
        flash('Please provide a valid URL starting with http:// or https://', 'danger')
        return redirect(url_for('main.profile'))
    
    current_user.avatar_url = avatar_url
    db.session.commit()
    flash('Avatar updated successfully!', 'success')
    return redirect(url_for('main.profile'))

@auth.route('/update-display-name', methods=['POST'])
@login_required
def update_display_name():
    """Update user display name"""
    display_name = request.form.get('display_name', '').strip()
    
    if not display_name:
        flash('Vui lòng nhập tên hiển thị.', 'danger')
        return redirect(url_for('main.profile'))
    
    if len(display_name) > 100:
        flash('Tên hiển thị không được vượt quá 100 ký tự.', 'danger')
        return redirect(url_for('main.profile'))
    
    current_user.display_name = display_name
    db.session.commit()
    flash('Tên hiển thị đã được cập nhật!', 'success')
    return redirect(url_for('main.profile'))



