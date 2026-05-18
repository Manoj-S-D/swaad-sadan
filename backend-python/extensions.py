"""Flask extensions initialization"""
import sqlite3
import json
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS

# Initialize extensions (without app)
jwt = JWTManager()
bcrypt = Bcrypt()
cors = CORS()

# Database connection
db_path = None

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

def init_db(database_path):
    """Initialize SQLite database with tables"""
    global db_path
    db_path = database_path
    
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
