from flask import Flask, render_template, jsonify, request, send_from_directory
from config import Config
from extensions import jwt, bcrypt, cors, init_db
import os

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions with app
cors.init_app(app)
jwt.init_app(app)
bcrypt.init_app(app)

# Initialize Database (auto-detects PostgreSQL or SQLite)
init_db(
    database_url=app.config.get('DATABASE_URL'),
    database_path=app.config['DATABASE_PATH']
)

# Import routes
from routes import auth, products, orders, catering, events, subscriptions, franchise, admin, payment, settings, loyalty, coupons, service_requests

# Register blueprints
app.register_blueprint(auth.bp, url_prefix='/api/auth')
app.register_blueprint(products.bp, url_prefix='/api/products')
app.register_blueprint(orders.bp, url_prefix='/api/orders')
app.register_blueprint(catering.bp, url_prefix='/api/catering')
app.register_blueprint(events.bp, url_prefix='/api/events')
app.register_blueprint(subscriptions.bp, url_prefix='/api/subscriptions')
app.register_blueprint(franchise.bp, url_prefix='/api/franchise')
app.register_blueprint(admin.bp, url_prefix='/api/admin')
app.register_blueprint(payment.bp, url_prefix='/api/payment')
app.register_blueprint(settings.bp, url_prefix='/api/settings')
app.register_blueprint(loyalty.bp, url_prefix='/api/loyalty')
app.register_blueprint(coupons.bp, url_prefix='/api/coupons')
app.register_blueprint(service_requests.bp, url_prefix='/api/requests')

#  ==================== WEB ROUTES ====================

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/events')
def events_page():
    return render_template('events.html')

@app.route('/catering')
def catering_page():
    return render_template('catering.html')

@app.route('/subscriptions')
def subscriptions_page():
    return render_template('subscriptions.html')

@app.route('/health-box')
def health_box():
    return render_template('health_box.html')

@app.route('/franchise')
def franchise_page():
    return render_template('franchise.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/my-orders')
def my_orders():
    return render_template('orders.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/request-details')
def request_details():
    return render_template('request_details.html')

@app.route('/admin')
def admin_dashboard():
    return render_template('admin.html')

@app.route('/admin-dashboard')
def admin_dashboard_redirect():
    """Redirect old URL to new admin URL"""
    from flask import redirect
    return redirect('/admin')

@app.route('/admin/manage-products')
def admin_manage_products():
    return render_template('admin_products.html')

@app.route('/admin/manage-subscriptions')
def admin_manage_subscriptions():
    return render_template('admin_subscriptions.html')

@app.route('/admin/manage-catering')
def admin_manage_catering():
    return render_template('admin_catering.html')

@app.route('/admin/manage-events')
def admin_manage_events():
    return render_template('admin_events.html')

@app.route('/admin/manage-coupons')
def admin_manage_coupons():
    return render_template('admin_coupons.html')

@app.route('/admin/manage-orders')
def admin_manage_orders():
    return render_template('admin_orders.html')

@app.route('/admin/live-bookings')
def admin_live_bookings():
    from datetime import datetime
    current_date = datetime.now().strftime('%B %d, %Y')
    return render_template('admin_schedule.html', current_date=current_date)

# ==================== API ROUTES ====================

@app.route('/api/health')
def health():
    from extensions import use_postgres, db_url, db_path
    return jsonify({
        'status': 'OK',
        'message': 'SWAAD SADAN API is running',
        'database': 'PostgreSQL' if use_postgres else 'SQLite',
        'db_info': db_url if use_postgres else db_path
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'message': 'Internal server error'}), 500

# Create default admin user on first run
def create_default_admin():
    from models import User
    from extensions import bcrypt as bcrypt_ext
    
    admin_exists = User.find_by_email(app.config['ADMIN_EMAIL'])
    
    if not admin_exists:
        hashed_password = bcrypt_ext.generate_password_hash(app.config['ADMIN_PASSWORD']).decode('utf-8')
        admin_user = {
            'name': 'Admin',
            'email': app.config['ADMIN_EMAIL'],
            'phone': app.config['CONTACT_PHONE'],
            'password': hashed_password,
            'role': 'admin',
            'isActive': True,
            'addresses': []
        }
        User.create(admin_user)
        print(f"✅ Default admin created: {app.config['ADMIN_EMAIL']}")

if __name__ == '__main__':
    create_default_admin()
    port = int(os.getenv('PORT', 5000))
    print(f"\n{'='*60}")
    print(f"🚀 SWAAD SADAN - Web Application Running!")
    print(f"{'='*60}")
    print(f"🌍 Homepage:        http://localhost:{port}")
    print(f"🍽️  Menu:            http://localhost:{port}/menu")
    print(f"🎉 Events:          http://localhost:{port}/events")
    print(f"📦 Subscriptions:   http://localhost:{port}/subscriptions")
    print(f"💪 Health Box:      http://localhost:{port}/health-box")
    print(f"🏢 Franchise:       http://localhost:{port}/franchise")
    print(f"👨‍💼 Admin Dashboard: http://localhost:{port}/admin")
    print(f"{'='*60}")
    print(f"\n👤 Admin Login Credentials:")
    print(f"   Email:    {app.config['ADMIN_EMAIL']}")
    print(f"   Password: {app.config['ADMIN_PASSWORD']}")
    print(f"\n📊 Admin Management URLs:")
    print(f"   Products:      http://localhost:{port}/admin/manage-products")
    print(f"   Orders:        http://localhost:{port}/admin/manage-orders")
    print(f"   Subscriptions: http://localhost:{port}/admin/manage-subscriptions")
    print(f"   Catering:      http://localhost:{port}/admin/manage-catering")
    print(f"   Events:        http://localhost:{port}/admin/manage-events")
    print(f"   Coupons:       http://localhost:{port}/admin/manage-coupons")
    print(f"\n{'='*60}\n")
    app.run(debug=True, port=port, host='0.0.0.0')
