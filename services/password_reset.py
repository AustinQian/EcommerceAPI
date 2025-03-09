from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
#from config import Config
from app import mail

SECRET_KEY="secret"
SECURITY_PASSWORD_SALT="salt"

def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    return serializer.dumps(email, salt=SECURITY_PASSWORD_SALT)

def verify_reset_token(token, expiration=3600):  # Token expires in 1 hour
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    try:
        email = serializer.loads(token, salt=SECURITY_PASSWORD_SALT, max_age=expiration)
        return email
    except:
        return None
    
def send_reset_email(email, token):
    reset_link = str(f"http://127.0.0.1:5000/api/auth/reset_password/{token}")
    
    msg = Message(
        subject="Password Reset Request",
        recipients=[email],
        body=f"Click the link to reset your password: {reset_link}"
    )

    mail.send(msg)
