from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import get_db
from models import User
from datetime import datetime
import json

bp = Blueprint('coupons', __name__)

def is_admin(user_id):
    """Check if user is admin"""
    user = User.find_by_id(user_id)
    return user and user.get('role') == 'admin'

@bp.route('/', methods=['GET'])
def get_active_coupons():
    """Get all active coupons"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT * FROM coupons 
            WHERE isActive = TRUE AND expiryDate >= date('now')
            ORDER BY createdAt DESC
        ''')
        coupons = cursor.fetchall()
        db.close()
        
        coupons_list = [dict(c) for c in coupons]
        
        return jsonify({
            'success': True,
            'coupons': coupons_list
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/validate', methods=['POST'])
@jwt_required()
def validate_coupon():
    """Validate a coupon code"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        code = data.get('code', '').upper()
        order_total = data.get('orderTotal', 0)
        
        if not code:
            return jsonify({'success': False, 'message': 'Coupon code required'}), 400
        
        db = get_db()
        cursor = db.cursor()
        
        # Get coupon
        cursor.execute('SELECT * FROM coupons WHERE code = ? AND isActive = TRUE', (code,))
        coupon = cursor.fetchone()
        
        if not coupon:
            db.close()
            return jsonify({'success': False, 'message': 'Invalid or expired coupon'}), 404
        
        # Check expiry
        if coupon['expiryDate'] < datetime.now().strftime('%Y-%m-%d'):
            db.close()
            return jsonify({'success': False, 'message': 'Coupon has expired'}), 400
        
        # Check usage limit
        if coupon['usedCount'] >= coupon['usageLimit']:
            db.close()
            return jsonify({'success': False, 'message': 'Coupon usage limit reached'}), 400
        
        # Check minimum order value (handle NULL/None values)
        min_order_value = coupon['minOrderValue'] or 0
        if order_total < min_order_value:
            db.close()
            return jsonify({
                'success': False, 
                'message': f'Minimum order value ₹{min_order_value} required'
            }), 400
        
        # Check if user already used this coupon
        cursor.execute('''
            SELECT COUNT(*) as count FROM coupon_usage 
            WHERE couponId = ? AND userId = ?
        ''', (coupon['id'], user_id))
        usage_count = cursor.fetchone()['count']
        
        if usage_count > 0:
            db.close()
            return jsonify({'success': False, 'message': 'You have already used this coupon'}), 400
        
        # Calculate discount
        discount = 0
        if coupon['type'] == 'flat':
            discount = coupon['value']
        elif coupon['type'] == 'percentage':
            discount = (order_total * coupon['value']) / 100
            if coupon['maxDiscount'] and discount > coupon['maxDiscount']:
                discount = coupon['maxDiscount']
        
        db.close()
        
        return jsonify({
            'success': True,
            'coupon': dict(coupon),
            'discount': round(discount, 2)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/create', methods=['POST'])
@jwt_required()
def create_coupon():
    """Create a new coupon (Admin only)"""
    try:
        user_id = get_jwt_identity()
        if not is_admin(user_id):
            return jsonify({'success': False, 'message': 'Admin privileges required'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['code', 'type', 'value', 'expiryDate']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'{field} is required'}), 400
        
        code = data['code'].upper()
        
        db = get_db()
        cursor = db.cursor()
        
        # Check if code already exists
        cursor.execute('SELECT id FROM coupons WHERE code = ?', (code,))
        if cursor.fetchone():
            db.close()
            return jsonify({'success': False, 'message': 'Coupon code already exists'}), 400
        
        # Create coupon
        cursor.execute('''
            INSERT INTO coupons (
                code, type, value, maxDiscount, minOrderValue, 
                category, description, expiryDate, usageLimit, isActive
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            code,
            data['type'],
            data['value'],
            data.get('maxDiscount'),
            data.get('minOrderValue', 0),
            data.get('category'),
            data.get('description'),
            data['expiryDate'],
            data.get('usageLimit', 100),
            data.get('isActive', 1)  # Will be converted to TRUE by UnifiedCursor
        ))
        
        db.commit()
        coupon_id = cursor.lastrowid
        db.close()
        
        return jsonify({
            'success': True,
            'message': 'Coupon created successfully',
            'couponId': coupon_id
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/<coupon_id>', methods=['DELETE'])
@jwt_required()
def delete_coupon(coupon_id):
    """Deactivate a coupon (Admin only)"""
    try:
        user_id = get_jwt_identity()
        if not is_admin(user_id):
            return jsonify({'success': False, 'message': 'Admin privileges required'}), 403
        
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('UPDATE coupons SET isActive = FALSE WHERE id = ?', (coupon_id,))
        db.commit()
        
        if cursor.rowcount == 0:
            db.close()
            return jsonify({'success': False, 'message': 'Coupon not found'}), 404
        
        db.close()
        
        return jsonify({
            'success': True,
            'message': 'Coupon deactivated successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

def record_coupon_usage(coupon_id, user_id, order_id, discount_amount):
    """Record coupon usage when order is placed"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Record usage
        cursor.execute('''
            INSERT INTO coupon_usage (couponId, userId, orderId, discountAmount)
            VALUES (?, ?, ?, ?)
        ''', (coupon_id, user_id, order_id, discount_amount))
        
        # Increment used count
        cursor.execute('''
            UPDATE coupons SET usedCount = usedCount + 1 WHERE id = ?
        ''', (coupon_id,))
        
        db.commit()
        db.close()
        
        return True
        
    except Exception as e:
        print(f"Error recording coupon usage: {e}")
        return False
