from flask import Blueprint, jsonify, request, current_app
import razorpay
import hmac
import hashlib

bp = Blueprint('payment', __name__)

def get_razorpay_client():
    """Get Razorpay client instance"""
    key_id = current_app.config.get('RAZORPAY_KEY_ID')
    key_secret = current_app.config.get('RAZORPAY_KEY_SECRET')
    
    if not key_id or not key_secret:
        return None
    
    return razorpay.Client(auth=(key_id, key_secret))

@bp.route('/key', methods=['GET'])
def get_key():
    """Get Razorpay public key for frontend"""
    key_id = current_app.config.get('RAZORPAY_KEY_ID')
    
    if not key_id:
        return jsonify({
            'success': False,
            'message': 'Razorpay not configured. Add RAZORPAY_KEY_ID to .env file'
        }), 400
    
    return jsonify({
        'success': True,
        'key': key_id
    })

@bp.route('/create-order', methods=['POST'])
def create_payment_order():
    """Create Razorpay order for checkout"""
    try:
        client = get_razorpay_client()
        
        if not client:
            return jsonify({
                'success': False,
                'message': 'Razorpay not configured. Add keys to .env file'
            }), 400
        
        data = request.get_json()
        amount = int(data.get('amount', 0)) * 100  # Convert to paise (₹1 = 100 paise)
        
        if amount <= 0:
            return jsonify({'success': False, 'message': 'Invalid amount'}), 400
        
        # Create Razorpay order
        order_data = {
            'amount': amount,
            'currency': 'INR',
            'payment_capture': 1  # Auto capture payment
        }
        
        razorpay_order = client.order.create(data=order_data)
        
        return jsonify({
            'success': True,
            'orderId': razorpay_order['id'],
            'amount': razorpay_order['amount'],
            'currency': razorpay_order['currency']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Payment order creation failed: {str(e)}'
        }), 500

@bp.route('/verify', methods=['POST'])
def verify_payment():
    """Verify Razorpay payment signature"""
    try:
        data = request.get_json()
        
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')
        
        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return jsonify({'success': False, 'message': 'Missing payment details'}), 400
        
        # Verify signature
        key_secret = current_app.config.get('RAZORPAY_KEY_SECRET')
        
        if not key_secret:
            return jsonify({'success': False, 'message': 'Razorpay not configured'}), 400
        
        # Create signature string
        message = f"{razorpay_order_id}|{razorpay_payment_id}"
        generated_signature = hmac.new(
            key_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Verify
        if generated_signature == razorpay_signature:
            return jsonify({
                'success': True,
                'message': 'Payment verified successfully',
                'paymentId': razorpay_payment_id
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Payment verification failed'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Payment verification error: {str(e)}'
        }), 500
