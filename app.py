from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# App-instellingen
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Vervang door een veilige, unieke sleutel

# Database-configuratie
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://annelaurevanoverbeeke:<password>@localhost/concept'  # Vervang <password> door je PostgreSQL-wachtwoord
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialiseer de database
db = SQLAlchemy(app)

# Importeer modellen (voorkom circulaire import)
from models import User, Item

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Both username and password are required.', 'error')
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password_hash=hashed_password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'error')
            print(f"Error: {e}")
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Both username and password are required.', 'error')
            return redirect(url_for('login'))

        user = User.query.filter_by(username=username).first()
        if user is None or not check_password_hash(user.password_hash, password):
            flash('Invalid username or password.', 'error')
            return redirect(url_for('login'))

        session['user_id'] = user.id
        flash(f'Welcome, {username}!', 'success')
        return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Initialiseer de database als het script direct wordt uitgevoerd
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
