from flask import Flask, render_template, request, jsonify, url_for, flash, session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from login import login_bp
from signup import signup_bp
import secrets

SECRET_KEY = secrets.token_hex(16)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:BookClub123@localhost/HealthCaseApp'
app.config['SECRET_KEY'] = SECRET_KEY
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

app.register_blueprint(login_bp)
app.register_blueprint(signup_bp)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('login.login'))
    return render_template('dashboard.html')

if __name__ == '__main__':
    with app.app_context():  
        db.create_all()
    app.run(debug=True)
    app.run(debug=True)
