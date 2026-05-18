from flask import Blueprint, jsonify
from models import Settings

bp = Blueprint('settings', __name__)

@bp.route('/', methods=['GET'])
def get_settings():
    """Get app settings"""
    try:
        settings = Settings.get_settings()
        return jsonify({
            'success': True,
            'settings': settings
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
