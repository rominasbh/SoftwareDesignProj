from flask import Flask, request, redirect, url_for, render_template, session, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management

# Dummy database of users for illustration
users_db = {
    'user1': {'password': 'pass1', 'profile_complete': True},
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
        users_db[username] = {'password': password, 'profile_complete': False}

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
    if not username or username not in users_db:
        flash('User not found. Please login again.')
        return redirect(url_for('login'))
    if request.method == 'POST':
        # Profile completion logic
        users_db[username]['profile_complete'] = True
        flash('Profile Complete, continue to FuelMetrics.')  # Flash message
        #return redirect(url_for('complete'))  # Redirect to profile or dashboard
        return redirect(url_for('dashboard'))  # Redirect to profile or dashboard
    #return render_template('profile.html')

    # Check profile completion status on every request
    profile_complete = is_profile_complete(username)
    return render_template('profile.html', profile_complete=profile_complete)



@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/fuel_quote', methods=['GET'])
def fuel_quote():
    # No change needed for form submission handling, as it's done client-side
    return render_template('fuel_quote.html')


@app.route('/fuel_history')
def fuel_history():
    # Logic to fetch and display fuel quote history
    return render_template('fuel_history.html')


@app.route('/logout')
def logout():
    # Remove 'username' from session
    session.pop(session.get('username'), None)  
    # Redirect to the login page
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
