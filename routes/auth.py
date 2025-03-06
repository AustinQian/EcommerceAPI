from flask import Blueprint, request, jsonify, url_for
from models import db
from itsdangerous import URLSafeTimedSerializer
from models.user import User
from config import Config
from flask_jwt_extended import create_access_token
from services.email_verification import generate_verification_token, send_verification_email, verify_verification_token
from services.validation import is_valid_email, is_valid_password

auth_bp = Blueprint("auth", __name__)

# Secret key serializer
serializer = URLSafeTimedSerializer("asecretkey")


# User Registration
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    confirm_password = data.get("confirm_password")
    existing_user = User.query.filter_by(username=data['username']).first()

    # Check for existing user
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"error": "Username already exists"}), 400

    existing_email = User.query.filter_by(email=email).first()
    if existing_email:
        return jsonify({"error": "Email already registered"}), 400

    if not username or not email or not password:
        return jsonify({"error": "Missing fields"}), 400
    
    if password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400
    
    # Validate email format
    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format"}), 400

    # Validate password complexity
    if not is_valid_password(password):
        return jsonify({
            "error": "Password must be at least 8 characters long and include a mix of letters, numbers, and symbols."
        }), 400

    user = User(username=username, email=email)
    user.set_password(password)

    # Generate Email Verification Token
    token = generate_verification_token(email)  # Implement token generation

    try:
        # Send Verification Email
        send_verification_email(user.email, token)

        # Only commit the user after email is sent successfully
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User registered successfully. Please verify your email."}), 201

    except Exception as e:
        # Rollback if email sending fails
        db.session.rollback()
        return jsonify({"error": "Failed to send verification email", "details": str(e)}), 500



# User Login
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Email not found"}), 401
    
    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format"}), 401


    if not user.check_password(password):
        return jsonify({"error": "Incorrect password"}), 401
    
    if not user.email_verified:
        return jsonify({"error": "Email not verified. Please check your email."}), 403

    access_token = create_access_token(identity=user.id)
    return jsonify({"access_token": access_token}), 200

# Email verification route
@auth_bp.route("/verify/<token>", methods=["GET"])
def verify_email(token):
    email = verify_verification_token(token)
    if not email:
        return jsonify({"error": "Invalid or expired verification link"}), 400
    
    # Find the user with the email
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # ✅ Mark email as verified
    if user.email_verified:
        return jsonify({"message": "Email already verified."}), 200
    
    user.email_verified = True
    db.session.commit()

    return jsonify({"message": "Email successfully verified."}), 200