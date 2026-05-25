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
