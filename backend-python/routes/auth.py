from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import User, Database
from extensions import bcrypt, get_db
from email_validator import validate_email, EmailNotValidError
import json

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['POST'], strict_slashes=False)
def register():
    """Register new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'{field} is required'}), 400
        
        # Validate email
        try:
            validate_email(data['email'])
        except EmailNotValidError:
            return jsonify({'success': False, 'message': 'Invalid email address'}), 400
        
        # Check if user exists
        existing_user = User.find_by_email(data['email'])
        if existing_user:
            return jsonify({'success': False, 'message': 'Email already registered'}), 400
        
        # Hash password
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        
        # Create user
        user_data = {
            'name': data['name'],
            'email': data['email'],
            'phone': data['phone'],
            'password': hashed_password,
            'role': 'customer',
            'isActive': True,
            'addresses': []
        }
        
        user_id = User.create(user_data)
        
        # Generate token
        access_token = create_access_token(identity=user_id)
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'token': access_token,
            'user': {
                'id': user_id,
                'name': data['name'],
                'email': data['email'],
                'phone': data['phone'],
                'role': 'customer'
            }
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/login', methods=['POST'], strict_slashes=False)
def login():
    """User login"""
    try:
        data = request.get_json()
        
        if 'email' not in data or 'password' not in data:
            return jsonify({'success': False, 'message': 'Email and password required'}), 400
        
        # Find user
        user = User.find_by_email(data['email'])
        if not user:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
        
        # Check if active
        if not user.get('isActive', True):
            return jsonify({'success': False, 'message': 'Account is deactivated'}), 401
        
        # Verify password
        if not bcrypt.check_password_hash(user['password'], data['password']):
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
        
        # Generate token
        access_token = create_access_token(identity=str(user['id']))
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': access_token,
            'user': {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'phone': user['phone'],
                'role': user.get('role', 'customer')
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user details"""
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        # Remove password from response
        user_data = dict(user)
        user_data.pop('password', None)
        
        return jsonify({
            'success': True,
            'user': user_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/update-profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        db = Database.get_db()
        cursor = db.cursor()
        
        # Build update query dynamically
        updates = []
        values = []
        
        if 'name' in data:
            updates.append('name = ?')
            values.append(data['name'])
        
        if 'phone' in data:
            updates.append('phone = ?')
            values.append(data['phone'])
        
        if 'addresses' in data:
            updates.append('addresses = ?')
            values.append(json.dumps(data['addresses']))
        
        if not updates:
            db.close()
            return jsonify({'success': False, 'message': 'No fields to update'}), 400
        
        values.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        
        cursor.execute(query, values)
        db.commit()
        db.close()
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/addresses', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_addresses():
    """Get user's saved addresses"""
    try:
        user_id = get_jwt_identity()
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT * FROM user_addresses 
            WHERE userId = ? 
            ORDER BY isDefault DESC, createdAt DESC
        ''', (user_id,))
        addresses = cursor.fetchall()
        db.close()
        
        return jsonify({
            'success': True,
            'addresses': [dict(addr) for addr in addresses]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/addresses', methods=['POST'], strict_slashes=False)
@jwt_required()
def add_address():
    """Add new address"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        db = get_db()
        cursor = db.cursor()
        
        # If this is set as default, unset all others
        if data.get('isDefault'):
            cursor.execute('UPDATE user_addresses SET isDefault = FALSE WHERE userId = ?', (user_id,))
        
        cursor.execute('''
            INSERT INTO user_addresses (
                userId, label, addressLine1, addressLine2, city, state, pincode, 
                landmark, latitude, longitude, isDefault
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            data.get('label', 'Home'),
            data['addressLine1'],
            data.get('addressLine2'),
            data['city'],
            data['state'],
            data['pincode'],
            data.get('landmark'),
            data.get('latitude'),
            data.get('longitude'),
            1 if data.get('isDefault') else 0
        ))
        
        address_id = cursor.lastrowid
        db.commit()
        db.close()
        
        return jsonify({
            'success': True,
            'message': 'Address added successfully',
            'addressId': address_id
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/addresses/<address_id>', methods=['PUT'], strict_slashes=False)
@jwt_required()
def update_address(address_id):
    """Update an address"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        db = get_db()
        cursor = db.cursor()
        
        # Verify ownership
        cursor.execute('SELECT id FROM user_addresses WHERE id = ? AND userId = ?', (address_id, user_id))
        if not cursor.fetchone():
            db.close()
            return jsonify({'success': False, 'message': 'Address not found'}), 404
        
        # If setting as default, unset all others
        if data.get('isDefault'):
            cursor.execute('UPDATE user_addresses SET isDefault = FALSE WHERE userId = ?', (user_id,))
        
        updates = []
        values = []
        
        for field in ['label', 'addressLine1', 'addressLine2', 'city', 'state', 'pincode', 'landmark', 'latitude', 'longitude']:
            if field in data:
                updates.append(f'{field} = ?')
                values.append(data[field])
        
        if 'isDefault' in data:
            updates.append('isDefault = ?')
            values.append(1 if data['isDefault'] else 0)
        
        if updates:
            updates.append('updatedAt = CURRENT_TIMESTAMP')
            values.append(address_id)
            cursor.execute(f"UPDATE user_addresses SET {', '.join(updates)} WHERE id = ?", values)
            db.commit()
        
        db.close()
        
        return jsonify({
            'success': True,
            'message': 'Address updated successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/addresses/<address_id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
def delete_address(address_id):
    """Delete an address"""
    try:
        user_id = get_jwt_identity()
        
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('DELETE FROM user_addresses WHERE id = ? AND userId = ?', (address_id, user_id))
        
        if cursor.rowcount == 0:
            db.close()
            return jsonify({'success': False, 'message': 'Address not found'}), 404
        
        db.commit()
        db.close()
        
        return jsonify({
            'success': True,
            'message': 'Address deleted successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
