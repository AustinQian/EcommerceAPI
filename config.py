import os



class Config:
    MAIL_USERNAME="ubunteen2@gmail.com"
    MAIL_PASSWORD="vzur kuqv uutx cntn"
    MAIL_DEFAULT_SENDER="ubunteen2@gmail.com"
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://postgres:btVxwAkNCOWGYGueFDnVeIdERgDVJqOc@shinkansen.proxy.rlwy.net:31878/railway")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "aedcd0bcdc4449c12c09e5b13aef1cf1b343d1315cb33fa0c6a7c6b54181ba25")  # Change in production
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_SERVER = "smtp.gmail.com"
    SECRET_KEY = os.getenv("SECRET_KEY", "secret")
    SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT", "salt")
