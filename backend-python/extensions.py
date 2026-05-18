"""Flask extensions initialization"""
import sqlite3
import json
import os
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS

# Initialize extensions (without app)
jwt = JWTManager()
bcrypt = Bcrypt()
cors = CORS()

# Database configuration
db_url = None
db_path = None
use_postgres = False

# Import PostgreSQL only if needed
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

class UnifiedCursor:
    """Wrapper cursor that works with both SQLite and PostgreSQL"""
    
    def __init__(self, cursor, is_postgres=False):
        self.cursor = cursor
        self.is_postgres = is_postgres
        self.lastrowid = None
    
    def execute(self, query, params=None):
        """Execute query with automatic conversion"""
        if self.is_postgres:
            # Convert ? to %s for PostgreSQL
            query = query.replace('?', '%s')
            
            # Convert SQLite json_extract to PostgreSQL ->
            # Example: json_extract(payment, '$.status') becomes payment->>'status'
            import re
            query = re.sub(r"json_extract\((\w+),\s*'\$\.(\w+)'\)", r"\1->>'\2'", query)
            
            # Convert SQLite date functions to PostgreSQL
            # Cast to TEXT for compatibility with TEXT date columns
            query = query.replace("date('now')", "CURRENT_DATE::TEXT")
            query = query.replace("datetime('now')", "CURRENT_TIMESTAMP::TEXT")
            
            # Convert hardcoded boolean 0 and 1 values in INSERT VALUES
            # Match only single digit 0 or 1 surrounded by commas/parentheses
            if 'INSERT INTO' in query.upper():
                # These patterns ensure we only match single digit 0 or 1
                query = re.sub(r',\s*1\s*\)', ', TRUE)', query)  # ", 1)" at end
                query = re.sub(r',\s*0\s*\)', ', FALSE)', query)  # ", 0)" at end  
                query = re.sub(r'\(\s*1\s*,', '(TRUE,', query)  # "(1," at start
                query = re.sub(r'\(\s*0\s*,', '(FALSE,', query)  # "(0," at start
                query = re.sub(r',\s*1\s*,', ', TRUE,', query)  # ", 1," in middle
                query = re.sub(r',\s*0\s*,', ', FALSE,', query)  # ", 0," in middle
            
            # Convert INSERT to use RETURNING id
            if 'INSERT INTO' in query.upper() and 'RETURNING' not in query.upper():
                query = query.rstrip(';').rstrip() + ' RETURNING id'
            
            # Convert integer params (0/1) to boolean for PostgreSQL boolean columns
            if params:
                params = self._convert_params_for_postgres(query, params)
        
        result = self.cursor.execute(query, params or ())
        
        # Handle RETURNING id for PostgreSQL - fetch it immediately and store
        if self.is_postgres and 'RETURNING id' in query.upper():
            try:
                returned = self.cursor.fetchone()
                if returned:
                    self.lastrowid = returned['id'] if isinstance(returned, dict) else returned[0]
            except:
                # If no result or error, leave lastrowid as None
                pass
        
        return result
    
    def fetchone(self):
        """Fetch one row and convert booleans to integers"""
        row = self.cursor.fetchone()
        if row and self.is_postgres:
            return self._convert_row(row)
        return row
    
    def fetchall(self):
        """Fetch all rows and convert booleans to integers"""
        rows = self.cursor.fetchall()
        if rows and self.is_postgres:
            return [self._convert_row(row) for row in rows]
        return rows
    
    def _convert_row(self, row):
        """Convert PostgreSQL dict/booleans to SQLite-compatible format"""
        if isinstance(row, dict):
            # Convert dict to support both dict['key'] and row[0] access
            # Also fix PostgreSQL lowercase column names to match SQLite case
            converted = {}
            
            # Map PostgreSQL lowercase to original SQLite case
            case_map = {
                'isactive': 'isActive',
                'isavailable': 'isAvailable',
                'isveg': 'isVeg',
                'ishealthbox': 'isHealthBox',
                'createdat': 'createdAt',
                'updatedat': 'updatedAt',
                'userid': 'userId',
                'ordertype': 'orderType',
                'ordernumber': 'orderNumber',
                'deliveryaddress': 'deliveryAddress',
                'specialinstructions': 'specialInstructions',
                'mealsperdday': 'mealsPerDay',
                'usagelimit': 'usageLimit',
                'usedcount': 'usedCount',
                'minordervalue': 'minOrderValue',
                'maxdiscount': 'maxDiscount',
                'expirydate': 'expiryDate',
                'priceperperson': 'pricePerPerson',
                'menuitems': 'menuItems',
                'minguests': 'minGuests',
                'maxguests': 'maxGuests',
                'eventtype': 'eventType',
                'requestnumber': 'requestNumber',
                'servicetype': 'serviceType',
                'packageid': 'packageId',
                'requestdata': 'requestData',
                'scheduleddate': 'scheduledDate',
                'scheduledtime': 'scheduledTime',
                'totalamount': 'totalAmount',
                'requestid': 'requestId',
                'senderid': 'senderId',
                'senderrole': 'senderRole',
                'couponid': 'couponId',
                'orderid': 'orderId',
                'discountamount': 'discountAmount',
                'usedat': 'usedAt',
                'totalearned': 'totalEarned',
                'totalredeemed': 'totalRedeemed',
                'contactinfo': 'contactInfo',
                'deliverycharges': 'deliveryCharges',
                'parcelcharge': 'parcelCharge',
                'trustbadges': 'trustBadges'
            }
            
            for key, value in row.items():
                # Convert key case
                correct_case_key = case_map.get(key.lower(), key)
                
                # Convert boolean to int
                if isinstance(value, bool):
                    converted[correct_case_key] = 1 if value else 0
                else:
                    converted[correct_case_key] = value
            
            # Create a hybrid object that supports both dict and tuple access
            class DictRow(dict):
                def __getitem__(self, key):
                    if isinstance(key, int):
                        # For integer index, return values in order
                        return list(self.values())[key]
                    return super().__getitem__(key)
            
            return DictRow(converted)
        return row
    
    def _convert_params_for_postgres(self, query, params):
        """Convert integer 0/1 to boolean False/True for PostgreSQL boolean columns"""
        # Define ALL boolean columns for each table
        boolean_columns = {
            'users': ['isActive'],
            'products': ['isVeg', 'isHealthBox', 'isAvailable'],
            'coupons': ['isActive'],
            'subscription_plans': ['isActive'],
            'catering_packages': ['isActive'],
            'event_packages': ['isActive'],
            'orders': [],  # No boolean columns
            'settings': [],  # No boolean columns
            'loyalty_points': [],  # No boolean columns
            'coupon_usage': [],  # No boolean columns
            'service_requests': [],  # No boolean columns
            'request_messages': []  # No boolean columns
        }
        
        # Extract table name from query
        table_name = None
        if 'INSERT INTO' in query.upper():
            import re
            match = re.search(r'INSERT INTO (\w+)', query, re.IGNORECASE)
            if match:
                table_name = match.group(1)
        elif 'UPDATE' in query.upper():
            import re
            match = re.search(r'UPDATE (\w+)', query, re.IGNORECASE)
            if match:
                table_name = match.group(1)
        
        if not table_name or table_name not in boolean_columns:
            return params
        
        bool_cols = boolean_columns.get(table_name, [])
        if not bool_cols:
            return params  # No boolean columns in this table
        
        # Extract column names from query
        if 'INSERT INTO' in query.upper():
            import re
            # Match: INSERT INTO table (col1, col2, ...) VALUES
            match = re.search(r'\(([^)]+)\)\s*VALUES', query, re.IGNORECASE)
            if match:
                columns = [col.strip() for col in match.group(1).split(',')]
                
                # Convert params to list if it's tuple
                params_list = list(params)
                for idx, col in enumerate(columns):
                    if col in bool_cols and idx < len(params_list):
                        val = params_list[idx]
                        # Convert 0/1 to False/True
                        if val == 0:
                            params_list[idx] = False
                        elif val == 1:
                            params_list[idx] = True
                return tuple(params_list)
        
        elif 'UPDATE' in query.upper():
            # For UPDATE queries - convert all 0/1 integers to booleans
            # This is a heuristic since we can't easily parse UPDATE SET clauses
            params_list = list(params)
            for idx, val in enumerate(params_list):
                # Only convert if it's exactly 0 or 1
                if val == 0:
                    params_list[idx] = False
                elif val == 1:
                    params_list[idx] = True
            return tuple(params_list)
        
        return params

class UnifiedConnection:
    """Wrapper connection that provides unified interface"""
    
    def __init__(self, conn, is_postgres=False):
        self.conn = conn
        self.is_postgres = is_postgres
    
    def cursor(self):
        """Return wrapped cursor"""
        if self.is_postgres:
            cursor = self.conn.cursor()
        else:
            cursor = self.conn.cursor()
        return UnifiedCursor(cursor, self.is_postgres)
    
    def commit(self):
        return self.conn.commit()
    
    def rollback(self):
        return self.conn.rollback()
    
    def close(self):
        return self.conn.close()
    
    @property
    def row_factory(self):
        if not self.is_postgres:
            return self.conn.row_factory
        return None
    
    @row_factory.setter
    def row_factory(self, value):
        if not self.is_postgres:
            self.conn.row_factory = value

def get_db():
    """Get unified database connection"""
    if use_postgres:
        conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        return UnifiedConnection(conn, is_postgres=True)
    else:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return UnifiedConnection(conn, is_postgres=False)

def init_db(database_url=None, database_path=None):
    """Initialize database (PostgreSQL or SQLite)"""
    global db_url, db_path, use_postgres
    
    # Determine which database to use
    if database_url and HAS_POSTGRES:
        db_url = database_url
        use_postgres = True
        print("🐘 Using PostgreSQL database")
        return _init_postgres()
    else:
        db_path = database_path
        use_postgres = False
        print("📁 Using SQLite database")
        return _init_sqlite()

def _init_sqlite():
    """Initialize SQLite database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'customer',
            isActive INTEGER DEFAULT 1,
            addresses TEXT DEFAULT '[]',
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT,
            price REAL NOT NULL,
            image TEXT,
            isVeg INTEGER DEFAULT 1,
            isHealthBox INTEGER DEFAULT 0,
            isAvailable INTEGER DEFAULT 1,
            rating REAL DEFAULT 0,
            reviews TEXT DEFAULT '[]',
            nutrition TEXT DEFAULT '{}',
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orderNumber TEXT UNIQUE NOT NULL,
            userId INTEGER NOT NULL,
            items TEXT NOT NULL,
            orderType TEXT NOT NULL,
            deliveryAddress TEXT,
            pricing TEXT NOT NULL,
            payment TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            specialInstructions TEXT,
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (userId) REFERENCES users (id)
        )
    ''')
    
    # Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            deliveryCharges TEXT NOT NULL,
            parcelCharge INTEGER DEFAULT 10,
            offers TEXT DEFAULT '[]',
            contactInfo TEXT NOT NULL,
            trustBadges TEXT DEFAULT '{}',
            updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Loyalty Points table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS loyalty_points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userId INTEGER NOT NULL,
            points INTEGER DEFAULT 0,
            totalEarned INTEGER DEFAULT 0,
            totalRedeemed INTEGER DEFAULT 0,
            updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (userId) REFERENCES users (id)
        )
    ''')
    
    # Coupons table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS coupons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            type TEXT NOT NULL,
            value REAL NOT NULL,
            maxDiscount REAL,
            minOrderValue REAL DEFAULT 0,
            category TEXT,
            description TEXT,
            expiryDate TEXT NOT NULL,
            usageLimit INTEGER DEFAULT 1,
            usedCount INTEGER DEFAULT 0,
            isActive INTEGER DEFAULT 1,
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Coupon Usage table (track which users used which coupons)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS coupon_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            couponId INTEGER NOT NULL,
            userId INTEGER NOT NULL,
            orderId INTEGER NOT NULL,
            discountAmount REAL NOT NULL,
            usedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (couponId) REFERENCES coupons (id),
            FOREIGN KEY (userId) REFERENCES users (id),
            FOREIGN KEY (orderId) REFERENCES orders (id)
        )
    ''')
    
    # Subscription Plans table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscription_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            duration TEXT NOT NULL,
            price REAL NOT NULL,
            mealsPerDay INTEGER DEFAULT 1,
            features TEXT DEFAULT '[]',
            isActive INTEGER DEFAULT 1,
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Catering Packages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS catering_packages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            type TEXT NOT NULL,
            minGuests INTEGER NOT NULL,
            maxGuests INTEGER,
            pricePerPerson REAL NOT NULL,
            menuItems TEXT DEFAULT '[]',
            features TEXT DEFAULT '[]',
            isActive INTEGER DEFAULT 1,
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Event Packages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS event_packages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            eventType TEXT NOT NULL,
            capacity INTEGER NOT NULL,
            price REAL NOT NULL,
            duration TEXT,
            inclusions TEXT DEFAULT '[]',
            venue TEXT,
            isActive INTEGER DEFAULT 1,
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Service Requests table (for catering, events, subscriptions)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS service_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            requestNumber TEXT UNIQUE NOT NULL,
            userId INTEGER NOT NULL,
            serviceType TEXT NOT NULL,
            packageId INTEGER,
            requestData TEXT NOT NULL,
            scheduledDate TEXT,
            scheduledTime TEXT,
            status TEXT DEFAULT 'pending',
            totalAmount REAL,
            notes TEXT,
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (userId) REFERENCES users (id)
        )
    ''')
    
    # Request Messages table (for admin-customer chat)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS request_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            requestId INTEGER NOT NULL,
            senderId INTEGER NOT NULL,
            senderRole TEXT NOT NULL,
            message TEXT NOT NULL,
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (requestId) REFERENCES service_requests (id),
            FOREIGN KEY (senderId) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print("✅ SQLite Database Initialized Successfully")
    return db_path

def _init_postgres():
    """Initialize PostgreSQL database"""
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'customer',
            isActive BOOLEAN DEFAULT TRUE,
            addresses JSONB DEFAULT '[]',
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT,
            price REAL NOT NULL,
            image TEXT,
            isVeg BOOLEAN DEFAULT TRUE,
            isHealthBox BOOLEAN DEFAULT FALSE,
            isAvailable BOOLEAN DEFAULT TRUE,
            rating REAL DEFAULT 0,
            reviews JSONB DEFAULT '[]',
            nutrition JSONB DEFAULT '{}',
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            orderNumber TEXT UNIQUE NOT NULL,
            userId INTEGER NOT NULL,
            items JSONB NOT NULL,
            orderType TEXT NOT NULL,
            deliveryAddress TEXT,
            pricing JSONB NOT NULL,
            payment JSONB NOT NULL,
            status TEXT DEFAULT 'pending',
            specialInstructions TEXT,
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (userId) REFERENCES users (id)
        )
    ''')
    
    # Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id SERIAL PRIMARY KEY,
            deliveryCharges JSONB NOT NULL,
            parcelCharge INTEGER DEFAULT 10,
            offers JSONB DEFAULT '[]',
            contactInfo JSONB NOT NULL,
            trustBadges JSONB DEFAULT '{}',
            updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Loyalty Points table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS loyalty_points (
            id SERIAL PRIMARY KEY,
            userId INTEGER NOT NULL,
            points INTEGER DEFAULT 0,
            totalEarned INTEGER DEFAULT 0,
            totalRedeemed INTEGER DEFAULT 0,
            updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (userId) REFERENCES users (id)
        )
    ''')
    
    # Coupons table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS coupons (
            id SERIAL PRIMARY KEY,
            code TEXT UNIQUE NOT NULL,
            type TEXT NOT NULL,
            value REAL NOT NULL,
            maxDiscount REAL,
            minOrderValue REAL DEFAULT 0,
            category TEXT,
            description TEXT,
            expiryDate TEXT NOT NULL,
            usageLimit INTEGER DEFAULT 1,
            usedCount INTEGER DEFAULT 0,
            isActive BOOLEAN DEFAULT TRUE,
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Coupon Usage table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS coupon_usage (
            id SERIAL PRIMARY KEY,
            couponId INTEGER NOT NULL,
            userId INTEGER NOT NULL,
            orderId INTEGER NOT NULL,
            discountAmount REAL NOT NULL,
            usedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (couponId) REFERENCES coupons (id),
            FOREIGN KEY (userId) REFERENCES users (id),
            FOREIGN KEY (orderId) REFERENCES orders (id)
        )
    ''')
    
    # Subscription Plans table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscription_plans (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            duration TEXT NOT NULL,
            price REAL NOT NULL,
            mealsPerDay INTEGER DEFAULT 1,
            features JSONB DEFAULT '[]',
            isActive BOOLEAN DEFAULT TRUE,
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Catering Packages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS catering_packages (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            type TEXT NOT NULL,
            minGuests INTEGER NOT NULL,
            maxGuests INTEGER,
            pricePerPerson REAL NOT NULL,
            menuItems JSONB DEFAULT '[]',
            features JSONB DEFAULT '[]',
            isActive BOOLEAN DEFAULT TRUE,
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Event Packages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS event_packages (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            eventType TEXT NOT NULL,
            capacity INTEGER NOT NULL,
            price REAL NOT NULL,
            duration TEXT,
            inclusions JSONB DEFAULT '[]',
            venue TEXT,
            isActive BOOLEAN DEFAULT TRUE,
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Service Requests table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS service_requests (
            id SERIAL PRIMARY KEY,
            requestNumber TEXT UNIQUE NOT NULL,
            userId INTEGER NOT NULL,
            serviceType TEXT NOT NULL,
            packageId INTEGER,
            requestData JSONB NOT NULL,
            scheduledDate TEXT,
            scheduledTime TEXT,
            status TEXT DEFAULT 'pending',
            totalAmount REAL,
            notes TEXT,
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (userId) REFERENCES users (id)
        )
    ''')
    
    # Request Messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS request_messages (
            id SERIAL PRIMARY KEY,
            requestId INTEGER NOT NULL,
            senderId INTEGER NOT NULL,
            senderRole TEXT NOT NULL,
            message TEXT NOT NULL,
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (requestId) REFERENCES service_requests (id),
            FOREIGN KEY (senderId) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print("✅ PostgreSQL Database Initialized Successfully")
    return db_url
