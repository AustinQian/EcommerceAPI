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
    try:
        print("Received GET request for cart")
        email = request.args.get('email')
        print(f"Email from request: {email}")
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
            
        user = verify_user_email(email)
        if not user:
            return jsonify({'error': 'Invalid email'}), 400
        print(f"User verified: {user.id}")

        cart = Cart.query.filter_by(user_id=user.id).first()
        if not cart:
            print(f"No cart found for user {user.id}")
            return jsonify([]), 200
        print(f"Cart found: {cart.id}")
        
        try:
            cart_items = CartProduct.query.filter_by(cart_id=cart.id).all()
            print(f"Found {len(cart_items)} items in cart")
            
            results = []
            for item in cart_items:
                product = Product.query.get(item.product_id)
                if product:
                    results.append({
                        'cart_id': cart.id,
                        'product_id': product.id,
                        'quantity': item.quantity,
                        'product_name': product.name,  
                        'price': product.price,
                        'image_url': product.image_url,
                        'stock': product.stock
                    })
                else:
                    print(f"Warning: Product {item.product_id} not found for cart item")
            
            return jsonify(results), 200
            
        except Exception as e:
            print(f"Error querying cart items: {str(e)}")
            return jsonify({
                'error': 'Failed to retrieve cart items',
                'message': str(e)
            }), 500
            
    except Exception as e:
        print(f"Unexpected error in get_cart: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve cart',
            'message': str(e)
        }), 500

# POST /cart - Add a product to the cart (or update quantity if already in cart)
@cart_bp.route('', methods=['POST'])
def add_to_cart():
    try:
        # Log incoming request data
        print("Received request data:", request.get_json())
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        # Log parsed data
        print("Parsed request data:", data)
            
        # Validate required fields
        product_id = data.get('product_id')
        if not product_id:
            return jsonify({'error': 'product_id is required'}), 400
            
        quantity = data.get('quantity', 1)
        if not isinstance(quantity, int) or quantity < 1:
            return jsonify({'error': 'quantity must be a positive integer'}), 400
            
        email = data.get('email')
        print(f"Attempting to verify email: {email}")
        user = verify_user_email(email)
        if not user:
            return jsonify({'error': 'Invalid email'}), 400
        print(f"User verified: {user.id}")
        
        # Ensure the product exists and check stock availability
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        print(f"Product found: {product.id}, Stock: {product.stock}")
            
        if product.stock < quantity:
            return jsonify({'error': 'Not enough stock available'}), 400
        
        # Check if the user has a cart
        cart = Cart.query.filter_by(user_id=user.id).first()
        if not cart:
            print(f"Creating new cart for user {user.id}")
            cart = Cart(user_id=user.id)
            db.session.add(cart)
            try:
                db.session.commit()
                print("New cart created successfully")
            except Exception as e:
                print(f"Error creating cart: {str(e)}")
                db.session.rollback()
                return jsonify({'error': 'Failed to create cart', 'message': str(e)}), 500
        
        # Check if the product is already in the cart
        try:
            final_quantity = quantity  # Initialize final quantity
            association = CartProduct.query.filter_by(cart_id=cart.id, product_id=product_id).first()
            if association:
                print(f"Updating existing cart item. Old quantity: {association.quantity}")
                association.quantity += quantity
                final_quantity = association.quantity
                print(f"New quantity: {final_quantity}")
            else:
                print("Adding new product to cart")
                new_assoc = CartProduct(cart_id=cart.id, product_id=product_id, quantity=quantity)
                db.session.add(new_assoc)
            
            # Check if the final quantity exceeds available stock
            if final_quantity > product.stock:
                return jsonify({'error': 'Not enough stock available for the total quantity'}), 400
            
            db.session.commit()
            print("Cart updated successfully")

            return jsonify({
                'message': 'Product added to cart successfully',
                'cart_id': cart.id,
                'product_id': product_id,
                'quantity': final_quantity
            }), 200
            
        except Exception as e:
            print(f"Error updating cart: {str(e)}")
            db.session.rollback()
            return jsonify({
                'error': 'Failed to update cart',
                'message': str(e)
            }), 500
        
    except Exception as e:
        print(f"Unexpected error in add_to_cart: {str(e)}")
        if 'db' in locals():
            db.session.rollback()
        return jsonify({
            'error': 'Failed to add product to cart',
            'message': str(e)
        }), 500

# DELETE /cart/<cart_id>/products/<product_id> - Remove an item from the cart
@cart_bp.route('/<int:cart_id>/products/<int:product_id>', methods=['DELETE'])
def remove_from_cart(cart_id, product_id):
    try:
        print(f"Attempting to remove product {product_id} from cart {cart_id}")
        
        # Get email from query parameters or JSON body
        email = request.args.get('email')
        if not email:
            data = request.get_json()
            if data:
                email = data.get('email')
        
        print(f"Email from request: {email}")
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
            
        user = verify_user_email(email)
        if not user:
            return jsonify({'error': 'Invalid email'}), 400
        print(f"User verified: {user.id}")

        # Ensure the cart belongs to the current user
        cart = Cart.query.filter_by(id=cart_id, user_id=user.id).first()
        if not cart:
            print(f"Cart {cart_id} not found for user {user.id}")
            return jsonify({'error': 'Cart not found'}), 404
        print(f"Cart found: {cart.id}")

        # Check if the product exists in the cart
        cart_product = CartProduct.query.filter_by(cart_id=cart.id, product_id=product_id).first()
        if not cart_product:
            print(f"Product {product_id} not found in cart {cart.id}")
            return jsonify({'error': 'Product not found in cart'}), 404
        print(f"Found product {product_id} in cart")

        try:
            CartProduct.query.filter_by(cart_id=cart.id, product_id=product_id).delete()
            db.session.commit()
            print(f"Successfully removed product {product_id} from cart {cart.id}")
            return jsonify({'message': 'Item removed from cart'}), 200
            
        except Exception as e:
            print(f"Error removing product from cart: {str(e)}")
            db.session.rollback()
            return jsonify({
                'error': 'Failed to remove item from cart',
                'message': str(e)
            }), 500
            
    except Exception as e:
        print(f"Unexpected error in remove_from_cart: {str(e)}")
        if 'db' in locals():
            db.session.rollback()
        return jsonify({
            'error': 'Failed to process request',
            'message': str(e)
        }), 500

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
