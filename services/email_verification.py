from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from app import mail  # Import the initialized mail instance

SECRET_KEY="secret"
SECURITY_PASSWORD_SALT="salt"

# Generate a verification token for email
def generate_verification_token(email):
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    return serializer.dumps(email, salt=SECURITY_PASSWORD_SALT)

# Send email verification link
def send_verification_email(email, token):
    verification_link = str(f"https://ecommerceapi-production-48c7.up.railway.app/api/auth/verify/{token}")
    msg = Message(
        subject="Email Verification",
        recipients=[email],
        body=f"Click the link to verify your email: {verification_link}",
    )
    mail.send(msg)

# Verify the token
def verify_verification_token(token, expiration=3600):  # 1-hour expiration
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    try:
        email = serializer.loads(token, salt=SECURITY_PASSWORD_SALT, max_age=expiration)
        return email
    except Exception:
        return None