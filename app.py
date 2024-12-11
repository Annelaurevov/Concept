import os
import requests

from flask import Flask, session, render_template, request, redirect, flash, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash

from models import *

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
db.init_app(app)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SERVER_NAME'] = 'localhost:5000'

Session(app)

# Decorator to enforce login
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("You must be logged in to access this page.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    # Unsplash API-instellingen
    url = "https://api.unsplash.com/search/photos"
    headers = {
        "Authorization": "Client-ID jFzLzxaW0qjrN4uxry35H7Fchc9ObBt0copcgEGfRDE"
    }
    params = {
        "query": "interior design",  # Zoekterm
        "per_page": 9,  # Aantal resultaten per pagina
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Controleer op fouten
        data = response.json()
        images = [{"url": img["urls"]["regular"]} for img in data["results"]]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching images: {e}")
        images = []

    return render_template('index.html', images=images)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm-password")

        if not username or not password:
            flash("Both username and password are required.", "error")
            return redirect(url_for("register"))

        # Check if the user already exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "error")
            return redirect(url_for("register"))
        
        if password != confirm_password:
            flash("Not same password!", "error")
            return redirect(url_for("register"))
    
        # Create a new user and hash the password
        new_user = User(username=username)
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred during registration. Please try again.", "error")
            print(f"Error: {e}")
            return redirect(url_for("register"))

    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Controleer of de gebruiker bestaat
        user = User.query.filter_by(username=username).first()
        if not user:
            flash('Gebruiker bestaat niet.', 'danger')
            return redirect(url_for('login'))

        # Controleer het wachtwoord
        if not user.check_password(password):
            flash('Ongeldig wachtwoord.', 'danger')
            return redirect(url_for('login'))

        # Zet de gebruiker in de sessie
        session['user_id'] = user.id
        flash('Succesvol ingelogd.', 'success')
        return redirect(url_for('index'))

    return render_template('login.html')

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
