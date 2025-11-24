import os
# Set default database URL for testing before importing main
os.environ.setdefault('DATABASE_URL', 'sqlite:///:memory:')
# Set dummy OpenAI API key for testing
os.environ.setdefault('OPENAI_API_KEY_CYB_SEC', 'dummy-key')

import pytest
from main import app as flask_app
from main import db as flask_db
from main import User

@pytest.fixture
def app():
    # Update config for testing
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,  # Disable CSRF for easier testing
        'SERVER_NAME': 'localhost.localdomain' # helps with url_for
    })

    with flask_app.app_context():
        flask_db.create_all()
        yield flask_app
        flask_db.session.remove()
        flask_db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db(app):
    return flask_db

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
