from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import get_db
import json

bp = Blueprint('loyalty', __name__)

@bp.route('/my-points', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_my_points():
    """Get user's loyalty points"""
    try:
        user_id = get_jwt_identity()
        db = get_db()
        cursor = db.cursor()
        
        # Get or create loyalty points record
        cursor.execute('SELECT * FROM loyalty_points WHERE userId = ?', (user_id,))
        points_record = cursor.fetchone()
        
        if not points_record:
            # Create new record
            cursor.execute('''
                INSERT INTO loyalty_points (userId, points, totalEarned, totalRedeemed)
                VALUES (?, 0, 0, 0)
            ''', (user_id,))
            db.commit()
            
            cursor.execute('SELECT * FROM loyalty_points WHERE userId = ?', (user_id,))
            points_record = cursor.fetchone()
        
        db.close()
        
        return jsonify({
            'success': True,
            'points': dict(points_record)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/redeem', methods=['POST'])
@jwt_required()
def redeem_points():
    """Redeem loyalty points for discount"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        points_to_redeem = data.get('points', 0)
        
        if points_to_redeem <= 0:
            return jsonify({'success': False, 'message': 'Invalid points amount'}), 400
        
        db = get_db()
        cursor = db.cursor()
        
        # Get current points
        cursor.execute('SELECT * FROM loyalty_points WHERE userId = ?', (user_id,))
        points_record = cursor.fetchone()
        
        if not points_record or points_record['points'] < points_to_redeem:
            db.close()
            return jsonify({'success': False, 'message': 'Insufficient points'}), 400
        
        # Calculate discount (1 point = ₹1)
        discount_amount = points_to_redeem
        
        # Update points
        new_points = points_record['points'] - points_to_redeem
        new_redeemed = points_record['totalRedeemed'] + points_to_redeem
        
        cursor.execute('''
            UPDATE loyalty_points 
            SET points = ?, totalRedeemed = ?, updatedAt = CURRENT_TIMESTAMP
            WHERE userId = ?
        ''', (new_points, new_redeemed, user_id))
        
        db.commit()
        db.close()
        
        return jsonify({
            'success': True,
            'message': f'Redeemed {points_to_redeem} points',
            'discount': discount_amount,
            'remainingPoints': new_points
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

def award_points(user_id, order_total):
    """Award loyalty points for an order (5% of order total)"""
    try:
        points_earned = int(order_total * 0.05)  # 5% cashback as points
        
        db = get_db()
        cursor = db.cursor()
        
        # Get or create loyalty points record
        cursor.execute('SELECT * FROM loyalty_points WHERE userId = ?', (user_id,))
        points_record = cursor.fetchone()
        
        if points_record:
            new_points = points_record['points'] + points_earned
            new_total_earned = points_record['totalEarned'] + points_earned
            
            cursor.execute('''
                UPDATE loyalty_points 
                SET points = ?, totalEarned = ?, updatedAt = CURRENT_TIMESTAMP
                WHERE userId = ?
            ''', (new_points, new_total_earned, user_id))
        else:
            cursor.execute('''
                INSERT INTO loyalty_points (userId, points, totalEarned, totalRedeemed)
                VALUES (?, ?, ?, 0)
            ''', (user_id, points_earned, points_earned))
        
        db.commit()
        db.close()
        
        return points_earned
        
    except Exception as e:
        print(f"Error awarding points: {e}")
        return 0
