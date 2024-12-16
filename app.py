import os
from flask_migrate import Migrate
import requests
import openai

from flask import Flask, session, render_template, request, redirect, flash, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
from scribble import generate_random_scribble, plot_scribble, generate_daily_scribble
from datetime import datetime
from PIL import Image  
from io import BytesIO


from models import *
app = Flask(__name__)
app.secret_key = "key"

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///instance/Concept.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

db.init_app(app)

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
    url = "https://api.unsplash.com/search/photos"
    headers = {
        "Authorization": "Client-ID jFzLzxaW0qjrN4uxry35H7Fchc9ObBt0copcgEGfRDE"
    }
    params = {
        "query": "nature", 
        "per_page": 30
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        images = [{"url": img["urls"]["regular"]} for img in data["results"]]
    except Exception as e:
        print(f"Error: {e}")
        images = []

    return render_template("index.html", images=images)

@app.route("/photos", methods=["GET"])
def photos():
    category = request.args.get('category', 'interior')
    query = request.args.get('query', '')

    url = "https://api.unsplash.com/search/photos"
    headers = {
        "Authorization": "Client-ID jFzLzxaW0qjrN4uxry35H7Fchc9ObBt0copcgEGfRDE"
    }
    params = {
        "query": f"{category} {query}",
        "per_page": 20,
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        images = [
            {
                "id": i,
                "url": img["urls"]["regular"],
                "description": img.get("description", "No description available")
            }
            for i, img in enumerate(data["results"])
        ]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching images: {e}")
        images = []

    return render_template('photos.html', images=images, category=category)

@app.route('/art', methods=['GET', 'POST'])
def art():
    api_url = "https://www.rijksmuseum.nl/api/en/collection"
    query = request.form.get('query', 'paintings')
    page = request.args.get('page', 1)

    params = {
        "key": "wKdQj5hU",
        "q": query,
        "ps": 20,
        "imgonly": True,
        "p": page
    }

    artworks = []
    try:
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        for i, item in enumerate(data.get("artObjects", [])):
            image_url = item.get("webImage", {}).get("url", None)
            if not image_url:
                continue

            artworks.append({
                "id": i,
                "title": item.get("title", "Untitled"),
                "artist": item.get("principalOrFirstMaker", "Unknown"),
                "image_url": image_url,
                "info_url": item.get("links", {}).get("web", "#")
            })
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Rijksmuseum API: {e}")

    return render_template('art.html', artworks=artworks, query=query, page=page)

@app.route('/recipes', methods=['GET'])
def recipes():
    query = request.args.get('query', 'pastries')
    url = "https://api.edamam.com/search"
    params = {
        "q": query,
        "app_id": "482eb6d9",
        "app_key": "d8b388214cd3dd949a059e7967b004cc",
        "to": 8
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        recipes = [
            {
                "id": i,
                "title": hit["recipe"]["label"],
                "image": hit["recipe"].get("image", ""),
                "url": hit["recipe"].get("url", ""),
                "description": hit["recipe"].get("source", "No description available")
            }
            for i, hit in enumerate(data.get("hits", []))
        ]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching recipes: {e}")
        recipes = []

    return render_template('recipes.html', recipes=recipes, query=query)


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
    flash("You have been logged out.")
    return redirect(url_for("index"))

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/save/<item_type>', methods=["POST"])
@login_required
def save_item(item_type):
    user_id = session["user_id"]
    data = request.form

    if item_type == "photo":
        user_id = session.get("user_id")  # Haal de user_id uit de sessie
        image_id = request.form.get("image_id")  # Zorg dat dit overeenkomt met je HTML formulier
        url = request.form.get("image_url")
        description = request.form.get("description", "No description available")

        if not image_id or not url:
            flash("Missing image data.", "error")
            return redirect(request.referrer)

        # Controleer of de afbeelding al geliket is
        existing_like = SavedImage.query.filter_by(user_id=user_id, image_id=image_id).first()
        if existing_like:
            flash("You have already liked this image!", "warning")
            return redirect(request.referrer)

        # Voeg een nieuwe like toe
        new_like = SavedImage(
            user_id=user_id,
            image_id=image_id,
            url=url,
            description=description
        )

        db.session.add(new_like)
        db.session.commit()

        flash("Image liked successfully!", "success")
            

    elif item_type == "recipe":
        item_id = data.get("recipe_id")
        label = data.get("recipe_title")
        url = data.get("recipe_url")
        description = data.get("recipe_description", "No description available")
        recipe_image = data.get("recipe_image")

        print(f"Recipe Image Received: {recipe_image}")  # Debug: Controleer de input

        if not item_id or not url or not label:
            return jsonify({"success": False, "message": "Missing recipe data"}), 400

        existing = SavedRecipe.query.filter_by(user_id=user_id, id=item_id).first()
        if existing:
            flash("Already liked the recipe")
            return redirect(request.referrer)

        new_item = SavedRecipe(
            user_id=user_id,
            recipe_id=item_id,
            label=label,
            url=url,
            description=description,
            recipe_image=recipe_image
        )
        db.session.add(new_item)
        db.session.commit()

        flash("Recipe saved successfully!", "success")
        

    elif item_type == "art":
        item_id = data.get("art_id")
        title = data.get("title")
        artist = data.get("artist", "Unknown")
        url = data.get("info_url")
        image_url = data.get("image_url")

        if not item_id or not title or not url:
            return jsonify({"success": False, "message": "Missing art data"}), 400

        existing = SavedArt.query.filter_by(user_id=user_id, id=item_id).first()
        if existing:
            flash("Already liked the artwork")
            return redirect(request.referrer)

        new_item = SavedArt(
            user_id=user_id,
            id=item_id,
            title=title,
            artist=artist,
            info_url=url,
            image_url=image_url
        )
        new_item.likes = 1

        db.session.add(new_item)
        db.session.commit()
        flash("Artwork saved successfully!", "success")
    
    return redirect(request.referrer)

@app.route('/delete/<item_type>', methods=["POST"])
@login_required
def delete_item(item_type):
    user_id = session["user_id"]
    item_id = request.form.get("item_id")

    if not item_id:
        flash(f"Missing {item_type} data. Cannot delete.", "error")
        return redirect(url_for("favorites"))

    if item_type == "photo":
        item = SavedImage.query.filter_by(user_id=user_id, image_id=item_id).first()
        redirect_route = "favorites_photos"
    elif item_type == "recipe":
        item = SavedRecipe.query.filter_by(user_id=user_id, recipe_id=item_id).first()
        redirect_route = "favorites_recipes"
    elif item_type == "art":
        item = SavedArt.query.filter_by(user_id=user_id, id=item_id).first()
        redirect_route = "favorites_art"
    else:
        flash(f"Invalid {item_type}. Cannot delete.", "error")
        return redirect(url_for("favorites"))

    if not item:
        flash(f"{item_type.capitalize()} not found or you do not have permission to delete it.", "error")
        return redirect(url_for(redirect_route))

    try:
        db.session.delete(item)
        db.session.commit()
        flash(f"{item_type.capitalize()} deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting {item_type}: {e}")
        flash(f"Error deleting {item_type}. Please try again.", "error")

    return redirect(url_for(redirect_route))

@app.route('/favorites_photos')
@login_required
def favorites_photos():
    user_id = session["user_id"]
    saved_images = SavedImage.query.filter_by(user_id=user_id).all()
    return render_template('favorites_photos.html', saved_images=saved_images)


@app.route('/favorites_art')
@login_required
def favorites_art():
    user_id = session["user_id"]
    saved_artworks = SavedArt.query.filter_by(user_id=user_id).all()
    for artwork in saved_artworks:
        print(f"Artwork ID: {artwork.id}, Title: {artwork.title}, URL: {artwork.info_url}")

    print(saved_artworks)
    return render_template('favorites_art.html', saved_artworks=saved_artworks)

@app.route('/favorites_recipes')
@login_required
def favorites_recipes():
    user_id = session["user_id"]
    saved_recipes = SavedRecipe.query.filter_by(user_id=user_id).all()
    print(saved_recipes)  # Debug: Check welke data wordt teruggegeven
    for recipe in saved_recipes:
        print(f"Recipe Image: {recipe.recipe_image}")  # Check de waarde van recipe_image
    return render_template('favorites_recipes.html', saved_recipes=saved_recipes)


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
@login_required
def doodles():
    today = datetime.now().date()

    # Haal doodles van vandaag op
    todays_doodles = Doodle.query.filter(Doodle.date == today).all()

    if not todays_doodles:
        # Geen doodle vandaag? Genereer een nieuwe
        filename = generate_daily_scribble()
        new_doodle = Doodle(filename=filename, date=today)
        db.session.add(new_doodle)
        db.session.commit()
        todays_doodles = [new_doodle]


    # Bereken likes per submission met JOIN en GROUP BY
    submissions = (
        db.session.query(UserDoodle, func.count(Like.id).label("like_count"))
        .join(Doodle, Doodle.id == UserDoodle.doodle_id)
        .outerjoin(Like, Like.doodle_id == UserDoodle.id)
        .filter(Doodle.date == today)
        .group_by(UserDoodle.id)
        .all()
    )

    # Totaal aantal likes van vandaag
    total_likes = sum(like_count for _, like_count in submissions)

    # Bereken meest gelikete doodle(s)
    max_likes = max((like_count for _, like_count in submissions), default=0)
    most_liked_doodles = [
        {"doodle": submission, "like_count": like_count}
        for submission, like_count in submissions
        if like_count == max_likes
    ]

    # Haal alle likes van de huidige gebruiker op
    user_likes = {like.doodle_id for like in Like.query.filter_by(user_id=session['user_id']).all()}

    # Haal alle unieke datums op
    all_dates = db.session.query(Doodle.date).distinct().order_by(Doodle.date.desc()).all()


    return render_template(
        "doodles.html",
        today = today,
        todays_doodles=todays_doodles,
        submissions=submissions,
        total_likes=total_likes,
        most_liked_doodles=most_liked_doodles,
        user_likes=user_likes,
        all_dates=all_dates
    )

@app.route("/upload_doodle", methods=["POST"])
@login_required
def upload_doodle():
    file = request.files.get("uploaded_doodle")
    if file:
        # Controleer of de map bestaat
        upload_folder = "static/doodles_user"
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        # Koppel aan de Doodle of the Day
        today = datetime.now().date()
        todays_doodle = Doodle.query.filter_by(date=today).first()
        if not todays_doodle:
            flash("Doodle of the Day bestaat niet. Probeer later opnieuw.", "error")
            return redirect(url_for("doodles"))

        new_submission = UserDoodle(
            user_id=session["user_id"],
            doodle_id=todays_doodle.id,
            filename=filename,
            likes=0
        )
        db.session.add(new_submission)
        db.session.commit()
        flash("Je doodle is geüpload!", "success")
    else:
        flash("Geen bestand geselecteerd!", "error")

    return redirect(url_for("doodles"))

@app.route('/like_doodle/<int:doodle_id>', methods=["POST"])
@login_required
def like_doodle(doodle_id):
    user_id = session['user_id']
    
    # Controleer of de gebruiker al een like heeft gegeven
    existing_like = Like.query.filter_by(user_id=user_id, doodle_id=doodle_id).first()
    
    if existing_like:
        # Verwijder de like (unlike)
        db.session.delete(existing_like)
        flash("Like removed!", "success")
    else:
        # Voeg een nieuwe like toe
        new_like = Like(user_id=user_id, doodle_id=doodle_id)
        db.session.add(new_like)
        flash("Doodle liked!", "success")
    
    db.session.commit()
    return redirect(request.referrer)

@app.route("/doodles_by_date/<date>")
@login_required
def doodles_by_date(date):
    try:
        selected_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        flash("Invalid date format. Please use YYYY-MM-DD.", "error")
        return redirect(url_for("doodles"))

    # Haal doodles van de geselecteerde datum op
    selected_doodles = Doodle.query.filter(Doodle.date == selected_date).all()

    # Bereken totaal aantal likes per doodle
    submissions = (
        db.session.query(UserDoodle, func.count(Like.id).label("like_count"))
        .join(Doodle, Doodle.id == UserDoodle.doodle_id)
        .outerjoin(Like, Like.doodle_id == UserDoodle.id)
        .filter(Doodle.date == selected_date)
        .group_by(UserDoodle.id)
        .all()
    )

    # Bereken totaal aantal likes
    total_likes = sum([like_count for _, like_count in submissions])

    # Bereken de meest gelikete doodle(s)
    max_likes = max([like_count for _, like_count in submissions], default=0)
    most_liked_doodles = [
        {"doodle": submission, "like_count": like_count}
        for submission, like_count in submissions
        if like_count == max_likes
    ]

    # Haal alle unieke datums op
    all_dates = db.session.query(Doodle.date).distinct().order_by(Doodle.date.desc()).all()

    return render_template(
        "doodles.html",
        today=selected_date,
        todays_doodles=selected_doodles,
        submissions=submissions,
        total_likes=total_likes,
        most_liked_doodles=most_liked_doodles,
        user_likes={like.doodle_id for like in Like.query.filter_by(user_id=session['user_id']).all()},
        all_dates=all_dates
    )


if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)