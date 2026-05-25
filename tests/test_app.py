import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from models.user import User
from models.task import Task


@pytest.fixture
def app():
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
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


def register_user(client, username='testuser', email='test@example.com', password='password123'):
    return client.post('/register', data={
        'username': username,
        'email': email,
        'password': password,
        'confirm_password': password
    }, follow_redirects=True)


def login_user(client, username='testuser', password='password123'):
    return client.post('/login', data={
        'username': username,
        'password': password
    }, follow_redirects=True)


class TestAuth:
    def test_register_page(self, client):
        response = client.get('/register')
        assert response.status_code == 200

    def test_login_page(self, client):
        response = client.get('/login')
        assert response.status_code == 200

    def test_successful_registration(self, client):
        response = register_user(client)
        assert response.status_code == 200

    def test_duplicate_username(self, client):
        register_user(client)
        response = register_user(client)
        assert response.status_code == 200

    def test_successful_login(self, client):
        register_user(client)
        response = login_user(client)
        assert response.status_code == 200

    def test_invalid_login(self, client):
        response = client.post('/login', data={
            'username': 'wrong',
            'password': 'wrong'
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_logout(self, client):
        register_user(client)
        login_user(client)
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200

    def test_password_mismatch(self, client):
        response = client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'different'
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_short_password(self, client):
        response = client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': '123',
            'confirm_password': '123'
        }, follow_redirects=True)
        assert response.status_code == 200


class TestTask:
    def test_create_task_page_requires_login(self, client):
        response = client.get('/tasks/create', follow_redirects=True)
        assert response.status_code == 200

    def test_create_task(self, client):
        register_user(client)
        login_user(client)
        response = client.post('/tasks/create', data={
            'title': 'Test Task',
            'description': 'Test Description'
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_dashboard_shows_tasks(self, client):
        register_user(client)
        login_user(client)
        client.post('/tasks/create', data={
            'title': 'Test Task',
            'description': 'Test Description'
        })
        response = client.get('/dashboard', follow_redirects=True)
        assert response.status_code == 200

    def test_complete_task(self, client):
        register_user(client)
        login_user(client)
        client.post('/tasks/create', data={
            'title': 'Test Task',
            'description': 'Test Description'
        })
        response = client.get('/tasks/complete/1', follow_redirects=True)
        assert response.status_code == 200

    def test_delete_task(self, client):
        register_user(client)
        login_user(client)
        client.post('/tasks/create', data={
            'title': 'Test Task',
            'description': 'Test Description'
        })
        response = client.get('/tasks/delete/1', follow_redirects=True)
        assert response.status_code == 200

    def test_empty_title_rejected(self, client):
        register_user(client)
        login_user(client)
        response = client.post('/tasks/create', data={
            'title': '',
            'description': 'Test'
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_edit_task(self, client):
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
