# Tests for user profile operations# test_profile.py
import pytest
import sys
import os
sys.path.append(os.path.abspath('../'))
from app import create_app , hash_password, check_password
from models import db, User, ProfileInfo
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


def test_access_profile_without_login(client):
    # Test that trying to access profile without logging in redirects to login page
    pass

def test_access_profile_authenticated(client):
    # Create a user and log in to access the profile page
    pass

def test_access_profile_with_invalid_user(client):
    # Test that trying to access profile with invalid user in session redirects to login page with flash message
    pass

def test_profile_update_with_valid_data(client):
    # After logging in, post valid data to the profile update route and verify the changes
    pass

def test_profile_update_with_invalid_data(client):
    # Post invalid data to the profile update route and verify the error message

    pass

def test_profile_completion(client):
    # Create a user
    with client.application.app_context():  # Ensure using the application context
        # Create a user
        hashed_pw = hash_password('Password1!')
        user = User(username='testprofile', password=hashed_pw)
        db.session.add(user)
        db.session.commit()
    
    # Log in the user
    response = client.post('/login', data={
        'username': 'testprofile',
        'password': 'Password1!'
    }, follow_redirects=True)
    
    # Initially, the profile is not complete
    assert 'Please complete your profile' in str(response.data)

    # Complete the profile
    response = client.post('/profile', data={
        'full_name': 'Test User',
        'address1': '123 Test St',
        'city': 'Testville',
        'state': 'TX',
        'zip_code': '12345'
    }, follow_redirects=True)

    assert 'Profile Saved' in str(response.data)
    
    # Verify profile is marked complete
    with client.application.app_context():
        updated_user = User.query.filter_by(username='testprofile').first()
        assert updated_user.profile_complete is True

    # Clean up test data
    with client.application.app_context():
        db.session.delete(user)
        db.session.commit()



def test_redirect_incomplete_profile(client):

    with client.application.app_context():
        # Create and log in a user with an incomplete profile
        hashed_pw = hash_password('Secure123!')
        user = User(username='incompleteuser', password=hashed_pw, profile_complete=False)
        db.session.add(user)
        db.session.commit()
        username = user.username  # Store username to a variable before exiting the context
    
    with client.session_transaction() as session:
        session['username'] = username  # Use the stored username
    
    response = client.get('/', follow_redirects=True)
    assert b'Please complete your profile' in response.data
    assert request.path == url_for('main.profile')
    
    # Clean up
    with client.application.app_context():
        db.session.delete(user)
        db.session.commit()



def test_redirect_complete_profile(client):
    with client.application.app_context():
        # Create and log in a user with a complete profile
        hashed_pw = hash_password('Secure123!')
        user = User(username='completeuser', password=hashed_pw, profile_complete=True)
        db.session.add(user)
        db.session.commit()
        username = user.username  

    with client.session_transaction() as session:
        session['username'] = username
    
    response = client.get('/', follow_redirects=True)
    assert b'Welcome to your dashboard' in response.data
    assert request.path == url_for('main.dashboard')
    
    # Clean up
    with client.application.app_context():
        db.session.delete(user)
        db.session.commit()
