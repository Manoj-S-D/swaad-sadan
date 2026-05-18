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

@bp.route('/', methods=['GET'], strict_slashes=False)
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

@bp.route('/validate', methods=['POST'], strict_slashes=False)
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
        
        # Get and validate minOrderValue - ensure it's a number, default to 0
        min_order_value = data.get('minOrderValue', 0)
        if min_order_value is None or (isinstance(min_order_value, str) and min_order_value.strip() == ''):
            min_order_value = 0
        try:
            min_order_value = float(min_order_value)
        except (ValueError, TypeError):
            min_order_value = 0
        
        # Get and validate maxDiscount
        max_discount = data.get('maxDiscount')
        if max_discount is not None:
            try:
                max_discount = float(max_discount)
            except (ValueError, TypeError):
                max_discount = None
        
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
            max_discount,
            min_order_value,
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
    db = None
    try:
        db = get_db()
        cursor = db.cursor()
        
        print(f"📝 Recording coupon usage - Coupon ID: {coupon_id}, User ID: {user_id}, Order ID: {order_id}, Discount: ₹{discount_amount}")
        
        # First, get current usedCount
        cursor.execute('SELECT code, usedCount FROM coupons WHERE id = ?', (coupon_id,))
        before = cursor.fetchone()
        if before:
            print(f"📊 BEFORE: Coupon '{before['code']}' usedCount = {before['usedCount']}")
        
        # Record usage in coupon_usage table
        cursor.execute('''
            INSERT INTO coupon_usage (couponId, userId, orderId, discountAmount)
            VALUES (?, ?, ?, ?)
        ''', (coupon_id, user_id, order_id, discount_amount))
        
        print(f"✅ Coupon usage record inserted into coupon_usage table")
        
        # Increment used count in coupons table
        cursor.execute('''
            UPDATE coupons SET usedCount = usedCount + 1 WHERE id = ?
        ''', (coupon_id,))
        
        print(f"✅ UPDATE query executed")
        
        # Commit the transaction
        db.commit()
        print(f"✅ Database commit successful")
        
        # Verify the update AFTER commit
        cursor.execute('SELECT code, usedCount FROM coupons WHERE id = ?', (coupon_id,))
        after = cursor.fetchone()
        if after:
            print(f"📊 AFTER: Coupon '{after['code']}' usedCount = {after['usedCount']}")
            if after['usedCount'] == before['usedCount']:
                print(f"❌ WARNING: usedCount did NOT increment! Still at {after['usedCount']}")
            else:
                print(f"✅ usedCount successfully incremented from {before['usedCount']} to {after['usedCount']}")
        
        db.close()
        
        print(f"✅ Coupon usage recording completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error recording coupon usage: {e}")
        import traceback
        traceback.print_exc()
        if db:
            try:
                db.rollback()
                db.close()
            except:
                pass
        return False
