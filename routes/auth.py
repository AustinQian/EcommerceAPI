from flask import Blueprint, request, jsonify
from models import db
from models.user import User
from flask_jwt_extended import create_access_token

auth_bp = Blueprint("auth", __name__)

# User Registration
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    confirm_password = data.get("confirm_password")
    existing_user = User.query.filter_by(username=data['username']).first()

    #Check for existing username
    if existing_user:
        return jsonify({"error": "Username already existed"}), 400
    
    # Check if passwords match
    if password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400

    #Check for missing fiels
    if not username or not email or not password or not confirm_password:
        return jsonify({"error": "All fields are required"}), 400
    
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"error": "Username already exists"}), 400

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

# User Login
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Email not found"}), 401

    if not user.check_password(password):
        return jsonify({"error": "Incorrect password"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({"access_token": access_token}), 200
