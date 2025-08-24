from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import mysql.connector
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# use env var in real deployments
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-only-secret")

# ---- DB connection (simple for dev) ----
db = mysql.connector.connect(
    host="localhost",
    user="secuser",
    password="12345678",   # <-- your actual DB password
    database="securedevops"
)
cursor = db.cursor(dictionary=True)

# ---- decorators for auth / roles ----
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            flash("Please log in first.", "error")
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return wrapper

def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'username' not in session:
                flash("Please log in first.", "error")
                return redirect(url_for('login'))
            if session.get('role') not in roles:
                flash("Access denied: insufficient role.", "error")
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return wrapper
    return decorator

# ---- routes ----
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        if not username or not password:
            flash("Username and password are required.", "error")
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password)
        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, hashed_pw)
            )
            db.commit()
            flash("User registered successfully! Please log in.", "success")
            return redirect(url_for('login'))
        except mysql.connector.Error as e:
            # likely duplicate username (UNIQUE constraint)
            flash("Username already exists.", "error")
            return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # if already logged in, skip
    if 'username' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            session['role'] = user['role'] or 'user'
            flash(f"Welcome, {user['username']}!", "success")
            # support ?next=/some/path
            nxt = request.args.get('next')
            return redirect(nxt or url_for('dashboard'))
        else:
            flash("Invalid credentials.", "error")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=session.get('username'))

@app.route('/admin')
@roles_required('admin')
def admin_panel():
    return render_template('admin.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out.", "success")
    return redirect(url_for('home'))

if __name__ == '__main__':
    # run on 5003 to match your setup
    app.run(debug=True, port=5003, host='0.0.0.0')
