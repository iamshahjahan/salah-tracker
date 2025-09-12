# 🚀 Salah Tracker Deployment Guide

## 📋 Prerequisites

### Server Requirements
- **OS**: Amazon Linux 2 or Ubuntu 20.04+
- **RAM**: Minimum 2GB (4GB recommended)
- **Storage**: Minimum 20GB
- **Python**: 3.8+
- **Node.js**: 16+ (for any frontend builds)

### Local Requirements
- **SSH Key**: `/Users/mohammadshahjahan/Downloads/salah-tracker-server-1.pem`
- **Server Access**: `ssh -i /Users/mohammadshahjahan/Downloads/salah-tracker-server-1.pem ec2-user@13.233.86.216`

## 🔧 Step 1: Server Setup

### Connect to Server
```bash
ssh -i /Users/mohammadshahjahan/Downloads/salah-tracker-server-1.pem ec2-user@13.233.86.216
```

### Update System
```bash
sudo yum update -y  # For Amazon Linux
# OR
sudo apt update && sudo apt upgrade -y  # For Ubuntu
```

### Install Python 3.8+
```bash
# Amazon Linux 2
sudo yum install python3 python3-pip python3-devel -y

# Ubuntu
sudo apt install python3 python3-pip python3-venv python3-dev -y
```

### Install MySQL
```bash
# Amazon Linux 2
sudo yum install mysql-server -y
sudo systemctl start mysqld
sudo systemctl enable mysqld

# Ubuntu
sudo apt install mysql-server -y
sudo systemctl start mysql
sudo systemctl enable mysql
```

### Install Redis
```bash
# Amazon Linux 2
sudo yum install redis -y
sudo systemctl start redis
sudo systemctl enable redis

# Ubuntu
sudo apt install redis-server -y
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### Install Nginx
```bash
# Amazon Linux 2
sudo yum install nginx -y
sudo systemctl start nginx
sudo systemctl enable nginx

# Ubuntu
sudo apt install nginx -y
sudo systemctl start nginx
sudo systemctl enable nginx
```

### Install Git
```bash
# Amazon Linux 2
sudo yum install git -y

# Ubuntu
sudo apt install git -y
```

## 🗄️ Step 2: Database Setup

### Secure MySQL Installation
```bash
sudo mysql_secure_installation
```

### Create Database and User
```bash
sudo mysql -u root -p
```

```sql
CREATE DATABASE salah_tracker;
CREATE USER 'salah_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON salah_tracker.* TO 'salah_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## 📁 Step 3: Application Deployment

### Create Application Directory
```bash
sudo mkdir -p /var/www/salah-tracker
sudo chown ec2-user:ec2-user /var/www/salah-tracker
cd /var/www/salah-tracker
```

### Clone Repository (if using Git)
```bash
git clone https://github.com/yourusername/salah-tracker.git .
```

### OR Upload Files Manually
```bash
# From your local machine, upload files
scp -i /Users/mohammadshahjahan/Downloads/salah-tracker-server-1.pem -r /Users/mohammadshahjahan/salah-tracker/* ec2-user@13.233.86.216:/var/www/salah-tracker/
```

### Create Virtual Environment
```bash
cd /var/www/salah-tracker
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## ⚙️ Step 4: Configuration

### Create Environment File
```bash
cp env.example .env
nano .env
```

### Update .env with Production Values
```env
# Database Configuration
DATABASE_URL=mysql://salah_user:your_secure_password@localhost/salah_tracker

# Flask Configuration
SECRET_KEY=your_very_secure_secret_key_here
FLASK_ENV=production
FLASK_DEBUG=False

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key_here

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=trackersalah@gmail.com
MAIL_PASSWORD=your_app_password_here

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# External APIs
ALADHAN_API_BASE_URL=https://api.aladhan.com
BIGDATA_CLOUD_API_KEY=your_api_key_here

# Logging
LOG_LEVEL=INFO
```

### Set File Permissions
```bash
chmod 600 .env
chmod +x *.py
```

## 🗃️ Step 5: Database Migration

### Initialize Database
```bash
cd /var/www/salah-tracker
source venv/bin/activate
python -c "from database import db; from main import app; app.app_context().push(); db.create_all()"
```

### OR Run Migration Scripts
```bash
python migration_add_new_features.py
```

## 🔄 Step 6: Celery Setup

### Create Celery Service File
```bash
sudo nano /etc/systemd/system/salah-celery.service
```

```ini
[Unit]
Description=Salah Tracker Celery Worker
After=network.target

[Service]
Type=forking
User=ec2-user
Group=ec2-user
EnvironmentFile=/var/www/salah-tracker/.env
WorkingDirectory=/var/www/salah-tracker
ExecStart=/var/www/salah-tracker/venv/bin/celery -A celery_config worker --loglevel=info --detach
ExecStop=/bin/kill -s TERM $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

### Create Celery Beat Service File
```bash
sudo nano /etc/systemd/system/salah-celery-beat.service
```

```ini
[Unit]
Description=Salah Tracker Celery Beat Scheduler
After=network.target

[Service]
Type=forking
User=ec2-user
Group=ec2-user
EnvironmentFile=/var/www/salah-tracker/.env
WorkingDirectory=/var/www/salah-tracker
ExecStart=/var/www/salah-tracker/venv/bin/celery -A celery_config beat --loglevel=info --detach
ExecStop=/bin/kill -s TERM $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

### Start Celery Services
```bash
sudo systemctl daemon-reload
sudo systemctl enable salah-celery
sudo systemctl enable salah-celery-beat
sudo systemctl start salah-celery
sudo systemctl start salah-celery-beat
```

## 🌐 Step 7: Nginx Configuration

### Create Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/salah-tracker
```

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/salah-tracker/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /logs {
        deny all;
    }
}
```

### Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/salah-tracker /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🚀 Step 8: Gunicorn Setup

### Install Gunicorn
```bash
source venv/bin/activate
pip install gunicorn
```

### Create Gunicorn Service
```bash
sudo nano /etc/systemd/system/salah-tracker.service
```

```ini
[Unit]
Description=Salah Tracker Gunicorn Application
After=network.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=/var/www/salah-tracker
Environment="PATH=/var/www/salah-tracker/venv/bin"
EnvironmentFile=/var/www/salah-tracker/.env
ExecStart=/var/www/salah-tracker/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 main:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

### Start Application
```bash
sudo systemctl daemon-reload
sudo systemctl enable salah-tracker
sudo systemctl start salah-tracker
```

## 🔒 Step 9: SSL Certificate (Optional but Recommended)

### Install Certbot
```bash
# Amazon Linux 2
sudo yum install certbot python3-certbot-nginx -y

# Ubuntu
sudo apt install certbot python3-certbot-nginx -y
```

### Get SSL Certificate
```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## 📊 Step 10: Monitoring & Logs

### Check Service Status
```bash
sudo systemctl status salah-tracker
sudo systemctl status salah-celery
sudo systemctl status salah-celery-beat
sudo systemctl status nginx
```

### View Logs
```bash
# Application logs
sudo journalctl -u salah-tracker -f

# Celery logs
sudo journalctl -u salah-celery -f
sudo journalctl -u salah-celery-beat -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Application logs
tail -f /var/www/salah-tracker/logs/app.log
```

## 🔧 Step 11: Firewall Configuration

### Configure Security Groups (AWS Console)
- **HTTP**: Port 80 (0.0.0.0/0)
- **HTTPS**: Port 443 (0.0.0.0/0)
- **SSH**: Port 22 (Your IP only)

### Configure Local Firewall
```bash
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
```

## 🚀 Step 12: Deployment Script

### Create Deployment Script
```bash
nano /var/www/salah-tracker/deploy.sh
```

```bash
#!/bin/bash
set -e

echo "🚀 Starting deployment..."

# Pull latest changes
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Run database migrations
python -c "from database import db; from main import app; app.app_context().push(); db.create_all()"

# Restart services
sudo systemctl restart salah-tracker
sudo systemctl restart salah-celery
sudo systemctl restart salah-celery-beat

echo "✅ Deployment completed successfully!"
```

### Make Script Executable
```bash
chmod +x deploy.sh
```

## 🎯 Quick Deployment Commands

### One-Line Deployment (after initial setup)
```bash
cd /var/www/salah-tracker && ./deploy.sh
```

### Manual Restart
```bash
sudo systemctl restart salah-tracker
sudo systemctl restart salah-celery
sudo systemctl restart salah-celery-beat
sudo systemctl restart nginx
```

## 🔍 Troubleshooting

### Common Issues
1. **Permission Denied**: Check file ownership and permissions
2. **Database Connection**: Verify MySQL is running and credentials are correct
3. **Celery Not Working**: Check Redis is running and accessible
4. **Static Files Not Loading**: Verify Nginx configuration and file paths

### Health Check
```bash
curl http://localhost:5000/health
curl http://your-domain.com/health
```

## 📱 Final Steps

1. **Test the application** at `http://your-domain.com`
2. **Verify email functionality** by testing registration
3. **Check Celery tasks** are running properly
4. **Monitor logs** for any errors
5. **Set up monitoring** (optional)

## 🎉 Congratulations!

Your Salah Tracker app is now deployed and running on your EC2 server!

**Access your app at**: `http://your-domain.com` or `http://13.233.86.216`
