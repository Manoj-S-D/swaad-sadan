from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import get_db
import json

bp = Blueprint('catering', __name__)

@bp.route('/', methods=['GET'])
def get_catering():
    """Get all catering packages"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM catering_packages WHERE isActive = 1 ORDER BY pricePerPerson ASC')
        packages = [dict(row) for row in cursor.fetchall()]
        
        # Parse JSON fields
        for package in packages:
            package['menuItems'] = json.loads(package.get('menuItems', '[]'))
            package['features'] = json.loads(package.get('features', '[]'))
        
        conn.close()
        return jsonify({'success': True, 'packages': packages})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/all', methods=['GET'])
@jwt_required()
def get_all_packages():
    """Get all catering packages (admin only)"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Get user role
        current_user_id = get_jwt_identity()
        cursor.execute('SELECT role FROM users WHERE id = ?', (current_user_id,))
        user = cursor.fetchone()
        
        if not user or user['role'] != 'admin':
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        cursor.execute('SELECT * FROM catering_packages ORDER BY createdAt DESC')
        packages = [dict(row) for row in cursor.fetchall()]
        
        # Parse JSON fields
        for package in packages:
            package['menuItems'] = json.loads(package.get('menuItems', '[]'))
            package['features'] = json.loads(package.get('features', '[]'))
        
        conn.close()
        return jsonify({'success': True, 'packages': packages})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/', methods=['POST'])
@jwt_required()
def create_package():
    """Create new catering package (admin only)"""
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
            INSERT INTO catering_packages 
            (name, description, type, minGuests, maxGuests, pricePerPerson, menuItems, features, isActive)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['name'],
            data.get('description', ''),
            data['type'],
            data['minGuests'],
            data.get('maxGuests'),
            data['pricePerPerson'],
            json.dumps(data.get('menuItems', [])),
            json.dumps(data.get('features', [])),
            data.get('isActive', 1)
        ))
        
        package_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Catering package created successfully',
            'packageId': package_id
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/<int:package_id>', methods=['PUT'])
@jwt_required()
def update_package(package_id):
    """Update catering package (admin only)"""
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
            UPDATE catering_packages 
            SET name = ?, description = ?, type = ?, minGuests = ?, maxGuests = ?, 
                pricePerPerson = ?, menuItems = ?, features = ?, isActive = ?
            WHERE id = ?
        ''', (
            data['name'],
            data.get('description', ''),
            data['type'],
            data['minGuests'],
            data.get('maxGuests'),
            data['pricePerPerson'],
            json.dumps(data.get('menuItems', [])),
            json.dumps(data.get('features', [])),
            data.get('isActive', 1),
            package_id
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Catering package updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/<int:package_id>', methods=['DELETE'])
@jwt_required()
def delete_package(package_id):
    """Delete catering package (admin only)"""
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
        cursor.execute('UPDATE catering_packages SET isActive = 0 WHERE id = ?', (package_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Catering package deleted successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
