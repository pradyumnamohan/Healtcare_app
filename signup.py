from flask import Blueprint, request, redirect, url_for, render_template
from models import User, db, bcrypt
from datetime import datetime

signup_bp = Blueprint('signup_bp', __name__)

# Update the form action URL in the template
@signup_bp.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html')  # Use the template file instead of inline HTML

@signup_bp.route('/signup', methods=['POST'])
def signup_post():
    # Get form data
    try:
        hashed_password = bcrypt.generate_password_hash(request.form.get('password')).decode('utf-8')
        new_user = User(
            email=request.form.get('email'),
            password=hashed_password,
            name=request.form.get('name'),
            age=int(request.form.get('age')),
            gender=request.form.get('gender'),
            blood_group=request.form.get('blood_group'),
            date_of_birth=datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d'),
            primary_guardian=request.form.get('primary_guardian'),
            primary_guardian_contact=request.form.get('primary_guardian_contact'),
            family_doctor=request.form.get('family_doctor'),
            family_doctor_contact=request.form.get('family_doctor_contact')
        )
        
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login_bp.login'))
    except Exception as e:
        print(f"Error: {str(e)}")
        return redirect(url_for('signup.signup_post'))