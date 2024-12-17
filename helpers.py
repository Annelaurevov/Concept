import os
import hashlib
import requests
from hashlib import md5
from werkzeug.utils import secure_filename
from sqlalchemy.sql import func
from models import db, Doodle, SavedImage, SavedArt, \
    SavedRecipe, UserDoodle, Like
from flask import session, redirect, url_for, flash
from datetime import datetime
from functools import wraps

# __________________________________________________________________________#
#                           UTILITY FUNCTIONS                               #
# __________________________________________________________________________#


def login_required(f):
    """
    A decorator to ensure a user is logged in before accessing a route.

    Args:
        f (function): The route function to decorate.

    Returns:
        function: The wrapped function that checks login status.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("You must be logged in to access this page.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def generate_hash(value):
    """
    Generate a unique hash for a given value.

    Args:
        value (str): The input value to hash.

    Returns:
        str: A unique hash generated using MD5.
    """
    return hashlib.md5(value.encode()).hexdigest()


def save_uploaded_file(file, upload_folder):
    """
    Save an uploaded file to the specified folder.

    Args:
        file (FileStorage): The uploaded file from the form.
        upload_folder (str): The folder path where the file will be saved.

    Returns:
        tuple: The secure filename and its path.
    """
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)  # Ensure the upload folder exists
    filename = secure_filename(file.filename)  # Sanitize the file name
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)  # Save the file to the upload folder
    return filename, filepath
# __________________________________________________________________________#
#                              API FETCHING                                 #
# __________________________________________________________________________#


def fetch_api_data(api_url, params=None, headers=None):
    """
    Fetch data from an API endpoint using requests.

    Args:
        api_url (str): The API URL.
        params (dict): Query parameters for the API request.
        headers (dict): HTTP headers for the API request.

    Returns:
        dict: The JSON response from the API or None if an error occurs.
    """
    try:
        response = requests.get(api_url, params=params, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad status codes
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching API data: {e}")
        flash("An error occurred while fetching data from the API.", "error")
        return None

# __________________________________________________________________________#
#                         ITEM PROCESSING FUNCTIONS                         #
# __________________________________________________________________________#


def process_photo(data, user_id):
    """
    Process and save a photo item for the user.

    Args:
        data (dict): The form data containing photo information.
        user_id (int): The ID of the user saving the photo.
    """
    image_url = data.get("image_url")
    if not image_url:
        flash("Invalid image URL.", "error")
        return

    # Generate image_id as a unique hash of the image_url
    image_id = md5(image_url.encode()).hexdigest()

    new_image = SavedImage(
        user_id=user_id,
        image_id=image_id,
        url=image_url,
        description=data.get("description", "No description available"),
    )

    try:
        db.session.add(new_image)
        db.session.commit()
        flash("Photo saved successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error saving photo: {e}", "error")


def process_art(data, user_id):
    """
    Process and save an art item for the user.

    Args:
        data (dict): The form data containing art information.
        user_id (int): The ID of the user saving the art.
    """
    new_art = SavedArt(
        user_id=user_id,
        title=data.get("title", "Untitled"),
        artist=data.get("artist", "Unknown"),
        image_url=data.get("image_url"),
        info_url=data.get("info_url", "#")
    )

    try:
        db.session.add(new_art)
        db.session.commit()
        flash("Artwork saved successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error saving art: {e}", "error")


def process_recipe(data, user_id):
    """
    Process and save a recipe item for the user.

    Args:
        data (dict): The form data containing recipe information.
        user_id (int): The ID of the user saving the recipe.
    """
    new_recipe = SavedRecipe(
        user_id=user_id,
        title=data.get("title"),
        url=data.get("url"),
        image=data.get("image"),
        description=data.get("description", "")
    )
    try:
        db.session.add(new_recipe)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f"Error saving recipe: {e}", "error")


def fetch_user_favorites(model, user_id):
    """
    Fetch all favorites of a specific user for a given model.

    Args:
        model (db.Model): The SQLAlchemy model to query.
        user_id (int): The ID of the user whose favorites to fetch.

    Returns:
        list: A list of items from the specified model belonging to the user.
    """
    return model.query.filter_by(user_id=user_id).all()


def delete_item_helper(item_type, user_id, item_id):
    """
    Delete a saved item from the user's favorites.

    Args:
        item_type (str): The type of item to delete
            ("photo", "art", or "recipe").
        user_id (int): The ID of the user deleting the item.
        item_id (str): The ID of the item to delete
            (should be convertible to integer).
    """
    try:
        item_id = int(item_id)  # Ensure item_id is an integer
    except ValueError:
        flash("Invalid item ID format.", "error")
        return

    # Map the item_type to the corresponding model
    if item_type == "photo":
        model = SavedImage
    elif item_type == "art":
        model = SavedArt
    elif item_type == "recipe":
        model = SavedRecipe
    else:
        flash("Invalid item type.", "error")
        return

    # Query and delete the item
    item = model.query.filter_by(id=item_id, user_id=user_id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        flash("Item deleted successfully!", "success")
    else:
        flash("Item not found.", "error")


# __________________________________________________________________________#
#                               DOODLES                                     #
# __________________________________________________________________________#

def fetch_doodles_by_date(selected_date):
    """
    Retrieve all doodles for a specific date from the database.

    Args:
        selected_date (date): The date to filter doodles by.

    Returns:
        list: A list of Doodle objects for the selected date.
    """
    return Doodle.query.filter(Doodle.date == selected_date).all()


def get_todays_doodle():
    """
    Retrieve today's Doodle of the Day from the database.

    Returns:
        Doodle: The Doodle object for today's date, or None if not found.
    """
    today = datetime.now().date()
    return Doodle.query.filter(Doodle.date == today).first()


def add_user_doodle(user_id, doodle_id, filename):
    """
    Add a user's doodle submission to the database.

    Args:
        user_id (int): The ID of the user submitting the doodle.
        doodle_id (int): The ID of the Doodle of the Day.
        filename (str): The filename of the uploaded doodle.
    """
    new_submission = UserDoodle(
        user_id=user_id,
        doodle_id=doodle_id,
        filename=filename,
    )

    try:
        db.session.add(new_submission)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f"Error saving doodle submission: {e}", "error")


def fetch_doodle_submissions_and_likes(selected_date):
    """
    Fetch all user submissions and likes for a specific date's doodles.

    Args:
        selected_date (date): The date to filter doodles by.

    Returns:
        list: A list of UserDoodle objects and their associated Doodle data.
    """
    submissions = (
        db.session.query(UserDoodle, func.count(Like.id).label("like_count"))
        .join(Doodle, Doodle.id == UserDoodle.doodle_id)
        .outerjoin(Like, Like.doodle_id == UserDoodle.id)
        .filter(Doodle.date == selected_date)
        .group_by(UserDoodle.id)
        .all()
    )

    return submissions


def calculate_doodle_statistics(submissions):
    """
    Calculate total likes and identify the most liked doodles.

    Args:
        submissions (list): A list of tuples (UserDoodle, like_count).

    Returns:
        tuple: Total likes and the most liked doodles as a list.
    """
    # Bereken de totale likes uit de like_count van elke tuple
    total_likes = sum([like_count for _, like_count in submissions])

    # Zoek het hoogste aantal likes
    max_likes = max([like_count for _, like_count in submissions], default=0)

    # Vind de meest geliefde doodles
    most_liked_doodles = [
        {"doodle": submission, "like_count": like_count}
        for submission, like_count in submissions
        if like_count == max_likes
    ]

    return total_likes, most_liked_doodles


def fetch_user_likes(user_id):
    """
    Retrieve all doodles liked by a specific user.

    Args:
        user_id (int): The ID of the user.

    Returns:
        list: A list of Like objects associated with the user.
    """
    return Like.query.filter(Like.user_id == user_id).all()


def fetch_all_doodle_dates():
    """
    Retrieve all dates with existing doodles from the database.

    Returns:
        list: A list of unique dates with doodles, formatted as strings.
    """
    return [
        date.strftime("%Y-%m-%d")
        for (date,) in db.session
        .query(Doodle.date)
        .distinct()
        .order_by(Doodle.date.desc())
        .all()
    ]
