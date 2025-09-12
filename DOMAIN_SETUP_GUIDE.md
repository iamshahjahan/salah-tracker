# 🌐 Domain Setup Guide - salahtracker.app

## 📋 Overview
This guide will help you connect your `salahtracker.app` domain to your EC2 server at `13.233.86.216`.

## 🔧 Step 1: Configure DNS Records in Namecheap

### Access Namecheap DNS Management
1. **Login to Namecheap**: Go to [namecheap.com](https://namecheap.com) and login
2. **Go to Domain List**: Click on "Domain List" in your account
3. **Select Domain**: Click "Manage" next to `salahtracker.app`
4. **DNS Management**: Click on "Advanced DNS" tab

### Configure DNS Records

#### A Record (Main Domain)
```
Type: A Record
Host: @
Value: 13.233.86.216
TTL: Automatic (or 300)
```

#### A Record (WWW Subdomain)
```
Type: A Record
Host: www
Value: 13.233.86.216
TTL: Automatic (or 300)
```

#### Optional: CNAME Record (Alternative)
```
Type: CNAME Record
Host: www
Value: salahtracker.app
TTL: Automatic (or 300)
```

## 🔧 Step 2: Update Nginx Configuration

### Update Server Configuration
```bash
ssh -i /Users/mohammadshahjahan/Downloads/salah-tracker-server-1.pem ec2-user@13.233.86.216
sudo nano /etc/nginx/conf.d/salah-tracker.conf
```

### Replace with Domain Configuration
```nginx
server {
    listen 80;
    server_name salahtracker.app www.salahtracker.app;

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

### Test and Reload Nginx
```bash
sudo nginx -t
sudo systemctl reload nginx
```

## 🔧 Step 3: Configure AWS Security Group

### Open Required Ports
1. **Go to AWS Console**: EC2 → Security Groups
2. **Select Your Instance's Security Group**
3. **Add Inbound Rules**:

```
Type: HTTP
Port: 80
Source: 0.0.0.0/0

Type: HTTPS
Port: 443
Source: 0.0.0.0/0

Type: SSH
Port: 22
Source: Your IP (for security)
```

## 🔧 Step 4: SSL Certificate (Recommended)

### Install Certbot
```bash
sudo dnf install certbot python3-certbot-nginx -y
```

### Get SSL Certificate
```bash
sudo certbot --nginx -d salahtracker.app -d www.salahtracker.app
```

### Auto-renewal Setup
```bash
sudo systemctl enable certbot-renew.timer
sudo systemctl start certbot-renew.timer
```

## 🔧 Step 5: Update Application Configuration

### Update CORS Settings
```bash
cd /var/www/salah-tracker
nano .env
```

Add/Update:
```env
CORS_ORIGINS=https://salahtracker.app,https://www.salahtracker.app,http://salahtracker.app,http://www.salahtracker.app
```

### Restart Application
```bash
sudo systemctl restart salah-tracker
```

## 🔧 Step 6: Test Domain Configuration

### Check DNS Propagation
```bash
# Check if domain points to your server
nslookup salahtracker.app
nslookup www.salahtracker.app

# Test from your local machine
curl -I http://salahtracker.app
curl -I https://salahtracker.app
```

### Test Application
```bash
# Test locally on server
curl http://localhost:5000

# Test domain access
curl http://salahtracker.app
```

## ⏱️ DNS Propagation Time

**Important**: DNS changes can take **24-48 hours** to fully propagate worldwide.

### Check Propagation Status
- **Online Tools**: [whatsmydns.net](https://whatsmydns.net)
- **Command Line**: `nslookup salahtracker.app`

## 🔍 Troubleshooting

### Common Issues

#### 1. Domain Not Resolving
```bash
# Check DNS records
dig salahtracker.app
nslookup salahtracker.app

# Wait for propagation (up to 48 hours)
```

#### 2. Nginx Configuration Error
```bash
# Test configuration
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log
```

#### 3. Application Not Accessible
```bash
# Check application status
sudo systemctl status salah-tracker

# Check application logs
sudo journalctl -u salah-tracker -f
```

#### 4. SSL Certificate Issues
```bash
# Check certificate status
sudo certbot certificates

# Renew if needed
sudo certbot renew
```

## 🎯 Final Configuration

### Complete Nginx Configuration (with SSL)
```nginx
server {
    listen 80;
    server_name salahtracker.app www.salahtracker.app;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name salahtracker.app www.salahtracker.app;

    ssl_certificate /etc/letsencrypt/live/salahtracker.app/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/salahtracker.app/privkey.pem;

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

## 🎉 Success Checklist

- [ ] DNS A records configured in Namecheap
- [ ] Nginx configuration updated with domain
- [ ] AWS Security Group allows ports 80/443
- [ ] SSL certificate installed (optional but recommended)
- [ ] Application restarted with new configuration
- [ ] Domain resolves to your server IP
- [ ] Website accessible via domain

## 🚀 Your App Will Be Live At:
- **HTTP**: `http://salahtracker.app`
- **HTTPS**: `https://salahtracker.app` (after SSL setup)
- **WWW**: `http://www.salahtracker.app`

**Congratulations! Your Salah Tracker app will be accessible via your custom domain!** 🎉
