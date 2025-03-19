from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models.cart import Cart
from models.product import Product
from models import db

cart_bp = Blueprint('cart_bp', __name__, url_prefix='/cart')

# GET /cart - Retrieve the current user's cart items
@cart_bp.route('', methods=['GET'])
@login_required
def get_cart():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    results = []
    for item in cart_items:
        results.append({
            'cart_id': item.id,
            'product_id': item.product_id,
            'quantity': item.quantity,
            'product_name': item.product.name,
            'price': item.product.price
        })
    return jsonify(results), 200

# POST /cart - Add a product to the cart (or update quantity if already in cart)
@cart_bp.route('', methods=['POST'])
@login_required
def add_to_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    # Ensure the product exists and check stock availability if needed
    product = Product.query.get_or_404(product_id)
    if product.stock < quantity:
        return jsonify({'error': 'Not enough stock available'}), 400

    # Check if the product is already in the user's cart
    cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = Cart(user_id=current_user.id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)
    db.session.commit()
    return jsonify({'message': 'Product added to cart successfully'}), 200

# DELETE /cart/<cart_id> - Remove an item from the cart
@cart_bp.route('/<int:cart_id>', methods=['DELETE'])
@login_required
def remove_from_cart(cart_id):
    cart_item = Cart.query.filter_by(id=cart_id, user_id=current_user.id).first_or_404()
    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'message': 'Item removed from cart'}), 200

# POST /cart/checkout - Checkout all items in the cart
@cart_bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    # Retrieve optional credits to apply from request body
    data = request.get_json() or {}
    credits_to_apply = float(data.get('credits_to_apply', 0.0))
    
    # 1) Retrieve the user's cart items
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        return jsonify({'message': 'Cart is empty'}), 400

    # 2) Calculate total cart cost
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    # 3) (Optional) Apply credits to reduce the total price
    if credits_to_apply > 0:
        # Validate that the user has enough credits
        if current_user.credits < credits_to_apply:
            return jsonify({'error': 'Not enough credits'}), 400
        
        # Apply only as much credits as the total price (avoid negative totals)
        applicable_credits = min(credits_to_apply, total_price)
        total_price -= applicable_credits
        current_user.credits -= applicable_credits

    # 4) Verify stock availability for each product in the cart
    for item in cart_items:
        product = Product.query.get(item.product_id)
        if product.stock < item.quantity:
            return jsonify({
                'error': f'Not enough stock for {product.name}. Available: {product.stock}'
            }), 400

    # 5) Deduct stock and clear the cart
    for item in cart_items:
        product = Product.query.get(item.product_id)
        product.stock -= item.quantity
        db.session.delete(item)

    # 6) Award credits to the user based on the total purchase amount
    credits_earned = current_user.award_credits(total_price)

    db.session.commit()

    return jsonify({
        'message': 'Checkout successful',
        'final_total': total_price,
        'credits_earned': credits_earned,
        'remaining_credits': current_user.credits
    }), 200


