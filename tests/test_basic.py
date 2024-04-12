import pytest
import sys
import os
sys.path.append(os.path.abspath('../'))
from app import create_app, hash_password, check_password
from models import User, ProfileInfo, FuelQuote, db
from config import TestConfig


@pytest.fixture
def client():
    
    app = create_app(TestConfig)  # Use your test configuration here
    # Push an application context for the tests
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Create schema before we begin the tests
        yield client
        with app.app_context():
            db.session.remove()
            db.drop_all()  # Clean up the database after tests are done

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 302  # Expected redirect to login since we are not logged in

def test_register(client):
    # Ensure registration page can be accessed
    response = client.get('/register')
    assert response.status_code == 200
    # Test valid registration
    response = client.post('/register', data={
        'username': 'newuser',
        'password': 'Password1!'
    }, follow_redirects=True)
    assert b'Registration successful' in response.data
    # Ensure the user was added to the database
    with client.application.app_context():
        user = User.query.filter_by(username='newuser').first()
        assert user is not None

def test_login(client):
    # Hash the password before storing it using the same method as  app
    hashed_pw = hash_password('Password1!')
    
    # Create a user with the hashed password
    with client.application.app_context():
        user = User(username='testuser', password=hashed_pw)
        db.session.add(user)
        db.session.commit()

    # Test login
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'Password1!'
    }, follow_redirects=True)
    assert b'Invalid username or password.' not in response.data


def test_profile_access(client):
    # Create a user for the test
    with client.application.app_context():
        hashed_pw = hash_password('Password1!')
        user = User(username='testuser', password=hashed_pw)
        db.session.add(user)
        db.session.commit()

    # Login as the user and test profile access in one client session
    with client.session_transaction() as session:
        session['username'] = 'testuser'  # Set the user session manually

    response = client.get('/profile')
    assert response.status_code == 200
    # The profile page content should be in the response
    assert b'Client Profile Management' in response.data

    # Clean up the test user after the test
    with client.application.app_context():
        db.session.delete(user)
        db.session.commit()


def test_logout(client):
    # Create a user for the test
    with client.application.app_context():
        hashed_pw = hash_password('Password1!')
        user = User(username='testuser', password=hashed_pw)
        db.session.add(user)
        db.session.commit()

    # Log in as the user
    with client.session_transaction() as session:
        session['username'] = 'testuser'  # Manually set the user session

    # Log out
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data  # Check for login page content after logout

    # Clean up the test user after the test
    with client.application.app_context():
        db.session.delete(user)
        db.session.commit()



def test_full_user_flow(client):
    # Register the user
    response = client.post('/register', data={
        'username': 'testuserflow',
        'password': 'Password1!'
    }, follow_redirects=True)
    assert b'Registration successful' in response.data
    
    # Log in the user
    response = client.post('/login', data={
        'username': 'testuserflow',
        'password': 'Password1!'
    }, follow_redirects=True)
    # The following line is where your test failed
    # We are expecting to be taken to the profile page, since the user's profile is not complete
    assert b'Client Profile Management' in response.data  # The profile page has 'Client Profile Management' in the HTML

    # Fill in the profile information
    response = client.post('/profile', data={
        'full_name': 'Test User',
        'address1': '123 Test St',
        'city': 'Testville',
        'state': 'TX',
        'zip_code': '12345'
    }, follow_redirects=True)
    assert b'Profile Saved' in response.data

    # Now the user should be redirected to the dashboard after login
    response = client.get('/dashboard')
    assert b'Dashboard' in response.data  # Now we check for 'Dashboard' because the profile is complete

    # Clean up by removing the user
    with client.application.app_context():
        user = User.query.filter_by(username='testuserflow').first()
        if user:
            db.session.delete(user)
            db.session.commit()





