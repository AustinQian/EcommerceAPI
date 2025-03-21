from models import db
from .product import Product
from .relation import cart_product

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('_user.id'), nullable=False)
    products = db.relationship('Product', secondary=cart_product, backref='carts')
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    user = db.relationship("User", backref="cart_items")
    product = db.relationship("Product", backref="cart_items")
