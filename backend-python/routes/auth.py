from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import User, Database
from extensions import bcrypt
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
