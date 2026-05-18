# 🎯 RENDER DEPLOYMENT - QUICK REFERENCE

## ⚙️ **SERVICE CONFIGURATION**

| Setting | Value |
|---------|-------|
| **Name** | `swaad-sadan` |
| **Environment** | `Docker` |
| **Region** | Singapore / Frankfurt (choose closest) |
| **Branch** | `main` |
| **Root Directory** | `backend-python` |
| **Dockerfile Path** | `./Dockerfile` (auto-detected) |

---

## 🔐 **ENVIRONMENT VARIABLES** (Copy & Paste)

```bash
# Security (CHANGE THESE!)
SECRET_KEY=generate-random-32-char-string-here
JWT_SECRET_KEY=generate-different-random-string-here

# Flask
FLASK_ENV=production
PORT=10000

# Database
DATABASE_PATH=/app/data/swaad_sadan.db

# Business Info
CONTACT_EMAIL=swaadsadancafe@gmail.com
CONTACT_PHONE=8296064418
UPI_ID=8296064418@paytm

# Pricing
BASE_DELIVERY_CHARGE=30
PARCEL_CHARGE=10
FREE_DELIVERY_ABOVE=500

# Admin
ADMIN_EMAIL=admin@swaadsadan.com
ADMIN_PASSWORD=ChangeThisPassword123

# Razorpay (GET FROM RAZORPAY.COM)
RAZORPAY_KEY_ID=rzp_test_XXXXXXXXXXXXXXXX
RAZORPAY_KEY_SECRET=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

---

## 📝 **STEP-BY-STEP RENDER SETUP**

### **1. Prerequisites**
- [ ] GitHub account created
- [ ] Code pushed to GitHub repository
- [ ] Razorpay account created
- [ ] Razorpay API keys obtained

### **2. Render Setup**
1. Go to https://render.com/
2. Sign up / Login
3. Click **"New +"** → **"Web Service"**
4. Click **"Connect a repository"**
5. Select your GitHub repository
6. Click **"Connect"**

### **3. Configure Service**
Fill in these fields:

**Basic Settings:**
- Name: `swaad-sadan`
- Environment: `Docker`
- Region: (Choose closest to you)
- Branch: `main`

**Advanced Settings:**
- Root Directory: `backend-python`
- Auto-Deploy: `Yes` (recommended)

### **4. Add Environment Variables**
Click **"Advanced"** → **"Add Environment Variable"**

Add ALL variables from the table above, one by one:
- Click **"+ Add Environment Variable"**
- Enter **Key** (e.g., `SECRET_KEY`)
- Enter **Value** (your actual value)
- Repeat for all variables

### **5. Deploy**
1. Click **"Create Web Service"**
2. Wait 5-10 minutes for deployment
3. Watch logs for any errors
4. Once deployed, click on the URL

### **6. Verify Deployment**
Your app will be at: `https://swaad-sadan.onrender.com`

Test these:
- [ ] Homepage loads
- [ ] Can register/login
- [ ] Menu displays
- [ ] Can add to cart
- [ ] Admin login works
- [ ] Payment method appears

---

## 🔑 **HOW TO GET RAZORPAY KEYS**

### **Option 1: Test Keys (For Testing)**
1. Sign up at https://razorpay.com/
2. Login to Dashboard
3. Go to **Settings** → **API Keys**
4. Make sure **Test Mode** is ON (toggle at top)
5. Click **"Generate Test Key"**
6. Copy:
   - **Key Id**: `rzp_test_XXXXXXXX`
   - **Key Secret**: Click "Show" to reveal, then copy

### **Option 2: Live Keys (For Production)**
1. Complete KYC verification (business details, PAN, bank account)
2. Wait for approval (1-2 days)
3. Go to **Settings** → **API Keys**
4. Switch to **Live Mode** (toggle at top)
5. Click **"Generate Live Key"**
6. Copy both keys

---

## 🔐 **HOW TO GENERATE SECRET KEYS**

### **Method 1: Online Generator**
1. Visit https://randomkeygen.com/
2. Find **"504 bit WPA Key"**
3. Copy one for `SECRET_KEY`
4. Copy another different one for `JWT_SECRET_KEY`

### **Method 2: Python (Local)**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
Run twice, use different outputs for both keys.

### **Method 3: PowerShell**
```powershell
# For SECRET_KEY
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})

# For JWT_SECRET_KEY (run again)
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
```

---

## ⚡ **QUICK TROUBLESHOOTING**

### **Deploy Failed?**
- ✅ Check Dockerfile is in `backend-python/` folder
- ✅ Verify all environment variables are set
- ✅ Check logs in Render dashboard
- ✅ Ensure requirements.txt has all dependencies

### **502 Bad Gateway?**
- ⏳ Wait 2-3 minutes (app is starting)
- ✅ Check if PORT is set to 10000
- ✅ Verify app.py runs locally first

### **Payment Not Working?**
- ✅ Verify Razorpay keys are correct
- ✅ Check browser console for errors (F12)
- ✅ Ensure both keys are from same mode (test/live)
- ✅ Check `/api/payment/key` endpoint returns key

### **Database Resets on Restart?**
- ⚠️ Expected behavior on Render free tier with SQLite
- ✅ Upgrade to PostgreSQL for persistent data
- ✅ Or upgrade to paid Render plan with persistent disk

---

## 💡 **PRO TIPS**

1. **Use Test Keys First**: Deploy with Razorpay test keys, test everything, then switch to live keys

2. **Monitor Logs**: Keep logs open during first deployment to catch errors early

3. **Test Payment Flow**: 
   - Test card: `4111 1111 1111 1111`
   - Any CVV and future expiry date

4. **Free Tier Limits**:
   - App sleeps after 15 mins of inactivity
   - First request after sleep takes 30+ seconds
   - SQLite data resets on redeploy

5. **Custom Domain** (Optional):
   - Buy domain (GoDaddy, Namecheap)
   - Add in Render: Settings → Custom Domains
   - Update DNS records

---

## ✅ **DEPLOYMENT CHECKLIST**

### **Before Deploying:**
- [ ] Code pushed to GitHub
- [ ] Razorpay keys obtained
- [ ] Random secret keys generated
- [ ] Admin password changed from default

### **During Deployment:**
- [ ] Service configured correctly
- [ ] All environment variables added
- [ ] Deployment started successfully
- [ ] No errors in build logs

### **After Deployment:**
- [ ] Website accessible
- [ ] Can register/login
- [ ] Payment popup works
- [ ] Admin panel accessible
- [ ] All features tested

---

## 📱 **YOUR LIVE URLS**

After deployment:
- **Website**: `https://swaad-sadan.onrender.com`
- **Admin**: `https://swaad-sadan.onrender.com/admin`
- **API**: `https://swaad-sadan.onrender.com/api`

---

## 📞 **SUPPORT**

If you need help:
1. Check `RENDER_DEPLOYMENT.md` for detailed guide
2. Check `RAZORPAY_KEYS_GUIDE.md` for key setup
3. Read `DOCKER_GUIDE.md` for Docker info
4. Email: swaadsadancafe@gmail.com

---

**🚀 Ready to deploy in 10 minutes!**
