from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from typing import Dict, List, Any
from models.product import Product  # Import product model
from models.category import Category  # Import category model
from models.order import Order  # Import order model (for best sellers)
from models.order_item import OrderItem  # Import order model (for best sellers)
from models.user import User  # If you want personalized recommendations
from models import db  # Database instance
from sqlalchemy.exc import SQLAlchemyError

home_bp = Blueprint("home", __name__)

def serialize_product(product: Product) -> Dict[str, Any]:
    """Serialize a product object to a dictionary."""
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "stock": product.stock,
        "image_url": product.image_url,
        "seller_id": product.seller_id,
        "category_id": product.category_id,
        "created_at": product.created_at.isoformat() if product.created_at else None
    }

def serialize_category(category: Category) -> Dict[str, Any]:
    """Serialize a category object to a dictionary."""
    return {
        "id": category.id,
        "name": category.name,
        "description": category.description
    }

@home_bp.route("/latest", methods=["GET"])
def homepage() -> tuple[Dict[str, Any], int]:
    """
    Get featured products, categories, and best sellers for the homepage.
    
    Returns:
        tuple: (JSON response, HTTP status code)
    """
    try:
        featured_products = Product.query.order_by(Product.created_at.desc()).limit(5).all()
        categories = Category.query.limit(5).all()
        
        # Optimized best sellers query with proper joins
        best_sellers = (
            db.session.query(Product)
            .join(OrderItem, OrderItem.product_id == Product.id)
            .join(Order, OrderItem.order_id == Order.id)
            .filter(Order.status == 'completed')  # Only count completed orders
            .group_by(Product.id)
            .order_by(db.func.count(OrderItem.id).desc())
            .limit(5)
            .all()
        )

        response = {
            "featured_products": [serialize_product(product) for product in featured_products],
            "categories": [serialize_category(category) for category in categories],
            "best_sellers": [serialize_product(product) for product in best_sellers],
        }

        return jsonify(response), 200
    except SQLAlchemyError as e:
        return jsonify({"error": "Database error occurred"}), 500

@home_bp.route('', methods=["GET"])
def all_products():
    try:
        # Get category filter from query parameters
        category_id = request.args.get('category', type=int)
        
        # Base query
        query = Product.query
        
        # Apply category filter if provided
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        products = query.all()
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
                "category_name": product.category.name if product.category else None,
                "created_at": product.created_at.isoformat() if product.created_at else None,
                "uniqueLink": product.uniqueLink
            })
        return jsonify(product_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to retrieve all categories
@home_bp.route("/categories", methods=["GET"])
def get_categories() -> tuple[Dict[str, Any], int]:
    """
    Get all categories.
    
    Returns:
        tuple: (JSON response, HTTP status code)
    """
    try:
        categories = Category.query.all()
        return jsonify([serialize_category(category) for category in categories]), 200
    except SQLAlchemyError as e:
        return jsonify({"error": "Database error occurred"}), 500

@home_bp.route("/daily", methods=["POST"])
def daily_login() -> tuple[Dict[str, Any], int]:
    """
    Record a daily login and calculate rewards.
    
    Request Body:
        user_id (int): The ID of the user logging in
    
    Returns:
        tuple: (JSON response, HTTP status code)
    """
    try:
        data = request.get_json()
        if not data or 'user_id' not in data:
            return jsonify({"error": "Missing user_id in request body"}), 400
            
        user_id = data.get("user_id")
        if not isinstance(user_id, int):
            return jsonify({"error": "user_id must be an integer"}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Initialize login_streak to 0 if it's NULL
        if user.login_streak is None:
            user.login_streak = 0

        current_date = datetime.utcnow()
        last_login_date = user.last_login_date

        # Check if user already logged in today
        if last_login_date and last_login_date.date() == current_date.date():
            return jsonify({"error": "Already logged in today"}), 400

        # Update streak
        if last_login_date and (current_date - last_login_date) <= timedelta(days=1):
            user.login_streak += 1
        else:
            user.login_streak = 1

        user.last_login_date = current_date
        reward = calculate_reward(user.login_streak)
        
        db.session.commit()

        return jsonify({
            "message": "Daily login recorded",
            "streak": user.login_streak,
            "reward": reward
        }), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

def calculate_reward(streak: int) -> int:
    """
    Calculate reward based on login streak.
    
    Args:
        streak (int): Current login streak
        
    Returns:
        int: Reward amount
    """
    if streak < 3:
        return 10
    elif streak < 7:
        return 50
    else:
        return 100

@home_bp.route("/product/<int:product_id>", methods=["GET"])
def get_product_details(product_id):
    """
    Get detailed information about a specific product.
    
    Args:
        product_id (int): The ID of the product to retrieve
        
    Returns:
        JSON response with product details
    """
    try:
        product = Product.query.get_or_404(product_id)
        
        return jsonify({
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "stock": product.stock,
            "image_url": product.image_url,
            "seller_id": product.seller_id,
            "category_id": product.category_id,
            "category_name": product.category.name if product.category else None,
            "created_at": product.created_at.isoformat() if product.created_at else None,
            "seller_name": product.seller.username if product.seller else None,
            "average_rating": product.average_rating if hasattr(product, 'average_rating') else None,
            "review_count": product.review_count if hasattr(product, 'review_count') else 0,
            "uniqueLink": product.uniqueLink
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# GET /search - Search for products
@home_bp.route('/search', methods=['GET'])
def search_products():
    try:
        # Get search parameters
        query = request.args.get('q', '').strip()
        category = request.args.get('category', type=int)
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)

        # Build the base query
        base_query = Product.query

        # Apply search filters
        if query:
            # Search in product name and description
            base_query = base_query.filter(
                db.or_(
                    Product.name.ilike(f'%{query}%'),
                    Product.description.ilike(f'%{query}%')
                )
            )

        if category:
            base_query = base_query.filter(Product.category_id == category)

        if min_price is not None:
            base_query = base_query.filter(Product.price >= min_price)

        if max_price is not None:
            base_query = base_query.filter(Product.price <= max_price)

        # Get all matching products
        products = base_query.all()

        # Format the response
        results = []
        for product in products:
            results.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': product.price,
                'stock': product.stock,
                'image_url': product.image_url,
                'category_id': product.category_id,
                'category_name': product.category.name if product.category else None,
                'created_at': product.created_at.isoformat() if product.created_at else None
            })

        return jsonify(results), 200

    except Exception as e:
        print(f"Error in search_products: {str(e)}")
        return jsonify({
            'error': 'Failed to search products',
            'message': str(e)
        }), 500


