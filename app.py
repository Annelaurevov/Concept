import os
from config import Config
from flask_migrate import Migrate
from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect,
    flash,
    url_for,
    jsonify,
)
from flask_session import Session
from scribble import generate_daily_scribble
from datetime import datetime
from helpers import (
    fetch_api_data,
    generate_hash,
    login_required,
    process_photo,
    process_art,
    process_recipe,
    delete_item_helper,
    fetch_user_favorites,
    fetch_doodles_by_date,
    fetch_doodle_submissions_and_likes,
    calculate_doodle_statistics,
    fetch_user_likes,
    fetch_all_doodle_dates,
    save_uploaded_file,
    get_todays_doodle,
    add_user_doodle
)
from models import db, Doodle, SavedImage, SavedArt, SavedRecipe, Like, User

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback_key")

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = \
    "postgresql://annelaurevanoverbeeke:<Nulu2911>@localhost/concept"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)

# Configure sessions
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# _________________________________________________________________________#
#                                    HOMEPAGE                              #
# _________________________________________________________________________#


@app.route('/')
def index():
    """
    Render the homepage with random Unsplash images.
    Fetches random images from Unsplash using API and displays them.
    """
    headers = {"Authorization": f"Client-ID {Config.UNSPLASH_API_KEY}"}
    params = {"count": 40, "query": Config.UNSPLASH_DEFAULT_QUERY}

    # Fetch data from Unsplash API
    data = fetch_api_data(Config.UNSPLASH_RANDOM_URL,
                          params=params, headers=headers)

    # Extract and format image data
    images = [
        {"id": generate_hash(img["urls"]["regular"]),
         "url": img["urls"]["regular"]}
        for img in data if "urls" in img and "regular" in img["urls"]
    ] if data else []

    return render_template("index.html", images=images)

# _________________________________________________________________________#
#                              LOGIN/REGISTER                              #
# _________________________________________________________________________#


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Register a new user.
    Validates inputs, hashes passwords, and stores them in the database.
    """
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm-password")

        # Validate required fields
        if not username or not password:
            flash("Both username and password are required.", "error")
            return redirect(url_for("register"))

        # Check if the user already exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "error")
            return redirect(url_for("register"))

        # Validate password confirmation
        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for("register"))

        # Create a new user with hashed password
        new_user = User(username=username)
        new_user.set_password(password)

        # Add user to database
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred during registration. \
                  Please try again.", "error")
            print(f"Error: {e}")
            return redirect(url_for("register"))

    return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Log in an existing user.
    Validates credentials and stores the session.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Validate user existence
        user = User.query.filter_by(username=username).first()
        if not user:
            flash('User does not exist.', 'danger')
            return redirect(url_for('login'))

        # Validate password
        if not user.check_password(password):
            flash('Invalid password.', 'danger')
            return redirect(url_for('login'))

        # Store user in session
        session['user_id'] = user.id
        flash('Successfully logged in.', 'success')
        return redirect(url_for('index'))

    return render_template('login.html')


@app.route("/logout", methods=["GET"])
def logout():
    """
    Log out the current user.
    Clears the session and redirects to the homepage.
    """
    session.clear()
    flash("You have been logged out.", 'success')
    return redirect(url_for("index"))

# _________________________________________________________________________#
#                              CATEGORIES                                  #
# _________________________________________________________________________#


@app.route("/photos", methods=["GET"])
def photos():
    """
    Display photos from Unsplash based on category and query.
    Fetches photos from the Unsplash API and renders them in the template.
    """
    category = request.args.get('category', 'interior')
    query = request.args.get('query', '')

    headers = {"Authorization": f"Client-ID {Config.UNSPLASH_API_KEY}"}
    params = {"query": f"{category} {query}", "per_page": 20}

    data = fetch_api_data(Config.UNSPLASH_API_URL,
                          params=params, headers=headers)

    if not data or not data.get("results"):
        flash("No photos found for your query.", "warning")
        return render_template('photos.html', images=[], category=category)

    images = [
        {
            "id": generate_hash(img["urls"]["regular"]),
            "url": img["urls"]["regular"],
        }
        for img in data.get("results", [])
        if "urls" in img and "regular" in img["urls"]
    ] if data else []

    return render_template('photos.html', images=images, category=category)


@app.route('/art', methods=['GET'])
def art():
    """
    Display artworks from the Rijksmuseum API.
    Allows querying and paginated display of art data.
    """
    query = request.args.get('query', '')
    page = request.args.get('page', 1)

    params = {
        "key": Config.RIJKSMUSEUM_API_KEY,
        "q": query,
        "ps": 20,
        "imgonly": True,
        "p": page
    }

    data = fetch_api_data(Config.RIJKSMUSEUM_API_URL, params=params)

    if not data or not data.get("artObjects"):
        flash("No artworks found for your query.", "warning")
        return render_template(
            'art.html',
            artworks=[],
            query=query,
            page=int(page)
        )

    artworks = [
        {
            "id": generate_hash(item.get("webImage", {}).get("url", "")),
            "title": item.get("title", "Untitled"),
            "artist": item.get("principalOrFirstMaker", "Unknown"),
            "image_url": item.get("webImage", {}).get("url"),
            "info_url": item.get("links", {}).get("web", "#")
        }
        for item in data.get("artObjects", []) if item.get("webImage")
    ] if data else []

    return render_template(
        'art.html',
        artworks=artworks,
        query=query,
        page=int(page)
    )


@app.route('/recipes', methods=['GET'])
def recipes():
    query = request.args.get('query', 'pastries')

    params = {
        "q": query,
        "app_id": Config.EDAMAM_APP_ID,
        "app_key": Config.EDAMAM_APP_KEY,
        "to": 8
    }

    data = fetch_api_data(Config.EDAMAM_API_URL, params=params)
    print("DEBUG: Recipe Data:", data)

    if not data or not data.get("hits"):
        flash("No recipes found for your query.", "warning")
        return render_template('recipes.html', recipes=[], query=query)

    recipes = [
        {
            "title": hit["recipe"]["label"],  # Converteer label naar title
            "url": hit["recipe"].get("url", ""),
            "image": hit["recipe"].get("image", ""),
            "description": hit["recipe"].get("source",
                                             "No description available"),
        }
        for hit in data.get("hits", [])
    ]

    return render_template('recipes.html', recipes=recipes, query=query)


# _________________________________________________________________________#
#                              SAVE/DELETE ITEMS                           #
# _________________________________________________________________________#

@app.route('/save/<item_type>', methods=["POST"])
@login_required
def save_item(item_type):
    """
    Save an item (photo, art, or recipe) to the user's favorites.
    Determines the item type and processes it accordingly.
    """
    # Retrieve the current user's ID from the session
    user_id = session["user_id"]

    # Retrieve form data from the POST request
    data = request.form

    # Process the item based on its type
    if item_type == "photo":
        process_photo(data, user_id)
    elif item_type == "art":
        process_art(data, user_id)
    elif item_type == "recipe":
        process_recipe(data, user_id)
    else:
        # Handle invalid item types gracefully
        flash("Invalid item type.", "error")

    # Redirect the user back to the referring page
    return redirect(request.referrer)


@app.route('/delete/<item_type>', methods=["POST"])
@login_required
def delete_item(item_type):
    """
    Delete an item (photo, art, or recipe) from the user's favorites.
    Determines the item type and deletes it accordingly.
    """
    user_id = session["user_id"]
    item_id = request.form.get("item_id")

    # Use a helper function to delete the item based on its type
    delete_item_helper(item_type, user_id, item_id)

    # Redirect the user back to the referring page
    return redirect(request.referrer)

# _________________________________________________________________________#
#                              FAVORITES PAGE                              #
# _________________________________________________________________________#


@app.route('/favorites_photos', methods=['GET'])
@login_required
def favorites_photos():
    """
    Display a user's favorite photos.
    Fetches saved photos from the database and displays them.
    """
    saved_images = fetch_user_favorites(SavedImage, session["user_id"])
    return render_template('favorites_photos.html', saved_images=saved_images)


@app.route('/favorites_art', methods=['GET'])
@login_required
def favorites_art():
    """
    Display a user's favorite artworks.
    Fetches saved artworks from the database and displays them.
    """
    saved_artworks = fetch_user_favorites(SavedArt, session["user_id"])
    return render_template('favorites_art.html', saved_artworks=saved_artworks)


@app.route('/favorites_recipes', methods=['GET'])
@login_required
def favorites_recipes():
    """
    Display a user's favorite recipes.
    Fetches saved recipes from the database and displays them.
    """
    saved_recipes = fetch_user_favorites(SavedRecipe, session["user_id"])
    return render_template(
        'favorites_recipes.html',
        saved_recipes=saved_recipes
    )

# _________________________________________________________________________#
#                              DOODLES PAGE                                #
# _________________________________________________________________________#


@app.route("/doodles", defaults={"date": None}, methods=["GET", "POST"])
@app.route("/doodles/<date>", methods=["GET", "POST"])
@login_required
def doodles(date):
    if date:
        try:
            selected_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", "error")
            return redirect(url_for("doodles"))
    else:
        selected_date = datetime.now().date()

    # Fetching data
    todays_doodles = fetch_doodles_by_date(selected_date)
    submissions = fetch_doodle_submissions_and_likes(selected_date)
    total_likes, most_liked_doodles = calculate_doodle_statistics(submissions)
    user_likes = fetch_user_likes(session['user_id'])
    all_dates = fetch_all_doodle_dates()

    # Generate a new doodle for today if it doesn't exist
    if not todays_doodles and selected_date == datetime.now().date():
        filename = generate_daily_scribble()
        new_doodle = Doodle(filename=filename, date=selected_date)
        db.session.add(new_doodle)
        db.session.commit()
        todays_doodles.append(new_doodle)

    return render_template(
        "doodles.html",
        today=selected_date.strftime("%Y-%m-%d"),
        todays_doodles=todays_doodles,
        submissions=submissions,
        total_likes=total_likes,
        most_liked_doodles=most_liked_doodles,
        user_likes={like.doodle_id for like in user_likes},
        all_dates=all_dates
    )


@app.route("/upload_doodle", methods=["POST"])
@login_required
def upload_doodle():
    """
    Allow a user to upload a custom doodle for today's Doodle of the Day.
    Saves the uploaded file and associates it with today's doodle.
    """
    # Retrieve the uploaded file from the request
    file = request.files.get("uploaded_doodle")
    if file:
        # Define the folder to store user-uploaded doodles
        upload_folder = "static/doodles_user"

        # Save the uploaded file and get its filename
        filename, _ = save_uploaded_file(file, upload_folder)

        # Get today's Doodle of the Day from the database
        todays_doodle = get_todays_doodle()
        if not todays_doodle:
            # If no Doodle of the Day exists, inform the user
            flash("Doodle of the Day does not exist.\
                   Please try again later.", "error")
            return redirect(url_for("doodles"))

        # Add the user's doodle submission to the database
        add_user_doodle(
            user_id=session["user_id"],
            doodle_id=todays_doodle.id,
            filename=filename
        )

        flash("Your doodle has been uploaded!", "success")
    else:
        flash("No file selected!", "error")

    return redirect(url_for("doodles"))


@app.route('/like_doodle/<int:doodle_id>', methods=["POST"])
@login_required
def like_doodle(doodle_id):
    """
    Like or unlike a doodle.
    Toggles the like state for the given doodle ID for the logged-in user.
    """
    user_id = session['user_id']

    # Check if the user already liked this doodle
    existing_like = Like.query.filter_by(user_id=user_id,
                                         doodle_id=doodle_id).first()

    if existing_like:
        # Remove the like if it already exists
        db.session.delete(existing_like)
        flash("Like removed!", "success")
    else:
        # Add a new like if none exists
        new_like = Like(user_id=user_id, doodle_id=doodle_id)
        db.session.add(new_like)
        flash("Doodle liked!", "success")

    db.session.commit()

    # Redirect the user back to the previous page
    return redirect(request.referrer)

# _________________________________________________________________________#
#                              API TOKEN                                   #
# _________________________________________________________________________#


@app.route("/api/doodles/filter", methods=["GET"])
def filter_doodles():
    """
    API endpoint to filter doodles by date.
    Returns a JSON response with metadata for doodles on the specified date,
    or all doodles if no date is provided.
    """
    date = request.args.get("date")

    if date:
        # Query the database for doodles matching the specified date
        doodles = Doodle.query.filter(Doodle.date == date).all()
    else:
        # If no date is specified, fetch all doodles from the database
        doodles = Doodle.query.all()

    # Create a list of doodle metadata to include in the API response
    doodle_list = [{
        "id": doodle.id,
        "filename": doodle.filename,
        "likes": doodle.likes,
        "date": doodle.date.strftime('%Y-%m-%d')
    } for doodle in doodles]

    # Return a JSON response with the status and the list of doodles
    return jsonify({"status": "success", "data": doodle_list})


if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)
