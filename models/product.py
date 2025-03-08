from models import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = "product"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(255), nullable=True)
    seller_id = db.Column(db.Integer, db.ForeignKey("_user.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    seller = db.relationship("User", backref="products")
    category = db.relationship("Category", backref="product_list")

    def to_dict(self):
        """Convert Product object to dictionary (for JSON responses)"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "stock": self.stock,
            "image_url": self.image_url,
            "seller_id": self.seller_id,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else None, 
            "created_at": self.created_at.isoformat(),
        }
