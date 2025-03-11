from flask import Blueprint, request, jsonify
from models import db
from itsdangerous import URLSafeTimedSerializer
from models.user import User
from flask_jwt_extended import create_access_token
from flask_login import login_user
from services.email_verification import generate_verification_token, send_verification_email, verify_verification_token
from services.validation import is_valid_email, is_valid_password
from services import generate_reset_token, send_reset_email, verify_reset_token


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
        return jsonify({"error": "Username already exists"}), 401

    existing_email = User.query.filter_by(email=email).first()
    if existing_email:
        return jsonify({"error": "Email already registered"}), 401

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
    remember_me = data.get("remember", False)
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Email not found"}), 401
    
    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format"}), 401


    if not user.check_password(password):
        return jsonify({"error": "Incorrect password"}), 401
    
    if not user.email_verify:
        return jsonify({"error": "Email not verified. Please check your email."}), 403

    access_token = create_access_token(identity=user.id)
    login_user(user, remember=remember_me)
    return jsonify({"access_token": access_token, "remember: ": remember_me}), 200

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

    # Mark email as verified
    if user.email_verify:
        return jsonify({"message": "Email already verified."}), 200
    
    user.email_verify = True
    db.session.commit()

    return jsonify({"message": "Email successfully verified."}), 200

@auth_bp.route("/reset_request", methods=["POST"])
def request_password_reset():
    data = request.get_json()
    email = data.get("email")

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Email not found"}), 404

    token = generate_reset_token(email)
    send_reset_email(email, token)

    return jsonify({"message": "Password reset link sent to your email"}), 200


@auth_bp.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if request.method == "GET":
        return jsonify({"message": "Token is valid. Redirect to password reset form."})

    if request.method == "POST":
        data = request.get_json()
        new_password = data.get("password")
        confirm_password = data.get("confirm_password")
        
        # Validate token and update password
        email = verify_reset_token(token)
        if not email:
            return jsonify({"error": "Invalid or expired token"}), 400
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        if new_password!=confirm_password:
            return jsonify({"error": "New password does not match confirm password"}), 401
        
        user.set_password(new_password)
        db.session.commit()
        
        return jsonify({"message": "Password reset successful"}), 200

