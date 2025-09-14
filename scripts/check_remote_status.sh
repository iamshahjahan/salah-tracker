#!/bin/bash

# 📊 Remote Services Status Check Script
# This script will check the status of all services on the remote EC2 server

set -e

# Configuration
SERVER_IP="13.234.217.179"
SSH_KEY="/Users/mohammadshahjahan/Downloads/salah-tracker-server-1.pem"
SERVER_USER="ec2-user"
APP_DIR="/var/www/salah-tracker"

echo "📊 Checking remote services status..."

# Check if SSH key exists
if [ ! -f "$SSH_KEY" ]; then
    echo "❌ SSH key file '$SSH_KEY' not found!"
    echo "Please make sure the SSH key is in the current directory."
    exit 1
fi

# Set proper permissions for SSH key
chmod 600 "$SSH_KEY"

# Check services status on the remote server
ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" << 'EOF'
    echo "🔍 Service Status Check - $(date)"
    echo "=================================="
    
    # Check Redis
    echo "📦 Redis Status:"
    if redis-cli ping > /dev/null 2>&1; then
        echo "✅ Redis is running and responding"
        redis-cli info memory | grep used_memory_human || echo "Memory info not available"
    else
        echo "❌ Redis is not responding"
    fi
    echo ""
    
    # Check MySQL
    echo "🗄️  MySQL Status:"
    if sudo systemctl is-active --quiet mysqld; then
        echo "✅ MySQL is running"
        sudo systemctl status mysqld --no-pager -l | head -3
    else
        echo "❌ MySQL is not running"
    fi
    echo ""
    
    # Check Nginx
    echo "🌐 Nginx Status:"
    if sudo systemctl is-active --quiet nginx; then
        echo "✅ Nginx is running"
        sudo systemctl status nginx --no-pager -l | head -3
    else
        echo "❌ Nginx is not running"
    fi
    echo ""
    
    # Check Celery Worker
    echo "👷 Celery Worker Status:"
    if sudo systemctl is-active --quiet celery-worker; then
        echo "✅ Celery worker is running"
        sudo systemctl status celery-worker --no-pager -l | head -3
    else
        echo "❌ Celery worker is not running"
    fi
    echo ""
    
    # Check Celery Beat
    echo "⏰ Celery Beat Status:"
    if sudo systemctl is-active --quiet celery-beat; then
        echo "✅ Celery beat is running"
        sudo systemctl status celery-beat --no-pager -l | head -3
    else
        echo "❌ Celery beat is not running"
    fi
    echo ""
    
    # Check Flask Application
    echo "🐍 Flask Application Status:"
    cd /var/www/salah-tracker
    if [ -f logs/flask.pid ] && kill -0 $(cat logs/flask.pid) 2>/dev/null; then
        echo "✅ Flask application is running (PID: $(cat logs/flask.pid))"
        echo "📊 Process info:"
        ps -p $(cat logs/flask.pid) -o pid,ppid,cmd,etime 2>/dev/null || echo "Process info not available"
    else
        echo "❌ Flask application is not running"
    fi
    echo ""
    
    # Check application logs for errors
    echo "📝 Recent Application Logs:"
    echo "============================"
    if [ -f logs/flask_app.log ]; then
        echo "Flask app logs (last 5 lines):"
        tail -5 logs/flask_app.log
    else
        echo "No Flask logs found"
    fi
    echo ""
    
    # Check system resources
    echo "💻 System Resources:"
    echo "==================="
    echo "CPU Usage:"
    top -bn1 | grep "Cpu(s)" || echo "CPU info not available"
    echo ""
    echo "Memory Usage:"
    free -h
    echo ""
    echo "Disk Usage:"
    df -h / | tail -1
    echo ""
    
    # Check network connectivity
    echo "🌐 Network Connectivity:"
    echo "========================"
    echo "Server IP: $(curl -s ifconfig.me || echo 'Unable to get external IP')"
    echo "Local IP: $(hostname -I | awk '{print $1}')"
    echo ""
    
    # Check application endpoints (if accessible)
    echo "🔗 Application Health Check:"
    echo "============================"
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:5001/health 2>/dev/null; then
        echo "✅ Application health endpoint responding"
    else
        echo "❌ Application health endpoint not responding"
    fi
    echo ""
    
    echo "✅ Status check completed!"
EOF

echo ""
echo "📊 Remote services status check completed!"
echo ""
echo "🔗 Server: $SERVER_IP"
echo "📁 App Directory: $APP_DIR"
echo ""
echo "💡 Useful commands:"
echo "==================="
echo "Restart services: ./restart_remote_services.sh"
echo "View live logs: ssh -i $SSH_KEY $SERVER_USER@$SERVER_IP 'cd $APP_DIR && tail -f logs/flask_app.log'"
echo "SSH to server: ssh -i $SSH_KEY $SERVER_USER@$SERVER_IP"
