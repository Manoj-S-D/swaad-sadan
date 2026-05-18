# 🐳 DOCKER DEPLOYMENT GUIDE

## Quick Start

### **Prerequisites:**
- Docker installed on your system
- Docker Compose installed (usually comes with Docker Desktop)

---

## 🚀 **Method 1: Using Docker Compose (Recommended)**

### **1. Add Razorpay Keys to .env file:**

Create or edit `backend-python/.env`:
```env
# Add your Razorpay keys here
RAZORPAY_KEY_ID=rzp_test_your_key_here
RAZORPAY_KEY_SECRET=your_razorpay_secret_here

# Other settings (optional, defaults are set)
SECRET_KEY=your-random-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
ADMIN_PASSWORD=your-admin-password
```

### **2. Run the Application:**
```bash
# From the swaad_sadan folder (root directory)
docker-compose up -d
```

### **3. Access Your Application:**
- **Website**: http://localhost:5000
- **Admin Panel**: http://localhost:5000/admin
- **Admin Login**: 
  - Email: `admin@swaadsadan.com`
  - Password: `admin123` (or your custom password from .env)

### **4. View Logs:**
```bash
docker-compose logs -f
```

### **5. Stop the Application:**
```bash
docker-compose down
```

### **6. Stop and Remove All Data:**
```bash
docker-compose down -v
```

---

## 🛠️ **Method 2: Using Docker Only**

### **1. Build the Docker Image:**
```bash
cd backend-python
docker build -t swaad-sadan:latest .
```

### **2. Run the Container:**
```bash
docker run -d \
  --name swaad-sadan \
  -p 5000:5000 \
  -e SECRET_KEY="your-secret-key" \
  -e JWT_SECRET_KEY="your-jwt-secret" \
  -e RAZORPAY_KEY_ID="rzp_test_your_key" \
  -e RAZORPAY_KEY_SECRET="your_razorpay_secret" \
  -e ADMIN_PASSWORD="your-admin-password" \
  -v swaad-sadan-data:/app/data \
  swaad-sadan:latest
```

### **3. View Logs:**
```bash
docker logs -f swaad-sadan
```

### **4. Stop the Container:**
```bash
docker stop swaad-sadan
docker rm swaad-sadan
```

---

## 📁 **Docker Entry Point**

The Docker container entry point is configured in the **Dockerfile**:

```dockerfile
# Entry point command
CMD ["python", "app.py"]
```

### **What Happens:**
1. **Working Directory**: `/app` (inside container)
2. **Base Directory**: `backend-python/` (your source code)
3. **Entry Script**: `app.py` (main Flask application)
4. **Port**: 5000 (exposed to your host machine)

### **File Structure Inside Container:**
```
/app/
├── app.py              ← Entry point (CMD runs this)
├── config.py
├── extensions.py
├── models.py
├── requirements.txt
├── routes/
│   ├── auth.py
│   ├── orders.py
│   ├── payment.py
│   └── ...
├── templates/
│   ├── home.html
│   ├── cart.html
│   └── ...
├── static/
│   ├── css/
│   └── js/
└── data/
    └── swaad_sadan.db  ← SQLite database (persistent volume)
```

---

## 🔧 **What Docker Does Automatically**

### **1. Installs Python Dependencies:**
```dockerfile
RUN pip install --no-cache-dir -r requirements.txt
```

Installs:
- Flask
- Flask-JWT-Extended
- Flask-CORS
- Razorpay
- And all other packages from `requirements.txt`

### **2. Sets Up Environment:**
```dockerfile
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
```

### **3. Creates Data Directory:**
```dockerfile
RUN mkdir -p /app/data
```

### **4. Health Check:**
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/settings')"
```

---

## 🌍 **Environment Variables for Docker**

You can pass environment variables in three ways:

### **1. Via .env file (Docker Compose):**
```yaml
# docker-compose.yml uses .env automatically
environment:
  - RAZORPAY_KEY_ID=${RAZORPAY_KEY_ID}
```

### **2. Via -e flag (Docker run):**
```bash
docker run -e RAZORPAY_KEY_ID="rzp_test_xxx" ...
```

### **3. Via --env-file flag:**
```bash
docker run --env-file backend-python/.env ...
```

---

## 📊 **Volume Mounting (Data Persistence)**

### **Docker Compose (Automatic):**
```yaml
volumes:
  - swaad-sadan-data:/app/data
```

### **Docker Run (Manual):**
```bash
-v swaad-sadan-data:/app/data
```

### **What This Does:**
- SQLite database persists across container restarts
- Data is NOT lost when you stop/start container
- Data IS lost only when you run `docker-compose down -v`

---

## 🚨 **Important Notes**

### **⚠️ For Production Deployment:**

1. **Don't use SQLite in production** - it will be reset on Render/cloud platforms
2. **Use PostgreSQL** for production (Render offers free PostgreSQL)
3. **Change default secrets** before deploying
4. **Use Razorpay LIVE keys** for real payments
5. **Set FLASK_ENV=production** in production

### **✅ For Local Development:**
- SQLite works fine
- Use Razorpay TEST keys
- FLASK_ENV=development is okay

---

## 🧹 **Cleanup Commands**

### **Remove All Containers:**
```bash
docker rm -f $(docker ps -aq)
```

### **Remove All Images:**
```bash
docker rmi -f $(docker images -q)
```

### **Remove All Volumes:**
```bash
docker volume prune
```

### **Full Cleanup:**
```bash
docker system prune -a --volumes
```

---

## 🔍 **Debugging**

### **Check if Container is Running:**
```bash
docker ps
```

### **Check Container Logs:**
```bash
docker logs swaad-sadan
```

### **Access Container Shell:**
```bash
docker exec -it swaad-sadan /bin/bash
```

### **Check Database:**
```bash
docker exec -it swaad-sadan ls -la /app/data
```

---

## 📞 **Need Help?**

If you encounter issues:
1. Check logs: `docker-compose logs -f`
2. Verify .env file has correct keys
3. Ensure ports are not in use: `netstat -ano | findstr :5000`
4. Restart Docker service

---

## ✅ **Verification Checklist**

After starting Docker:
- [ ] Container is running: `docker ps`
- [ ] Website accessible: http://localhost:5000
- [ ] No errors in logs: `docker logs swaad-sadan`
- [ ] Admin panel works: http://localhost:5000/admin
- [ ] Payment page loads (check browser console)
- [ ] Database file exists: `docker exec swaad-sadan ls /app/data`

---

**🎉 Your application is now running in Docker!**
