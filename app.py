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
