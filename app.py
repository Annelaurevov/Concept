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
from PIL import Image  
from io import BytesIO


from models import *

app = Flask(__name__)
app.secret_key = "key"

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/annelaurevanoverbeeke/Documents/Programeerproject2/Concept/instance/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


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
                "title": hit["recipe"]["label"],
                "image": hit["recipe"].get("image", ""),  # Controleer of de afbeelding aanwezig is
                "url": hit["recipe"].get("url", ""),  # Controleer of de URL aanwezig is
            }
            for hit in data.get("hits", [])
        ]
       
    except requests.exceptions.RequestException as e:
        print(f"Error fetching recipes: {e}")
        recipes = []

    return render_template('recipes.html', recipes=recipes, query=query)

@app.route("/photos")
def photos():
    category = request.args.get('category', 'interior')  # Default category
    query = request.args.get('query', '')  # Search term
    
    # Unsplash API-instellingen
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
        response.raise_for_status()  # Controleer op fouten
        data = response.json()
        images = [{"url": img["urls"]["regular"]} for img in data["results"]]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching images: {e}")
        images = []

    return render_template('photos.html', images=images, category=category)

@app.route('/art', methods=['GET', 'POST'])
def art():
    api_url = "https://www.rijksmuseum.nl/api/en/collection"
    query = request.form.get('query', 'paintings')  # Haal de zoekterm op uit het formulier
    page = request.args.get('page', 1)  # Voeg een pagina-parameter toe voor nieuwe resultaten

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

        for item in data.get("artObjects", []):
            title = item.get("title", "Untitled")
            artist = item.get("principalOrFirstMaker", "Unknown")
            image_url = item.get("webImage", {}).get("url", None)
            info_url = item.get("links", {}).get("web", "#")

            if not image_url:
                continue  # Sla over als er geen afbeelding is

            artworks.append({
                "title": title,
                "artist": artist,
                "image_url": image_url,
                "info_url": info_url,
            })
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Rijksmuseum API: {e}")

    return render_template('art.html', artworks=artworks, query=query, page=page)

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

@app.route('/save_recipe', methods=["POST"])
@login_required
def save_recipe():
    recipe_id = request.form.get("recipe_id")
    label = request.form.get("recipe_title")
    url = request.form.get("recipe_url")
    description = request.form.get("recipe_description", "No description available")

    if not recipe_id or not url or not label:
        return jsonify({"success": False, "message": "Missing recipe data"}), 400

    # Controleer of het recept al is opgeslagen
    existing = SavedRecipe.query.filter_by(user_id=session['user_id'], recipe_id=recipe_id).first()
    if existing:
        return jsonify({"success": False, "message": "Recipe already saved"}), 409

    # Opslaan in de database
    new_saved_recipe = SavedRecipe(
        user_id=session['user_id'],
        recipe_id=recipe_id,
        label=label,
        url=url,
        description=description
    )
    try:
        db.session.add(new_saved_recipe)
        db.session.commit()
        flash("Recipe saved successfully!", "success")
    except Exception as e:
        db.session.rollback()
        print(f"Error saving recipe: {e}")
        flash("Error saving recipe. Please try again.", "error")

    return redirect(url_for("favorites"))

@app.route('/save_art', methods=["POST"])
@login_required
def save_art():
    art_id = request.form.get("art_id")
    title = request.form.get("title")
    artist = request.form.get("artist", "Unknown")
    info_url = request.form.get("info_url")

    if not art_id or not title or not info_url:
        return jsonify({"success": False, "message": "Missing artwork data"}), 400

    # Controleer of het kunstwerk al is opgeslagen
    existing = SavedArt.query.filter_by(user_id=session['user_id'], id=art_id).first()
    if existing:
        return jsonify({"success": False, "message": "Artwork already saved"}), 409

    # Opslaan in de database
    new_artwork = SavedArt(
        user_id=session['user_id'],
        title=title,
        artist=artist,
        info_url=info_url
    )
    try:
        db.session.add(new_artwork)
        db.session.commit()
        flash("Artwork saved successfully!", "success")
    except Exception as e:
        db.session.rollback()
        print(f"Error saving artwork: {e}")
        flash("Error saving artwork. Please try again.", "error")

    return redirect(url_for("favorites"))


@app.route('/favorites')
@login_required
def favorites():
    user_id = session["user_id"]

    # Haal opgeslagen foto's, recepten en kunst op
    saved_images = SavedImage.query.filter_by(user_id=user_id).all()
    saved_recipes = SavedRecipe.query.filter_by(user_id=user_id).all()
    saved_artworks = SavedArt.query.filter_by(user_id=user_id).all()  # Nieuwe kunstcategorie

    return render_template(
        'favorites.html', 
        saved_images=saved_images, 
        saved_recipes=saved_recipes, 
        saved_artworks=saved_artworks
    )


@app.route('/delete_recipe', methods=["POST"])
@login_required
def delete_recipe():
    recipe_id = request.form.get("recipe_id")

    if not recipe_id:
        flash("Missing recipe data. Cannot delete.", "error")
        return redirect(url_for("favorites"))

    # Zoek het recept in de database
    saved_recipe = SavedRecipe.query.filter_by(user_id=session['user_id'], id=recipe_id).first()
    if not saved_recipe:
        flash("Recipe not found or you do not have permission to delete it.", "error")
        return redirect(url_for("favorites"))

    # Verwijder het recept
    try:
        db.session.delete(saved_recipe)
        db.session.commit()
        flash("Recipe deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting recipe: {e}")
        flash("Error deleting recipe. Please try again.", "error")

    return redirect(url_for("favorites"))


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
        filename = generate_daily_scribble() 
        new_doodle = Doodle(filename=filename, date=today)
        db.session.add(new_doodle)
        db.session.commit()
        todays_doodles = [new_doodle]  

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
    with app.app_context():
        app.run(debug=True)
