from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask import current_app

# These will be initialized properly in Front.py
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