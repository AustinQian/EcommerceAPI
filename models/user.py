from models import db
from flask_bcrypt import Bcrypt
from datetime import datetime
from flask_login import UserMixin

bcrypt = Bcrypt()

class User(UserMixin, db.Model):
    __tablename__ = "_user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(10), nullable=False, default="customer")  # "seller" or "customer"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    email_verify = db.Column(db.Boolean, default=False)
    credits = db.Column(db.Float, default=0.0)


    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def award_credits(self, purchase_amount, credit_rate=0.01):
        credits_earned = purchase_amount * credit_rate
        self.credits += credits_earned
        return credits_earned

    
    def __init__(self, email, password, credits=0.0):
        self.email = email
        self.password = password
        self.credits = credits