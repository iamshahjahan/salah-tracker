# ⚡ Quick Deployment Guide

## 🚀 One-Command Deployment

### Prerequisites
1. **SSH Key**: Make sure `salah-tracker-server-1.pem` is in `/Users/mohammadshahjahan/Downloads/`
2. **Server Access**: Your EC2 server should be running and accessible

### Deploy Now!
```bash
./deploy_to_server.sh
```

This script will:
- ✅ Upload all your files to the server
- ✅ Install required packages (Python, MySQL, Redis, Nginx)
- ✅ Set up the virtual environment
- ✅ Install Python dependencies
- ✅ Create the basic .env file

## 🔧 Manual Steps After Deployment

### 1. SSH into your server
```bash
ssh -i /Users/mohammadshahjahan/Downloads/salah-tracker-server-1.pem ec2-user@13.233.86.216
```

### 2. Set up the database
```bash
cd /var/www/salah-tracker

# Secure MySQL installation
sudo mysql_secure_installation

# Create database and user
sudo mysql -u root -p
```

```sql
CREATE DATABASE salah_tracker;
CREATE USER 'salah_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON salah_tracker.* TO 'salah_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3. Update environment file
```bash
nano .env
```

Update these critical values:
- `SECRET_KEY` - Generate a secure random key
- `JWT_SECRET_KEY` - Generate another secure key
- `DATABASE_URL` - Use the password you created above
- `MAIL_PASSWORD` - Your Gmail app password

### 4. Initialize the database
```bash
source venv/bin/activate
python -c "from database import db; from main import app; app.app_context().push(); db.create_all()"
```

### 5. Set up services
```bash
# Copy service files (from DEPLOYMENT_GUIDE.md)
sudo cp /var/www/salah-tracker/DEPLOYMENT_GUIDE.md /tmp/guide.md

# Start services
sudo systemctl start salah-tracker
sudo systemctl start salah-celery
sudo systemctl start salah-celery-beat
```

## 🌐 Access Your App

### Test locally on server
```bash
curl http://localhost:5000
```

### Access from browser
- **IP Address**: `http://13.233.86.216`
- **Domain**: `http://your-domain.com` (if you set up DNS)

## 🔍 Quick Health Check

```bash
# Check if services are running
sudo systemctl status salah-tracker
sudo systemctl status nginx

# Check logs
sudo journalctl -u salah-tracker -f
```

## 🆘 Need Help?

1. **Check the full guide**: `DEPLOYMENT_GUIDE.md`
2. **View logs**: `sudo journalctl -u salah-tracker -f`
3. **Test database**: `mysql -u salah_user -p salah_tracker`
4. **Test Redis**: `redis-cli ping`

## 🎯 Expected Result

After deployment, you should see:
- ✅ Beautiful landing page at `http://13.233.86.216`
- ✅ User registration and login working
- ✅ Prayer times loading correctly
- ✅ Email notifications working
- ✅ Celery tasks running in background

**Your Salah Tracker app will be live and running!** 🎉
