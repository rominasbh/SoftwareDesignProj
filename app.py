from flask import Flask, request, redirect, url_for, render_template, session, flash, Blueprint
from models import db, User, FuelQuote, ProfileInfo
from datetime import datetime
# from config import Config
from config import Config, TestConfig
from flask_migrate import Migrate
import bcrypt
import re
from functools import wraps




main = Blueprint('main', __name__)

def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)
    
    # Initialize the database and other extensions
    db.init_app(app)
    migrate = Migrate(app, db)

    
    app.register_blueprint(main, url_prefix='/')  # Register the blueprint with no prefix

    return app



def authenticate(username, password):
    user = User.query.filter_by(username=username).first()
    if user and check_password(user.password, password):  # No extra encoding here
        return True
    return False



def is_profile_complete(username):
    user = User.query.filter_by(username=username).first()
    return user.profile_complete if user else False



def require_profile_complete(f):
    @login_required
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in session:
            user = User.query.filter_by(username=session['username']).first()
            if user and not is_profile_complete(user.username):
                flash('Please complete your profile.')
                return redirect(url_for('main.profile'))
        return f(*args, **kwargs)
    return decorated_function


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('You need to be logged in to access this page.')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function




# @app.route('/')
@main.route('/')

def home():
    # Redirect to dashboard if logged in, else login page
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        if user and is_profile_complete(user.username):
            return redirect(url_for('main.dashboard'))
        # elif user and not is_profile_complete(user.username):
        #     return redirect(url_for('main.profile'))
    return redirect(url_for('main.login'))




def hash_password(password):
    password_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode('utf-8')  # Decoding to string to store in the database as text



def check_password(stored_hash, provided_password):
    try:
        # Ensure both the stored hash and the provided password are in bytes format
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode('utf-8')
        provided_password_bytes = provided_password.encode('utf-8')
        
        # Check the password
        return bcrypt.checkpw(provided_password_bytes, stored_hash)
    except ValueError as e:
        # Log the error or handle it as needed
        print(f"Error checking password: {e}")
        return False



def is_username_valid(username):
    """Check that the username is between 5 and 25 characters and contains only alphanumeric characters."""
    if not (5 <= len(username) <= 25):
        return False, "Username must be between 5 and 25 characters."
    if not re.match("^[A-Za-z0-9]+$", username):
        return False, "Username should only contain alphanumeric characters."
    return True, ""

def is_password_valid(password):
    """Make sure the password has at least one number, one uppercase letter, one lowercase letter, and is at least 8 characters long."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search("[a-z]", password) or not re.search("[A-Z]", password):
        return False, "Password must include both uppercase and lowercase letters."
    if not re.search("[0-9]", password):
        return False, "Password must contain at least one number."
    return True, ""





@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Validate username and password
        username_valid, username_message = is_username_valid(username)
        if not username_valid:
            flash(username_message)
            return render_template('register.html')

        password_valid, password_message = is_password_valid(password)
        if not password_valid:
            flash(password_message)
            return render_template('register.html')

        # Check for existing user
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.')
            return render_template('register.html')

        # Hash password and save the new user
        hashed_password = hash_password(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. Please log in.')
        return redirect(url_for('main.login'))

    return render_template('register.html')





@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Server-side validation for empty inputs (additional security layer)
        if not username or not password:
            flash("Please fill in all fields.")
            return render_template('login.html')

        # Authenticate user
        if authenticate(username, password):
            session['username'] = username  # Store username in session
            return redirect(url_for('main.dashboard')) if is_profile_complete(username) else redirect(url_for('main.profile'))
        
        flash('Invalid username or password.')
    
    return render_template('login.html')



def validate_address(address):
    """Check if the address contains both letters and numbers."""
    return bool(re.search(r'[0-9]', address)) and bool(re.search(r'[a-zA-Z]', address))

def validate_name_or_city(name):
    """Check if the name or city contains only letters and spaces."""
    return bool(re.search(r'^[A-Za-z\s]+$', name))

def validate_zip_code(zip_code):
    """Check if the zip code is valid (5 to 9 digits)."""
    return bool(re.search(r'^[0-9]{5}(-[0-9]{4})?$', zip_code))


@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    username = session.get('username')
    if not username:
        flash('User not found. Please log in again.')
        return redirect(url_for('main.login'))

    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User not found. Please log in again.')
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        address1 = request.form.get('address1', '').strip()
        address2 = request.form.get('address2', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        zip_code = request.form.get('zip_code', '').strip()

        # Server-side validation checks
        if not (full_name and validate_name_or_city(full_name) and
                address1 and validate_address(address1) and
                city and validate_name_or_city(city) and
                state and
                zip_code and validate_zip_code(zip_code)):
            flash('Please fill all required fields correctly.')
            return render_template('profile.html', user=user, profile_complete=user.profile_complete)

        if address2 and not validate_address(address2):
            flash('Secondary address must include both letters and numbers if provided.')
            return render_template('profile.html', user=user, profile_complete=user.profile_complete)

        # Update or create profile info
        if not user.profile_info:
            user.profile_info = ProfileInfo(user_id=user.id)
            db.session.add(user.profile_info)

        user.profile_info.full_name = full_name
        user.profile_info.address1 = address1
        user.profile_info.address2 = address2
        user.profile_info.city = city
        user.profile_info.state = state
        user.profile_info.zip_code = zip_code

        # Mark profile as complete if not already set
        user.profile_complete = True

        # Commit changes to the database
        db.session.commit()

        flash('Profile Saved. Continue to FuelMetrics.')
        return redirect(url_for('main.profile'))  # Redirect to profile to see changes

    return render_template('profile.html', user=user, profile_complete=user.profile_complete)



@main.route('/dashboard')
@require_profile_complete
def dashboard():
    return render_template('dashboard.html')






@main.route('/fuel_quote', methods=['GET', 'POST'])
@require_profile_complete
def fuel_quote():
    if 'username' not in session:
        flash('Please log in to access the fuel quote page.')
        return redirect(url_for('main.login'))

    user = User.query.filter_by(username=session['username']).first()
    if not user:
        flash('Session error, please log in again.')
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        gallons_requested = request.form.get('gallons', type=float)
        delivery_date_str = request.form.get('delivery_date')
        delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%d')

        # Assuming deliveryFee, pricePerGallon, and taxRate are constants or derived from somewhere
        deliveryFee = 1.75
        pricePerGallon = 3.05
        taxRate = 0.0775

        basePrice = pricePerGallon * gallons_requested
        taxFee = basePrice * taxRate
        totalPrice = deliveryFee + taxFee + basePrice

        # Create and save the new fuel quote
        new_quote = FuelQuote(
            user_id=user.id,
            gallons_requested=gallons_requested,
            delivery_date=delivery_date,
            total_amount_due=totalPrice,
            price_per_gallon=pricePerGallon,
            delivery_fee=deliveryFee
        )
        db.session.add(new_quote)
        db.session.commit()

        flash('Fuel quote saved successfully. View in Quote History')
        return redirect(url_for('main.fuel_quote'))  # consider Redirecting to the history page to view the quote

    # If GET request, just display the form with existing user info
    return render_template('fuel_quote.html', profile_info=user.profile_info)






@main.route('/fuel_history')
@require_profile_complete
def fuel_history():
    if 'username' not in session:
        flash('Please log in to view fuel quote history.')
        return redirect(url_for('main.login'))

    user = User.query.filter_by(username=session['username']).first()
    if not user:
        flash('User not found. Please login again.')
        return redirect(url_for('main.login'))

    # Fetch user's fuel quote history from the database
    user_quotes = FuelQuote.query.filter_by(user_id=user.id).all()

    return render_template('fuel_history.html', user_quotes=user_quotes)



@main.route('/logout')
def logout():
    # Remove 'username' from session
    session.pop('username', None)  
    # Redirect to the login page
    return redirect(url_for('main.login'))

# if __name__ == '__main__':
#     # app.run(debug=True)
#     create_app().run()

if __name__ == '__main__':
    create_app().run(debug=True)


