from flask import Blueprint, request, redirect, url_for, render_template, flash
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

signup_bp = Blueprint('signup', __name__)

# Initialize extensions (make sure they're initialized in your main app)
db = SQLAlchemy()
bcrypt = Bcrypt()

# User Model
class User(db.Model):
    userid = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    primary_guardian = db.Column(db.String(255), nullable=False)
    primary_guardian_contact = db.Column(db.String(15), nullable=False)
    family_doctor = db.Column(db.String(255))
    family_doctor_contact = db.Column(db.String(15))
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

# Signup Page Route (GET)
@signup_bp.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html')

# Signup Form Submission (POST)
@signup_bp.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    password = request.form.get('password')
    name = request.form.get('name')
    age = request.form.get('age')
    gender = request.form.get('gender')
    blood_group = request.form.get('blood_group')
    date_of_birth = request.form.get('date_of_birth')
    primary_guardian = request.form.get('primary_guardian')
    primary_guardian_contact = request.form.get('primary_guardian_contact')
    family_doctor = request.form.get('family_doctor')
    family_doctor_contact = request.form.get('family_doctor_contact')

    # Check if email is already registered
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash('Error: Email already registered. Please use another email.', 'danger')
        return redirect(url_for('signup.signup'))

    # Hash the password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Create new user
    new_user = User(
        email=email,
        password=hashed_password,
        name=name,
        age=int(age),
        gender=gender,
        blood_group=blood_group,
        date_of_birth=datetime.strptime(date_of_birth, '%Y-%m-%d'),
        primary_guardian=primary_guardian,
        primary_guardian_contact=primary_guardian_contact,
        family_doctor=family_doctor,
        family_doctor_contact=family_doctor_contact
    )

    # Save to database
    try:
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login.login'))
    except Exception as e:
        db.session.rollback()
        flash('Error: Registration failed. Please try again.', 'danger')
        print(str(e))  # Log error for debugging
        return redirect(url_for('signup.signup'))
