import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    
    # PostgreSQL Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://swaad_sadan_user:lWZIgIDhWCs3nIzklYlE7FSLcp2IzGXT@dpg-d85ctlbtqb8s73fu1rkg-a/swaad_sadan')
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = 2592000  # 30 days
    
    # Contact
    CONTACT_EMAIL = os.getenv('CONTACT_EMAIL', 'swaadsadancafe@gmail.com')
    CONTACT_PHONE = os.getenv('CONTACT_PHONE', '8296064418')
    UPI_ID = os.getenv('UPI_ID', '8296064418@paytm')
    
    # Charges
    BASE_DELIVERY_CHARGE = int(os.getenv('BASE_DELIVERY_CHARGE', 30))
    PARCEL_CHARGE = int(os.getenv('PARCEL_CHARGE', 10))
    FREE_DELIVERY_ABOVE = int(os.getenv('FREE_DELIVERY_ABOVE', 500))
    
    # Admin
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@swaadsadan.com')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    # Razorpay Payment Gateway
    RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID', '')
    RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET', '')
