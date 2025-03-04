from flask import Blueprint, request, jsonify, url_for
from models import db
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from models.user import User
from flask_jwt_extended import create_access_token
from app import mail

auth_bp = Blueprint("auth", __name__)

# Secret key serializer
serializer = URLSafeTimedSerializer("asecretkey")

# Send email verification
def send_verification_email(user):
    token = serializer.dumps(user.email, salt="email-confirm")
    confirm_url = url_for("auth.verify_email", token=token, _external=True)
    msg = Message("Confirm Your Email", sender="your_email@gmail.com", recipients=[user.email])
    msg.body = f"Please click the link to verify your email: {confirm_url}"
    mail.send(msg)

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

    send_verification_email(user)

    return jsonify({"message": "User registered. Please check your email to verify your account."}), 201


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
    
    if not user.email.verified:
        return jsonify({"error": "Email not verified. Please check your email."}), 403

    access_token = create_access_token(identity=user.id)
    return jsonify({"access_token": access_token}), 200

# Email verification route
@auth_bp.route("/verify/<token>", methods=["GET"])
def verify_email(token):
    try:
        email = serializer.loads(token, salt="email-confirm", max_age=3600)  # 1-hour expiry
    except:
        return jsonify({"error": "Invalid or expired verification link"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.email_verified:
        return jsonify({"message": "Email already verified"}), 200

    user.email_verified = True
    db.session.commit()
    return jsonify({"message": "Email successfully verified"}), 200