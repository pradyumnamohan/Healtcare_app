from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin

# Initialize without app
db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model, UserMixin):
    userid = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    primary_guardian = db.Column(db.String(100), nullable=True)
    primary_guardian_contact = db.Column(db.String(15), nullable=True)
    family_doctor = db.Column(db.String(100), nullable=True)
    family_doctor_contact = db.Column(db.String(15), nullable=True)

    def __repr__(self):
        return f"User('{self.name}', '{self.email}')"