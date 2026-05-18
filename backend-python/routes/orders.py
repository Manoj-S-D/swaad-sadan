from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Order, Settings, Database, User

bp = Blueprint('orders', __name__)

def is_admin(user_id):
    """Check if user is admin"""
    user = User.find_by_id(user_id)
    return user and user.get('role') == 'admin'

@bp.route('/', methods=['POST'])
@jwt_required()
def create_order():
    """Create new order"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Calculate pricing
        subtotal = sum(item['price'] * item['quantity'] for item in data['items'])
        
        settings = Settings.get_settings()
        delivery_charge = 0
        parcel_charge = settings.get('parcelCharge', 10)
        discount = 0
        coupon_discount = 0
        points_discount = 0
        
        # Handle delivery charge - only for delivery orders
        if data['orderType'] == 'delivery':
            if subtotal < settings['deliveryCharges']['freeDeliveryAbove']:
                delivery_charge = settings['deliveryCharges']['baseCharge']
        
        # Calculate total before discount
        total_before_discount = subtotal + delivery_charge + parcel_charge
        
        # Handle coupon discount
        if data.get('couponCode'):
            from routes.coupons import record_coupon_usage
            db = Database.get_db()
            cursor = db.cursor()
            cursor.execute('SELECT * FROM coupons WHERE code = ? AND isActive = TRUE', (data['couponCode'],))
            coupon = cursor.fetchone()
            
            if coupon:
                # Calculate coupon discount
                if coupon['type'] == 'flat':
                    coupon_discount = coupon['value']
                elif coupon['type'] == 'percentage':
                    coupon_discount = (total_before_discount * coupon['value']) / 100
                    if coupon['maxDiscount'] and coupon_discount > coupon['maxDiscount']:
                        coupon_discount = coupon['maxDiscount']
            
            db.close()
        
        # Handle loyalty points redemption
        if data.get('pointsToRedeem', 0) > 0:
            from routes.loyalty import award_points
            points_to_use = int(data['pointsToRedeem'])
            
            # Verify user has enough points
            db = Database.get_db()
            cursor = db.cursor()
            cursor.execute('SELECT points FROM loyalty_points WHERE userId = ?', (user_id,))
            points_record = cursor.fetchone()
            
            if points_record and points_record['points'] >= points_to_use:
                points_discount = points_to_use
                
                # Deduct points
                cursor.execute('''
                    UPDATE loyalty_points 
                    SET points = points - ?, totalRedeemed = totalRedeemed + ?, updatedAt = CURRENT_TIMESTAMP
                    WHERE userId = ?
                ''', (points_to_use, points_to_use, user_id))
                db.commit()
            
            db.close()
        
        # Calculate final discount and total
        discount = coupon_discount + points_discount
        total = total_before_discount - discount
        
        order_data = {
            'user': user_id,
            'items': data['items'],
            'orderType': data['orderType'],
            'deliveryAddress': data.get('deliveryAddress'),
            'pricing': {
                'subtotal': subtotal,
                'deliveryCharge': delivery_charge,
                'parcelCharge': parcel_charge,
                'couponDiscount': coupon_discount,
                'pointsDiscount': points_discount,
                'discount': discount,
                'total': total
            },
            'payment': {
                'method': data.get('paymentMethod', 'COD'),
                'status': data.get('paymentStatus', 'pending'),
                'paymentId': data.get('paymentId', '')
            },
            'status': 'pending',
            'specialInstructions': data.get('specialInstructions', '')
        }
        
        order_id = Order.create(order_data)
        
        # Record coupon usage if coupon was used
        if data.get('couponCode') and coupon_discount > 0:
            from routes.coupons import record_coupon_usage
            record_coupon_usage(coupon['id'], user_id, order_id, coupon_discount)
        
        order = Order.find_by_id(order_id)
        
        return jsonify({
            'success': True,
            'message': 'Order placed successfully',
            'order': order,
            'discountApplied': discount
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/my-orders', methods=['GET'])
@jwt_required()
def get_my_orders():
    """Get user's orders"""
    try:
        user_id = get_jwt_identity()
        orders = Order.find_by_user(user_id)
        
        return jsonify({
            'success': True,
            'count': len(orders),
            'orders': orders
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/<order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """Get order details"""
    try:
        order = Order.find_by_id(order_id)
        if not order:
            return jsonify({'success': False, 'message': 'Order not found'}), 404
        
        return jsonify({
            'success': True,
            'order': order
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/<order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    """Update order status (Admin only)"""
    try:
        user_id = get_jwt_identity()
        if not is_admin(user_id):
            return jsonify({'success': False, 'message': 'Admin privileges required'}), 403
        
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'success': False, 'message': 'Status is required'}), 400
        
        if new_status not in ['pending', 'confirmed', 'preparing', 'ready', 'completed', 'cancelled']:
            return jsonify({'success': False, 'message': 'Invalid status'}), 400
        
        # Get order details before updating
        db = Database.get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
        order = cursor.fetchone()
        
        if not order:
            db.close()
            return jsonify({'success': False, 'message': 'Order not found'}), 404
        
        # Update status in database
        cursor.execute('UPDATE orders SET status = ? WHERE id = ?', (new_status, order_id))
        db.commit()
        db.close()
        
        # Award loyalty points if order is completed
        if new_status == 'completed':
            from routes.loyalty import award_points
            import json
            
            pricing = json.loads(order['pricing'])
            points_earned = award_points(order['userId'], pricing['total'])
        
        return jsonify({
            'success': True,
            'message': 'Order status updated successfully',
            'pointsEarned': points_earned if new_status == 'completed' else 0
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
