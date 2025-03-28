from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from models import db
from models.group_buy import GroupBuy
from models.group_buy_participant import GroupBuyParticipant
from models.product import Product
from models.cart import Cart  # if needed to apply discount
from datetime import datetime
import random
import string
import secrets
from flask_jwt_extended import jwt_required, get_jwt_identity

def generate_unique_link():
    """Generate a unique link for the group buy."""
    alphabet = string.ascii_letters + string.digits
    while True:
        link = ''.join(secrets.choice(alphabet) for _ in range(8))
        if not GroupBuy.query.filter_by(unique_link=link).first():
            return link

groupbuy_bp = Blueprint('groupbuy_bp', __name__)

@groupbuy_bp.route('/create', methods=['POST'])
def create_group_buy():
    """Create a new group buy."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # Validate required fields
        required_fields = ['product_id', 'min_participants', 'discount_percentage']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
                
        # Validate values
        if data['min_participants'] < 2:
            return jsonify({'error': 'Minimum participants must be at least 2'}), 400
            
        if not 0 <= data['discount_percentage'] <= 100:
            return jsonify({'error': 'Discount percentage must be between 0 and 100'}), 400
            
        # Check if product exists and has stock
        product = Product.query.get(data['product_id'])
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        if product.stock <= 0:
            return jsonify({'error': 'Product is out of stock'}), 400
            
        # Generate unique link
        unique_link = generate_unique_link()
            
        # Create group buy
        group_buy = GroupBuy(
            product_id=data['product_id'],
            discount_percentage=data['discount_percentage'],
            min_participants=data['min_participants']
        )
        
        # Set the unique link for both group buy and product
        group_buy.unique_link = unique_link
        product.uniqueLink = unique_link
        
        # Set end date if provided
        if 'end_date' in data:
            try:
                group_buy.end_date = datetime.fromisoformat(data['end_date'])
            except ValueError:
                return jsonify({'error': 'Invalid end_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}), 400
        
        db.session.add(group_buy)
        db.session.commit()
        
        return jsonify({
            'message': 'Group buy created successfully',
            'group_buy': {
                'id': group_buy.id,
                'product_id': group_buy.product_id,
                'product_name': product.name,
                'min_participants': group_buy.min_participants,
                'current_participants': 0,
                'discount_percentage': group_buy.discount_percentage,
                'unique_link': unique_link,
                'end_date': group_buy.end_date.isoformat() if group_buy.end_date else None,
                'status': 'active'
            }
        }), 201
        
    except Exception as e:
        print(f"Error creating group buy: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@groupbuy_bp.route('/products', methods=['GET'])
def get_available_products():
    """
    Get list of products available for group buy.
    """
    try:
        # Get all products that are in stock
        products = Product.query.filter(Product.stock > 0).all()
        
        return jsonify([{
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "stock": product.stock,
            "image_url": product.image_url,
            "category": product.category.name if product.category else None
        } for product in products]), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@groupbuy_bp.route('/<unique_link>', methods=['GET'])
def get_group_buy(unique_link):
    # Retrieve details about a specific group buy using the unique link.
    group_buy = GroupBuy.query.filter_by(unique_link=unique_link).first()
    participants = group_buy.get_participant_count()
    if not group_buy:
        return jsonify({'error': 'Group buy not found'}), 404

    return jsonify({
        'id': group_buy.id,
        'product_id': group_buy.product_id,
        'discount_percentage': group_buy.discount_percentage,
        'min_participants': group_buy.min_participants,
        'current_participants': group_buy.current_participants,
        'unique_link': group_buy.unique_link,
        'is_active': group_buy.is_active,
        'participant_count': participants
    }), 200

@groupbuy_bp.route('/join/<unique_link>', methods=['POST'])
def join_group_buy(unique_link):
    """Join a group buy using the unique link."""
    try:
        # Find the group buy
        group_buy = GroupBuy.query.filter_by(unique_link=unique_link).first()
        if not group_buy:
            return jsonify({'error': 'Group buy not found'}), 404

        # Check if group buy is still active
        if not group_buy.is_active:
            return jsonify({'error': 'Group buy is no longer active'}), 400

        # Increment participants
        group_buy.current_participants += 1

        # If we reached min_participants, activate the group buy
        if group_buy.current_participants >= group_buy.min_participants:
            group_buy.is_active = True

        db.session.commit()
        
        return jsonify({
            'message': 'Joined group buy successfully',
            'current_participants': group_buy.current_participants,
            'min_participants': group_buy.min_participants,
            'is_active': group_buy.is_active
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to join group buy: {str(e)}'}), 500

@groupbuy_bp.route('/apply-discount/<int:cart_id>', methods=['POST'])
def apply_group_buy_discount(cart_id):
    # Apply the group-buy discount to the items in the user's cart (if applicable).
    data = request.get_json()
    group_buy_id = data.get('group_buy_id')
    if not group_buy_id:
        return jsonify({'error': 'Missing group_buy_id'}), 400

    group_buy = GroupBuy.query.get(group_buy_id)
    if not group_buy:
        return jsonify({'error': 'Group buy not found'}), 404

    if group_buy.current_participants < group_buy.min_participants:
        return jsonify({'error': 'Not enough participants to activate discount'}), 400

    # Check the user's cart
    cart_item = Cart.query.filter_by(id=cart_id, user_id=current_user.id).first()
    if not cart_item:
        return jsonify({'error': 'Cart item not found or not owned by user'}), 404

    # Verify the cart item is the same product as the group buy product
    if cart_item.product_id != group_buy.product_id:
        return jsonify({'error': 'This cart item does not match the group buy product'}), 400

    # Apply discount
    discount = group_buy.discount_percentage
    # e.g., if discount = 10, reduce the price by 10%
    # (You might store the discounted price or adjust it at checkout.)
    # For demonstration, let's say we have a "discounted_price" field in Cart
    original_price = cart_item.product.price
    new_price = original_price * (1 - discount / 100.0)
    # store or update accordingly
    cart_item.discounted_price = round(new_price, 2)

    db.session.commit()
    return jsonify({
        'message': 'Discount applied to cart item',
        'original_price': original_price,
        'discounted_price': cart_item.discounted_price
    }), 200

