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
