from flask import Blueprint

# Import all blueprints
from .auth import auth_bp
from .cart import cart_bp
from .group_buy import groupbuy_bp
from .home import home_bp
from .product import product_bp

# List of blueprints for easy import in app.py
blueprints = [auth_bp, home_bp, product_bp, cart_bp, groupbuy_bp]
