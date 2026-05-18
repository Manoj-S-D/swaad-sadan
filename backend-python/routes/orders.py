from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Order, Settings, Database, User
from datetime import datetime

bp = Blueprint('orders', __name__)

def is_admin(user_id):
    """Check if user is admin"""
    user = User.find_by_id(user_id)
    return user and user.get('role') == 'admin'

@bp.route('/', methods=['POST'], strict_slashes=False)
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
        
        # Prepare payment details with transaction data for refunds
        # Normalize payment method to lowercase
        payment_method = data.get('paymentMethod', 'COD').lower()
        payment_status = data.get('paymentStatus', 'pending')
        
        # Only mark as paid if we have transaction ID (proof of payment)
        razorpay_payment_id = data.get('razorpay_payment_id', '')
        if payment_method == 'online' and not razorpay_payment_id:
            payment_status = 'pending'
        
        payment_details = {
            'method': payment_method,
            'status': payment_status,
            'paymentId': data.get('paymentId', ''),
            'transactionId': razorpay_payment_id,
            'orderId': data.get('razorpay_order_id', ''),
            'signature': data.get('razorpay_signature', ''),
            'amount': total,
            'currency': 'INR',
            'timestamp': datetime.now().isoformat() if razorpay_payment_id else None
        }
        
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
            'payment': payment_details,
            'status': 'pending',
            'specialInstructions': data.get('specialInstructions', '')
        }
        
        order_id = Order.create(order_data)
        
        # Record coupon usage if coupon was used
        if data.get('couponCode') and coupon_discount > 0 and coupon:
            from routes.coupons import record_coupon_usage
            record_coupon_usage(coupon['id'], user_id, order_id, coupon_discount)
            print(f"📊 Coupon {coupon['code']} used. Incrementing usage count.")
        
        order = Order.find_by_id(order_id)
        
        return jsonify({
            'success': True,
            'message': 'Order placed successfully',
            'order': order,
            'discountApplied': discount
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/my-orders', methods=['GET'], strict_slashes=False)
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
        
        # Parse payment info
        payment_info = order['payment']
        if isinstance(payment_info, str):
            import json
            payment_info = json.loads(payment_info)
        
        # Process refund if order is being cancelled and payment was made online
        refund_id = None
        if new_status == 'cancelled' and payment_info.get('status') == 'paid' and payment_info.get('transactionId'):
            try:
                # Import razorpay client
                from routes.payment import get_razorpay_client
                client = get_razorpay_client()
                
                if client:
                    # Process full refund
                    refund = client.payment.refund(payment_info['transactionId'], {
                        'speed': 'normal'
                    })
                    refund_id = refund['id']
                    
                    # Update payment status in order
                    payment_info['refundId'] = refund_id
                    payment_info['refundStatus'] = refund['status']
                    payment_info['refundedAt'] = datetime.now().isoformat()
                    
                    # Update payment info in database
                    import json
                    cursor.execute(
                        'UPDATE orders SET payment = ? WHERE id = ?',
                        (json.dumps(payment_info), order_id)
                    )
            except Exception as refund_error:
                # Log refund error but don't fail the status update
                print(f"Refund error: {str(refund_error)}")
        
        # Update status in database
        cursor.execute('UPDATE orders SET status = ? WHERE id = ?', (new_status, order_id))
        db.commit()
        db.close()
        
        # Award loyalty points if order is completed
        points_earned = 0
        if new_status == 'completed':
            from routes.loyalty import award_points
            import json
            
            pricing = order['pricing']
            # Parse JSON only if it's a string (SQLite), PostgreSQL JSONB returns already parsed
            if isinstance(pricing, str):
                pricing = json.loads(pricing)
            points_earned = award_points(order['userId'], pricing['total'])
        
        response_data = {
            'success': True,
            'message': 'Order status updated successfully',
            'pointsEarned': points_earned
        }
        
        if refund_id:
            response_data['refund'] = {
                'processed': True,
                'refundId': refund_id,
                'message': 'Refund initiated successfully. Amount will be credited to customer account in 5-7 business days.'
            }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/<order_id>/comment', methods=['POST'], strict_slashes=False)
@jwt_required()
def add_order_comment(order_id):
    """Add comment and rating to an order (Customer only)"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Verify order belongs to user
        db = Database.get_db()
        cursor = db.cursor()
        cursor.execute('SELECT userId FROM orders WHERE id = ?', (order_id,))
        order = cursor.fetchone()
        
        if not order:
            db.close()
            return jsonify({'success': False, 'message': 'Order not found'}), 404
        
        # Check if userId field exists, handle both 'userId' and 'user' column names
        order_user_id = order.get('userId') or order.get('user')
        if not order_user_id or order_user_id != user_id:
            db.close()
            return jsonify({'success': False, 'message': 'Unauthorized - This order does not belong to you'}), 403
        
        # Check if comment already exists
        cursor.execute('SELECT id FROM order_comments WHERE orderId = ? AND userId = ?', (order_id, user_id))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing comment
            cursor.execute('''
                UPDATE order_comments 
                SET rating = ?, comment = ?, updatedAt = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (data.get('rating'), data.get('comment'), existing['id']))
            comment_id = existing['id']
        else:
            # Create new comment
            cursor.execute('''
                INSERT INTO order_comments (orderId, userId, rating, comment)
                VALUES (?, ?, ?, ?)
            ''', (order_id, user_id, data.get('rating'), data.get('comment')))
            comment_id = cursor.lastrowid
        
        db.commit()
        db.close()
        
        return jsonify({
            'success': True,
            'message': 'Thank you for your feedback!',
            'commentId': comment_id
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/<order_id>/comments', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_order_comments(order_id):
    """Get comments for an order (Admin or order owner)"""
    try:
        user_id = get_jwt_identity()
        
        db = Database.get_db()
        cursor = db.cursor()
        
        # Check if user is admin or order owner
        cursor.execute('SELECT userId FROM orders WHERE id = ?', (order_id,))
        order = cursor.fetchone()
        
        if not order:
            db.close()
            return jsonify({'success': False, 'message': 'Order not found'}), 404
        
        if not is_admin(user_id) and order['userId'] != user_id:
            db.close()
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        # Get comments
        cursor.execute('''
            SELECT c.*, u.name as userName 
            FROM order_comments c
            JOIN users u ON c.userId = u.id
            WHERE c.orderId = ?
            ORDER BY c.createdAt DESC
        ''', (order_id,))
        comments = cursor.fetchall()
        db.close()
        
        return jsonify({
            'success': True,
            'comments': [dict(c) for c in comments]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/comments/<comment_id>/reply', methods=['PUT'], strict_slashes=False)
@jwt_required()
def reply_to_comment(comment_id):
    """Admin reply to customer comment"""
    try:
        user_id = get_jwt_identity()
        if not is_admin(user_id):
            return jsonify({'success': False, 'message': 'Admin privileges required'}), 403
        
        data = request.get_json()
        admin_reply = data.get('reply')
        
        if not admin_reply:
            return jsonify({'success': False, 'message': 'Reply text required'}), 400
        
        db = Database.get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            UPDATE order_comments 
            SET adminReply = ?, repliedAt = CURRENT_TIMESTAMP, updatedAt = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (admin_reply, comment_id))
        
        if cursor.rowcount == 0:
            db.close()
            return jsonify({'success': False, 'message': 'Comment not found'}), 404
        
        db.commit()
        db.close()
        
        return jsonify({
            'success': True,
            'message': 'Reply added successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
