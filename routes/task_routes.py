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
from datetime import datetime

# Create the task management blueprint
task_bp = Blueprint('task', __name__)


@task_bp.route('/dashboard')
@login_required
def dashboard():
    """Display all tasks belonging to the logged-in user.

    Supports search, category filtering, and status filtering.
    Tasks are ordered by creation date (newest first).
    """
    search_query = request.args.get('search', '')
    category_filter = request.args.get('category', '')
    status_filter = request.args.get('status', '')

    query = Task.query.filter_by(user_id=current_user.id)

    if search_query:
        query = query.filter(Task.title.contains(search_query) | Task.description.contains(search_query))

    if category_filter:
        query = query.filter_by(category=category_filter)

    if status_filter == 'completed':
        query = query.filter_by(completed=True)
    elif status_filter == 'pending':
        query = query.filter_by(completed=False)

    tasks = query.order_by(Task.created_at.desc()).all()
    return render_template('dashboard.html', tasks=tasks, search_query=search_query,
                          category_filter=category_filter, status_filter=status_filter)


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
        priority = request.form.get('priority', 'medium')
        category = request.form.get('category')
        due_date = request.form.get('due_date')

        # Validation: title cannot be empty
        if not title or not title.strip():
            flash('Task title is required', 'danger')
            return render_template('create_task.html')

        task = Task(
            title=title.strip(),
            description=description,
            priority=priority,
            category=category,
            user_id=current_user.id
        )
        if due_date:
            task.due_date = datetime.strptime(due_date, '%Y-%m-%d')
        db.session.add(task)
        db.session.commit()

        task_count = Task.query.filter_by(user_id=current_user.id).count()
        flash('Task created successfully!', 'success')
        redirect_url = url_for('task.dashboard')
        if task_count == 1:
            redirect_url += '?created=1'
        return redirect(redirect_url)

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

    # Security: ensure the task belongs to the current user
    if task.user_id != current_user.id:
        flash('You do not have permission to edit this task', 'danger')
        return redirect(url_for('task.dashboard'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        priority = request.form.get('priority', 'medium')
        category = request.form.get('category')
        due_date = request.form.get('due_date')

        if not title or not title.strip():
            flash('Task title is required', 'danger')
            return render_template('edit_task.html', task=task)

        task.title = title.strip()
        task.description = description
        task.priority = priority
        task.category = category
        if due_date:
            task.due_date = datetime.strptime(due_date, '%Y-%m-%d')
        else:
            task.due_date = None
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

    # Toggle the completed flag
    task.completed = not task.completed
    db.session.commit()

    flash('Task status updated!', 'success')
    return redirect(url_for('task.dashboard', completed=task.id))
