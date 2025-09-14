#!/bin/bash

# 🔄 Remote Services Restart Script
# This script will restart all services on the remote EC2 server
# Updated for Amazon Linux 2023 with proper service management

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
    echo "Please make sure the SSH key is in the correct location."
    exit 1
fi

# Set proper permissions for SSH key
chmod 600 "$SSH_KEY"

echo "🔧 Restarting services on remote server..."

ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" << 'EOF'
    set -e
    
    echo "🛑 Stopping all services..."
    
    # Stop systemd services (ignore errors if they don't exist)
    sudo systemctl stop salah-tracker 2>/dev/null || echo "Flask app not running as systemd service"
    sudo systemctl stop celery-worker 2>/dev/null || echo "Celery worker not running as systemd service"
    sudo systemctl stop celery-beat 2>/dev/null || echo "Celery beat not running as systemd service"
    
    # Kill any existing Python processes (more thorough cleanup)
    pkill -f "python.*main.py" 2>/dev/null || echo "No Python main.py processes found"
    pkill -f "celery.*worker" 2>/dev/null || echo "No Celery worker processes found"
    pkill -f "celery.*beat" 2>/dev/null || echo "No Celery beat processes found"
    
    # Additional cleanup for any remaining Celery processes
    pkill -f "celery" 2>/dev/null || echo "No additional Celery processes found"
    
    # Clean up any stale PID files
    rm -f logs/flask.pid logs/celery_worker.pid logs/celery_beat.pid 2>/dev/null || true
    
    echo "⏳ Waiting for processes to stop..."
    sleep 3
    
    echo "🔄 Restarting core services..."
    
    # Check and restart Redis (check if it's running first)
    if netstat -tlnp 2>/dev/null | grep -q ":6379.*LISTEN"; then
        echo "✅ Redis is already running on port 6379"
    else
        echo "🔄 Starting Redis..."
        # Try different Redis service names for Amazon Linux 2023
        if systemctl is-active --quiet redis6 2>/dev/null; then
            sudo systemctl restart redis6
            echo "✅ Redis6 restarted"
        elif systemctl is-active --quiet redis 2>/dev/null; then
            sudo systemctl restart redis
            echo "✅ Redis restarted"
        else
            echo "⚠️ Redis service not found, trying to start manually"
            sudo systemctl start redis6 2>/dev/null || sudo systemctl start redis 2>/dev/null || echo "Could not start Redis"
        fi
    fi
    
    # Check and restart MariaDB (check if it's running first)
    if netstat -tlnp 2>/dev/null | grep -q ":3306.*LISTEN"; then
        echo "✅ MariaDB is already running on port 3306"
    else
        echo "🔄 Starting MariaDB..."
        # Try different MariaDB service names for Amazon Linux 2023
        if systemctl is-active --quiet mariadb 2>/dev/null; then
            sudo systemctl restart mariadb
            echo "✅ MariaDB restarted"
        elif systemctl is-active --quiet mariadb105-server 2>/dev/null; then
            sudo systemctl restart mariadb105-server
            echo "✅ MariaDB105-server restarted"
        else
            echo "⚠️ MariaDB service not found, trying to start manually"
            sudo systemctl start mariadb 2>/dev/null || sudo systemctl start mariadb105-server 2>/dev/null || echo "Could not start MariaDB"
        fi
    fi
    
    # Restart Nginx
    sudo systemctl restart nginx
    echo "✅ Nginx restarted"
    
    echo "🚀 Starting application services..."
    cd /var/www/salah-tracker
    
    # Ensure virtual environment exists and is activated
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    
    # Install/update dependencies
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt > /dev/null 2>&1
    
    # Start Celery Worker (with proper logging configuration)
    echo "🔄 Starting Celery Worker..."
    nohup celery -A celery_config worker --loglevel=info --concurrency=2 --logfile=logs/celery_worker.log --pidfile=logs/celery_worker.pid --detach > /dev/null 2>&1
    echo "✅ Celery Worker started"
    
    # Start Celery Beat (with proper logging configuration)
    echo "🔄 Starting Celery Beat..."
    nohup celery -A celery_config beat --loglevel=info --logfile=logs/celery_beat.log --pidfile=logs/celery_beat.pid --detach > /dev/null 2>&1
    echo "✅ Celery Beat started"
    
    # Start Flask Application
    echo "🔄 Starting Flask Application..."
    nohup python main.py > logs/flask_app.log 2>&1 &
    echo $! > logs/flask.pid
    echo "✅ Flask Application started (PID: $(cat logs/flask.pid))"
    
    echo "⏳ Waiting for services to initialize..."
    sleep 5
    
    echo "🔍 Checking service status..."
    
    # Check Redis (check if port is listening)
    if netstat -tlnp 2>/dev/null | grep -q ":6379.*LISTEN"; then
        echo "✅ Redis is running and listening on port 6379"
    else
        echo "❌ Redis is not running or not listening on port 6379"
    fi
    
    # Check MariaDB (check if port is listening)
    if netstat -tlnp 2>/dev/null | grep -q ":3306.*LISTEN"; then
        echo "✅ MariaDB is running and listening on port 3306"
    else
        echo "❌ MariaDB is not running or not listening on port 3306"
    fi
    
    # Check Nginx
    if systemctl is-active --quiet nginx; then
        echo "✅ Nginx is running"
    else
        echo "❌ Nginx is not running"
    fi
    
    # Check Celery Worker (check for actual processes, not just PID files)
    if pgrep -f "celery.*worker" > /dev/null; then
        WORKER_PIDS=$(pgrep -f "celery.*worker" | tr '\n' ' ')
        echo "✅ Celery Worker is running (PIDs: $WORKER_PIDS)"
    else
        echo "❌ Celery Worker is not running"
    fi
    
    # Check Celery Beat (check for actual processes, not just PID files)
    if pgrep -f "celery.*beat" > /dev/null; then
        BEAT_PID=$(pgrep -f "celery.*beat")
        echo "✅ Celery Beat is running (PID: $BEAT_PID)"
    else
        echo "❌ Celery Beat is not running"
    fi
    
    # Check Flask Application
    if [ -f logs/flask.pid ] && kill -0 $(cat logs/flask.pid) 2>/dev/null; then
        echo "✅ Flask Application is running (PID: $(cat logs/flask.pid))"
    else
        echo "❌ Flask Application is not running"
    fi
    
    echo ""
    echo "📊 Port Status:"
    netstat -tlnp | grep -E ":(80|5001|6379|3306)" || echo "No services listening on expected ports"
    
    echo ""
    echo "🌐 Testing Application Access:"
    if curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:5001/; then
        echo "✅ Flask application is accessible locally"
    else
        echo "❌ Flask application is not accessible locally"
    fi
    
    if curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost/; then
        echo "✅ Application is accessible through Nginx"
    else
        echo "❌ Application is not accessible through Nginx"
    fi
    
    echo ""
    echo "📝 Recent logs:"
    echo "==============="
    echo "Flask app logs (last 5 lines):"
    tail -5 logs/flask_app.log 2>/dev/null || echo "No Flask logs found"
    
    echo ""
    echo "Celery worker logs (last 5 lines):"
    tail -5 logs/celery_worker.log 2>/dev/null || echo "No Celery worker logs found"
    
    echo ""
    echo "Celery beat logs (last 5 lines):"
    tail -5 logs/celery_beat.log 2>/dev/null || echo "No Celery beat logs found"
    
    echo ""
    echo "✅ Services restart completed!"
EOF

echo ""
echo "🎉 Remote services restart completed!"
echo ""
echo "📋 Service Status Summary:"
echo "=========================="
echo "🔗 Server: $SERVER_IP"
echo "📁 App Directory: $APP_DIR"
echo ""
echo "🔍 To check logs manually:"
echo "ssh -i $SSH_KEY $SERVER_USER@$SERVER_IP 'cd $APP_DIR && tail -f logs/flask_app.log'"
echo ""
echo "🔍 To check service status:"
echo "ssh -i $SSH_KEY $SERVER_USER@$SERVER_IP 'cd $APP_DIR && ps aux | grep -E \"(python|celery)\" | grep -v grep'"
echo ""
echo "🔍 To restart individual services:"
echo "ssh -i $SSH_KEY $SERVER_USER@$SERVER_IP 'cd $APP_DIR && source venv/bin/activate && celery -A celery_config worker --loglevel=info --detach'"