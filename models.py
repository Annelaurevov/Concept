from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    # Relationships
    saved_images = db.relationship('SavedImage', backref='user', lazy=True)
    saved_art = db.relationship('SavedArt', backref='user', lazy=True)
    saved_recipes = db.relationship('SavedRecipe', backref='user', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy=True)
    doodle_comments = db.relationship('DoodleComment', backref='user', lazy=True)

    def set_password(self, password):
        """Hash the password and save it using a compatible method."""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """Check if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    item_type = db.Column(db.String, nullable=False)  # 'photo', 'recipe', or 'art'
    item_id = db.Column(db.String, nullable=False)  # The ID of the specific item
    text = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class SavedImage(db.Model):
    __tablename__ = "saved_images"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image_id = db.Column(db.String, nullable=False)
    url = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    likes = db.Column(db.Integer, default=0)  # Likes column added

class SavedArt(db.Model):
    __tablename__ = "saved_art"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String, nullable=False)
    artist = db.Column(db.String, nullable=True)
    info_url = db.Column(db.String, nullable=False)
    likes = db.Column(db.Integer, default=0) 
    image_url = db.Column(db.String, nullable=True) 

class SavedRecipe(db.Model):
    __tablename__ = "saved_recipes"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipe_id = db.Column(db.String, nullable=False)
    label = db.Column(db.String, nullable=False)
    url = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    recipe_image = db.Column(db.String(10000), nullable=True)
    likes = db.Column(db.Integer, default=0)  

class Doodle(db.Model):
    __tablename__ = "doodles"
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String, nullable=False)
    likes = db.Column(db.Integer, default=0)
    date = db.Column(db.Date, nullable=False)
    comments = db.relationship('DoodleComment', backref='doodle', lazy=True)
    submissions = db.relationship("UserDoodle", backref="doodle", lazy=True)

class UserDoodle(db.Model):
    __tablename__ = "user_doodles"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doodle_id = db.Column(db.Integer, db.ForeignKey("doodles.id"), nullable=False)
    filename = db.Column(db.String, nullable=False)
    likes = db.Column(db.Integer, default=0)

    user = db.relationship('User', backref='user_doodles', lazy=True)

class DoodleComment(db.Model):
    __tablename__ = "doodle_comments"
    id = db.Column(db.Integer, primary_key=True)
    doodle_id = db.Column(db.Integer, db.ForeignKey("doodles.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    text = db.Column(db.String, nullable=False)

class Like(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doodle_id = db.Column(db.Integer, db.ForeignKey('user_doodles.id'), nullable=False)
    unique_constraint = db.UniqueConstraint('user_id', 'doodle_id', name='unique_user_like')
