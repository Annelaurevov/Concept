import os
import requests
import openai

from flask import Flask, session, render_template, request, redirect, flash, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from scribble import generate_random_scribble, plot_scribble, generate_daily_scribble
from datetime import datetime


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
openai.api_key = "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"

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
    category = request.args.get('category', 'interior')  # Default category
    query = request.args.get('query', '')  # Search term
    
    # Unsplash API-instellingen
    url = "https://api.unsplash.com/search/photos"
    headers = {
        "Authorization": "Client-ID jFzLzxaW0qjrN4uxry35H7Fchc9ObBt0copcgEGfRDE"
    }
    params = {
        "query": f"{category} {query}", 
        "per_page": 8, 
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Controleer op fouten
        data = response.json()
        images = [{"url": img["urls"]["regular"]} for img in data["results"]]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching images: {e}")
        images = []

    return render_template('index.html', images=images, category=category)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm-password")
        print(f"Password: {password}, Confirm Password: {confirm_password}")


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

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/save', methods=["POST"])
@login_required
def save_image():
    image_id = request.form.get("image_id")
    image_url = request.form.get("image_url")
    description = request.form.get("description")

    if not description:
        description = "No description available"
    
    # Debugging logs
    print(f"Received data: image_id={image_id}, image_url={image_url}, description={description}")
    
    if not image_id or not image_url:
        return jsonify({"success": False, "message": "Missing image data"}), 400

    # Controleer of de afbeelding al is opgeslagen
    existing = SavedImage.query.filter_by(user_id=session['user_id'], image_id=image_id).first()
    if existing:
        return jsonify({"success": False, "message": "Image already saved"}), 409

    # Opslaan in de database
    new_saved_image = SavedImage(
        user_id=session['user_id'],
        image_id=image_id,
        url=image_url,
        description=description or "No description available"
    )
    try:
        db.session.add(new_saved_image)
        db.session.commit()
        flash("Image saved successfully!", "success")
    except Exception as e:
        db.session.rollback()
        print(f"Error saving image: {e}")
        flash("Error saving image. Please try again.", "error")
     
    return redirect(url_for("favorites"))
    

@app.route('/favorites')
@login_required
def favorites():
    # Haal opgeslagen afbeeldingen van de gebruiker op
    user_id = session["user_id"]
    saved_images = SavedImage.query.filter_by(user_id=user_id).all()
    return render_template('favorites.html', saved_images=saved_images)

@app.route('/delete', methods=["POST"])
@login_required
def delete_image():
    image_id = request.form.get("image_id")

    if not image_id:
        flash("Missing image data. Cannot delete.", "error")
        return redirect(url_for("favorites"))

    # Zoek de afbeelding in de database
    saved_image = SavedImage.query.filter_by(user_id=session['user_id'], id=image_id).first()
    if not saved_image:
        flash("Image not found or you do not have permission to delete it.", "error")
        return redirect(url_for("favorites"))

    # Verwijder de afbeelding
    try:
        db.session.delete(saved_image)
        db.session.commit()
        flash("Image deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting image: {e}")
        flash("Error deleting image. Please try again.", "error")

    return redirect(url_for("favorites"))

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Gebruik "gpt-4" als je toegang hebt tot GPT-4
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message},
            ]
        )
        reply = response['choices'][0]['message']['content']
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/doodles")
def doodles():
    today = datetime.now().date()
    
    # Verkrijg de doodles die vandaag zijn toegevoegd
    todays_doodles = Doodle.query.filter_by(date=today).all()

    if not todays_doodles:
        # Geen doodles voor vandaag, dus maak een nieuwe aan
        filename = generate_daily_scribble()  # Zorg ervoor dat deze functie een bestandsnaam retourneert
        new_doodle = Doodle(filename=filename, date=today)
        db.session.add(new_doodle)
        db.session.commit()
        todays_doodles = [new_doodle]  # Voeg de nieuw aangemaakte doodle toe aan de lijst

    return render_template("doodles.html", todays_doodles=todays_doodles)

@app.route("/upload_doodle", methods=["POST"])
@login_required
def upload_doodle():
    file = request.files.get("uploaded_doodle")
    if file:
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        filepath = os.path.join("static/user_doodles", filename)
        file.save(filepath)

        new_doodle = UserDoodle(
            user_id=session["user_id"],
            filename=filename,
            likes=0
        )
        db.session.add(new_doodle)
        db.session.commit()
        flash("Je doodle is geüpload!", "success")
    else:
        flash("Geen bestand geselecteerd!", "error")
    return redirect(url_for("doodles"))


@app.route("/like/<int:doodle_id>", methods=["POST"])
@login_required
def like_doodle(doodle_id):
    doodle = UserDoodle.query.get(doodle_id)
    if doodle:
        doodle.likes += 1
        db.session.commit()
        return jsonify({"likes": doodle.likes}), 200
    return jsonify({"error": "Doodle niet gevonden"}), 404


@app.route("/comment/<int:doodle_id>", methods=["POST"])
@login_required
def comment_doodle(doodle_id):
    doodle = UserDoodle.query.get(doodle_id)
    if doodle:
        comment_text = request.form.get("comment")
        new_comment = DoodleComment(
            doodle_id=doodle_id,
            user_id=session["user_id"],
            text=comment_text
        )
        db.session.add(new_comment)
        db.session.commit()
        return jsonify({"message": "Comment toegevoegd!"}), 200
    return jsonify({"error": "Doodle niet gevonden"}), 404


@app.route("/leaderboard")
def leaderboard():
    top_doodles = UserDoodle.query.order_by(desc(UserDoodle.likes)).limit(10).all()
    return render_template("leaderboard.html", user_doodles=top_doodles)


if __name__ == "__main__":
    app.run(debug=True)
