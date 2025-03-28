from flask import Blueprint, request, jsonify
from models.cart import Cart
from models.product import Product
from models.cart_product import CartProduct
from models import db
from models.user import User

cart_bp = Blueprint('cart_bp', __name__)

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

def verify_user_email(email):
    """Helper function to verify user email"""
    if not email:
        return None
    user = User.query.filter_by(email=email).first()
    if not user:
        return None
    return user

# GET /cart - Retrieve the current user's cart items
@cart_bp.route('', methods=['GET'])
def get_cart():
    email = request.args.get('email')
    user = verify_user_email(email)
    if not user:
        return jsonify({'error': 'Invalid email'}), 400

    category = request.args.get('category')
    cart = Cart.query.filter_by(user_id=user.id).first()
    if not cart:
        return jsonify([]), 200
    
    query = CartProduct.query.filter_by(cart_id=cart.id)
    if category:
        query = query.join(Product).filter(Product.category == category)
    
    cart_items = query.all()
    results = []
    for item in cart_items:
        results.append({
            'cart_id': item.cart_id,
            'product_id': item.product_id,
            'quantity': item.quantity,
            'product_name': item.product.name,  
            'price': item.product.price,
            'image_url': item.product.image_url,
            'category': item.product.category,
            'stock': item.product.stock
        })
    return jsonify(results), 200

# POST /cart - Add a product to the cart (or update quantity if already in cart)
@cart_bp.route('', methods=['POST'])
def add_to_cart():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        # Validate required fields
        product_id = data.get('product_id')
        if not product_id:
            return jsonify({'error': 'product_id is required'}), 400
            
        quantity = data.get('quantity', 1)
        if not isinstance(quantity, int) or quantity < 1:
            return jsonify({'error': 'quantity must be a positive integer'}), 400
            
        email = data.get('email')
        user = verify_user_email(email)
        if not user:
            return jsonify({'error': 'Invalid email'}), 400
        
        # Ensure the product exists and check stock availability
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
            
        if product.stock < quantity:
            return jsonify({'error': 'Not enough stock available'}), 400
        
        # Check if the user has a cart
        cart = Cart.query.filter_by(user_id=user.id).first()
        if not cart:
            cart = Cart(user_id=user.id)
            db.session.add(cart)
            db.session.commit()
        
        # Check if the product is already in the cart
        association = CartProduct.query.filter_by(cart_id=cart.id, product_id=product_id).first()
        if association:
            association.quantity += quantity
        else:
            new_assoc = CartProduct(cart_id=cart.id, product_id=product_id, quantity=quantity)
            db.session.add(new_assoc)
        
        db.session.commit()

        return jsonify({
            'message': 'Product added to cart successfully',
            'cart_id': cart.id,
            'product_id': product_id,
            'quantity': quantity
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to add product to cart',
            'message': str(e)
        }), 500

# DELETE /cart/<cart_id> - Remove an item from the cart
@cart_bp.route('/<int:cart_id>/products/<int:product_id>', methods=['DELETE'])
def remove_from_cart(cart_id, product_id):
    email = request.args.get('email')
    user = verify_user_email(email)
    if not user:
        return jsonify({'error': 'Invalid email'}), 400

    # Ensure the cart belongs to the current user
    cart = Cart.query.filter_by(id=cart_id, user_id=user.id).first_or_404()

    CartProduct.query.filter_by(cart_id=cart.id, product_id=product_id).delete()
    db.session.commit()
    return jsonify({'message': 'Item removed from cart'}), 200

# POST /cart/checkout - Checkout all items in the cart
@cart_bp.route('/checkout', methods=['POST'])
def checkout():
    data = request.get_json() or {}
    email = data.get('email')
    user = verify_user_email(email)
    if not user:
        return jsonify({'error': 'Invalid email'}), 400
    
    # Retrieve optional credits to apply from request body
    credits_to_apply = float(data.get('credits_to_apply', 0.0))
    
    cart = Cart.query.filter_by(user_id=user.id).first()
    if not cart:
        return jsonify({'message': 'Cart is empty'}), 400
    
    cart_items = db.session.query(CartProduct).filter_by(cart_id=cart.id).all()
    if not cart_items:
        return jsonify({'message': 'Cart is empty'}), 400

    total_price = 0
    for item in cart_items:
        product = Product.query.get(item.product_id)
        total_price += product.price * item.quantity

    if credits_to_apply > 0:
        # Validate that the user has enough credits
        if user.credits < credits_to_apply:
            return jsonify({'error': 'Not enough credits'}), 400
        
        # Apply only as much credits as the total price (avoid negative totals)
        applicable_credits = min(credits_to_apply, total_price)
        total_price -= applicable_credits
        user.credits -= applicable_credits

    for item in cart_items:
        product = Product.query.get(item.product_id)
        if product.stock < item.quantity:
            return jsonify({
                'error': f'Not enough stock for {product.name}. Available: {product.stock}'
            }), 400

    for item in cart_items:
        product = Product.query.get(item.product_id)
        product.stock -= item.quantity
        # Remove the association via ORM
        CartProduct.query.filter_by(cart_id=cart.id, product_id=item.product_id).delete()

    credits_earned = user.award_credits(total_price)
    
    # Set the checked status to True after successful checkout
    cart.checked = True
    db.session.commit()

    return jsonify({
        'message': 'Checkout successful',
        'final_total': total_price,
        'credits_earned': credits_earned,
        'remaining_credits': user.credits
    }), 200

@cart_bp.route('/apply-coupon', methods=['POST'])
def apply_coupon():
    data = request.get_json()
    email = data.get('email')
    user = verify_user_email(email)
    if not user:
        return jsonify({'error': 'Invalid email'}), 400

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
    cart = Cart.query.filter_by(user_id=user.id).first()
    if not cart:
        return jsonify({"error": "Cart is empty"}), 400
    
    cart_items = db.session.query(CartProduct).filter_by(cart_id=cart.id).all()
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
