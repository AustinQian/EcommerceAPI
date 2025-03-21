from models import db
from .cart_product import CartProduct

class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('_user.id'), nullable=False)

    # Use an association relationship to CartProduct objects
    items = db.relationship("CartProduct", backref="cart", lazy=True)

    # Associate the cart with its owner via a distinct backref name.
    user = db.relationship("User", backref="carts")
