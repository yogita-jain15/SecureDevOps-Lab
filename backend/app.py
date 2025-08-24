from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
import os, re, logging
import mysql.connector
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-only-secret")

# ---------- Logging (security) ----------
os.makedirs("backend/logs", exist_ok=True)
logging.basicConfig(
    filename="backend/logs/security.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

# ---------- DB connection ----------
db = mysql.connector.connect(
    host="localhost",
    user="secuser",
    password="12345678",    # <-- your DB password
    database="securedevops"
)
cursor = db.cursor(dictionary=True)

# ---------- Helpers: auth / roles ----------
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

# ---------- Simple input-validation signals (defense-in-depth) ----------
USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{3,32}$")
def validate_username(u: str) -> bool:
    return bool(USERNAME_RE.match(u or ""))

def is_suspicious(text: str) -> bool:
    if not text: 
        return False
    # crude tripwires; **not** the primary defense
    patterns = ["'", "\"", ";", "--", "/*", "*/", " OR ", " or ", "#"]
    return any(p in text for p in patterns)

# ---------- Routes ----------
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = (request.form.get('username') or "").strip()
        password = request.form.get('password') or ""
        if not username or not password:
            flash("Username and password are required.", "error")
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password)
        try:
            # Ensure new users get role='user'
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                (username, hashed_pw, "user")
            )
            db.commit()
            flash("User registered successfully! Please log in.", "success")
            return redirect(url_for('login'))
        except mysql.connector.Error as e:
            logging.warning(f"[REGISTER][DB ERROR] user={username} err={e}")
            flash("Username already exists.", "error")
            return redirect(url_for('register'))
    return render_template('register.html')

# -------- SAFE LOGIN (production) --------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = (request.form.get('username') or "").strip()
        password = request.form.get('password') or ""

        # soft validation / tripwire logging
        if not validate_username(username):
            logging.warning(f"[SAFE_LOGIN][INVALID USERNAME FORMAT] u={username} ip={request.remote_addr}")
            return "Invalid username format."
        if is_suspicious(username) or is_suspicious(password):
            logging.warning(f"[SAFE_LOGIN][SUSPECT INPUT] u={username} ip={request.remote_addr}")

        # Parameterized query (real defense)
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            session['role'] = user.get('role', 'user')
            logging.info(f"[SAFE_LOGIN][SUCCESS] u={username} ip={request.remote_addr}")
            nxt = request.args.get('next')
            return redirect(nxt or url_for('dashboard'))
        else:
            logging.info(f"[SAFE_LOGIN][FAIL] u={username} ip={request.remote_addr}")
            flash("Invalid credentials.", "error")
            return redirect(url_for('login'))

    return render_template('login.html')

# -------- VULNERABLE LOGIN (lab only) --------
SHOW_VULN = os.environ.get("SHOW_VULN", "1") == "1"   # set to 0 to disable in prod

@app.route('/vuln_login', methods=['GET', 'POST'])
def vuln_login():
    if not SHOW_VULN:
        abort(404)

    if request.method == 'POST':
        username = request.form.get('username', "")
        password = request.form.get('password', "")

        # INTENTIONALLY INSECURE: string concatenation causes SQL injection
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        try:
            cursor.execute(query)
            user = cursor.fetchone()
        except Exception as e:
            logging.error(f"[VULN_LOGIN][SQL ERROR] {e} :: query={query}")
            return "SQL error occurred (see server logs)."

        if user:
            session['username'] = user['username']
            session['role'] = user.get('role', 'user')
            return ("VULN LOGIN SUCCESS (intentionally insecure). "
                    "<br><a href='/dashboard'>Go to dashboard</a>")
        else:
            if is_suspicious(username) or is_suspicious(password):
                logging.warning(f"[VULN_LOGIN][SUSPECT INPUT] u={username} p={password} ip={request.remote_addr}")
            return "Invalid credentials (vuln route). Try the safe Login instead."

    # barebones form (kept inline to emphasize difference)
    return """
      <h2>Vulnerable Login (for lab demo only)</h2>
      <form method="POST">
        <label>Username</label> <input name="username"><br><br>
        <label>Password</label> <input type="password" name="password"><br><br>
        <button type="submit">Login</button>
      </form>
      <p>⚠️ This route concatenates user input into SQL; it is vulnerable to SQL injection.</p>
    """

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
    app.run(debug=True, port=5003, host='0.0.0.0')
