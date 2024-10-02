from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .. import db
from ..models import Task
import markdown
import bleach
from datetime import datetime, timezone

bp = Blueprint('tasks', __name__)

@bp.route('/')
@login_required
def index():
    tasks = db.session.execute(db.select(Task).filter_by(user_id=current_user.id).order_by(Task.priority.desc(), Task.created_at.desc())).scalars().all()
    return render_template('index.html', tasks=tasks)

@bp.route('/create_task', methods=['POST'])
@login_required
def create_task():
    content = request.form.get('content')
    priority = request.form.get('priority', 0)
    
    html_content = markdown.markdown(content, extensions=['extra'])
    sanitized_content = bleach.clean(html_content, tags=['p', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'img'], attributes={'img': ['src', 'alt']})
    
    task = Task(content=sanitized_content, priority=priority, user_id=current_user.id)
    db.session.add(task)
    db.session.commit()
    return redirect(url_for('tasks.index'))

@bp.route('/update_task/<int:task_id>', methods=['POST'])
@login_required
def update_task(task_id):
    task = db.session.get(Task, task_id)
    if not task or task.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    content = request.form.get('content')
    priority = request.form.get('priority')
    
    html_content = markdown.markdown(content, extensions=['extra'])
    sanitized_content = bleach.clean(html_content, tags=['p', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'img'], attributes={'img': ['src', 'alt']})
    
    task.content = sanitized_content
    task.priority = priority
    task.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return redirect(url_for('tasks.index'))

@bp.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task or task.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('tasks.index'))