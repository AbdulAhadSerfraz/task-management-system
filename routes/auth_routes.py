"""
Authentication Routes (Blueprint: auth)
----------------------------------------
Handles user registration, login, logout, and the home page redirect.

Routes:
    /           -> Redirects to dashboard (if logged in) or login page
    /login      -> GET: Shows login form  |  POST: Authenticates user
    /register   -> GET: Shows register form  |  POST: Creates new user
    /logout     -> Logs out the current user and redirects to login

Validation Rules (Registration):
    - All fields are required
    - Password must match confirmation
    - Password must be at least 6 characters
    - Username and email must be unique
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models.user import User

# Create the authentication blueprint
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def home():
    """Root URL: redirect based on authentication status."""
    if current_user.is_authenticated:
        return redirect(url_for('task.dashboard'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login.

    GET: Display the login form.
    POST: Validate credentials against the database.
        - If valid: start user session and redirect to dashboard.
        - If invalid: show error flash message and reload form.
    """
    # Already logged-in users go straight to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('task.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Look up the user by username
        user = User.query.filter_by(username=username).first()

        # Verify password against stored hash
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('task.dashboard'))

        flash('Invalid username or password', 'danger')

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle new user registration.

    GET: Display the registration form.
    POST: Validate input, check uniqueness, create user in database.
    """
    if current_user.is_authenticated:
        return redirect(url_for('task.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')

        # --- Validation ---

        # Check all fields are filled
        if not username or not email or not password:
            flash('All fields are required', 'danger')
            return render_template('register.html')

        # Check passwords match
        if password != confirm:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')

        # Check minimum password length
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return render_template('register.html')

        # Check username uniqueness
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('register.html')

        # Check email uniqueness
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('register.html')

        # --- Create User ---
        user = User(username=username, email=email)
        user.set_password(password)  # Hash the password before storing
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/logout')
@login_required  # Only accessible by logged-in users
def logout():
    """Log out the current user and redirect to login page."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
