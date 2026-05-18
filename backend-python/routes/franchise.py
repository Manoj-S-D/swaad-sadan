from flask import Blueprint, jsonify

bp = Blueprint('franchise', __name__)

@bp.route('/', methods=['GET'])
def get_franchise():
    return jsonify({'success': True, 'message': 'Franchise routes - coming soon'})
