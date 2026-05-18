from datetime import datetime
import json
import time

class Database:
    """Database helper class"""
    
    @staticmethod
    def get_db():
        from extensions import get_db
        return get_db()
    
    @staticmethod
    def row_to_dict(row):
        """Convert SQLite Row to dictionary"""
        if row is None:
            return None
        return dict(row)

class User:
    """User model"""
    
    @staticmethod
    def create(data):
        db = Database.get_db()
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO users (name, email, phone, password, role, isActive, addresses)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['name'],
            data['email'],
            data['phone'],
            data['password'],
            data.get('role', 'customer'),
            data.get('isActive', 1),
            json.dumps(data.get('addresses', []))
        ))
        db.commit()
        user_id = cursor.lastrowid
        db.close()
        return user_id
    
    @staticmethod
    def find_by_email(email):
        db = Database.get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        db.close()
        return Database.row_to_dict(user)
    
    @staticmethod
    def find_by_id(user_id):
        db = Database.get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        db.close()
        return Database.row_to_dict(user)

class Product:
    """Product model"""
    
    @staticmethod
    def create(data):
        db = Database.get_db()
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO products (name, description, category, price, image, isVeg, isHealthBox, isAvailable, nutrition)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['name'],
            data.get('description', ''),
            data.get('category', ''),
            data['price'],
            data.get('image', ''),
            data.get('isVeg', 1),
            data.get('isHealthBox', 0),
            data.get('isAvailable', 1),
            json.dumps(data.get('nutrition', {}))
        ))
        db.commit()
        product_id = cursor.lastrowid
        db.close()
        return product_id
    
    @staticmethod
    def find_all(filters=None, include_unavailable=False):
        db = Database.get_db()
        cursor = db.cursor()
        
        # For admin, include all products; for customers, only available ones
        if include_unavailable:
            query = 'SELECT * FROM products WHERE 1=1'
        else:
            # Use TRUE for PostgreSQL compatibility (converts to 1 for SQLite)
            query = 'SELECT * FROM products WHERE isAvailable = TRUE'
        
        params = []
        
        if filters:
            if 'category' in filters:
                query += ' AND category = ?'
                params.append(filters['category'])
            if 'isVeg' in filters:
                query += ' AND isVeg = TRUE' if filters['isVeg'] else ' AND isVeg = FALSE'
            if 'isHealthBox' in filters:
                query += ' AND isHealthBox = TRUE' if filters['isHealthBox'] else ' AND isHealthBox = FALSE'
        
        cursor.execute(query, params)
        products = cursor.fetchall()
        db.close()
        return [Database.row_to_dict(p) for p in products]
    
    @staticmethod
    def find_by_id(product_id):
        db = Database.get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        product = cursor.fetchone()
        db.close()
        return Database.row_to_dict(product)
    
    @staticmethod
    def update(product_id, data):
        db = Database.get_db()
        cursor = db.cursor()
        
        fields = []
        values = []
        
        for key, value in data.items():
            if key in ['name', 'description', 'category', 'price', 'image', 'isVeg', 'isHealthBox', 'isAvailable']:
                fields.append(f'{key} = ?')
                values.append(value)
        
        if fields:
            values.append(product_id)
            cursor.execute(f'UPDATE products SET {", ".join(fields)} WHERE id = ?', values)
            db.commit()
        
        db.close()
    
    @staticmethod
    def delete(product_id):
        db = Database.get_db()
        cursor = db.cursor()
        cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
        db.commit()
        db.close()

class Order:
    """Order model"""
    
    @staticmethod
    def create(data):
        db = Database.get_db()
        cursor = db.cursor()
        
        # Generate order number
        cursor.execute('SELECT COUNT(*) as count FROM orders')
        count = cursor.fetchone()[0]
        order_number = f"SS{int(time.time())}{count + 1}"
        
        cursor.execute('''
            INSERT INTO orders (orderNumber, userId, items, orderType, deliveryAddress, pricing, payment, status, specialInstructions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            order_number,
            data['user'],
            json.dumps(data['items']),
            data['orderType'],
            data.get('deliveryAddress', ''),
            json.dumps(data['pricing']),
            json.dumps(data['payment']),
            data.get('status', 'pending'),
            data.get('specialInstructions', '')
        ))
        db.commit()
        order_id = cursor.lastrowid
        db.close()
        return order_id
    
    @staticmethod
    def find_by_user(user_id):
        db = Database.get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM orders WHERE userId = ? ORDER BY createdAt DESC', (user_id,))
        orders = cursor.fetchall()
        db.close()
        return [Database.row_to_dict(o) for o in orders]
    
    @staticmethod
    def find_by_id(order_id):
        db = Database.get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
        order = cursor.fetchone()
        db.close()
        return Database.row_to_dict(order)
    
    @staticmethod
    def find_all(filters=None):
        db = Database.get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM orders ORDER BY createdAt DESC')
        orders = cursor.fetchall()
        db.close()
        return [Database.row_to_dict(o) for o in orders]

class Settings:
    """Settings model"""
    
    @staticmethod
    def get_settings():
        db = Database.get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM settings WHERE id = 1')
        settings = cursor.fetchone()
        
        if not settings:
            # Create default settings
            default_settings = {
                'deliveryCharges': json.dumps({
                    'baseCharge': 30,
                    'perKmCharge': 5,
                    'freeDeliveryAbove': 500
                }),
                'parcelCharge': 10,
                'offers': json.dumps([]),
                'contactInfo': json.dumps({
                    'email': 'swaadsadancafe@gmail.com',
                    'phone': '8296064418',
                    'upiId': '8296064418@paytm'
                }),
                'trustBadges': json.dumps({
                    'freshVegetables': True,
                    'qualityGrains': True,
                    'bestOil': True,
                    'hygienicPreparation': True
                })
            }
            # Don't specify id - let database auto-generate or use default
            cursor.execute('''
                INSERT INTO settings (deliveryCharges, parcelCharge, offers, contactInfo, trustBadges)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                default_settings['deliveryCharges'],
                default_settings['parcelCharge'],
                default_settings['offers'],
                default_settings['contactInfo'],
                default_settings['trustBadges']
            ))
            db.commit()
            cursor.execute('SELECT * FROM settings WHERE id = 1')
            settings = cursor.fetchone()
        
        db.close()
        result = Database.row_to_dict(settings)
        
        # Parse JSON fields
        if result:
            result['deliveryCharges'] = json.loads(result['deliveryCharges'])
            result['offers'] = json.loads(result['offers'])
            result['contactInfo'] = json.loads(result['contactInfo'])
            result['trustBadges'] = json.loads(result['trustBadges'])
        
        return result
    
    @staticmethod
    def update_settings(data):
        db = Database.get_db()
        cursor = db.cursor()
        # Update settings implementation
        db.close()
