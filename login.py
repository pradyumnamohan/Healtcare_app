from flask import Blueprint, request, redirect, url_for, render_template, flash, session
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

login_bp = Blueprint('login', __name__)

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()

# User Model (Ensure this matches your database structure)
class User(db.Model):
    userid = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

# Login Page Route (GET)
@login_bp.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

# Login Form Submission (POST)
@login_bp.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')

    # Find user by email
    user = User.query.filter_by(email=email).first()
    
    if user and bcrypt.check_password_hash(user.password, password):
        session['user_id'] = user.userid  # Store user ID in session
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid email or password. Please try again.', 'danger')
        return redirect(url_for('login.login'))

# Logout Route
@login_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login.login'))
