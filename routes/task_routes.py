from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models.task import Task

task_bp = Blueprint('task', __name__)


@task_bp.route('/dashboard')
@login_required
def dashboard():
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()
    return render_template('dashboard.html', tasks=tasks)


@task_bp.route('/tasks/create', methods=['GET', 'POST'])
@login_required
def create_task():
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
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('You do not have permission to modify this task', 'danger')
        return redirect(url_for('task.dashboard'))
    task.completed = not task.completed
    db.session.commit()
    flash('Task status updated!', 'success')
    return redirect(url_for('task.dashboard'))
