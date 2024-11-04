import pytest
from app import create_app
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.test_client() as client:
        yield client

def test_login_page(client):
    """Test that login page loads correctly"""
    rv = client.get('/login')
    assert rv.status_code == 200
    assert b'Login' in rv.data

def test_register_page(client):
    """Test that register page loads correctly"""
    rv = client.get('/register')
    assert rv.status_code == 200
    assert b'Register' in rv.data

def test_invalid_login(client):
    """Test login with invalid credentials"""
    rv = client.post('/login', data=dict(
        username='nonexistent',
        password='wrong'
    ), follow_redirects=True)
    assert b'Invalid username or password' in rv.data