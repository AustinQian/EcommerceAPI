from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from models import db
from models.group_buy import GroupBuy
from models.group_buy_participant import GroupBuyParticipant
from models.product import Product
from models.cart import Cart  # if needed to apply discount

group_buy_bp = Blueprint('group_buy_bp', __name__, url_prefix='/groupbuy')

@group_buy_bp.route('', methods=['POST'])
@login_required
def create_group_buy():
    # Create a new group buy for a specific product.
    data = request.get_json()
    product_id = data.get('product_id')
    discount_percentage = data.get('discount_percentage')
    min_participants = data.get('min_participants')

    # Validate input
    if not product_id or discount_percentage is None or not min_participants:
        return jsonify({'error': 'Missing required fields'}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    # Create a new group buy
    group_buy = GroupBuy(
        product_id=product_id,
        discount_percentage=discount_percentage,
        min_participants=min_participants
    )
    db.session.add(group_buy)
    db.session.commit()

    return jsonify({
        'message': 'Group buy created',
        'group_buy_id': group_buy.id,
        'unique_link': group_buy.unique_link
    }), 201

@group_buy_bp.route('/<unique_link>', methods=['GET'])
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

@group_buy_bp.route('/join/<unique_link>', methods=['POST'])
@login_required
def join_group_buy(unique_link):
    # Join a group buy using the unique link.
    group_buy = GroupBuy.query.filter_by(unique_link=unique_link).first()
    if not group_buy:
        return jsonify({'error': 'Group buy not found'}), 404

    if not group_buy.is_active:
        return jsonify({'error': 'Group buy is no longer active'}), 400

    # Check if user already joined
    existing_participant = GroupBuyParticipant.query.filter_by(
        group_buy_id=group_buy.id,
        user_id=current_user.id
    ).first()
    if existing_participant:
        return jsonify({'message': 'You have already joined this group buy'}), 200

    # Add participant
    participant = GroupBuyParticipant(
        group_buy_id=group_buy.id,
        user_id=current_user.id
    )
    db.session.add(participant)
    group_buy.current_participants += 1

    # If we reached min_participants, we can mark group buy as "activated"
    if group_buy.current_participants >= group_buy.min_participants:
        # You can do more logic here, e.g., mark group_buy as "activated"
        # so the discount can be applied.
        pass

    db.session.commit()
    return jsonify({'message': 'Joined group buy successfully'}), 200

@group_buy_bp.route('/apply-discount/<int:cart_id>', methods=['POST'])
@login_required
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

