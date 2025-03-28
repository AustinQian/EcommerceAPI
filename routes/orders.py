from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from models.order import Order
from models.order_item import OrderItem
from models import db

orders_bp = Blueprint('orders_bp', __name__, url_prefix='/orders')

@orders_bp.route('', methods=['GET'])
@login_required
def get_user_orders():
    """
    Get all orders for the current user.
    
    Returns:
        JSON response containing order history with details
    """
    try:
        # Get all orders for the current user
        orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
        
        order_list = []
        for order in orders:
            # Get all items for this order
            order_items = OrderItem.query.filter_by(order_id=order.id).all()
            
            # Format order items
            items = []
            for item in order_items:
                items.append({
                    "product_id": item.product_id,
                    "product_name": item.product.name,
                    "quantity": item.quantity,
                    "price": item.price,
                    "image_url": item.product.image_url
                })
            
            # Format order details
            order_list.append({
                "order_id": order.id,
                "created_at": order.created_at.isoformat(),
                "total_amount": order.total_amount,
                "status": order.status,
                "items": items,
                "credits_used": order.credits_used,
                "credits_earned": order.credits_earned
            })
            
        return jsonify(order_list), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@orders_bp.route('/<int:order_id>', methods=['GET'])
@login_required
def get_order_details(order_id):
    """
    Get detailed information about a specific order.
    
    Args:
        order_id (int): The ID of the order to retrieve
        
    Returns:
        JSON response with detailed order information
    """
    try:
        # Get order and verify ownership
        order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
        
        # Get order items
        order_items = OrderItem.query.filter_by(order_id=order.id).all()
        
        # Format order items
        items = []
        for item in order_items:
            items.append({
                "product_id": item.product_id,
                "product_name": item.product.name,
                "quantity": item.quantity,
                "price": item.price,
                "image_url": item.product.image_url,
                "category": item.product.category.name if item.product.category else None
            })
        
        # Format order details
        order_details = {
            "order_id": order.id,
            "created_at": order.created_at.isoformat(),
            "total_amount": order.total_amount,
            "status": order.status,
            "items": items,
            "credits_used": order.credits_used,
            "credits_earned": order.credits_earned,
            "shipping_address": order.shipping_address if hasattr(order, 'shipping_address') else None,
            "payment_method": order.payment_method if hasattr(order, 'payment_method') else None
        }
        
        return jsonify(order_details), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500 