import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://momori:123456@localhost/ecommerce")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "aedcd0bcdc4449c12c09e5b13aef1cf1b343d1315cb33fa0c6a7c6b54181ba25")  # Change in production
