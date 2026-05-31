"""
Authentication Routes Module
----------------------------
Handles user registration, login, and logout functionality.
Includes server-side validation, flash messaging, and session management.

Routes:
    /register  → GET/POST  → User registration with validation
    /login     → GET/POST  → User login with session creation
    /logout    → GET       → Clear session and redirect
"""

import re
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models.user import User

# ── Blueprint Setup ──────────────────────────────────────────────────────────
auth_bp = Blueprint('auth', __name__, url_prefix='/')

# ── Validation Helpers ───────────────────────────────────────────────────────

def validate_username(username):
    """Check username: 3-20 chars, alphanumeric + underscore only."""
    if not username or len(username) < 3 or len(username) > 20:
        return "Username must be between 3 and 20 characters."
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return "Username can only contain letters, numbers, and underscores."
    return None


def validate_email(email):
    """Check email format using regex."""
    if not email:
        return "Email is required."
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return "Please enter a valid email address."
    return None


def validate_password(password):
    """Enforce strong password policy."""
    if not password or len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search(r'[A-Z]', password):
        return "Password must contain at least one uppercase letter."
    if not re.search(r'[a-z]', password):
        return "Password must contain at least one lowercase letter."
    if not re.search(r'[0-9]', password):
        return "Password must contain at least one digit."
    return None


# ── Routes ───────────────────────────────────────────────────────────────────

@auth_bp.route('/')
def home():
    """Landing page: redirect authenticated users to dashboard, else to login."""
    if current_user.is_authenticated:
        return redirect(url_for('task.dashboard'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration with comprehensive validation."""
    # Redirect already-logged-in users
    if current_user.is_authenticated:
        return redirect(url_for('task.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # ── Field-level validation ──
        error = validate_username(username)
        if error:
            flash(error, 'danger')
            return render_template('register.html', username=username, email=email)

        error = validate_email(email)
        if error:
            flash(error, 'danger')
            return render_template('register.html', username=username, email=email)

        error = validate_password(password)
        if error:
            flash(error, 'danger')
            return render_template('register.html', username=username, email=email)

        if password != confirm_password:
            flash("Passwords do not match.", 'danger')
            return render_template('register.html', username=username, email=email)

        # ── Uniqueness checks ──
        if User.query.filter_by(username=username).first():
            flash("Username already taken. Please choose another.", 'warning')
            return render_template('register.html', username=username, email=email)

        if User.query.filter_by(email=email).first():
            flash("An account with this email already exists.", 'warning')
            return render_template('register.html', username=username, email=email)

        # ── Create user ──
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully! Please log in.", 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login with session creation via Flask-Login."""
    # Redirect already-logged-in users
    if current_user.is_authenticated:
        return redirect(url_for('task.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        if not username or not password:
            flash("Please enter both username and password.", 'danger')
            return render_template('login.html', username=username)

        # Lookup user by username
        user = User.query.filter_by(username=username).first()

        if user is None:
            flash("Username not found. Please check your credentials or register.", 'danger')
            return render_template('login.html', username=username)

        if not user.check_password(password):
            flash("Incorrect password. Please try again.", 'danger')
            return render_template('login.html', username=username)

        # ── Authenticate ──
        login_user(user, remember=remember)
        flash(f"Welcome back, {user.username}!", 'success')

        # Redirect to originally requested page (if any) or dashboard
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
        return redirect(url_for('task.dashboard'))

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Log out the current user and clear their session."""
    logout_user()
    flash("You have been logged out successfully.", 'info')
    return redirect(url_for('auth.login'))
