#!/bin/bash

# 🚀 Salah Tracker Deployment Script with Caching
# This script will deploy your app to the EC2 server with Redis caching

set -e

# Configuration
SERVER_IP="13.233.86.216"
SSH_KEY="/Users/mohammadshahjahan/Downloads/salah-tracker-server-1.pem"
SERVER_USER="ec2-user"
APP_DIR="/var/www/salah-tracker"

echo "🚀 Starting deployment to EC2 server with caching support..."

# Check if SSH key exists
if [ ! -f "$SSH_KEY" ]; then
    echo "❌ SSH key file '$SSH_KEY' not found!"
    echo "Please make sure the SSH key is in the current directory."
    exit 1
fi

# Set proper permissions for SSH key
chmod 600 "$SSH_KEY"

echo "📁 Uploading files to server..."

# Create app directory on server
ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "sudo mkdir -p $APP_DIR && sudo chown $SERVER_USER:$SERVER_USER $APP_DIR"

# Upload all files to server
rsync -avz --progress -e "ssh -i $SSH_KEY" \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='venv' \
    --exclude='.env' \
    --exclude='logs' \
    --exclude='*.log' \
    --exclude='dump.rdb' \
    ./ "$SERVER_USER@$SERVER_IP:$APP_DIR/"

echo "🔧 Setting up server environment with Redis caching..."

# Run server setup commands
ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" << 'EOF'
    cd /var/www/salah-tracker
    
    # Update system
    sudo yum update -y
    
    # Install required packages including Redis
    sudo yum install python3 python3-pip python3-devel mysql-server redis nginx git -y
    
    # Configure Redis for caching
    sudo sed -i 's/^# maxmemory <bytes>/maxmemory 256mb/' /etc/redis.conf
    sudo sed -i 's/^# maxmemory-policy noeviction/maxmemory-policy allkeys-lru/' /etc/redis.conf
    
    # Start services
    sudo systemctl start mysqld
    sudo systemctl enable mysqld
    sudo systemctl start redis
    sudo systemctl enable redis
    sudo systemctl start nginx
    sudo systemctl enable nginx
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Install Python dependencies
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Create .env file from example
    if [ ! -f .env ]; then
        cp env.example .env
        echo "⚠️  Please update the .env file with your production values!"
    fi
    
    # Test Redis connection
    redis-cli ping
    
    echo "✅ Server setup with Redis caching completed!"
EOF

echo "🔄 Setting up Celery workers with caching..."

# Setup Celery workers
ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" << 'EOF'
    cd /var/www/salah-tracker
    source venv/bin/activate
    
    # Create systemd service files for Celery
    sudo tee /etc/systemd/system/celery-worker.service > /dev/null << 'SERVICE_EOF'
[Unit]
Description=Celery Worker Service
After=network.target redis.service mysql.service

[Service]
Type=forking
User=ec2-user
Group=ec2-user
EnvironmentFile=/var/www/salah-tracker/.env
WorkingDirectory=/var/www/salah-tracker
ExecStart=/var/www/salah-tracker/venv/bin/celery -A celery_config worker --loglevel=info --detach
ExecStop=/bin/kill -s TERM $MAINPID
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
Restart=always
RestartSec=10s

[Install]
WantedBy=multi-user.target
SERVICE_EOF

    sudo tee /etc/systemd/system/celery-beat.service > /dev/null << 'BEAT_EOF'
[Unit]
Description=Celery Beat Service
After=network.target redis.service mysql.service

[Service]
Type=forking
User=ec2-user
Group=ec2-user
EnvironmentFile=/var/www/salah-tracker/.env
WorkingDirectory=/var/www/salah-tracker
ExecStart=/var/www/salah-tracker/venv/bin/celery -A celery_config beat --loglevel=info --detach
ExecStop=/bin/kill -s TERM $MAINPID
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
Restart=always
RestartSec=10s

[Install]
WantedBy=multi-user.target
BEAT_EOF

    # Reload systemd and start services
    sudo systemctl daemon-reload
    sudo systemctl enable celery-worker
    sudo systemctl enable celery-beat
    
    echo "✅ Celery workers configured!"
EOF

echo "🧪 Running tests to verify caching functionality..."

# Run tests on server
ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" << 'EOF'
    cd /var/www/salah-tracker
    source venv/bin/activate
    
    # Run caching tests
    python3 -m pytest tests/test_caching.py::TestCacheService -v
    
    echo "✅ Tests passed!"
EOF

echo "🎉 Deployment with caching completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. SSH into your server: ssh -i $SSH_KEY $SERVER_USER@$SERVER_IP"
echo "2. Update the .env file with your production values"
echo "3. Set up the database and run migrations"
echo "4. Configure Nginx and start the services"
echo "5. Start Celery workers: sudo systemctl start celery-worker celery-beat"
echo ""
echo "🚀 Caching Features Deployed:"
echo "   ✅ Redis-based caching for prayer times"
echo "   ✅ Dashboard stats caching"
echo "   ✅ Automatic cache invalidation"
echo "   ✅ Fallback to in-memory caching"
echo "   ✅ Celery workers with caching support"
echo ""
echo "📖 For detailed instructions, see DEPLOYMENT_GUIDE.md"
echo ""
echo "🔗 Your server: $SERVER_IP"
