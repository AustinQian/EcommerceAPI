from flask import Blueprint, request, jsonify
from models.product import Product
from models import db
from datetime import datetime

product_bp = Blueprint('product_bp', __name__)

# GET /products - List products with optional filtering
@product_bp.route('', methods=['GET'])
def list_products():
    search = request.args.get('search')
    category_id = request.args.get('category_id')
    query = Product.query

    if search:
        like_pattern = f"%{search}%"
        query = query.filter(Product.name.ilike(like_pattern))
    if category_id:
        query = query.filter(Product.category_id == category_id)

    products = query.all()
    results = []
    for p in products:
        results.append({
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'price': p.price,
            'stock': p.stock,
            'image_url': p.image_url,
            'seller_id': p.seller_id,
            'category_id': p.category_id,
            'created_at': p.created_at.isoformat() if p.created_at else None
        })
    return jsonify(results), 200

# GET /products/<id> - Retrieve a specific product
@product_bp.route('/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get_or_404(id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'stock': product.stock,
        'image_url': product.image_url,
        'seller_id': product.seller_id,
        'category_id': product.category_id,
        'created_at': product.created_at.isoformat() if product.created_at else None
    }), 200

# POST /products - Create a new product
@product_bp.route('', methods=['POST'])
def create_product():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    price = data.get('price')
    stock = data.get('stock', 0)
    image_url = data.get('image_url')
    seller_id = data.get('seller_id')  # In a real scenario, use current_user.id
    category_id = data.get('category_id')

    if not name or not description or price is None or not seller_id or not category_id:
        return jsonify({'error': 'Missing required fields'}), 400

    new_product = Product(
        name=name,
        description=description,
        price=price,
        stock=stock,
        image_url=image_url,
        seller_id=seller_id,
        category_id=category_id,
        created_at=datetime.utcnow()
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'message': 'Product created successfully', 'product_id': new_product.id}), 201

# PUT /products/<id> - Update an existing product
@product_bp.route('/<int:id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get_or_404(id)
    data = request.get_json()

    product.name = data.get('name', product.name)
    product.description = data.get('description', product.description)
    product.price = data.get('price', product.price)
    product.stock = data.get('stock', product.stock)
    product.image_url = data.get('image_url', product.image_url)
    product.category_id = data.get('category_id', product.category_id)

    db.session.commit()
    return jsonify({'message': 'Product updated successfully'}), 200

# DELETE /products/<id> - Delete a product
@product_bp.route('/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'}), 200
