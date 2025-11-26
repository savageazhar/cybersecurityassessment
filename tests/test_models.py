from app.models import User

def test_user_creation(user):
    assert user.name == "Test User"
    assert user.email == "test@example.com"
    assert user.phone == "1234567890"
    assert user.id is not None

def test_password_hashing(user):
    assert user.password_hash != "password"
    assert user.check_password("password") is True
    assert user.check_password("wrong_password") is False

def test_user_repr(user):
    # If the model had a __repr__ method, we'd test it here.
    # Since it doesn't, we can just check if str(user) works or add a test if we add __repr__
    pass
