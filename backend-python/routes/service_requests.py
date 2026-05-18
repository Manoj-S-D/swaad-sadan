from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import get_db
import json
import random
import string
from datetime import datetime

bp = Blueprint('requests', __name__)

def generate_request_number():
    """Generate unique request number"""
    prefix = 'REQ'
    timestamp = datetime.now().strftime('%Y%m%d')
    random_suffix = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}{timestamp}{random_suffix}"

@bp.route('/', methods=['POST'])
@jwt_required()
def create_request():
    """Create new service request"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Generate unique request number
        request_number = generate_request_number()
        
        # Insert request
        cursor.execute('''
            INSERT INTO service_requests 
            (requestNumber, userId, serviceType, packageId, requestData, scheduledDate, scheduledTime, totalAmount, notes, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            request_number,
            current_user_id,
            data['serviceType'],
            data.get('packageId'),
            json.dumps(data.get('requestData', {})),
            data.get('scheduledDate'),
            data.get('scheduledTime'),
            data.get('totalAmount'),
            data.get('notes', ''),
            'pending'
        ))
        
        request_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Request submitted successfully!',
            'requestNumber': request_number,
            'requestId': request_id
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/my-requests', methods=['GET'])
@jwt_required()
def get_my_requests():
    """Get user's requests"""
    try:
        current_user_id = int(get_jwt_identity())
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM service_requests 
            WHERE userId = ? 
            ORDER BY createdAt DESC
        ''', (current_user_id,))
        
        requests = [dict(row) for row in cursor.fetchall()]
        
        # Parse JSON fields
        for req in requests:
            req['requestData'] = json.loads(req.get('requestData', '{}'))
        
        conn.close()
        return jsonify({'success': True, 'requests': requests})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/all', methods=['GET'])
@jwt_required()
def get_all_requests():
    """Get all requests (admin only)"""
    try:
        current_user_id = int(get_jwt_identity())
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Check if user is admin
        cursor.execute('SELECT role FROM users WHERE id = ?', (current_user_id,))
        user = cursor.fetchone()
        
        if not user or user['role'] != 'admin':
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        # Get filter parameters
        service_type = request.args.get('serviceType')
        status = request.args.get('status')
        
        query = '''
            SELECT sr.*, u.name as userName, u.email as userEmail, u.phone as userPhone
            FROM service_requests sr
            JOIN users u ON sr.userId = u.id
            WHERE 1=1
        '''
        params = []
        
        if service_type:
            query += ' AND sr.serviceType = ?'
            params.append(service_type)
        
        if status:
            query += ' AND sr.status = ?'
            params.append(status)
        
        query += ' ORDER BY sr.createdAt DESC'
        
        cursor.execute(query, params)
        requests = [dict(row) for row in cursor.fetchall()]
        
        # Parse JSON fields
        for req in requests:
            req['requestData'] = json.loads(req.get('requestData', '{}'))
        
        conn.close()
        return jsonify({'success': True, 'requests': requests})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/<int:request_id>', methods=['GET'])
@jwt_required()
def get_request(request_id):
    """Get request details"""
    try:
        current_user_id = int(get_jwt_identity())
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Get user role
        cursor.execute('SELECT role FROM users WHERE id = ?', (current_user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        # Get request
        cursor.execute('''
            SELECT sr.*, u.name as userName, u.email as userEmail, u.phone as userPhone
            FROM service_requests sr
            JOIN users u ON sr.userId = u.id
            WHERE sr.id = ?
        ''', (request_id,))
        
        req = cursor.fetchone()
        
        if not req:
            return jsonify({'success': False, 'message': 'Request not found'}), 404
        
        # Check authorization - user must be admin OR the owner of the request
        if user['role'] != 'admin' and int(req['userId']) != current_user_id:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        request_data = dict(req)
        request_data['requestData'] = json.loads(request_data.get('requestData', '{}'))
        
        # Get messages
        cursor.execute('''
            SELECT rm.*, u.name as senderName
            FROM request_messages rm
            JOIN users u ON rm.senderId = u.id
            WHERE rm.requestId = ?
            ORDER BY rm.createdAt ASC
        ''', (request_id,))
        
        messages = [dict(row) for row in cursor.fetchall()]
        request_data['messages'] = messages
        
        conn.close()
        return jsonify({'success': True, 'request': request_data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/<int:request_id>/status', methods=['PUT'])
@jwt_required()
def update_request_status(request_id):
    """Update request status (admin only)"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Check if user is admin
        cursor.execute('SELECT role FROM users WHERE id = ?', (current_user_id,))
        user = cursor.fetchone()
        
        if not user or user['role'] != 'admin':
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        # Update status
        cursor.execute('''
            UPDATE service_requests 
            SET status = ?, updatedAt = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (data['status'], request_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Request {data["status"]} successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/<int:request_id>/messages', methods=['POST'])
@jwt_required()
def add_message(request_id):
    """Add message to request"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Get user role
        cursor.execute('SELECT role FROM users WHERE id = ?', (current_user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        # Check if user has access to this request
        cursor.execute('SELECT userId FROM service_requests WHERE id = ?', (request_id,))
        req = cursor.fetchone()
        
        if not req:
            return jsonify({'success': False, 'message': 'Request not found'}), 404
        
        if user['role'] != 'admin' and int(req['userId']) != current_user_id:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        # Insert message
        cursor.execute('''
            INSERT INTO request_messages (requestId, senderId, senderRole, message)
            VALUES (?, ?, ?, ?)
        ''', (request_id, current_user_id, user['role'], data['message']))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Message sent successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/live-upcoming', methods=['GET'])
@jwt_required()
def get_live_upcoming():
    """Get live and upcoming requests (admin only)"""
    try:
        current_user_id = int(get_jwt_identity())
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Check if user is admin
        cursor.execute('SELECT role FROM users WHERE id = ?', (current_user_id,))
        user = cursor.fetchone()
        
        if not user or user['role'] != 'admin':
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Get live requests (happening today)
        cursor.execute('''
            SELECT sr.*, u.name as userName, u.email as userEmail
            FROM service_requests sr
            JOIN users u ON sr.userId = u.id
            WHERE sr.status = 'confirmed' AND sr.scheduledDate = ?
            ORDER BY sr.scheduledTime ASC
        ''', (today,))
        
        live_requests = [dict(row) for row in cursor.fetchall()]
        
        # Get upcoming requests (future dates)
        cursor.execute('''
            SELECT sr.*, u.name as userName, u.email as userEmail
            FROM service_requests sr
            JOIN users u ON sr.userId = u.id
            WHERE sr.status = 'confirmed' AND sr.scheduledDate > ?
            ORDER BY sr.scheduledDate ASC, sr.scheduledTime ASC
        ''', (today,))
        
        upcoming_requests = [dict(row) for row in cursor.fetchall()]
        
        # Parse JSON fields
        for req in live_requests + upcoming_requests:
            req['requestData'] = json.loads(req.get('requestData', '{}'))
        
        conn.close()
        return jsonify({
            'success': True,
            'live': live_requests,
            'upcoming': upcoming_requests
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
