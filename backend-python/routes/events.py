from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import get_db
import json

bp = Blueprint('events', __name__)

@bp.route('/packages', methods=['GET'])
def get_packages():
    """Get all event packages"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM event_packages WHERE isActive = 1 ORDER BY price ASC')
        packages = [dict(row) for row in cursor.fetchall()]
        
        # Parse JSON fields
        for package in packages:
            package['inclusions'] = json.loads(package.get('inclusions', '[]'))
        
        conn.close()
        return jsonify({'success': True, 'packages': packages})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/packages/all', methods=['GET'])
@jwt_required()
def get_all_packages():
    """Get all event packages (admin only)"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Get user role
        current_user_id = get_jwt_identity()
        cursor.execute('SELECT role FROM users WHERE id = ?', (current_user_id,))
        user = cursor.fetchone()
        
        if not user or user['role'] != 'admin':
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        cursor.execute('SELECT * FROM event_packages ORDER BY createdAt DESC')
        packages = [dict(row) for row in cursor.fetchall()]
        
        # Parse JSON fields
        for package in packages:
            package['inclusions'] = json.loads(package.get('inclusions', '[]'))
        
        conn.close()
        return jsonify({'success': True, 'packages': packages})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/packages', methods=['POST'])
@jwt_required()
def create_package():
    """Create new event package (admin only)"""
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
        
        # Insert new package
        cursor.execute('''
            INSERT INTO event_packages 
            (name, description, eventType, capacity, price, duration, inclusions, venue, isActive)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['name'],
            data.get('description', ''),
            data['eventType'],
            data['capacity'],
            data['price'],
            data.get('duration', ''),
            json.dumps(data.get('inclusions', [])),
            data.get('venue', ''),
            data.get('isActive', 1)
        ))
        
        package_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Event package created successfully',
            'packageId': package_id
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/packages/<int:package_id>', methods=['PUT'])
@jwt_required()
def update_package(package_id):
    """Update event package (admin only)"""
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
        
        # Update package
        cursor.execute('''
            UPDATE event_packages 
            SET name = ?, description = ?, eventType = ?, capacity = ?, price = ?, 
                duration = ?, inclusions = ?, venue = ?, isActive = ?
            WHERE id = ?
        ''', (
            data['name'],
            data.get('description', ''),
            data['eventType'],
            data['capacity'],
            data['price'],
            data.get('duration', ''),
            json.dumps(data.get('inclusions', [])),
            data.get('venue', ''),
            data.get('isActive', 1),
            package_id
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Event package updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/packages/<int:package_id>', methods=['DELETE'])
@jwt_required()
def delete_package(package_id):
    """Delete event package (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Check if user is admin
        cursor.execute('SELECT role FROM users WHERE id = ?', (current_user_id,))
        user = cursor.fetchone()
        
        if not user or user['role'] != 'admin':
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        # Soft delete
        cursor.execute('UPDATE event_packages SET isActive = 0 WHERE id = ?', (package_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Event package deleted successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
