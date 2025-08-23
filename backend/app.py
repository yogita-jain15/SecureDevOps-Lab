from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "dev-secret-key"  # dev only!

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        # TEMP auth (we’ll replace with DB on Day 5)
        if username == "admin" and password == "password":
            flash("Login successful! Welcome, Admin.", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials", "error")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    # later: require login & role=admin
    return render_template("dashboard.html")

if __name__ == "__main__":
    # host=0.0.0.0 so you can hit it from Windows; keep debug for dev only
    app.run(debug=True, host="0.0.0.0", port=5003)

