from flask import Blueprint, request, redirect, url_for, render_template, flash, session, jsonify
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

    user = User.query.filter_by(email=email).first()
    
    if user and bcrypt.check_password_hash(u
                                           
                                           ser.password, password):
        session.permanent = True  # Make session permanent
        #session['user_id'] = user.id
        session['username'] = user.email
        session['logged_in'] = True  # Add this line
        return jsonify({'success': True, 'message': 'Login successful'})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401