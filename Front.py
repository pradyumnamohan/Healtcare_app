from flask import Flask, render_template, request, jsonify, url_for, flash, session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import secrets

# Initialize the Flask app and extensions first
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:BookClub123@localhost/HealthCareApp'
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Import blueprints after initializing db and bcrypt
from login import login_bp
from signup import signup_bp

# Register blueprints
app.register_blueprint(login_bp, url_prefix='/auth')
app.register_blueprint(signup_bp, url_prefix='/auth')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('auth.login'))  # Fixed URL pattern
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))  # Fixed URL pattern

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)