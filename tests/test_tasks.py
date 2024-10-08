import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app, db
from app.models import User, Task
from config import Config
from flask_login import login_user
from datetime import datetime, timezone

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

@pytest.fixture
def app():
    app = create_app(TestConfig)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def authenticated_client(app, client):
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
    
        client.post('/login', data={'username': 'testuser', 'password': 'password123'})
    
    return client

@pytest.fixture(autouse=True)
def setup_db(app):
    with app.app_context():
        db.create_all()
    yield
    with app.app_context():
        db.session.remove()
        db.drop_all()

def test_create_task(authenticated_client, app):
    # Backend
    with app.app_context():
        response = authenticated_client.post('/create_task', data={
            'content': 'Test task',
            'priority': '1'
        })
        assert response.status_code == 302  # Redirect after creation
        
        ## Front
        task = db.session.execute(db.select(Task)).scalar_one_or_none()
        assert task is not None
        assert task.content == '<p>Test task</p>'
        assert task.priority == 1

def test_update_task(authenticated_client, app):
    with app.app_context():
        # First, create a task
        authenticated_client.post('/create_task', data={
            'content': 'Original task',
            'priority': '0'
        })
        task = db.session.execute(db.select(Task)).scalar_one_or_none()
        
        # Now update the task
        response = authenticated_client.post(f'/update_task/{task.id}', data={
            'content': 'Updated task',
            'priority': '2'
        })
        assert response.status_code == 302  # Redirect after update
        
        db.session.refresh(task)
        assert task.content == '<p>Updated task</p>'
        assert task.priority == 2

def test_delete_task(authenticated_client, app):
    with app.app_context():
        # First, create a task
        authenticated_client.post('/create_task', data={
            'content': 'Task to delete',
            'priority': '1'
        })
        task = db.session.execute(db.select(Task)).scalar_one_or_none()
        
        # Now delete the task
        response = authenticated_client.post(f'/delete_task/{task.id}')
        assert response.status_code == 302  # Redirect after deletion
        
        deleted_task = db.session.get(Task, task.id)
        assert deleted_task is None

# Negative tests
def test_create_task_without_content(authenticated_client, app):
    with app.app_context():
        response = authenticated_client.post('/create_task', data={
            'content': '',
            'priority': '1'
        })
        assert response.status_code == 400  # Bad Request

def test_update_nonexistent_task(authenticated_client, app):
    with app.app_context():
        response = authenticated_client.post('/update_task/9999', data={
            'content': 'Updated task',
            'priority': '2'
        })
        assert response.status_code == 404  # Not Found

def test_delete_nonexistent_task(authenticated_client, app):
    with app.app_context():
        response = authenticated_client.post('/delete_task/9999')
        assert response.status_code == 404  # Not Found

def test_access_tasks_unauthenticated(client, app):
    response = client.get('/')
    assert response.status_code == 302  # Redirect to login page
    assert '/login' in response.location

if __name__ == '__main__':
    pytest.main([__file__])