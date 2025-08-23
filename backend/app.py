from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"  # needed for flash messages & sessions

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="secuser",
    password="12345678",  # use the same password you set
    database="securedevops"
)
cursor = db.cursor(dictionary=True)

@app.route('/')
def home():
    return render_template('home.html')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_pw = generate_password_hash(password)

        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, hashed_pw)
            )
            db.commit()
            flash("User registered successfully!", "success")
            return redirect(url_for('login'))
        except:
            flash("Username already exists!", "error")
            return redirect(url_for('register'))
    
    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['username'] = username
            flash(f"Login successful! Welcome {username}", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials!", "error")
            return redirect(url_for('login'))
    
    return render_template('login.html')

# Dashboard route
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash("Please login first.", "error")
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Logged out successfully.", "success")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=5003)
