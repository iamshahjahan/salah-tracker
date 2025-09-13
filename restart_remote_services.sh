#!/bin/bash

# 🔄 Remote Services Restart Script
# This script will restart all services on the remote EC2 server

set -e

# Configuration
SERVER_IP="13.234.217.179"
SSH_KEY="/Users/mohammadshahjahan/Downloads/salah-tracker-server-1.pem"
SERVER_USER="ec2-user"
APP_DIR="/var/www/salah-tracker"

echo "🔄 Starting remote services restart..."

# Check if SSH key exists
if [ ! -f "$SSH_KEY" ]; then
    echo "❌ SSH key file '$SSH_KEY' not found!"
    echo "Please make sure the SSH key is in the current directory."
    exit 1
fi

# Set proper permissions for SSH key
chmod 600 "$SSH_KEY"

echo "🔧 Restarting services on remote server..."

# Restart all services on the remote server
ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" << 'EOF'
    echo "🛑 Stopping all services..."
    
    # Stop Flask application (if running with systemd)
    sudo systemctl stop salah-tracker 2>/dev/null || echo "Flask app not running as systemd service"
    
    # Stop Celery workers
    sudo systemctl stop celery-worker 2>/dev/null || echo "Celery worker not running"
    sudo systemctl stop celery-beat 2>/dev/null || echo "Celery beat not running"
    
    # Kill any existing Python processes
    pkill -f "python.*main.py" 2>/dev/null || echo "No Python main.py processes found"
    pkill -f "celery.*worker" 2>/dev/null || echo "No Celery worker processes found"
    pkill -f "celery.*beat" 2>/dev/null || echo "No Celery beat processes found"
    
    echo "⏳ Waiting for processes to stop..."
    sleep 3
    
    echo "🔄 Restarting core services..."
    
    # Restart Redis
    sudo systemctl restart redis
    sudo systemctl status redis --no-pager -l
    
    # Restart MySQL
    sudo systemctl restart mysqld
    sudo systemctl status mysqld --no-pager -l
    
    # Restart Nginx
    sudo systemctl restart nginx
    sudo systemctl status nginx --no-pager -l
    
    echo "🚀 Starting application services..."
    
    # Navigate to app directory
    cd /var/www/salah-tracker
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Start Celery workers
    echo "Starting Celery worker..."
    sudo systemctl start celery-worker
    sudo systemctl status celery-worker --no-pager -l
    
    echo "Starting Celery beat..."
    sudo systemctl start celery-beat
    sudo systemctl status celery-beat --no-pager -l
    
    # Start Flask application in background
    echo "Starting Flask application..."
    nohup python3 main.py > logs/flask_app.log 2>&1 &
    echo $! > logs/flask.pid
    
    echo "⏳ Waiting for services to initialize..."
    sleep 5
    
    echo "🔍 Checking service status..."
    
    # Check Redis
    if redis-cli ping > /dev/null 2>&1; then
        echo "✅ Redis is running"
    else
        echo "❌ Redis is not responding"
    fi
    
    # Check MySQL
    if sudo systemctl is-active --quiet mysqld; then
        echo "✅ MySQL is running"
    else
        echo "❌ MySQL is not running"
    fi
    
    # Check Nginx
    if sudo systemctl is-active --quiet nginx; then
        echo "✅ Nginx is running"
    else
        echo "❌ Nginx is not running"
    fi
    
    # Check Celery worker
    if sudo systemctl is-active --quiet celery-worker; then
        echo "✅ Celery worker is running"
    else
        echo "❌ Celery worker is not running"
    fi
    
    # Check Celery beat
    if sudo systemctl is-active --quiet celery-beat; then
        echo "✅ Celery beat is running"
    else
        echo "❌ Celery beat is not running"
    fi
    
    # Check Flask application
    if [ -f logs/flask.pid ] && kill -0 $(cat logs/flask.pid) 2>/dev/null; then
        echo "✅ Flask application is running (PID: $(cat logs/flask.pid))"
    else
        echo "❌ Flask application is not running"
    fi
    
    echo "📊 Service status summary:"
    echo "=========================="
    sudo systemctl status redis mysqld nginx celery-worker celery-beat --no-pager -l
    
    echo "📝 Recent logs:"
    echo "==============="
    echo "Flask app logs (last 10 lines):"
    tail -10 logs/flask_app.log 2>/dev/null || echo "No Flask logs found"
    
    echo ""
    echo "Celery worker logs (last 5 lines):"
    sudo journalctl -u celery-worker --no-pager -n 5 2>/dev/null || echo "No Celery worker logs found"
    
    echo ""
    echo "Celery beat logs (last 5 lines):"
    sudo journalctl -u celery-beat --no-pager -n 5 2>/dev/null || echo "No Celery beat logs found"
    
    echo ""
    echo "✅ Services restart completed!"
EOF

echo ""
echo "🎉 Remote services restart completed!"
echo ""
echo "📋 Service Status:"
echo "=================="
echo "🔗 Server: $SERVER_IP"
echo "📁 App Directory: $APP_DIR"
echo ""
echo "🔍 To check logs manually:"
echo "ssh -i $SSH_KEY $SERVER_USER@$SERVER_IP 'cd $APP_DIR && tail -f logs/flask_app.log'"
echo ""
echo "🔍 To check service status:"
echo "ssh -i $SSH_KEY $SERVER_USER@$SERVER_IP 'sudo systemctl status redis mysqld nginx celery-worker celery-beat'"
echo ""
echo "🔍 To restart individual services:"
echo "ssh -i $SSH_KEY $SERVER_USER@$SERVER_IP 'sudo systemctl restart <service-name>'"
