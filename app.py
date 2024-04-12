from flask import Flask, request, redirect, url_for, render_template, session, flash
from models import db, User, FuelQuote, ProfileInfo
from datetime import datetime
from config import Config
from flask_migrate import Migrate
import bcrypt

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)




def authenticate(username, password):
    user = User.query.filter_by(username=username).first()
    if user and check_password(user.password, password):  # No extra encoding here
        return True
    return False



def is_profile_complete(username):
    user = User.query.filter_by(username=username).first()
    return user.profile_complete if user else False


@app.route('/')
def home():
    # Redirect to dashboard if logged in, else login page
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        if user and is_profile_complete(user.username):
            return redirect(url_for('dashboard'))
    return redirect(url_for('login'))




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





@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']   # Get password from form
        hashed_password = hash_password(password)  # Hash the password

        # Check for existing user
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('register'))

        # Save the new user
        new_user = User(username=username, password=hashed_password)  # Use hashed password
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html')






@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticate(username, password):
            session['username'] = username  # Store username in session
            if is_profile_complete(username):
                return redirect(url_for('dashboard'))
            
            return redirect(url_for('profile'))
        else:
            flash('Invalid username or password.')
    

    return render_template('login.html')



@app.route('/profile', methods=['GET', 'POST'])
def profile():
    username = session.get('username')
    if not username:
        flash('User not found. Please log in again.')
        return redirect(url_for('login'))

    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User not found. Please log in again.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Retrieve or create profile info
        profile_info = user.profile_info
        if not profile_info:
            profile_info = ProfileInfo(user_id=user.id)
            db.session.add(profile_info)

        # Update user profile info from form data
        profile_info.full_name = request.form.get('full_name', profile_info.full_name)
        profile_info.address1 = request.form.get('address1', profile_info.address1)
        profile_info.address2 = request.form.get('address2', profile_info.address2)
        profile_info.city = request.form.get('city', profile_info.city)
        profile_info.state = request.form.get('state', profile_info.state)
        profile_info.zip_code = request.form.get('zip_code', profile_info.zip_code)

        # Mark profile as complete if not already set
        if not user.profile_complete:
            user.profile_complete = True

        # Commit changes to the database
        db.session.commit()

        flash('Profile Saved. Continue to FuelMetrics.')
        return redirect(url_for('profile'))  # Redirect to profile to see changes

    # Pass profile_complete directly, no need to check separately since it's an attribute of the user
    return render_template('profile.html', user=user, profile_complete=user.profile_complete)


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')





@app.route('/fuel_quote', methods=['GET', 'POST'])
def fuel_quote():
    if 'username' not in session:
        flash('Please log in to access the fuel quote page.')
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session['username']).first()
    if not user:
        flash('Session error, please log in again.')
        return redirect(url_for('login'))

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
        return redirect(url_for('fuel_quote'))  # consider Redirecting to the history page to view the quote

    # If GET request, just display the form with existing user info
    return render_template('fuel_quote.html', profile_info=user.profile_info)





@app.route('/fuel_history')
def fuel_history():
    if 'username' not in session:
        flash('Please log in to view fuel quote history.')
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session['username']).first()
    if not user:
        flash('User not found. Please login again.')
        return redirect(url_for('login'))

    # Fetch user's fuel quote history from the database
    user_quotes = FuelQuote.query.filter_by(user_id=user.id).all()

    return render_template('fuel_history.html', user_quotes=user_quotes)



@app.route('/logout')
def logout():
    # Remove 'username' from session
    session.pop('username', None)  
    # Redirect to the login page
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
