from main import User
from flask import url_for

def test_signup_success(client, db):
    response = client.post('/signup', json={
        'name': 'New User',
        'email': 'new@example.com',
        'phone': '0987654321',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    assert response.status_code == 201
    assert b"Signup successful" in response.data

    # Verify user is in DB
    user = User.query.filter_by(email='new@example.com').first()
    assert user is not None
    assert user.name == 'New User'

def test_signup_validation_errors(client):
    # Missing fields
    response = client.post('/signup', json={
        'name': 'New User',
        # missing email
        'phone': '0987654321',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    assert response.status_code == 400
    assert b"All fields are required" in response.data

    # Password too short
    response = client.post('/signup', json={
        'name': 'New User',
        'email': 'short@example.com',
        'phone': '0987654321',
        'password': '123',
        'confirm_password': '123'
    })
    assert response.status_code == 400
    assert b"Password must be at least 6 characters long" in response.data

    # Passwords do not match
    response = client.post('/signup', json={
        'name': 'New User',
        'email': 'mismatch@example.com',
        'phone': '0987654321',
        'password': 'password123',
        'confirm_password': 'password456'
    })
    assert response.status_code == 400
    assert b"Passwords do not match" in response.data

def test_signup_duplicate_email(client, user):
    response = client.post('/signup', json={
        'name': 'Duplicate User',
        'email': 'test@example.com', # Existing email from fixture
        'phone': '1111111111',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    assert response.status_code == 400
    assert b"Email already registered" in response.data

def test_login_success(client, user):
    response = client.post('/login', json={
        'email_or_phone': 'test@example.com',
        'password': 'password'
    })
    assert response.status_code == 200
    assert b"Login successful" in response.data

def test_login_failure(client, user):
    # Wrong password
    response = client.post('/login', json={
        'email_or_phone': 'test@example.com',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    assert b"Invalid credentials" in response.data

    # Non-existent user
    response = client.post('/login', json={
        'email_or_phone': 'nonexistent@example.com',
        'password': 'password'
    })
    assert response.status_code == 401

def test_logout(auth_client):
    response = auth_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    # The flash message might not be rendered in the template 'prop_firm.html' (index page)
    # So we check if the user is no longer logged in by checking the response or session
    # or by trying to access a protected route

    # Check if we are redirected to index
    assert b"Welcome to Kimi AI" in response.data

    # Verify we can't access chat anymore
    chat_response = auth_client.get('/chat', follow_redirects=True)
    assert b"Login" in chat_response.data

def test_protected_routes(client):
    # Access chat without login
    response = client.get('/chat', follow_redirects=True)
    assert b"Login" in response.data # Should redirect to login page

    # Access chat with login (using auth_client)
    # Re-using logic from fixture inside test effectively
    pass
