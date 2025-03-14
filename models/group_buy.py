from models import db
from datetime import datetime
import uuid

class GroupBuy(db.Model):
    __tablename__ = 'group_buys'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    discount_percentage = db.Column(db.Float, nullable=False, default=0.0)
    min_participants = db.Column(db.Integer, nullable=False, default=2)
    current_participants = db.Column(db.Integer, default=0)
    unique_link = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relationship to track product (if needed)
    product = db.relationship("Product", backref="group_buys")

    def __init__(self, product_id, discount_percentage, min_participants):
        self.product_id = product_id
        self.discount_percentage = discount_percentage
        self.min_participants = min_participants
        # Generate a unique link for inviting friends (e.g., a UUID-based slug)
        self.unique_link = str(uuid.uuid4())[:8]
