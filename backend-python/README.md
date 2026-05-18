# SWAAD SADAN - Python Flask Application

A complete food service platform built with Python Flask and MongoDB.

## 🚀 Quick Start (Python)

### Prerequisites
- Python 3.8 or higher
- **No database installation needed!** Uses SQLite (local file)
- pip (Python package manager)

### Installation & Setup

1. **Install Python dependencies:**
```bash
cd backend-python
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
# Copy and edit .env file
cp .env.example .env
# Edit .env with your MongoDB URI
```

3. **Run the application:**
```bash
python app.py
```

The application will start at: **http://localhost:5000**

### Default Admin Credentials
- Email: admin@swaadsadan.com
- Password: admin123

(Admin user is created automatically on first run)

## 📁 Project Structure

```
backend-python/
├── app.py              # Main Flask application
├── models.py           # Database models
├── routes/             # API routes
│   ├── auth.py
│   ├── products.py
│   ├── orders.py
│   └── ...
├── templates/          # HTML templates
├── static/            # CSS, JS, images
├── config.py          # Configuration
└── requirements.txt   # Python dependencies
```

## 🎯 Features

All features from the original specification:
- ✅ Online Food Ordering
- ✅ Catering Services
- ✅ Event Booking
- ✅ Meal Subscriptions
- ✅ Health Box
- ✅ Franchise System
- ✅ Admin Dashboard
- ✅ Payment Integration (Razorpay)

## 📞 Contact

- Email: swaadsadancafe@gmail.com
- Phone: 8296064418
