from flask import Blueprint, jsonify
from models.product import Product  # Import product model
from models.category import Category  # Import category model
from models.order import Order  # Import order model (for best sellers)
from models.order_item import OrderItem  # Import order model (for best sellers)
from models.user import User  # If you want personalized recommendations
from models import db  # Database instance

home_bp = Blueprint("home", __name__)

@home_bp.route("/latest", methods=["GET"])
def homepage():# Fetch featured products (e.g., latest 5 products)
    featured_products = Product.query.order_by(Product.created_at.desc()).limit(5).all()
    
    # Fetch top categories
    categories = Category.query.limit(5).all()
    
    # Fetch best-selling products (products with the most orders)
    #best_sellers = db.session.query(Product).join(Order).group_by(Product.id).order_by(db.func.count(Order.id).desc()).limit(5).all()
    best_sellers = (
    db.session.query(Product)
    .join(OrderItem, OrderItem.product_id == Product.id)  # Join OrderItem to Product
    .join(Order, OrderItem.order_id == Order.id)  # Then join Order
    .group_by(Product.id)
    .order_by(db.func.count(OrderItem.id).desc())  # Count number of times the product was ordered
    .limit(5)
    .all()
)


    # Format response data
    response = {
        "featured_products": [product.to_dict() for product in featured_products],
        "categories": [category.to_dict() for category in categories],
        "best_sellers": [product.to_dict() for product in best_sellers],
    }

    return jsonify(response)

@home_bp.route("/home", methods=["GET"])
def all_products():
    products = Product.query.all()
    product_list = []
    for product in products:
        product_list.append({
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "stock": product.stock,
            "image_url": product.image_url,
            "seller_id": product.seller_id,
            "category_id": product.category_id,
            "created_at": product.created_at.isoformat() if product.created_at else None
        })
    return jsonify(product_list), 200


