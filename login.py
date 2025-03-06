from flask import Flask, render_template, request, redirect, url_for
from flask import Blueprint

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['GET'])
def login():
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login - Healthcare App</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Manuale:wght@700&display=swap');
            body {{
                margin: 0;
                font-family: Arial, sans-serif;
                background-color: #d5ecfc;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }}
            .login-container {{
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
                width: 100%;
                max-width: 400px;
            }}
            .login-title {{
                color: #002147;
                font-size: 28px;
                font-weight: bold;
                text-align: center;
                margin-bottom: 30px;
                font-family: 'Manuale', serif;
            }}
            .input-group {{
                margin-bottom: 20px;
            }}
            .input-group label {{
                display: block;
                margin-bottom: 8px;
                color: #002147;
                font-weight: bold;
            }}
            .input-group input {{
                width: 100%;
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 6px;
                font-size: 16px;
                box-sizing: border-box;
                transition: border-color 0.3s;
            }}
            .input-group input:focus {{
                border-color: #002147;
                outline: none;
            }}
            .login-btn {{
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
            }}
            .login-btn:hover {{
                background-color: #003166;
            }}
            .signup-link {{
                text-align: center;
                margin-top: 20px;
            }}
            .signup-link a {{
                color: #002147;
                text-decoration: none;
                font-weight: bold;
            }}
            .signup-link a:hover {{
                text-decoration: underline;
            }}
            .back-btn {{
                position: absolute;
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
        <div class="login-container">
            <h1 class="login-title">Login to Healthcare App</h1>
            <form action="/login" method="POST">
                <div class="input-group">
                    <label for="email">Email</label>
                    <input type="email" id="email" name="email" required>
                </div>
                <div class="input-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit" class="login-btn">Login</button>
            </form>
            <div class="signup-link">
                Don't have an account? <a href="/signup">Sign up</a>
            </div>
        </div>
    </body>
    </html>
    '''

@login_bp.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    # Add your login logic here
    return redirect(url_for('index'))