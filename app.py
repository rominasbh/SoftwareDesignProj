from flask import Flask, request, redirect, url_for, render_template, session, flash
from models import db, User, FuelQuote, ProfileInfo
from datetime import datetime
from config import Config
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)

# # Dummy database of users for illustration
# users_db = {
#     'user1': {
#         'password': 'pass1', 'profile_complete': True,
#         'profile_info': {
#             'full_name': 'Romina s',
#             'address1': '3607 washington ave',
#             'address2': '',
#             'city': 'Houston',
#             'state': 'Texas',
#             'zip_code': '78734',
#         },
#         'fuel_quote_history': [
#             {'date': '2023-03-15', 'gallons_requested': 100, 'total_amount_due': 505,'date_js': '2023-03-15', 'price': '305', 'delivery': '200','price_per_gallon':'3.05'},
#             {'date': '2023-03-20', 'gallons_requested': 150, 'total_amount_due': 657.5,'date_js': '2023-03-20', 'price': '475.5', 'delivery': '200','price_per_gallon':'3.05'},
#             {'date': '2023-05-15', 'gallons_requested': 200, 'total_amount_due': 810,'date_js': '2023-03-15', 'price': '305', 'delivery': '200','price_per_gallon':'3.05'},
#             {'date': '2023-10-20', 'gallons_requested': 150, 'total_amount_due': 657.5,'date_js': '2023-03-20', 'price': '475.5', 'delivery': '200','price_per_gallon':'3.05'},
#             {'date': '2024-01-15', 'gallons_requested': 200, 'total_amount_due': 810,'date_js': '2023-03-15', 'price': '305', 'delivery': '200','price_per_gallon':'3.05'},
#             {'date': '2024-03-28', 'gallons_requested': 160, 'total_amount_due': 688,'date_js': '2023-03-20', 'price': '475.5', 'delivery': '200','price_per_gallon':'3.05'}    
#         ]
#     },
#     'user2': {
#         'password': 'pass2',
#         'profile_complete': False,
#         'profile_info': {
#             'full_name': '',
#             'address1': '',
#             'address2': '',
#             'city': '',
#             'state': '',
#             'zip_code': '',
#         },
#         'fuel_quote_history': []
#     }

#     # Add other users 
# }

# check user authentication 
# def authenticate(username, password):
#     user = users_db.get(username)
#     if user and user['password'] == password:  # Direct password comparison
#         return True
#     return False

def authenticate(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.password == password:  # Consider hashing the password
        return True
    return False

#  check if profile is complete 
# def is_profile_complete(username):
#     return users_db.get(username, {}).get('profile_complete', False)
def is_profile_complete(username):
    user = User.query.filter_by(username=username).first()
    return user.profile_complete if user else False


# @app.route('/')
# def home():
#     # Redirect to dashboard if logged in, else login page
#     if 'username' in session:
#         return redirect(url_for('dashboard'))
#     return redirect(url_for('login'))
@app.route('/')
def home():
    # Redirect to dashboard if logged in, else login page
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        if user and is_profile_complete(user.username):
            return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']   # Hash this password

#         # Check if the username already exists in the dummy database
#         if username in users_db:
#             flash('Username already exists. Please choose a different one.')
#             #return render_template('register.html')
#             return redirect(url_for('register'))

#         # Proceed with registration if username is not taken
        
#         # Save the user with  password in the dummy database
#         users_db[username] = {'password': password, 'profile_complete': False, 'profile_info': {}}

#         flash('Registration successful. Please log in.')
#         return redirect(url_for('login'))

#     return render_template('register.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']   # Hash this password

        # Check if the username already exists in the dummy database
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('register'))

        # Proceed with registration if username is not taken
        
        # Save the user with  password db
        new_user = User(username=username, password=password)
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


# @app.route('/profile', methods=['GET', 'POST'])
# def profile():
    
#     username = session.get('username')
#     print(username)
#     if not username or username not in users_db:
#         flash('User not found. Please login again.')
#         return redirect(url_for('login'))

#     #user = users_db.get(username)
#     user = users_db[username]
#     print(user)
#     if request.method == 'POST':
#         # update user profile info in database 

#         #users_db[username]['profile_complete'] = True
#         user['profile_info'].update(request.form.to_dict())
#         user['profile_complete']=True
#         print(user['profile_complete'])
#         flash('Profile Saved, continue to FuelMetrics.')  # Flash message
#         return redirect(url_for('profile'))  # Redirect to profile to see changes 

#     # Check profile completion status on every request
#     profile_complete = is_profile_complete(username)
#     return render_template('profile.html',user=user, profile_complete=profile_complete)

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

# @app.route('/fuel_quote', methods=['GET'])
# def fuel_quote():
#     # No change needed for form submission handling, as it's done client-side
#     return render_template('fuel_quote.html')

# @app.route('/fuel_quote', methods=['GET', 'POST'])
# def fuel_quote():
#     username = session.get('username')
#     if not username or username not in users_db:
#         flash('Please log in to access the fuel quote page.')
#         return redirect(url_for('login'))

#     if request.method == 'POST':
#         # Process the submitted form data
#         gallons_requested = request.form.get('gallons', type=float)
#         delivery_date = request.form.get('delivery_date')
        
#         #delivery fee
#         deliveryFee = 1.75;

#         #base price calulation
#         pricePerGallon = 3.05;
#         basePrice = pricePerGallon * gallons_requested;
#         estimatedCost = basePrice;

#         #tax fee
#         taxRate = 0.0775;
#         taxFee = basePrice * taxRate;

#         #total price
#         totalPrice = deliveryFee + taxFee + basePrice;

#         # Save the quote to the user's history
#         users_db[username]['fuel_quote_history'].append({
#             'date': delivery_date,
#             'gallons_requested': gallons_requested,
#             'total_amount_due': totalPrice,
#             'date_js': delivery_date,
#             'price': estimatedCost,
#             'price_per_gallon': pricePerGallon,
#             'delivery': deliveryFee
#             #'tax': tax,

#         })

#         flash('Fuel quote saved successfully.\nView in Quote History')
#         # Redirect to the fuel history page or somewhere else to avoid form resubmission issues
#         return redirect(url_for('fuel_quote'))

#     # For a GET request, just display the form
#     user_profile_info = users_db[username]['profile_info']
#     return render_template('fuel_quote.html', profile_info=user_profile_info)



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



# @app.route('/fuel_history')
# def fuel_history():
#     username = session.get('username')
#     if not username or username not in users_db:
#         flash('Please log in to view fuel quote history.')
#         return redirect(url_for('login'))

#     # Fetch user's fuel quote history from the database
#     user_quotes = users_db.get(username, {}).get('fuel_quote_history', [])
    
#     # Format the dates in the fuel quote history for easy handling in JavaScript
#     for quote in user_quotes:
#         # Assume the date is stored in 'YYYY-MM-DD' format; adjust if necessary
#         quote['date_js'] = quote['date']
        

#     return render_template('fuel_history.html', user_quotes=user_quotes)

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
