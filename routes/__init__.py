from flask import Blueprint

# Import all blueprints
from .auth import auth_bp
from .home import home_bp

# List of blueprints for easy import in app.py
blueprints = [auth_bp, home_bp]
