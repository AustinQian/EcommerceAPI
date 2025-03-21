from models import db

class CartProduct(db.Model):
    __tablename__ = 'cart_product'
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), primary_key=True)
    quantity = db.Column(db.Integer, default=1)

    # Relationship to access product details directly
    product = db.relationship("Product", backref="cart_associations")
