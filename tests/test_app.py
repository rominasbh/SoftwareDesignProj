import pytest
import sys
import os
sys.path.append(os.path.abspath('/Users/rominasobhani/Desktop/Software Design/Project'))
import pytest
from app import create_app, db, User, ProfileInfo,hash_password, check_password, is_profile_complete,authenticate
from config import TestConfig

@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.session.remove()
            db.drop_all()

def test_home(client):
    response = client.get('/')
    assert response.status_code == 302  # Should redirect to login

def test_register(client):
    response = client.get('/register')
    assert response.status_code == 200

def test_login(client):
    response = client.get('/login')
    assert response.status_code == 200

def test_profile(client):
    response = client.get('/profile')
    assert response.status_code == 302  # Should redirect to login as no user is logged in

def test_dashboard(client):
    response = client.get('/dashboard')
    assert response.status_code == 302  # Should redirect to login as no user is logged in

def test_fuel_quote(client):
    response = client.get('/fuel_quote')
    assert response.status_code == 302  # Should redirect to login as no user is logged in

def test_fuel_history(client):
    response = client.get('/fuel_history')
    assert response.status_code == 302  # Should redirect to login as no user is logged in

def test_logout(client):
    response = client.get('/logout')
    assert response.status_code == 302  # Should redirect to login

def test_authenticate(client):
    hashed_pw = hash_password('SecurePassword123!')
    user = User(username='validuser', password=hashed_pw)
    with client.application.app_context():
        db.session.add(user)
        db.session.commit()
        assert authenticate('validuser', 'SecurePassword123!') == True
        assert authenticate('invaliduser', 'SecurePassword123!') == False
        assert authenticate('validuser', 'InvalidPassword123!') == False

def test_is_profile_complete(client):
    hashed_pw = hash_password('SecurePassword123!')
    user = User(username='validuser', password=hashed_pw, profile_complete=True)
    with client.application.app_context():
        db.session.add(user)
        db.session.commit()
        assert is_profile_complete('validuser') == True
        user.profile_complete = False
        db.session.commit()
        assert is_profile_complete('validuser') == False