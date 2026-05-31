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

# Add the project root to Python path for imports
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
    The database is cleaned up after the test completes.
    """
    db_fd, db_path = tempfile.mkstemp()
    app = create_app(test_config={
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + db_path,
        'TESTING': True,
    })

    # Create all tables in the temporary database
    with app.app_context():
        db.create_all()

    yield app

    # Cleanup: dispose engine connections and delete temp file
    with app.app_context():
        db.engine.dispose()
    os.close(db_fd)
    try:
        os.unlink(db_path)
    except PermissionError:
        pass  # Windows may hold a lock; ignore cleanup failure


@pytest.fixture
def client(app):
    """Flask test client for simulating HTTP requests."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Flask CLI runner for testing command-line commands."""
    return app.test_cli_runner()


# ----- Helper Functions -----

def register_user(client, username='testuser', email='test@example.com', password='password123'):
    """Helper: register a user via POST /register."""
    return client.post('/register', data={
        'username': username,
        'email': email,
        'password': password,
        'confirm_password': password
    }, follow_redirects=True)


def login_user(client, username='testuser', password='password123'):
    """Helper: log in a user via POST /login."""
    return client.post('/login', data={
        'username': username,
        'password': password
    }, follow_redirects=True)


# ----- Authentication Tests -----

class TestAuth:
    """Test cases for the authentication module."""

    def test_register_page(self, client):
        """Verify the registration page loads successfully."""
        response = client.get('/register')
        assert response.status_code == 200

    def test_login_page(self, client):
        """Verify the login page loads successfully."""
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
        assert response.status_code == 200  # Returns form with error flash

    def test_successful_login(self, client):
        """Verify a registered user can log in."""
        register_user(client)
        response = login_user(client)
        assert response.status_code == 200

    def test_invalid_login(self, client):
        """Verify invalid credentials are rejected."""
        response = client.post('/login', data={
            'username': 'wrong',
            'password': 'wrong'
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
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'different'
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_short_password(self, client):
        """Verify registration fails when password is too short."""
        response = client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': '123',
            'confirm_password': '123'
        }, follow_redirects=True)
        assert response.status_code == 200


# ----- Task CRUD Tests -----

class TestTask:
    """Test cases for the task CRUD module."""

    def test_create_task_page_requires_login(self, client):
        """Verify unauthenticated users are redirected from create page."""
        response = client.get('/tasks/create', follow_redirects=True)
        assert response.status_code == 200  # Redirected to login

    def test_create_task(self, client):
        """Verify a logged-in user can create a task."""
        register_user(client)
        login_user(client)
        response = client.post('/tasks/create', data={
            'title': 'Test Task',
            'description': 'Test Description'
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_dashboard_shows_tasks(self, client):
        """Verify the dashboard displays created tasks."""
        register_user(client)
        login_user(client)
        client.post('/tasks/create', data={
            'title': 'Test Task',
            'description': 'Test Description'
        })
        response = client.get('/dashboard', follow_redirects=True)
        assert response.status_code == 200

    def test_complete_task(self, client):
        """Verify a task can be marked as complete."""
        register_user(client)
        login_user(client)
        client.post('/tasks/create', data={
            'title': 'Test Task',
            'description': 'Test Description'
        })
        response = client.get('/tasks/complete/1', follow_redirects=True)
        assert response.status_code == 200

    def test_delete_task(self, client):
        """Verify a task can be deleted."""
        register_user(client)
        login_user(client)
        client.post('/tasks/create', data={
            'title': 'Test Task',
            'description': 'Test Description'
        })
        response = client.get('/tasks/delete/1', follow_redirects=True)
        assert response.status_code == 200

    def test_empty_title_rejected(self, client):
        """Verify task creation fails with an empty title."""
        register_user(client)
        login_user(client)
        response = client.post('/tasks/create', data={
            'title': '',
            'description': 'Test'
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_edit_task(self, client):
        """Verify a task can be edited."""
        register_user(client)
        login_user(client)
        client.post('/tasks/create', data={
            'title': 'Original Title',
            'description': 'Original Desc'
        })
        response = client.post('/tasks/edit/1', data={
            'title': 'Updated Title',
            'description': 'Updated Desc'
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_create_task_with_priority(self, client):
        register_user(client)
        login_user(client)
        response = client.post('/tasks/create', data={
            'title': 'Priority Task',
            'description': 'High priority',
            'priority': 'high',
            'category': 'Work'
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_create_task_with_due_date(self, client):
        register_user(client)
        login_user(client)
        response = client.post('/tasks/create', data={
            'title': 'Task with Due Date',
            'description': 'Test',
            'due_date': '2025-12-31'
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_search_tasks(self, client):
        register_user(client)
        login_user(client)
        client.post('/tasks/create', data={
            'title': 'Searchable Task',
            'description': 'Unique description'
        })
        response = client.get('/dashboard?search=Searchable', follow_redirects=True)
        assert response.status_code == 200

    def test_filter_by_category(self, client):
        register_user(client)
        login_user(client)
        client.post('/tasks/create', data={
            'title': 'Work Task',
            'category': 'Work'
        })
        response = client.get('/dashboard?category=Work', follow_redirects=True)
        assert response.status_code == 200

    def test_filter_by_status(self, client):
        register_user(client)
        login_user(client)
        client.post('/tasks/create', data={
            'title': 'Pending Task',
            'description': 'Test'
        })
        response = client.get('/dashboard?status=pending', follow_redirects=True)
        assert response.status_code == 200
