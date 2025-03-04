from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models so Flask-Migrate detects them
from models.user import User