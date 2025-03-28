from datetime import datetime
from models import db
from .cart_product import CartProduct

class Cart(db.Model):
    __tablename__ = 'cart'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('_user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    checked = db.Column(db.Boolean, default=False)  # New column for checked status
    
    # Relationships
    user = db.relationship('User', backref=db.backref('cart', uselist=False))
    
    # Association relationship to CartProduct objects
    items = db.relationship("CartProduct", backref="cart", lazy=True)
