# 🔑 WHERE TO ADD RAZORPAY KEYS

## 📍 **File Location**

```
swaad_sadan/
└── backend-python/
    └── .env  ← ADD KEYS HERE
```

Full path: `C:\Users\DMA2\swaad_sadan\backend-python\.env`

---

## ✏️ **What to Edit**

Open the file `backend-python/.env` and find these lines:

```env
# ==========================================
# RAZORPAY PAYMENT GATEWAY
# ==========================================
RAZORPAY_KEY_ID=your_razorpay_key_id_here
RAZORPAY_KEY_SECRET=your_razorpay_key_secret_here
```

**Replace:**
- `your_razorpay_key_id_here` → Your actual Razorpay Key ID
- `your_razorpay_key_secret_here` → Your actual Razorpay Key Secret

---

## 🔐 **How to Get Razorpay Keys**

### **Step 1: Create Razorpay Account**
1. Go to https://razorpay.com/
2. Click "Sign Up" (top right)
3. Fill in your business details
4. Verify your email

### **Step 2: Complete KYC (For Live Mode)**
- Add business details
- Upload PAN card
- Add bank account
- Wait for verification (1-2 days)

### **Step 3: Get API Keys**

#### **For Testing (Use Test Mode):**
1. Login to Razorpay Dashboard
2. Click on **"Settings"** (bottom left)
3. Click on **"API Keys"**
4. Under **"Test Mode"**, click **"Generate Test Key"**
5. Copy both:
   - **Key Id** (starts with `rzp_test_`)
   - **Key Secret** (click "Show" to reveal)

#### **For Production (Use Live Mode):**
1. Complete KYC first (required)
2. Go to **Settings → API Keys**
3. Switch to **"Live Mode"** (toggle at top)
4. Click **"Generate Live Key"**
5. Copy both:
   - **Key Id** (starts with `rzp_live_`)
   - **Key Secret**

---

## 📝 **Example .env File (After Adding Keys)**

```env
# Flask Configuration
SECRET_KEY=your-random-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-this-in-production
FLASK_ENV=development
PORT=5000

# Database
DATABASE_PATH=swaad_sadan.db

# Business Contact Information
CONTACT_EMAIL=swaadsadancafe@gmail.com
CONTACT_PHONE=8296064418
UPI_ID=8296064418@paytm

# Delivery Charges (in rupees)
BASE_DELIVERY_CHARGE=30
PARCEL_CHARGE=10
FREE_DELIVERY_ABOVE=500

# Admin Account
ADMIN_EMAIL=admin@swaadsadan.com
ADMIN_PASSWORD=admin123

# ==========================================
# RAZORPAY PAYMENT GATEWAY
# ==========================================
RAZORPAY_KEY_ID=rzp_test_AbCdEfGhIjKlMnOp
RAZORPAY_KEY_SECRET=1234567890ABCDEFabcdefghijklmno
```

> ⚠️ **Important**: These are example keys. Use your actual keys from Razorpay dashboard!

---

## 🧪 **Testing the Integration**

### **After Adding Keys:**

1. **Restart your application** (if running):
   ```bash
   # Stop the app (Ctrl+C)
   # Start again
   python app.py
   ```

2. **Test in Browser:**
   - Go to http://localhost:5000/menu
   - Add items to cart
   - Go to cart: http://localhost:5000/cart
   - Select **"Pay Online (Razorpay)"** as payment method
   - Click **"Proceed to Checkout"**
   - Razorpay popup should appear!

3. **Test Payment:**
   - Use Razorpay test card:
     - Card Number: `4111 1111 1111 1111`
     - CVV: Any 3 digits
     - Expiry: Any future date
   - Payment should succeed

---

## 🚀 **For Deployment (Render/Cloud)**

### **Don't Edit .env File!**

For deployment, add keys as **Environment Variables** in your hosting dashboard:

#### **On Render.com:**
1. Go to your service
2. Click **"Environment"**
3. Add variables:
   ```
   Key: RAZORPAY_KEY_ID
   Value: rzp_live_your_actual_key
   
   Key: RAZORPAY_KEY_SECRET
   Value: your_actual_secret
   ```
4. Click **"Save Changes"**

---

## ⚠️ **Security Warning**

### **NEVER:**
- ❌ Share your **Key Secret** with anyone
- ❌ Commit `.env` file to GitHub (it's already in `.gitignore`)
- ❌ Use **Live keys** for testing
- ❌ Expose keys in frontend code

### **ALWAYS:**
- ✅ Keep `.env` file private
- ✅ Use **Test keys** for development
- ✅ Use **Live keys** only in production
- ✅ Store keys in environment variables for deployment

---

## 🔍 **How to Verify Keys are Loaded**

### **Check in Browser Console:**
1. Open your website
2. Press `F12` (Developer Tools)
3. Go to **Console** tab
4. Type:
   ```javascript
   fetch('/api/payment/key')
     .then(r => r.json())
     .then(d => console.log(d))
   ```
5. You should see:
   ```json
   {
     "success": true,
     "key": "rzp_test_xxxxx"
   }
   ```

If you see an error, keys are not loaded correctly.

---

## 📂 **Files That Use Razorpay**

### **Backend:**
- `backend-python/.env` ← **ADD KEYS HERE**
- `backend-python/config.py` ← Reads keys from .env
- `backend-python/routes/payment.py` ← Uses keys for Razorpay API

### **Frontend:**
- `backend-python/templates/base.html` ← Razorpay script loaded
- `backend-python/static/js/main.js` ← Payment functions
- `backend-python/templates/cart.html` ← Checkout flow

---

## ✅ **Quick Checklist**

- [ ] Created Razorpay account
- [ ] Got API keys from dashboard
- [ ] Opened `backend-python/.env` file
- [ ] Replaced `your_razorpay_key_id_here` with actual Key ID
- [ ] Replaced `your_razorpay_key_secret_here` with actual Key Secret
- [ ] Saved the file
- [ ] Restarted the application
- [ ] Tested payment flow in browser
- [ ] Payment popup appears
- [ ] Test payment succeeds

---

## 🆘 **Troubleshooting**

### **Problem: "Razorpay not configured" error**
**Solution:** Keys not loaded. Check:
1. File path is correct: `backend-python/.env`
2. No typos in variable names
3. No extra spaces around `=`
4. Restarted application after adding keys

### **Problem: Payment popup doesn't appear**
**Solution:** Check browser console (F12) for errors:
1. Razorpay script loaded? (Check Network tab)
2. Key fetched successfully? (Call `/api/payment/key`)
3. JavaScript errors? (Check Console tab)

### **Problem: Payment verification fails**
**Solution:**
1. Verify **Key Secret** is correct
2. Check server logs for errors
3. Ensure both Key ID and Secret are from same mode (test/live)

---

## 📞 **Support**

If you need help:
1. Check Razorpay documentation: https://razorpay.com/docs/
2. Check application logs
3. Contact: swaadsadancafe@gmail.com

---

**🎉 Once keys are added, your payment gateway will work perfectly!**
