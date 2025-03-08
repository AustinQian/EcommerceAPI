from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models so Flask-Migrate detects them
from models.user import User
from models.product import Product
from models.order import Order
from models.cart import Cart
from models.order_item import OrderItem
from models.review import Review
from models.category import Category
