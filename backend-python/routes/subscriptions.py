from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import get_db
import json

bp = Blueprint('subscriptions', __name__)

@bp.route('/plans', methods=['GET'])
def get_plans():
    """Get all subscription plans"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Get only active plans for customers, or all for admin
        cursor.execute('SELECT * FROM subscription_plans WHERE isActive = TRUE ORDER BY price ASC')
        plans = [dict(row) for row in cursor.fetchall()]
        
        # Parse JSON fields (only if they're strings, PostgreSQL JSONB returns already parsed)
        for plan in plans:
            if isinstance(plan.get('features'), str):
                plan['features'] = json.loads(plan.get('features', '[]'))
        
        conn.close()
        return jsonify({'success': True, 'plans': plans})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/plans/all', methods=['GET'])
@jwt_required()
def get_all_plans():
    """Get all subscription plans (admin only)"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Get user role
        current_user_id = get_jwt_identity()
        cursor.execute('SELECT role FROM users WHERE id = ?', (current_user_id,))
        user = cursor.fetchone()
        
        if not user or user['role'] != 'admin':
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        cursor.execute('SELECT * FROM subscription_plans ORDER BY createdAt DESC')
        plans = [dict(row) for row in cursor.fetchall()]
        
        # Parse JSON fields (only if they're strings, PostgreSQL JSONB returns already parsed)
        for plan in plans:
            if isinstance(plan.get('features'), str):
                plan['features'] = json.loads(plan.get('features', '[]'))
        
        conn.close()
        return jsonify({'success': True, 'plans': plans})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/plans', methods=['POST'])
@jwt_required()
def create_plan():
    """Create new subscription plan (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Check if user is admin
        cursor.execute('SELECT role FROM users WHERE id = ?', (current_user_id,))
        user = cursor.fetchone()
        
        if not user or user['role'] != 'admin':
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        # Insert new plan
        cursor.execute('''
            INSERT INTO subscription_plans 
            (name, description, duration, price, mealsPerDay, features, isActive)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['name'],
            data.get('description', ''),
            data['duration'],
            data['price'],
            data.get('mealsPerDay', 1),
            json.dumps(data.get('features', [])),
            data.get('isActive', 1)
        ))
        
        plan_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Subscription plan created successfully',
            'planId': plan_id
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/plans/<int:plan_id>', methods=['PUT'])
@jwt_required()
def update_plan(plan_id):
    """Update subscription plan (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Check if user is admin
        cursor.execute('SELECT role FROM users WHERE id = ?', (current_user_id,))
        user = cursor.fetchone()
        
        if not user or user['role'] != 'admin':
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        # Update plan
        cursor.execute('''
            UPDATE subscription_plans 
            SET name = ?, description = ?, duration = ?, price = ?, 
                mealsPerDay = ?, features = ?, isActive = ?
            WHERE id = ?
        ''', (
            data['name'],
            data.get('description', ''),
            data['duration'],
            data['price'],
            data.get('mealsPerDay', 1),
            json.dumps(data.get('features', [])),
            data.get('isActive', 1),
            plan_id
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Subscription plan updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/plans/<int:plan_id>', methods=['DELETE'])
@jwt_required()
def delete_plan(plan_id):
    """Delete subscription plan (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Check if user is admin
        cursor.execute('SELECT role FROM users WHERE id = ?', (current_user_id,))
        user = cursor.fetchone()
        
        if not user or user['role'] != 'admin':
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        # Soft delete - just mark as inactive
        cursor.execute('UPDATE subscription_plans SET isActive = 0 WHERE id = ?', (plan_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Subscription plan deleted successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
