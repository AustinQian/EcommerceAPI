from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models.cart import Cart
from models.product import Product
from models.relation import cart_product
from models import db

cart_bp = Blueprint('cart_bp', __name__, url_prefix='/cart')

COUPONS = {
    "P1Q8": {
        "discount_percentage": 15,  # 15% discount
        "is_expired": False,
        "is_used": False
    },
    "ASCX": {
        "discount_percentage": 10,  # 10% discount
        "is_expired": True,        # Example of an expired coupon
        "is_used": False
    }
}


# GET /cart - Retrieve the current user's cart items
@cart_bp.route('', methods=['GET'])
@login_required
def get_cart():
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart:
        return jsonify([]), 200
    
    cart_items = db.session.query(cart_product).filter_by(cart_id=cart.id).all()
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
    print("Requested data", data)
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    # Ensure the product exists and check stock availability if needed
    product = Product.query.get_or_404(product_id)
    if product.stock < quantity:
        return jsonify({'error': 'Not enough stock available'}), 400

    # Check if the product is already in the user's cart
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.commit()

    # Check if the product is already in the cart
    association = db.session.query(cart_product).filter_by(
        cart_id=cart.id, product_id=product_id
    ).first()
    if association:
        # Update quantity if the product is already in the cart
        association.quantity += quantity
    else:
        # Add the product to the cart
        db.session.execute(cart_product.insert().values(
            cart_id=cart.id, product_id=product_id, quantity=quantity
        ))
    db.session.commit()
    
    return jsonify({'message': 'Product added to cart successfully'}), 200

# DELETE /cart/<cart_id> - Remove an item from the cart
@cart_bp.route('/<int:cart_id>/products/<int:product_id>', methods=['DELETE'])
@login_required
def remove_from_cart(cart_id, product_id):
    # Ensure the cart belongs to the current user
    cart = Cart.query.filter_by(id=cart_id, user_id=current_user.id).first_or_404()

    db.session.execute(cart_product.delete().where(
        (cart_product.c.cart_id == cart_id) & (cart_product.c.product_id == product_id)
    ))
    db.session.commit()
    return jsonify({'message': 'Item removed from cart'}), 200

# POST /cart/checkout - Checkout all items in the cart
@cart_bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    # Retrieve optional credits to apply from request body
    data = request.get_json() or {}
    credits_to_apply = float(data.get('credits_to_apply', 0.0))
    
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart:
        return jsonify({'message': 'Cart is empty'}), 400
    
    cart_items = db.session.query(cart_product).filter_by(cart_id=cart.id).all()
    if not cart_items:
        return jsonify({'message': 'Cart is empty'}), 400

    total_price = 0
    for item in cart_items:
        product = Product.query.get(item.product_id)
        total_price += product.price * item.quantity

    if credits_to_apply > 0:
        # Validate that the user has enough credits
        if current_user.credits < credits_to_apply:
            return jsonify({'error': 'Not enough credits'}), 400
        
        # Apply only as much credits as the total price (avoid negative totals)
        applicable_credits = min(credits_to_apply, total_price)
        total_price -= applicable_credits
        current_user.credits -= applicable_credits

    for item in cart_items:
        product = Product.query.get(item.product_id)
        if product.stock < item.quantity:
            return jsonify({
                'error': f'Not enough stock for {product.name}. Available: {product.stock}'
            }), 400

    for item in cart_items:
        product = Product.query.get(item.product_id)
        product.stock -= item.quantity
        db.session.execute(cart_product.delete().where(
            (cart_product.c.cart_id == cart.id) & (cart_product.c.product_id == item.product_id)
        ))

    credits_earned = current_user.award_credits(total_price)

    db.session.commit()

    return jsonify({
        'message': 'Checkout successful',
        'final_total': total_price,
        'credits_earned': credits_earned,
        'remaining_credits': current_user.credits
    }), 200


@cart_bp.route('/apply-coupon', methods=['POST'])
@login_required
def apply_coupon():
    # Validates a coupon code and applies a discount to the user's cart total.
    data = request.get_json()
    coupon_code = data.get('coupon_code')

    # 1) Validate coupon code input
    if not coupon_code or coupon_code not in COUPONS:
        return jsonify({"error": "Invalid coupon code"}), 400

    coupon_info = COUPONS[coupon_code]

    # 2) Check if coupon is expired or already used
    if coupon_info["is_expired"]:
        return jsonify({"error": "This coupon is expired"}), 400
    if coupon_info["is_used"]:
        return jsonify({"error": "This coupon has already been used"}), 400

    # 3) Calculate the user's cart total
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart:
        return jsonify({"error": "Cart is empty"}), 400
    
    cart_items = db.session.query(cart_product).filter_by(cart_id=cart.id).all()
    if not cart_items:
        return jsonify({"error": "Cart is empty"}), 400

    total_price = 0
    for item in cart_items:
        product = Product.query.get(item.product_id)
        total_price += product.price * item.quantity

    # 4) Apply the discount
    discount_percentage = coupon_info["discount_percentage"]
    discount_amount = total_price * (discount_percentage / 100.0)
    new_total = total_price - discount_amount

    # 5) Mark the coupon as used (if you only allow one-time usage)
    coupon_info["is_used"] = True

    # 6) Return the updated total
    return jsonify({
        "message": "Coupon applied successfully",
        "original_total": total_price,
        "discount_percentage": discount_percentage,
        "discount_amount": discount_amount,
        "new_total": new_total
    }), 200
