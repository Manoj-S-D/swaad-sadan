"""Flask extensions initialization"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS

# Initialize extensions
jwt = JWTManager()
bcrypt = Bcrypt()
cors = CORS()

# Database connection
database_url = None

def get_db():
    """Get PostgreSQL database connection"""
    conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
    return conn

def init_db(db_url):
    """Initialize PostgreSQL database with tables"""
    global database_url
    database_url = db_url
    
    conn = psycopg2.connect(database_url)
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
    cursor.close()
    conn.close()
    
    print("✅ PostgreSQL Database Initialized Successfully")
    return database_url
