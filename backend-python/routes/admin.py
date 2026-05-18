from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Database
import json

bp = Blueprint('admin', __name__)

def is_admin(user_id):
    """Check if user is admin"""
    user = User.find_by_id(user_id)
    return user and user.get('role') == 'admin'

@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get dashboard statistics (Admin only)"""
    try:
        user_id = get_jwt_identity()
        if not is_admin(user_id):
            return jsonify({'success': False, 'message': 'Admin privileges required'}), 403
        
        db = Database.get_db()
        cursor = db.cursor()
        
        # Get statistics
        cursor.execute('SELECT COUNT(*) as count FROM orders')
        total_orders = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'customer'")
        total_users = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM products')
        total_products = cursor.fetchone()['count']
        
        # Calculate revenue - PostgreSQL JSONB syntax
        cursor.execute("SELECT pricing FROM orders WHERE payment->>'status' = 'paid'")
        completed_orders = cursor.fetchall()
        total_revenue = 0
        for order in completed_orders:
            pricing = json.loads(order['pricing'])
            total_revenue += pricing.get('total', 0)
        
        db.close()
        
        stats = {
            'totalOrders': total_orders,
            'totalUsers': total_users,
            'totalProducts': total_products,
            'totalRevenue': total_revenue,
            'todayOrders': 0,
            'monthRevenue': 0,
            'activeSubscriptions': 0,
            'pendingCatering': 0,
            'pendingFranchise': 0
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/recent-orders', methods=['GET'])
@jwt_required()
def get_recent_orders():
    """Get recent orders (Admin only)"""
    try:
        user_id = get_jwt_identity()
        if not is_admin(user_id):
            return jsonify({'success': False, 'message': 'Admin privileges required'}), 403
        
        db = Database.get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM orders ORDER BY createdAt DESC LIMIT 10')
        orders = cursor.fetchall()
        db.close()
        
        orders_list = [Database.row_to_dict(o) for o in orders]
        
        return jsonify({
            'success': True,
            'orders': orders_list
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
