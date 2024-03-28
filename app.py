from flask import Flask, request, redirect, url_for, render_template, session, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management

# Dummy database of users for illustration
users_db = {
    'user1': {
        'password': 'pass1', 'profile_complete': True,
        'profile_info': {
            'full_name': 'Romina s',
            'address1': '3607 washington ave',
            'address2': '',
            'city': 'Houston',
            'state': 'Texas',
            'zip_code': '78734',
        },
        'fuel_quote_history': [
            {'date': '2023-03-15', 'gallons_requested': 100, 'total_amount_due': 200,'date_js': '2023-03-15', 'price': '150', 'delivery': '200'},
            {'date': '2023-03-20', 'gallons_requested': 150, 'total_amount_due': 300,'date_js': '2023-03-20', 'price': '100', 'delivery': '200'} 


        ]
    },
    'user2': {
        'password': 'pass2',
        'profile_complete': False,
        'profile_info': {
            'full_name': '',
            'address1': '',
            'address2': '',
            'city': '',
            'state': '',
            'zip_code': '',
        },
        'fuel_quote_history': []
    }

    # Add other users 
}

# check user authentication 
def authenticate(username, password):
    user = users_db.get(username)
    if user and user['password'] == password:  # Direct password comparison
        return True
    return False

#  check if profile is complete 
def is_profile_complete(username):
    return users_db.get(username, {}).get('profile_complete', False)

@app.route('/')
def home():
    # Redirect to dashboard if logged in, else login page
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username already exists in the dummy database
        if username in users_db:
            flash('Username already exists. Please choose a different one.')
            #return render_template('register.html')
            return redirect(url_for('register'))

        # Proceed with registration if username is not taken
        
        # Save the user with  password in the dummy database
        users_db[username] = {'password': password, 'profile_complete': False, 'profile_info': {}}

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
    print(username)
    if not username or username not in users_db:
        flash('User not found. Please login again.')
        return redirect(url_for('login'))

    #user = users_db.get(username)
    user = users_db[username]
    print(user)
    if request.method == 'POST':
        # update user profile info in database 

        #users_db[username]['profile_complete'] = True
        user['profile_info'].update(request.form.to_dict())
        user['profile_complete']=True
        print(user['profile_complete'])
        flash('Profile Saved, continue to FuelMetrics.')  # Flash message
        return redirect(url_for('profile'))  # Redirect to profile to see changes 

    # Check profile completion status on every request
    profile_complete = is_profile_complete(username)
    return render_template('profile.html',user=user, profile_complete=profile_complete)



@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# @app.route('/fuel_quote', methods=['GET'])
# def fuel_quote():
#     # No change needed for form submission handling, as it's done client-side
#     return render_template('fuel_quote.html')

@app.route('/fuel_quote', methods=['GET', 'POST'])
def fuel_quote():
    username = session.get('username')
    if not username or username not in users_db:
        flash('Please log in to access the fuel quote page.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Process the submitted form data
        gallons_requested = request.form.get('gallons', type=float)
        delivery_date = request.form.get('delivery_date')
        
        #delivery fee
        deliveryFee = 1.75;

        #base price calulation
        pricePerGallon = 3.05;
        basePrice = pricePerGallon * gallons_requested;
        estimatedCost = basePrice;

        #tax fee
        taxRate = 0.0775;
        taxFee = basePrice * taxRate;

        #total price
        totalPrice = deliveryFee + taxFee + basePrice;

        # Save the quote to the user's history
        users_db[username]['fuel_quote_history'].append({
            'date': delivery_date,
            'gallons_requested': gallons_requested,
            'total_amount_due': totalPrice,
            'date_js': delivery_date,
            'price': estimatedCost,
            #'price_per_gallon': price_per_gallon,
            'delivery': deliveryFee
            #'tax': tax,

        })

        flash('Fuel quote saved successfully.\nView in Quote History')
        # Redirect to the fuel history page or somewhere else to avoid form resubmission issues
        return redirect(url_for('fuel_quote'))

    # For a GET request, just display the form
    user_profile_info = users_db[username]['profile_info']
    return render_template('fuel_quote.html', profile_info=user_profile_info)



# @app.route('/fuel_history')
# def fuel_history():
#     # Logic to fetch and display fuel quote history

#     return render_template('fuel_history.html')

@app.route('/fuel_history')
def fuel_history():
    username = session.get('username')
    if not username or username not in users_db:
        flash('Please log in to view fuel quote history.')
        return redirect(url_for('login'))

    # Fetch user's fuel quote history from the database
    user_quotes = users_db.get(username, {}).get('fuel_quote_history', [])
    
    # Format the dates in the fuel quote history for easy handling in JavaScript
    for quote in user_quotes:
        # Assume the date is stored in 'YYYY-MM-DD' format; adjust if necessary
        quote['date_js'] = quote['date']
        

    return render_template('fuel_history.html', user_quotes=user_quotes)


@app.route('/logout')
def logout():
    # Remove 'username' from session
    session.pop('username', None)  
    # Redirect to the login page
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
