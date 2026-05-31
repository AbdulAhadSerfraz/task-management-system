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
        due_date: Optional due date for the task.
        priority: Priority level (low, medium, high).
        category: Optional task category for filtering.
        user_id: Foreign key referencing the owning user's ID.
    """
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.String(20), default='medium')
    category = db.Column(db.String(50), nullable=True)
    # Foreign key: links each task to its owning user
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
