from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
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


@home_bp.route("/daily", methods=["POST"])
def daily_login():
    data = request.get_json()
    user_id = data.get("user_id")
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Initialize login_streak to 0 if it's NULL
    if user.login_streak is None:
        user.login_streak = 0

    # Get the current date and the last login date
    current_date = datetime.utcnow()
    last_login_date = user.last_login_date


    # Check if the user logged in yesterday (to maintain the streak)
    if last_login_date and (current_date - last_login_date) <= timedelta(days=1):
        # User logged in consecutively
        user.login_streak += 1
    else:
        # Streak broken (more than 1 day since last login)
        user.login_streak = 1  # Reset streak to 1

    # Calculate the reward based on the streak
    reward = calculate_reward(user.login_streak)

    # Save changes to the database
    db.session.commit()

    # Return the response with the reward and streak
    return jsonify({
        "message": "Daily login recorded",
        "streak": user.login_streak,
        "reward": reward
    }), 200

def calculate_reward(streak):
    # Define reward logic based on the streak
    if streak < 3:
        return 10  # Small reward for short streaks
    elif streak < 7:
        return 50  # Medium reward for medium streaks
    else:
        return 100  # Large reward for long streaks


