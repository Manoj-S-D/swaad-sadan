# 🚀 RENDER DEPLOYMENT GUIDE - SWAAD SADAN

## 📋 REQUIRED INPUTS FOR RENDER

### 1. **Service Settings**

| Setting | Value |
|---------|-------|
| **Service Name** | `swaad-sadan` (or your choice) |
| **Environment** | `Docker` |
| **Region** | Choose closest to your location |
| **Branch** | `main` |
| **Root Directory** | `backend-python` |

### 2. **Build & Deploy Settings**

| Setting | Value |
|---------|-------|
| **Dockerfile Path** | `./Dockerfile` |
| **Docker Context** | `backend-python` |

> **Note**: Render will automatically detect and use the Dockerfile

---

## 🔑 ENVIRONMENT VARIABLES (CRITICAL!)

Add these in Render Dashboard → Environment → Environment Variables:

### **Security Keys (REQUIRED)**
```
SECRET_KEY=your-random-secret-key-min-32-chars
JWT_SECRET_KEY=your-jwt-secret-key-min-32-chars
```

> 🔐 **Generate secure keys**: Visit https://randomkeygen.com/ and use "504-bit WPA Key"

### **Flask Configuration**
```
FLASK_ENV=production
PORT=10000
```

### **Database**
```
DATABASE_PATH=/app/data/swaad_sadan.db
```

### **Business Information**
```
CONTACT_EMAIL=swaadsadancafe@gmail.com
CONTACT_PHONE=8296064418
UPI_ID=8296064418@paytm
```

### **Pricing Configuration**
```
BASE_DELIVERY_CHARGE=30
PARCEL_CHARGE=10
FREE_DELIVERY_ABOVE=500
```

### **Admin Credentials**
```
ADMIN_EMAIL=admin@swaadsadan.com
ADMIN_PASSWORD=your-secure-password-here
```

> ⚠️ **IMPORTANT**: Change the default admin password!

### **Razorpay Payment Gateway (REQUIRED for payments)**
```
RAZORPAY_KEY_ID=rzp_test_or_live_key_here
RAZORPAY_KEY_SECRET=your_razorpay_secret_here
```

---

## 💳 STEP 1: SETUP RAZORPAY

### **Get Razorpay Account:**
1. Sign up at https://razorpay.com/
2. Complete KYC verification (business details, PAN, bank account)
3. Navigate to **Dashboard → Settings → API Keys**

### **Get API Keys:**
- **Test Mode**: `rzp_test_xxxxxxxxxxxxx` (for testing)
- **Live Mode**: `rzp_live_xxxxxxxxxxxxx` (for production)

### **Get Secret Keys:**
- Click "Generate Test/Live Keys"
- Copy both **Key ID** and **Key Secret**
- Add them to `.env` file (see below)

### **Where to Add Keys:**

#### **For Local Development:**
1. Open `backend-python/.env` file
2. Replace these lines:
   ```env
   RAZORPAY_KEY_ID=your_razorpay_key_id_here
   RAZORPAY_KEY_SECRET=your_razorpay_key_secret_here
   ```
3. Save the file

#### **For Render Deployment:**
1. Go to Render Dashboard → Your Service → Environment
2. Add environment variables:
   - `RAZORPAY_KEY_ID` = your key ID
   - `RAZORPAY_KEY_SECRET` = your key secret
3. Save changes

---

## 🌐 STEP 2: DEPLOY TO RENDER

### **Option A: Deploy via GitHub (Recommended)**

1. **Create GitHub Repository:**
   ```bash
   # Navigate to your project
   cd C:\Users\DMA2\swaad_sadan
   
   # Initialize git (if not already)
   git init
   
   # Add all files
   git add .
   
   # Commit
   git commit -m "Initial commit - Swaad Sadan Web App"
   
   # Add remote (replace with your GitHub URL)
   git remote add origin https://github.com/YOUR_USERNAME/swaad-sadan.git
   
   # Push to GitHub
   git push -u origin main
   ```

2. **Connect to Render:**
   - Go to https://render.com/
   - Click **"New"** → **"Web Service"**
   - Click **"Connect Repository"**
   - Select your `swaad-sadan` repository

3. **Configure Service:**
   - **Name**: `swaad-sadan`
   - **Environment**: `Docker`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: `backend-python`
   
4. **Add Environment Variables:**
   - Click **"Advanced"**
   - Click **"Add Environment Variable"**
   - Add ALL the variables listed above

5. **Deploy:**
   - Click **"Create Web Service"**
   - Wait 5-10 minutes for deployment
   - Your app will be live at: `https://swaad-sadan.onrender.com`

---

### **Option B: Deploy via Render CLI**

```bash
# Install Render CLI
pip install render-cli

# Login to Render
render login

# Create service
render services create web swaad-sadan \
  --env python \
  --root backend-python \
  --build-command "pip install -r requirements.txt" \
  --start-command "python app.py"

# Add environment variables
render env set SECRET_KEY="your-secret-key"
render env set JWT_SECRET_KEY="your-jwt-secret"
render env set RAZORPAY_KEY_ID="your-razorpay-key"
render env set RAZORPAY_KEY_SECRET="your-razorpay-secret"

# Deploy
render deploy
```

---

## 🗄️ STEP 3: UPGRADE DATABASE (IMPORTANT!)

### **⚠️ SQLite Limitations:**
- Free tier Render **resets SQLite database** on every deployment
- **Data will be lost** when app restarts
- Not suitable for production with real users

### **✅ Solution: PostgreSQL (Recommended)**

#### **Option 1: Render PostgreSQL (Free)**
1. In Render Dashboard → **"New"** → **"PostgreSQL"**
2. Name: `swaad-sadan-db`
3. Plan: **Free** (good for 1GB data)
4. Click **"Create Database"**
5. Copy **Internal Database URL**
6. Add to environment variables:
   ```
   DATABASE_URL=postgresql://...
   ```

#### **Option 2: ElephantSQL (Free)**
1. Sign up at https://www.elephantsql.com/
2. Create instance: **"Tiny Turtle"** (free)
3. Copy database URL
4. Add to Render environment variables

#### **Code Changes for PostgreSQL:**
I can help you convert the code from SQLite to PostgreSQL - it requires updating `extensions.py` and installing `psycopg2`:

1. Update `requirements.txt`:
   ```
   psycopg2-binary==2.9.9
   ```

2. Update database connection (I can help with this!)

---

## 🔒 STEP 4: SECURITY CHECKLIST

### **Before Going Live:**

- [ ] Changed `SECRET_KEY` to a random 32+ character string
- [ ] Changed `JWT_SECRET_KEY` to a different random string
- [ ] Changed default admin password
- [ ] Set `FLASK_ENV=production`
- [ ] Added real Razorpay live keys (not test keys)
- [ ] Set up PostgreSQL database (if handling real orders)
- [ ] Tested payment flow with test keys
- [ ] Enabled HTTPS (Render provides this automatically)

---

## 📊 STEP 5: POST-DEPLOYMENT

### **Your App URLs:**
- **Website**: `https://swaad-sadan.onrender.com`
- **Admin Panel**: `https://swaad-sadan.onrender.com/admin`
- **API Base**: `https://swaad-sadan.onrender.com/api`

### **Test Your Deployment:**
1. Visit your website
2. Register a new account
3. Add items to cart
4. Test checkout with Razorpay test keys
5. Login to admin panel
6. Verify all features work

### **Monitor Your App:**
- **Logs**: Render Dashboard → Logs
- **Metrics**: Render Dashboard → Metrics
- **Events**: Render Dashboard → Events

---

## 💰 RENDER PRICING

### **Free Tier:**
- ✅ 750 hours/month (1 service running 24/7)
- ✅ Free SSL certificate (HTTPS)
- ✅ Automatic deployments from GitHub
- ⚠️ App sleeps after 15 minutes of inactivity
- ⚠️ First request after sleep takes 30+ seconds
- ⚠️ SQLite data resets on deployment

### **Paid Tier ($7/month):**
- ✅ Always-on (no sleeping)
- ✅ Faster performance
- ✅ More memory/CPU
- ✅ Can use persistent disk for SQLite (but PostgreSQL still recommended)

---

## 🆘 TROUBLESHOOTING

### **App Won't Start:**
- Check logs in Render Dashboard
- Verify all environment variables are set
- Ensure Dockerfile is in `backend-python/` folder

### **Payment Not Working:**
- Verify Razorpay keys are correct
- Check if using test keys (rzp_test_) for testing
- Check browser console for errors

### **Database Errors:**
- If using SQLite, data resets on restart (expected behavior)
- Upgrade to PostgreSQL for persistent data

### **502 Bad Gateway:**
- App is still starting (wait 1-2 minutes)
- Check if PORT environment variable is set

---

## 📞 NEED HELP?

1. Check Render logs first
2. Test locally with same environment variables
3. Verify all files are committed to GitHub
4. Contact: swaadsadancafe@gmail.com

---

## 🎉 SUCCESS CHECKLIST

After deployment, verify:
- [ ] Website loads successfully
- [ ] User registration works
- [ ] Login/logout works
- [ ] Menu displays products
- [ ] Add to cart works
- [ ] Checkout with COD works
- [ ] Razorpay payment works (test mode)
- [ ] Admin login works
- [ ] Admin can manage products
- [ ] Admin can view orders

---

**🚀 Your app is now live! Share your link with customers!**
