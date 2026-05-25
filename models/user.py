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
