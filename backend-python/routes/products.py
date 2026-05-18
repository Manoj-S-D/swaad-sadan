from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Product, User, Database
from bson import ObjectId

bp = Blueprint('products', __name__)

def is_admin(user_id):
    """Check if user is admin"""
    user = User.find_by_id(user_id)
    return user and user.get('role') == 'admin'

@bp.route('/', methods=['GET'])
def get_products():
    """Get all products"""
    try:
        # Get query parameters
        category = request.args.get('category')
        is_veg = request.args.get('isVeg')
        is_health_box = request.args.get('isHealthBox')
        search = request.args.get('search')
        include_all = request.args.get('includeAll', 'false').lower() == 'true'
        
        # Build filter
        filters = {}
        
        if category:
            filters['category'] = category
        if is_veg:
            filters['isVeg'] = is_veg.lower() == 'true'
        if is_health_box:
            filters['isHealthBox'] = is_health_box.lower() == 'true'
        
        # Get products (include_unavailable=True for admin to see catalog items)
        products = Product.find_all(filters, include_unavailable=include_all)
        
        # Apply search filter if needed (after fetching from DB)
        if search:
            search_lower = search.lower()
            products = [p for p in products if 
                        search_lower in p.get('name', '').lower() or 
                        search_lower in p.get('description', '').lower()]
        
        return jsonify({
            'success': True,
            'count': len(products),
            'products': products
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get single product"""
    try:
        product = Product.find_by_id(product_id)
        if not product:
            return jsonify({'success': False, 'message': 'Product not found'}), 404
        
        return jsonify({'success': True, 'product': product})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/', methods=['POST'])
@jwt_required()
def create_product():
    """Create product (Admin only)"""
    try:
        user_id = get_jwt_identity()
        if not is_admin(user_id):
            return jsonify({'success': False, 'message': 'Admin privileges required'}), 403
        
        data = request.get_json()
        product_id = Product.create(data)
        product = Product.find_by_id(product_id)
        
        return jsonify({
            'success': True,
            'message': 'Product created successfully',
            'product': product
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/<product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """Update product (Admin only)"""
    try:
        user_id = get_jwt_identity()
        if not is_admin(user_id):
            return jsonify({'success': False, 'message': 'Admin privileges required'}), 403
        
        data = request.get_json()
        Product.update(product_id, data)
        product = Product.find_by_id(product_id)
        
        return jsonify({
            'success': True,
            'message': 'Product updated successfully',
            'product': product
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/<product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """Delete product (Admin only)"""
    try:
        user_id = get_jwt_identity()
        if not is_admin(user_id):
            return jsonify({'success': False, 'message': 'Admin privileges required'}), 403
        
        Product.delete(product_id)
        
        return jsonify({
            'success': True,
            'message': 'Product deleted successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
