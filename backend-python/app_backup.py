from flask import Flask, render_template, jsonify
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

# Initialize SQLite Database
db_path = init_db(app.config['DATABASE_PATH'])

# Import routes
from routes import auth, products, orders, catering, events, subscriptions, franchise, admin, payment, settings

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

# Home route
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
def events():
    return render_template('events.html')

@app.route('/catering')
def catering():
    return render_template('catering.html')

@app.route('/subscriptions')
def subscriptions():
    return render_template('subscriptions.html')

@app.route('/health-box')
def health_box():
    return render_template('health_box.html')

@app.route('/franchise')
def franchise():
    return render_template('franchise.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/orders')
def orders():
    return render_template('orders.html')

@app.route('/admin')
def admin_dashboard():
    return render_template('admin.html')

# Health check
@app.route('/api/health')
def health():
    return jsonify({
        'status': 'OK',
        'message': 'SWAAD SADAN API is running',
        'database': 'SQLite (Local)',
        'db_file': app.config['DATABASE_PATH']
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'message': 'Resource not found'}), 404

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
    print(f"🚀 Server running on http://localhost:{port}")
    print(f"🌍 Environment: {app.config['FLASK_ENV']}")
    print(f"\n👤 Admin Login:")
    print(f"   Email: {app.config['ADMIN_EMAIL']}")
    print(f"   Password: {app.config['ADMIN_PASSWORD']}\n")
    app.run(debug=True, port=port, host='0.0.0.0')
