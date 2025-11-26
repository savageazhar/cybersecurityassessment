import os
# Set default database URL for testing before importing main
os.environ.setdefault('DATABASE_URL', 'sqlite:///:memory:')
# Set dummy OpenAI API key for testing
os.environ['OPENAI_API_KEY'] = 'dummy-key'
os.environ['GEMINI_API_KEY'] = 'AIzaSyA_... (rest of key)'

import sys
from os.path import abspath, dirname, join
sys.path.insert(0, abspath(join(dirname(__file__), '..')))

import pytest
from app import create_app, db as flask_db
from app.models import User

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,  # Disable CSRF for easier testing
        'SERVER_NAME': 'localhost.localdomain' # helps with url_for
    })

    with app.app_context():
        flask_db.create_all()
        yield app
        flask_db.session.remove()
        flask_db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db(app):
    with app.app_context():
        yield flask_db

@pytest.fixture
def user(app, db):
    u = User(name="Test User", email="test@example.com", phone="1234567890")
    u.set_password("password")
    db.session.add(u)
    db.session.commit()
    return u

@pytest.fixture
def auth_client(client, user):
    """A client that is already logged in."""
    client.post('/login', json={
        'email_or_phone': 'test@example.com',
        'password': 'password'
    })
    return client
