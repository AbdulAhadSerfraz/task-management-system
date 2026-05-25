# Task Management System — Complete Project Documentation

> **Project:** Task Management System  
> **Tech Stack:** Python, Flask, SQLite, Bootstrap 5, PyTest  
> **Repository:** [github.com/AbdulAhadSerfraz/task-management-system](https://github.com/AbdulAhadSerfraz/task-management-system)

---

## Table of Contents

1. [Project Structure](#1-project-structure)
2. [Architecture & Workflow](#2-architecture--workflow)
3. [Configuration](#3-configuration)
4. [Application Entry Point (Factory)](#4-application-entry-point-factory)
5. [Extensions (Shared Instances)](#5-extensions-shared-instances)
6. [Models](#6-models)
   - [User Model](#61-user-model)
   - [Task Model](#62-task-model)
7. [Routes (Blueprints)](#7-routes-blueprints)
   - [Authentication Routes](#71-authentication-routes)
   - [Task CRUD Routes](#72-task-crud-routes)
8. [Templates (HTML)](#8-templates-html)
9. [Static Assets (CSS)](#9-static-assets-css)
10. [Unit Tests](#10-unit-tests)
11. [API Route Reference](#11-api-route-reference)
12. [Database Schema](#12-database-schema)
13. [How to Run](#13-how-to-run)

---

## 1. Project Structure

```
task-management-system/
│
├── app.py                   # Application factory — creates Flask app
├── config.py                # Configuration settings (DB URI, secret key)
├── extensions.py            # Flask extensions (db, login_manager)
├── requirements.txt         # Python package dependencies
├── .gitignore               # Git ignore rules
├── README.md                # Project README (user-facing)
├── PROJECT_DOCUMENTATION.md # This file — full code documentation
│
├── screenshots/             # Application screenshots
│   ├── login.png
│   ├── register page.png
│   ├── dashboard.png
│   └── new task.png
│
├── models/                  # Database models (SQLAlchemy ORM)
│   ├── __init__.py
│   ├── user.py              # User model (authentication)
│   └── task.py              # Task model (CRUD operations)
│
├── routes/                  # Route blueprints
│   ├── __init__.py
│   ├── auth_routes.py       # Authentication (login/register/logout)
│   └── task_routes.py       # Task management (CRUD)
│
├── templates/               # Jinja2 HTML templates
│   ├── base.html            # Base layout with Bootstrap
│   ├── login.html           # Login form
│   ├── register.html        # Registration form
│   ├── dashboard.html       # Task dashboard (grid view)
│   ├── create_task.html     # Create task form
│   └── edit_task.html       # Edit task form
│
├── static/                  # Static assets
│   └── css/
│       └── style.css        # Custom styles (gradient, cards)
│
├── tests/                   # PyTest unit tests
│   ├── __init__.py
│   └── test_app.py          # 16 tests (auth + task CRUD)
│
└── utils/                   # Utility module (extensible)
    └── __init__.py
```

---

## 2. Architecture & Workflow

### Application Flow Diagram

```
User opens browser → http://localhost:5000
         │
         ▼
    ┌─────────────┐
    │  Home Page   │  Redirects to Login or Dashboard
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │   Register  │  Create account (username, email, password)
    └──────┬──────┘
           ▼
    ┌─────────────┐
    │    Login    │  Authenticate → session cookie created
    └──────┬──────┘
           ▼
    ┌─────────────┐      ┌──────────────────┐
    │  Dashboard  │──────│   Create Task    │
    │ (Task List) │      └──────────────────┘
    └──────┬──────┘
           │
    ┌──────▼──────┐      ┌──────────────────┐
    │  Task Card  │──────│   Edit Task      │
    │ (Actions)   │──────│   Delete Task    │
    │             │──────│   Complete/Undo  │
    └─────────────┘
```

### Architecture Pattern

This project follows the **Application Factory** pattern:

1. **`extensions.py`** — Creates shared instances (`db`, `login_manager`) at module level
2. **`config.py`** — Centralized configuration constants
3. **`app.py`** — `create_app()` function assembles the Flask app with all components
4. **`models/`** — Database models (SQLAlchemy ORM)
5. **`routes/`** — Blueprint-based route handlers
6. **`templates/`** — Jinja2 HTML templates
7. **`tests/`** — PyTest unit tests with isolated temp databases

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| App Factory pattern | Enables testing with different configs (temp DB, etc.) |
| Blueprints | Modular route organization (auth vs task) |
| `extensions.py` | Avoids circular imports between `app.py` and models |
| Werkzeug password hashing | Secure password storage (bcrypt/PBKDF2) |
| SQLite | Zero-configuration database, file-based |
| Bootstrap 5 CDN | Responsive UI without build tools |

---

## 3. Configuration

**File:** `config.py`

```python
"""
Configuration Module
-------------------
Central configuration settings for the Task Management Flask application.
Contains database URI, secret key, and other Flask/SQLAlchemy settings.
"""

import os

# Absolute path to the project root directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Secret key for session signing and CSRF protection
# In production, set SECRET_KEY as an environment variable
SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

# SQLite database file path (stored in the project root)
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'database.db')

# Disable Flask-SQLAlchemy event tracking (saves memory)
SQLALCHEMY_TRACK_MODIFICATIONS = False
```

**Explanation:**

| Variable | Purpose |
|----------|---------|
| `BASE_DIR` | Absolute path to the project root (used for database file location) |
| `SECRET_KEY` | Used by Flask to sign session cookies. Falls back to a dev key if env var not set |
| `SQLALCHEMY_DATABASE_URI` | Points to a `database.db` file in the project root |
| `SQLALCHEMY_TRACK_MODIFICATIONS` | Set to `False` to reduce memory usage |

---

## 4. Application Entry Point (Factory)

**File:** `app.py`

```python
"""
Application Entry Point (Factory Pattern)
-----------------------------------------
Creates and configures the Flask application using the create_app() factory
function. This pattern allows for easy testing with different configurations.

Flow:
  1. create_app() is called
  2. Flask app is created with settings from config.py
  3. Extensions (db, login_manager) are initialized with the app
  4. Models (User, Task) are imported to register them with SQLAlchemy
  5. Blueprints (auth, task) are registered for routing
  6. When run directly, tables are created and the dev server starts
"""

from flask import Flask
from config import SECRET_KEY, SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from extensions import db, login_manager


def create_app(test_config=None):
    """Application factory function.

    Creates a Flask app instance with the specified configuration.
    Accepts an optional test_config dict to override settings for testing.

    Args:
        test_config: Dictionary of config overrides (used by PyTest).

    Returns:
        A configured Flask application instance.
    """
    app = Flask(__name__)

    # Load default configuration from config.py
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

    # Override with test config if provided (used in test_app.py)
    if test_config:
        app.config.update(test_config)

    # Initialize Flask extensions with this app instance
    db.init_app(app)
    login_manager.init_app(app)

    # Import models to register them with SQLAlchemy
    # (imported here to avoid circular imports)
    from models.user import User
    from models.task import Task

    # Import and register route blueprints
    from routes.auth_routes import auth_bp
    from routes.task_routes import task_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(task_bp)

    return app


# Only runs when executing app.py directly (not during import)
if __name__ == '__main__':
    app = create_app()
    # Create all database tables if they don't exist
    with app.app_context():
        db.create_all()
    # Start the Flask development server
    app.run(debug=True)
```

**Explanation:**

- **`create_app(test_config=None)`** — Factory function that assembles the app. The `test_config` parameter allows PyTest to inject a temporary database URI without modifying `config.py`
- **`db.init_app(app)`** — Binds the SQLAlchemy instance to this app
- **`login_manager.init_app(app)`** — Binds Flask-Login to this app
- Models and blueprints are imported **inside** the function to avoid circular imports (since they import `db`/`login_manager` from `extensions`)
- **`db.create_all()`** runs at startup to ensure tables exist

---

## 5. Extensions (Shared Instances)

**File:** `extensions.py`

```python
"""
Extensions Module
-----------------
Initializes Flask extensions (SQLAlchemy and LoginManager) that are shared
across the entire application. Importing from here avoids circular imports
that occur when importing directly from app.py.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# SQLAlchemy ORM instance for database operations
db = SQLAlchemy()

# Flask-Login manager for session-based authentication
login_manager = LoginManager()
# Redirect unauthenticated users to the login page
login_manager.login_view = 'auth.login'
```

**Explanation:**

This file exists to solve the **circular import problem**. In a Flask app:

- `app.py` needs `db` and `login_manager`
- `models/user.py` needs `db` and `login_manager`  
- `routes/auth_routes.py` needs `db`
- `routes/task_routes.py` needs `db`

If `models/user.py` imported from `app.py`, and `app.py` imported from `models/user.py`, we'd get a circular import. By placing `db` and `login_manager` in `extensions.py`, all modules can safely import from it without cycles.

---

## 6. Models

### 6.1 User Model

**File:** `models/user.py`

```python
"""
User Model Module
-----------------
Defines the User database model and the Flask-Login user_loader callback.

Relationships:
    - User has many Task objects (one-to-many via tasks relationship)
    - Passwords are hashed using Werkzeug's generate_password_hash

Flask-Login Integration:
    @login_manager.user_loader tells Flask-Login how to retrieve a User
    from the database using the user ID stored in the session cookie.
"""

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login callback: loads a user from the database by ID.

    Args:
        user_id: The user ID stored in the session cookie (as string).

    Returns:
        User object or None if not found.
    """
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    """User model representing an authenticated user.

    Attributes:
        id: Primary key (auto-increment integer).
        username: Unique display name used for login.
        email: Unique email address.
        password_hash: Securely hashed password (never stored in plain text).
        tasks: One-to-many relationship with Task model.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    # Relationship: one User has many Tasks (cascade delete not enabled)
    tasks = db.relationship('Task', backref='owner', lazy='dynamic')

    def set_password(self, password):
        """Hash and store the given password.

        Args:
            password: Plain-text password to hash.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify the given password against the stored hash.

        Args:
            password: Plain-text password to verify.

        Returns:
            True if password matches, False otherwise.
        """
        return check_password_hash(self.password_hash, password)
```

**Key Points:**

| Feature | Implementation |
|---------|---------------|
| Password storage | Hashed with `werkzeug.security.generate_password_hash()` (PBKDF2 by default) |
| Login session | Flask-Login's `UserMixin` provides `is_authenticated`, `is_active`, etc. |
| User loader | `@login_manager.user_loader` callback loads user by ID from session cookie |
| Task relationship | `User.tasks` gives all tasks belonging to this user via SQLAlchemy relationship |

### 6.2 Task Model

**File:** `models/task.py`

```python
"""
Task Model Module
-----------------
Defines the Task database model for the task management system.

Relationships:
    - Task belongs to one User (many-to-one via user_id foreign key)
    - The 'owner' backref allows accessing task.owner to get the User
"""

from datetime import datetime
from extensions import db


class Task(db.Model):
    """Task model representing a single to-do item.

    Each task belongs to a user and tracks its completion status.

    Attributes:
        id: Primary key (auto-increment integer).
        title: Short task description (required, max 200 chars).
        description: Optional longer task details (text field).
        completed: Boolean flag indicating completion status.
        created_at: Timestamp set automatically when task is created.
        user_id: Foreign key referencing the owning user's ID.
    """
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign key: links each task to its owning user
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
```

**Key Points:**

| Field | Type | Notes |
|-------|------|-------|
| `id` | Integer (PK) | Auto-incremented |
| `title` | String(200) | Required, max 200 characters |
| `description` | Text | Optional |
| `completed` | Boolean | Defaults to `False` (pending) |
| `created_at` | DateTime | Auto-set on creation |
| `user_id` | Integer (FK) | References `users.id` |

**Foreign Key Relationship:**
- `user_id` → `users.id` creates a many-to-one relationship
- `task.owner` gives the User (via `backref='owner'`)
- `user.tasks` gives all tasks (via `relationship`)

---

## 7. Routes (Blueprints)

### 7.1 Authentication Routes

**File:** `routes/auth_routes.py`

```python
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
    if current_user.is_authenticated:
        return redirect(url_for('task.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

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
        if not username or not email or not password:
            flash('All fields are required', 'danger')
            return render_template('register.html')

        if password != confirm:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('register.html')

        # --- Create User ---
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Log out the current user and redirect to login page."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
```

**Route Summary:**

| Route | Methods | Auth Required | Description |
|-------|---------|---------------|-------------|
| `/` | GET | No | Redirects to dashboard or login |
| `/login` | GET, POST | No | Show form / authenticate user |
| `/register` | GET, POST | No | Show form / create user |
| `/logout` | GET | Yes | Clear session, redirect to login |

**Authentication Flow:**

```
Login Request
     │
     ├── Check if already logged in → redirect to dashboard
     │
     ├── POST?
     │    ├── Look up user by username
     │    ├── Verify password hash
     │    │    ├── Match → login_user(), session created → redirect dashboard
     │    │    └── No match → flash error → show form
     │    └── User not found → flash error → show form
     │
     └── GET → show login form
```

**Registration Validation:**

```
Register Request
     │
     ├── Check all fields filled
     ├── Check passwords match
     ├── Check password length ≥ 6
     ├── Check username uniqueness
     ├── Check email uniqueness
     │
     └── All pass → hash password → save user → redirect login
```

### 7.2 Task CRUD Routes

**File:** `routes/task_routes.py`

```python
"""
Task CRUD Routes (Blueprint: task)
----------------------------------
Handles all task management operations for authenticated users.

Routes:
    /dashboard              -> Display all tasks for the logged-in user
    /tasks/create           -> GET: Show create form  |  POST: Save new task
    /tasks/edit/<id>        -> GET: Show edit form  |  POST: Update task
    /tasks/delete/<id>      -> Delete a task (GET-only for simplicity)
    /tasks/complete/<id>    -> Toggle task completion status

Security:
    All routes require login (@login_required).
    Ownership is enforced: users can only see/edit/delete their own tasks.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models.task import Task

# Create the task management blueprint
task_bp = Blueprint('task', __name__)


@task_bp.route('/dashboard')
@login_required
def dashboard():
    """Display all tasks belonging to the logged-in user.

    Tasks are ordered by creation date (newest first).
    The template renders each task as a card with action buttons.
    """
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()
    return render_template('dashboard.html', tasks=tasks)


@task_bp.route('/tasks/create', methods=['GET', 'POST'])
@login_required
def create_task():
    """Create a new task.

    GET: Display the create task form.
    POST: Validate title, save task to database, redirect to dashboard.
    """
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')

        if not title or not title.strip():
            flash('Task title is required', 'danger')
            return render_template('create_task.html')

        task = Task(title=title.strip(), description=description, user_id=current_user.id)
        db.session.add(task)
        db.session.commit()

        flash('Task created successfully!', 'success')
        return redirect(url_for('task.dashboard'))

    return render_template('create_task.html')


@task_bp.route('/tasks/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    """Edit an existing task.

    GET: Display the edit form pre-filled with task data.
    POST: Update task title and/or description.

    Ownership check: Redirects with error if task belongs to another user.
    """
    task = Task.query.get_or_404(task_id)

    if task.user_id != current_user.id:
        flash('You do not have permission to edit this task', 'danger')
        return redirect(url_for('task.dashboard'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')

        if not title or not title.strip():
            flash('Task title is required', 'danger')
            return render_template('edit_task.html', task=task)

        task.title = title.strip()
        task.description = description
        db.session.commit()

        flash('Task updated successfully!', 'success')
        return redirect(url_for('task.dashboard'))

    return render_template('edit_task.html', task=task)


@task_bp.route('/tasks/delete/<int:task_id>')
@login_required
def delete_task(task_id):
    """Delete a task permanently.

    Ownership check: Only the task owner can delete it.
    """
    task = Task.query.get_or_404(task_id)

    if task.user_id != current_user.id:
        flash('You do not have permission to delete this task', 'danger')
        return redirect(url_for('task.dashboard'))

    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('task.dashboard'))


@task_bp.route('/tasks/complete/<int:task_id>')
@login_required
def complete_task(task_id):
    """Toggle the completion status of a task.

    If the task is pending, mark it as complete.
    If the task is complete, mark it as pending (undo).

    Ownership check: Only the task owner can modify it.
    """
    task = Task.query.get_or_404(task_id)

    if task.user_id != current_user.id:
        flash('You do not have permission to modify this task', 'danger')
        return redirect(url_for('task.dashboard'))

    task.completed = not task.completed
    db.session.commit()

    flash('Task status updated!', 'success')
    return redirect(url_for('task.dashboard'))
```

**Route Summary:**

| Route | Methods | Auth Required | Description |
|-------|---------|---------------|-------------|
| `/dashboard` | GET | Yes | Show all user's tasks (newest first) |
| `/tasks/create` | GET, POST | Yes | Create a new task |
| `/tasks/edit/<id>` | GET, POST | Yes | Edit existing task (ownership check) |
| `/tasks/delete/<id>` | GET | Yes | Delete task (ownership check) |
| `/tasks/complete/<id>` | GET | Yes | Toggle completed status (ownership check) |

**Security Pattern (Ownership Check):**

Every task-modifying route follows this pattern:

```python
# 1. Fetch task or return 404
task = Task.query.get_or_404(task_id)

# 2. Check ownership
if task.user_id != current_user.id:
    flash('Permission denied', 'danger')
    return redirect(url_for('task.dashboard'))

# 3. Perform operation
task.completed = not task.completed
db.session.commit()
```

---

## 8. Templates (HTML)

### 8.1 Base Template

**File:** `templates/base.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Task Manager - {% block title %}{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    {% if current_user.is_authenticated %}
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('task.dashboard') }}">Task Manager</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('task.dashboard') }}">Dashboard</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('task.create_task') }}">New Task</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('auth.logout') }}">Logout</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
    {% endif %}

    <div class="container mt-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        {% block content %}{% endblock %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

**Template Blocks:**

| Block Name | Purpose |
|------------|---------|
| `{% block title %}` | Sets the browser tab title (appended to "Task Manager - ") |
| `{% block content %}` | Main page content (overridden by child templates) |

**Features:**
- Navigation bar visible **only** when `current_user.is_authenticated`
- Flash messages display with Bootstrap alert classes (`success`, `danger`, `info`, `warning`)
- Responsive navbar with mobile toggle button
- Bootstrap 5 loaded from CDN (both CSS and JS)

### 8.2 Login Template

**File:** `templates/login.html`

```html
{% extends "base.html" %}
{% block title %}Login{% endblock %}
{% block content %}
<div class="row justify-content-center mt-5">
    <div class="col-md-4">
        <div class="card">
            <div class="card-header bg-primary text-white text-center">
                <h4>Login</h4>
            </div>
            <div class="card-body">
                <form method="POST">
                    <div class="mb-3">
                        <label for="username" class="form-label">Username</label>
                        <input type="text" class="form-control" id="username" name="username" required>
                    </div>
                    <div class="mb-3">
                        <label for="password" class="form-label">Password</label>
                        <input type="password" class="form-control" id="password" name="password" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Login</button>
                </form>
                <div class="text-center mt-3">
                    <a href="{{ url_for('auth.register') }}">Don't have an account? Register</a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### 8.3 Register Template

**File:** `templates/register.html`

```html
{% extends "base.html" %}
{% block title %}Register{% endblock %}
{% block content %}
<div class="row justify-content-center mt-5">
    <div class="col-md-4">
        <div class="card">
            <div class="card-header bg-success text-white text-center">
                <h4>Register</h4>
            </div>
            <div class="card-body">
                <form method="POST">
                    <div class="mb-3">
                        <label for="username" class="form-label">Username</label>
                        <input type="text" class="form-control" id="username" name="username" required>
                    </div>
                    <div class="mb-3">
                        <label for="email" class="form-label">Email</label>
                        <input type="email" class="form-control" id="email" name="email" required>
                    </div>
                    <div class="mb-3">
                        <label for="password" class="form-label">Password</label>
                        <input type="password" class="form-control" id="password" name="password" required>
                    </div>
                    <div class="mb-3">
                        <label for="confirm_password" class="form-label">Confirm Password</label>
                        <input type="password" class="form-control" id="confirm_password" name="confirm_password" required>
                    </div>
                    <button type="submit" class="btn btn-success w-100">Register</button>
                </form>
                <div class="text-center mt-3">
                    <a href="{{ url_for('auth.login') }}">Already have an account? Login</a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### 8.4 Dashboard Template

**File:** `templates/dashboard.html`

```html
{% extends "base.html" %}
{% block title %}Dashboard{% endblock %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h2>My Tasks</h2>
    <a href="{{ url_for('task.create_task') }}" class="btn btn-primary">+ New Task</a>
</div>

{% if tasks %}
    <div class="row">
        {% for task in tasks %}
            <div class="col-md-4 mb-3">
                <div class="card task-card {% if task.completed %}completed-task{% endif %}">
                    <div class="card-body">
                        <h5 class="card-title">{{ task.title }}</h5>
                        <p class="card-text">{{ task.description or 'No description' }}</p>
                        <div class="mb-2">
                            <span class="badge {% if task.completed %}bg-success{% else %}bg-warning{% endif %}">
                                {{ 'Completed' if task.completed else 'Pending' }}
                            </span>
                            <small class="text-muted ms-2">{{ task.created_at.strftime('%Y-%m-%d') }}</small>
                        </div>
                        <div class="d-flex gap-2">
                            <a href="{{ url_for('task.complete_task', task_id=task.id) }}" 
                               class="btn btn-sm {% if task.completed %}btn-secondary{% else %}btn-success{% endif %}">
                                {{ 'Undo' if task.completed else 'Complete' }}
                            </a>
                            <a href="{{ url_for('task.edit_task', task_id=task.id) }}" 
                               class="btn btn-sm btn-warning">Edit</a>
                            <a href="{{ url_for('task.delete_task', task_id=task.id) }}" 
                               class="btn btn-sm btn-danger" 
                               onclick="return confirm('Delete this task?')">Delete</a>
                        </div>
                    </div>
                </div>
            </div>
        {% endfor %}
    </div>
{% else %}
    <div class="text-center mt-5">
        <h4 class="text-muted">No tasks yet</h4>
        <p>Create your first task to get started!</p>
        <a href="{{ url_for('task.create_task') }}" class="btn btn-primary">Create Task</a>
    </div>
{% endif %}
{% endblock %}
```

**Dashboard States:**

| State | What's Displayed |
|-------|-----------------|
| Has tasks | Grid of task cards with action buttons |
| No tasks | "No tasks yet" message with "Create Task" button |
| Task completed | Card is dimmed (opacity 0.7) with strikethrough text |

### 8.5 Create Task Template

**File:** `templates/create_task.html`

```html
{% extends "base.html" %}
{% block title %}Create Task{% endblock %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h4>Create New Task</h4>
            </div>
            <div class="card-body">
                <form method="POST">
                    <div class="mb-3">
                        <label for="title" class="form-label">Task Title</label>
                        <input type="text" class="form-control" id="title" name="title" required>
                    </div>
                    <div class="mb-3">
                        <label for="description" class="form-label">Description</label>
                        <textarea class="form-control" id="description" name="description" rows="3"></textarea>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Create Task</button>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### 8.6 Edit Task Template

**File:** `templates/edit_task.html`

```html
{% extends "base.html" %}
{% block title %}Edit Task{% endblock %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header bg-warning">
                <h4>Edit Task</h4>
            </div>
            <div class="card-body">
                <form method="POST">
                    <div class="mb-3">
                        <label for="title" class="form-label">Task Title</label>
                        <input type="text" class="form-control" id="title" name="title" value="{{ task.title }}" required>
                    </div>
                    <div class="mb-3">
                        <label for="description" class="form-label">Description</label>
                        <textarea class="form-control" id="description" name="description" rows="3">{{ task.description or '' }}</textarea>
                    </div>
                    <button type="submit" class="btn btn-warning w-100">Update Task</button>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

---

## 9. Static Assets (CSS)

**File:** `static/css/style.css`

```css
/* ---- Page Background ---- */
body {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
}

/* ---- Card Styling ---- */
.card {
    border: none;
    border-radius: 1rem;
    box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

.card-header {
    border-radius: 1rem 1rem 0 0 !important;
}

/* ---- Navigation Bar ---- */
.navbar {
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* ---- Task Cards ---- */
.task-card {
    transition: transform 0.2s;
}

.task-card:hover {
    transform: translateY(-2px);
}

/* ---- Completed Task Styling ---- */
.completed-task {
    opacity: 0.7;
    text-decoration: line-through;
}

/* ---- Flash Messages ---- */
.alert {
    border-radius: 0.5rem;
}

/* ---- Buttons ---- */
.btn {
    border-radius: 0.5rem;
}
```

**CSS Breakdown:**

| Selector | Purpose |
|----------|---------|
| `body` | Purple gradient background spanning full viewport height |
| `.card` | Rounded corners (1rem), subtle shadow, no border |
| `.card-header` | Rounded top corners only |
| `.navbar` | Bottom shadow for depth |
| `.task-card` | Smooth hover animation (lifts 2px) |
| `.completed-task` | Dimmed with strikethrough for completed tasks |
| `.alert` | Rounded flash messages |
| `.btn` | Rounded buttons |

---

## 10. Unit Tests

**File:** `tests/test_app.py`

```python
"""
Unit Tests for Task Management System
======================================
Uses PyTest with a temporary SQLite database for each test to ensure
isolation. Tests cover both authentication and task CRUD functionality.

Fixtures:
    app   - Creates a Flask app with a temporary database file
    client - Flask test client for making HTTP requests

Test Classes:
    TestAuth - Tests registration, login, logout, and input validation
    TestTask - Tests task creation, editing, deleting, completion, and dashboard
"""

import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from extensions import db
from models.user import User
from models.task import Task


# ----- Fixtures -----

@pytest.fixture
def app():
    """Create a Flask app with a temporary SQLite database.

    Each test gets a fresh database file to ensure test isolation.
    """
    db_fd, db_path = tempfile.mkstemp()
    app = create_app(test_config={
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + db_path,
        'TESTING': True,
    })

    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.engine.dispose()
    os.close(db_fd)
    try:
        os.unlink(db_path)
    except PermissionError:
        pass


@pytest.fixture
def client(app):
    """Flask test client for simulating HTTP requests."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Flask CLI runner."""
    return app.test_cli_runner()


# ----- Helper Functions -----

def register_user(client, username='testuser', email='test@example.com', password='password123'):
    return client.post('/register', data={
        'username': username, 'email': email,
        'password': password, 'confirm_password': password
    }, follow_redirects=True)


def login_user(client, username='testuser', password='password123'):
    return client.post('/login', data={
        'username': username, 'password': password
    }, follow_redirects=True)


# ----- Authentication Tests -----

class TestAuth:
    """Test cases for the authentication module."""

    def test_register_page(self, client):
        """Verify the registration page loads."""
        response = client.get('/register')
        assert response.status_code == 200

    def test_login_page(self, client):
        """Verify the login page loads."""
        response = client.get('/login')
        assert response.status_code == 200

    def test_successful_registration(self, client):
        """Verify a user can register with valid data."""
        response = register_user(client)
        assert response.status_code == 200

    def test_duplicate_username(self, client):
        """Verify duplicate usernames are rejected."""
        register_user(client)
        response = register_user(client)
        assert response.status_code == 200

    def test_successful_login(self, client):
        """Verify a registered user can log in."""
        register_user(client)
        response = login_user(client)
        assert response.status_code == 200

    def test_invalid_login(self, client):
        """Verify invalid credentials are rejected."""
        response = client.post('/login', data={
            'username': 'wrong', 'password': 'wrong'
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_logout(self, client):
        """Verify a logged-in user can log out."""
        register_user(client)
        login_user(client)
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200

    def test_password_mismatch(self, client):
        """Verify registration fails when passwords don't match."""
        response = client.post('/register', data={
            'username': 'testuser', 'email': 'test@example.com',
            'password': 'password123', 'confirm_password': 'different'
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_short_password(self, client):
        """Verify registration fails when password is too short."""
        response = client.post('/register', data={
            'username': 'testuser', 'email': 'test@example.com',
            'password': '123', 'confirm_password': '123'
        }, follow_redirects=True)
        assert response.status_code == 200


# ----- Task CRUD Tests -----

class TestTask:
    """Test cases for the task CRUD module."""

    def test_create_task_page_requires_login(self, client):
        """Verify unauthenticated users are redirected from create page."""
        response = client.get('/tasks/create', follow_redirects=True)
        assert response.status_code == 200

    def test_create_task(self, client):
        """Verify a logged-in user can create a task."""
        register_user(client)
        login_user(client)
        response = client.post('/tasks/create', data={
            'title': 'Test Task', 'description': 'Test Description'
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_dashboard_shows_tasks(self, client):
        """Verify the dashboard displays created tasks."""
        register_user(client); login_user(client)
        client.post('/tasks/create', data={'title': 'Test Task', 'description': 'Test Desc'})
        response = client.get('/dashboard', follow_redirects=True)
        assert response.status_code == 200

    def test_complete_task(self, client):
        """Verify a task can be marked as complete."""
        register_user(client); login_user(client)
        client.post('/tasks/create', data={'title': 'Test Task', 'description': 'Test Desc'})
        response = client.get('/tasks/complete/1', follow_redirects=True)
        assert response.status_code == 200

    def test_delete_task(self, client):
        """Verify a task can be deleted."""
        register_user(client); login_user(client)
        client.post('/tasks/create', data={'title': 'Test Task', 'description': 'Test Desc'})
        response = client.get('/tasks/delete/1', follow_redirects=True)
        assert response.status_code == 200

    def test_empty_title_rejected(self, client):
        """Verify task creation fails with an empty title."""
        register_user(client); login_user(client)
        response = client.post('/tasks/create', data={
            'title': '', 'description': 'Test'
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_edit_task(self, client):
        """Verify a task can be edited."""
        register_user(client); login_user(client)
        client.post('/tasks/create', data={'title': 'Original', 'description': 'Original'})
        response = client.post('/tasks/edit/1', data={
            'title': 'Updated', 'description': 'Updated'
        }, follow_redirects=True)
        assert response.status_code == 200
```

**Test Coverage (16 tests):**

| Test | Category | What It Verifies |
|------|----------|-----------------|
| `test_register_page` | Auth | Register page loads (200) |
| `test_login_page` | Auth | Login page loads (200) |
| `test_successful_registration` | Auth | User can register |
| `test_duplicate_username` | Auth | Duplicate username rejected |
| `test_successful_login` | Auth | User can login after registering |
| `test_invalid_login` | Auth | Wrong credentials rejected |
| `test_logout` | Auth | Logged-in user can logout |
| `test_password_mismatch` | Auth | Non-matching passwords rejected |
| `test_short_password` | Auth | Short passwords rejected |
| `test_create_task_page_requires_login` | Task | Unauthenticated users redirected |
| `test_create_task` | Task | Task can be created |
| `test_dashboard_shows_tasks` | Task | Dashboard displays tasks |
| `test_complete_task` | Task | Task can be marked complete |
| `test_delete_task` | Task | Task can be deleted |
| `test_empty_title_rejected` | Task | Empty task title rejected |
| `test_edit_task` | Task | Task can be edited |

**Testing Strategy:**
- Each test uses a **fresh temporary SQLite database** (isolated)
- Helper functions `register_user()` and `login_user()` reduce boilerplate
- Tests follow redirects with `follow_redirects=True` to check final page
- No external dependencies or mocking needed

---

## 11. API Route Reference

| Method | Route | Description | Auth | Request Data | Response |
|--------|-------|-------------|------|-------------|----------|
| GET | `/` | Home redirect | No | — | 302 → `/login` or `/dashboard` |
| GET | `/login` | Login form | No | — | 200 (HTML form) |
| POST | `/login` | Authenticate | No | `username`, `password` | 302 → `/dashboard` or form with error |
| GET | `/register` | Register form | No | — | 200 (HTML form) |
| POST | `/register` | Create user | No | `username`, `email`, `password`, `confirm_password` | 302 → `/login` or form with error |
| GET | `/logout` | Logout | Yes | — | 302 → `/login` |
| GET | `/dashboard` | Task list | Yes | — | 200 (HTML with task cards) |
| GET | `/tasks/create` | Create form | Yes | — | 200 (HTML form) |
| POST | `/tasks/create` | Save task | Yes | `title`, `description` | 302 → `/dashboard` or form with error |
| GET | `/tasks/edit/<id>` | Edit form | Yes | — | 200 (pre-filled HTML form) |
| POST | `/tasks/edit/<id>` | Update task | Yes | `title`, `description` | 302 → `/dashboard` or form with error |
| GET | `/tasks/delete/<id>` | Delete task | Yes | — | 302 → `/dashboard` |
| GET | `/tasks/complete/<id>` | Toggle status | Yes | — | 302 → `/dashboard` |

---

## 12. Database Schema

### Table: `users`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT |
| `username` | VARCHAR(80) | NOT NULL, UNIQUE |
| `email` | VARCHAR(120) | NOT NULL, UNIQUE |
| `password_hash` | VARCHAR(256) | NOT NULL |

### Table: `tasks`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT |
| `title` | VARCHAR(200) | NOT NULL |
| `description` | TEXT | NULLABLE |
| `completed` | BOOLEAN | DEFAULT 0 |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP |
| `user_id` | INTEGER | NOT NULL, FOREIGN KEY → `users(id)` |

### Entity Relationship

```
┌──────────┐          ┌──────────┐
│   User   │          │   Task   │
├──────────┤          ├──────────┤
│ id (PK)  │◄─────────│ user_id  │
│ username │    1:N   │ title    │
│ email    │          │ description
│ password │          │ completed│
└──────────┘          │ created  │
                      └──────────┘
```

---

## 13. How to Run

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Setup & Run

```bash
# 1. Navigate to the project
cd task-management-system

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python app.py

# 4. Open in browser
# http://127.0.0.1:5000
```

### Run Tests

```bash
pytest tests/ -v
```

Expected result: **16 passed**

### Create Test User

```python
python -c "
from app import create_app
from extensions import db
from models.user import User

app = create_app()
with app.app_context():
    db.create_all()
    u = User(username='admin', email='admin@test.com')
    u.set_password('admin123')
    db.session.add(u)
    db.session.commit()
    print('Created: admin / admin123')
"
```
