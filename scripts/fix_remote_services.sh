#!/bin/bash

# 🔧 Fix Remote Services Script
# This script will fix Redis installation and Celery service issues

set -e

# Configuration
SERVER_IP="13.233.86.216"
SSH_KEY="/Users/mohammadshahjahan/Downloads/salah-tracker-server-1.pem"
SERVER_USER="ec2-user"
APP_DIR="/var/www/salah-tracker"

echo "🔧 Fixing remote services..."

# Check if SSH key exists
if [ ! -f "$SSH_KEY" ]; then
    echo "❌ SSH key file '$SSH_KEY' not found!"
    exit 1
fi

# Set proper permissions for SSH key
chmod 600 "$SSH_KEY"

# Fix services on the remote server
ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" << 'EOF'
    echo "🔧 Installing and configuring Redis..."
    
    # Install Redis
    sudo yum install redis -y
    
    # Configure Redis
    sudo sed -i 's/^# maxmemory <bytes>/maxmemory 256mb/' /etc/redis.conf
    sudo sed -i 's/^# maxmemory-policy noeviction/maxmemory-policy allkeys-lru/' /etc/redis.conf
    
    # Start and enable Redis
    sudo systemctl start redis
    sudo systemctl enable redis
    
    echo "✅ Redis installed and started"
    
    # Test Redis connection
    if redis-cli ping > /dev/null 2>&1; then
        echo "✅ Redis is responding"
    else
        echo "❌ Redis is not responding"
    fi
    
    echo ""
    echo "🔧 Fixing Celery services..."
    
    cd /var/www/salah-tracker
    
    # Stop existing Celery services
    sudo systemctl stop celery-worker 2>/dev/null || true
    sudo systemctl stop celery-beat 2>/dev/null || true
    
    # Kill any existing Celery processes
    pkill -f "celery.*worker" 2>/dev/null || true
    pkill -f "celery.*beat" 2>/dev/null || true
    
    # Create improved systemd service files
    sudo tee /etc/systemd/system/celery-worker.service > /dev/null << 'SERVICE_EOF'
[Unit]
Description=Celery Worker Service
After=network.target redis.service mariadb.service

[Service]
Type=simple
User=ec2-user
Group=ec2-user
EnvironmentFile=/var/www/salah-tracker/.env
WorkingDirectory=/var/www/salah-tracker
ExecStart=/var/www/salah-tracker/venv/bin/celery -A celery_config worker --loglevel=info
Restart=always
RestartSec=10s

[Install]
WantedBy=multi-user.target
SERVICE_EOF

    sudo tee /etc/systemd/system/celery-beat.service > /dev/null << 'BEAT_EOF'
[Unit]
Description=Celery Beat Service
After=network.target redis.service mariadb.service

[Service]
Type=simple
User=ec2-user
Group=ec2-user
EnvironmentFile=/var/www/salah-tracker/.env
WorkingDirectory=/var/www/salah-tracker
ExecStart=/var/www/salah-tracker/venv/bin/celery -A celery_config beat --loglevel=info
Restart=always
RestartSec=10s

[Install]
WantedBy=multi-user.target
BEAT_EOF

    # Reload systemd and start services
    sudo systemctl daemon-reload
    sudo systemctl enable celery-worker
    sudo systemctl enable celery-beat
    
    echo "✅ Celery services configured"
    
    echo ""
    echo "🚀 Starting all services..."
    
    # Start Redis
    sudo systemctl start redis
    
    # Start Celery services
    sudo systemctl start celery-worker
    sudo systemctl start celery-beat
    
    echo "⏳ Waiting for services to initialize..."
    sleep 5
    
    echo ""
    echo "🔍 Checking service status..."
    
    # Check Redis
    if redis-cli ping > /dev/null 2>&1; then
        echo "✅ Redis is running"
    else
        echo "❌ Redis is not responding"
    fi
    
    # Check Celery worker
    if sudo systemctl is-active --quiet celery-worker; then
        echo "✅ Celery worker is running"
    else
        echo "❌ Celery worker is not running"
        echo "Celery worker logs:"
        sudo journalctl -u celery-worker --no-pager -n 10
    fi
    
    # Check Celery beat
    if sudo systemctl is-active --quiet celery-beat; then
        echo "✅ Celery beat is running"
    else
        echo "❌ Celery beat is not running"
        echo "Celery beat logs:"
        sudo journalctl -u celery-beat --no-pager -n 10
    fi
    
    echo ""
    echo "📊 Final service status:"
    echo "========================"
    sudo systemctl status redis mariadb nginx celery-worker celery-beat --no-pager -l
    
    echo ""
    echo "✅ Service fixes completed!"
EOF

echo ""
echo "🎉 Remote services fix completed!"
echo ""
echo "📋 Next steps:"
echo "1. Check service status: ./check_remote_status.sh"
echo "2. Monitor logs: ssh -i $SSH_KEY $SERVER_USER@$SERVER_IP 'cd $APP_DIR && tail -f logs/flask_app.log'"
echo "3. Test caching functionality by completing a prayer"
