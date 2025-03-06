from flask import Blueprint, request, redirect, url_for, render_template, flash, session
from models import User, bcrypt  # Import from central models file

login_bp = Blueprint('login_bp', __name__)

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
        return redirect(url_for('index'))
    else:
        flash('Invalid email or password. Please try again.', 'danger')
        return redirect(url_for('login_bp.login'))