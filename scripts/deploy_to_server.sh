#!/bin/bash

# 🚀 Salah Tracker Deployment Script
# This script will deploy your app to the EC2 server

set -e

# Configuration
SERVER_IP="13.233.86.216"
SSH_KEY="salah-tracker-server-1.pem"
SERVER_USER="ec2-user"
APP_DIR="/var/www/salah-tracker"

echo "🚀 Starting deployment to EC2 server..."

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
    ./ "$SERVER_USER@$SERVER_IP:$APP_DIR/"

echo "🔧 Setting up server environment..."

# Run server setup commands
ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" << 'EOF'
    cd /var/www/salah-tracker
    
    # Update system
    sudo yum update -y
    
    # Install required packages
    sudo yum install python3 python3-pip python3-devel mysql-server redis nginx git -y
    
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
    
    echo "✅ Server setup completed!"
EOF

echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. SSH into your server: ssh -i $SSH_KEY $SERVER_USER@$SERVER_IP"
echo "2. Update the .env file with your production values"
echo "3. Set up the database and run migrations"
echo "4. Configure Nginx and start the services"
echo ""
echo "📖 For detailed instructions, see DEPLOYMENT_GUIDE.md"
echo ""
echo "🔗 Your server: $SERVER_IP"
