from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
#from config import Config  # Import your SECRET_KEY from config
from app import mail  # Import the initialized mail instance

# Generate a verification token for email
def generate_verification_token(email):
    SECRET_KEY="secret"
    SECURITY_PASSWORD_SALT="salt"
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    return serializer.dumps(email, salt=SECURITY_PASSWORD_SALT)

# Send email verification link
def send_verification_email(email, token):
    verification_link = str(f"http://127.0.0.1:5000/api/auth/verify/{token}")
    msg = Message(
        subject="Email Verification",
        recipients=[email],
        body=f"Click the link to verify your email: {verification_link}",
    )
    mail.send(msg)

# Verify the token
def verify_verification_token(token, expiration=3600):  # 1-hour expiration
    serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
    try:
        email = serializer.loads(token, salt=Config.SECURITY_PASSWORD_SALT, max_age=expiration)
        return email
    except Exception:
        return None