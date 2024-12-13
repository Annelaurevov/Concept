from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        """Hash the password and save it using a compatible method."""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """Check if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)
    
class SavedImage(db.Model):
    __tablename__ = "saved_images"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    image_id = db.Column(db.String, nullable=False)
    url = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)

class SavedRecipe(db.Model):
    __tablename__ = 'saved_recipes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)  # Verwijzing naar de `users` tabel
    recipe_id = db.Column(db.String, nullable=False)  # Unieke ID van het recept
    label = db.Column(db.String, nullable=False)  # Naam van het recept
    url = db.Column(db.String, nullable=False)  # Link naar het recept
    description = db.Column(db.String, nullable=True)  # Optionele beschrijving

class SavedArt(db.Model):
    __tablename__ = 'saved_art'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Correcte verwijzing naar `users`
    title = db.Column(db.String(150), nullable=False)
    artist = db.Column(db.String(100), nullable=True)
    info_url = db.Column(db.String(200), nullable=False)

class Doodle(db.Model):
    __tablename__ = "doodles"
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String, nullable=False)
    likes = db.Column(db.Integer, default=0)
    date = db.Column(db.Date, nullable=False)

class DoodleComment(db.Model):
    __tablename__ = "doodle_comments"
    id = db.Column(db.Integer, primary_key=True)
    doodle_id = db.Column(db.Integer, db.ForeignKey("doodles.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    text = db.Column(db.String, nullable=False)
