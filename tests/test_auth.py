# Tests for user profile operations# test_profile.py
import pytest
import sys
import os
# sys.path.append(os.path.abspath('../'))
sys.path.append(os.path.abspath('/Users/rominasobhani/Desktop/Software Design/Project')) #change this directory to where your project directory is located
from app import create_app , hash_password, check_password
from models import db, User, ProfileInfo
from config import TestConfig
from flask import request, url_for

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
    # Attempt to access the profile page without logging in
    response = client.get('/profile', follow_redirects=True)
    
    # Check that the response is a redirection to the login page
    assert response.status_code == 200
    assert b'Login' in response.data


    #  check the final URL if redirection was followed
    assert response.request.path == url_for('main.login')

def test_access_profile_authenticated(client):
    # Create a user and log in to access the profile page
    # Create user
    hashed_pw = hash_password('SecurePassword123!')
    user = User(username='validuser', password=hashed_pw)
    with client.application.app_context():
        db.session.add(user)
        db.session.commit()
        username = user.username

    # Log in the user
    with client.session_transaction() as session:
        session['username'] =username

    # Attempt to access the profile page
    response = client.get('/profile', follow_redirects=True)

    # Check for the correct status code to confirm access
    assert response.status_code == 200
    # Check if the response contains parts of the profile page, such as the form or user info
    assert b'Client Profile Management' in response.data
    assert b'Full Name:' in response.data

    # Clean up - delete the user after the test
    with client.application.app_context():
        db.session.delete(user)
        db.session.commit()
    

def test_access_profile_with_invalid_user(client):
    # Test that trying to access profile with invalid user in session redirects to login page with flash message
    with client.session_transaction() as session:
        # Set a username that does not exist
        session['username'] = 'nonexistentuser'
    
    # Attempt to access the profile page
    response = client.get('/profile', follow_redirects=True)
    
    # Check for redirection to the login page
    assert response.request.path == url_for('main.login')
    
    # Ensure the flash message is displayed
    assert b'User not found. Please log in again.' in response.data

def test_profile_update_with_valid_data(client):
    # After logging in, post valid data to the profile update route and verify the changes
     # Log in as a user first
    with client.application.app_context():
        hashed_pw = hash_password('Password1!')
        user = User(username='validuser', password=hashed_pw, profile_complete=False)
        db.session.add(user)
        db.session.commit()

    with client.session_transaction() as session:
        session['username'] = 'validuser'
    
    # Define valid profile data
    valid_data = {
        'full_name': 'John Doe',
        'address1': '123 Main St',
        'address2': 'Apt 4',
        'city': 'Anytown',
        'state': 'TX',
        'zip_code': '12345'
    }
    
    # Post valid data to the profile update route
    response = client.post('/profile', data=valid_data, follow_redirects=True)
    
    # Check that the profile was updated successfully
    assert b'Profile Saved. Continue to FuelMetrics.' in response.data
    
    # Verify the data was updated in the database
    with client.application.app_context():
        updated_user = User.query.filter_by(username='validuser').first()
        assert updated_user is not None
        assert updated_user.profile_info.full_name == 'John Doe'
        assert updated_user.profile_info.address1 == '123 Main St'
        assert updated_user.profile_info.address2 == 'Apt 4'
        assert updated_user.profile_info.city == 'Anytown'
        assert updated_user.profile_info.state == 'TX'
        assert updated_user.profile_info.zip_code == '12345'
    
    # Clean up
    with client.application.app_context():
        db.session.delete(user)
        db.session.commit()

def test_profile_update_with_invalid_data(client):
    # Post invalid data to the profile update route and verify the error message
    # First, create a user and log in
    hashed_pw = hash_password('Password1!')
    user = User(username='testuser', password=hashed_pw)
    with client.application.app_context():
        db.session.add(user)
        db.session.commit()
    
    with client.session_transaction() as session:
        session['username'] = 'testuser'
    
    # Now, send invalid data to the profile update route
    invalid_data = {
        'full_name': 'Invalid Name123',  # Numbers are invalid for full_name
        'address1': '123 Test St',
        'city': 'Testville',
        'state': 'TX',
        'zip_code': '1234'  # Zip code is too short
    }
    
    # Make the POST request with invalid data
    response = client.post('/profile', data=invalid_data, follow_redirects=True)
    
    # Check for validation error messages in response
    assert b'Full name should only contain letters and spaces.' in response.data
    assert b'Enter a valid zip code' in response.data
    
    # Clean up
    with client.application.app_context():
        db.session.delete(user)
        db.session.commit()

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

    response = client.get('/dashboard', follow_redirects=True)
    assert b'Please complete your profile.' in response.data
    assert response.request.path == url_for('main.profile')

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
    assert b'User Dashboard' in response.data
    assert response.request.path == url_for('main.dashboard')

    # Clean up
    with client.application.app_context():
        db.session.delete(user)
        db.session.commit()