from flask import Blueprint, request, redirect, url_for
from datetime import datetime

signup_bp = Blueprint('signup', __name__)

@signup_bp.route('/signup', methods=['GET'])
def signup():
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sign Up - Healthcare App</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Manuale:wght@700&display=swap');
            body {{
                margin: 0;
                font-family: Arial, sans-serif;
                background-color: #d5ecfc;
                padding: 40px 0;
            }}
            .signup-container {{
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
                width: 90%;
                max-width: 600px;
                margin: 0 auto;
            }}
            .signup-title {{
                color: #002147;
                font-size: 28px;
                font-weight: bold;
                text-align: center;
                margin-bottom: 30px;
                font-family: 'Manuale', serif;
            }}
            .form-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }}
            .input-group {{
                margin-bottom: 20px;
            }}
            .input-group.full-width {{
                grid-column: 1 / -1;
            }}
            .input-group label {{
                display: block;
                margin-bottom: 8px;
                color: #002147;
                font-weight: bold;
            }}
            .input-group input, .input-group select {{
                width: 100%;
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 6px;
                font-size: 16px;
                box-sizing: border-box;
                transition: border-color 0.3s;
            }}
            .input-group input:focus, .input-group select:focus {{
                border-color: #002147;
                outline: none;
            }}
            .signup-btn {{
                background-color: #002147;
                color: white;
                border: none;
                padding: 14px;
                width: 100%;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                transition: background-color 0.3s;
                grid-column: 1 / -1;
            }}
            .signup-btn:hover {{
                background-color: #003166;
            }}
            .login-link {{
                text-align: center;
                margin-top: 20px;
            }}
            .login-link a {{
                color: #002147;
                text-decoration: none;
                font-weight: bold;
            }}
            .login-link a:hover {{
                text-decoration: underline;
            }}
            .back-btn {{
                position: fixed;
                top: 20px;
                left: 20px;
                background: none;
                border: none;
                color: #002147;
                font-size: 16px;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 5px;
            }}
            .back-btn:hover {{
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <button class="back-btn" onclick="window.location.href='/'">
            ← Back to Home
        </button>
        <div class="signup-container">
            <h1 class="signup-title">Create Your Account</h1>
            <form action="/signup" method="POST" class="form-grid">
                <div class="input-group">
                    <label for="email">Email*</label>
                    <input type="email" id="email" name="email" required>
                </div>
                <div class="input-group">
                    <label for="password">Password*</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <div class="input-group">
                    <label for="name">Full Name*</label>
                    <input type="text" id="name" name="name" required>
                </div>
                <div class="input-group">
                    <label for="age">Age*</label>
                    <input type="number" id="age" name="age" min="1" required>
                </div>
                <div class="input-group">
                    <label for="gender">Gender*</label>
                    <select id="gender" name="gender" required>
                        <option value="">Select Gender</option>
                        <option value="Male">Male</option>
                        <option value="Female">Female</option>
                        <option value="Other">Other</option>
                    </select>
                </div>
                <div class="input-group">
                    <label for="blood_group">Blood Group*</label>
                    <select id="blood_group" name="blood_group" required>
                        <option value="">Select Blood Group</option>
                        <option value="A+">A+</option>
                        <option value="A-">A-</option>
                        <option value="B+">B+</option>
                        <option value="B-">B-</option>
                        <option value="O+">O+</option>
                        <option value="O-">O-</option>
                        <option value="AB+">AB+</option>
                        <option value="AB-">AB-</option>
                    </select>
                </div>
                <div class="input-group">
                    <label for="date_of_birth">Date of Birth*</label>
                    <input type="date" id="date_of_birth" name="date_of_birth" required>
                </div>
                <div class="input-group">
                    <label for="primary_guardian">Primary Guardian*</label>
                    <input type="text" id="primary_guardian" name="primary_guardian" required>
                </div>
                <div class="input-group">
                    <label for="primary_guardian_contact">Guardian Contact*</label>
                    <input type="tel" id="primary_guardian_contact" name="primary_guardian_contact" required>
                </div>
                <div class="input-group">
                    <label for="family_doctor">Family Doctor</label>
                    <input type="text" id="family_doctor" name="family_doctor">
                </div>
                <div class="input-group">
                    <label for="family_doctor_contact">Doctor Contact</label>
                    <input type="tel" id="family_doctor_contact" name="family_doctor_contact">
                </div>
                <button type="submit" class="signup-btn">Sign Up</button>
            </form>
            <div class="login-link">
                Already have an account? <a href="/login">Log in</a>
            </div>
        </div>
    </body>
    </html>
    '''

@signup_bp.route('/signup', methods=['POST'])
def signup_post():
    # Get form data
    data = {
        'email': request.form.get('email'),
        'password': request.form.get('password'),
        'name': request.form.get('name'),
        'age': request.form.get('age'),
        'gender': request.form.get('gender'),
        'blood_group': request.form.get('blood_group'),
        'date_of_birth': request.form.get('date_of_birth'),
        'primary_guardian': request.form.get('primary_guardian'),
        'primary_guardian_contact': request.form.get('primary_guardian_contact'),
        'family_doctor': request.form.get('family_doctor'),
        'family_doctor_contact': request.form.get('family_doctor_contact')
    }
    
    # Add your database insertion logic here
    
    return redirect(url_for('index'))