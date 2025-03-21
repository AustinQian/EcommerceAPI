from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models so Flask-Migrate detects them
from models.cart_product import CartProduct 
from models.cart import Cart
from models.category import Category
from models.group_buy_participant import GroupBuyParticipant
from models.group_buy import GroupBuy
from models.order_item import OrderItem
from models.order import Order
from models.product import Product
from models.review import Review
from models.user import User
