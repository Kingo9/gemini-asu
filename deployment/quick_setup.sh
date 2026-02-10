#!/bin/bash
# Quick setup script for EC2 - automates common deployment steps
# Run as: bash deployment/quick_setup.sh

set -e

echo "=== Train Booking Platform - Quick EC2 Setup ==="
echo ""

# Check if running on Ubuntu/Debian
if ! command -v apt &> /dev/null; then
    echo "Error: This script is designed for Ubuntu/Debian systems"
    exit 1
fi

# Check if running as ubuntu user
if [ "$USER" != "ubuntu" ] && [ "$USER" != "root" ]; then
    echo "Warning: This script is designed to run as 'ubuntu' user"
    echo "Current user: $USER"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "Step 1: Installing system dependencies..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx git curl

echo ""
echo "Step 2: Creating Python virtual environment..."
cd ~/gemini
python3 -m venv venv
source venv/bin/activate

echo ""
echo "Step 3: Installing Python dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt

echo ""
echo "Step 4: Creating log directories..."
sudo mkdir -p /var/log/train-booking
sudo chown $USER:$USER /var/log/train-booking

echo ""
echo "Step 5: Setting up environment file..."
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo "✓ Created backend/.env from template"
    echo ""
    echo "IMPORTANT: You must edit backend/.env and set:"
    echo "  - SECRET_KEY (generate with: python3 -c \"import secrets; print(secrets.token_urlsafe(32))\")"
    echo "  - AWS resource names (DynamoDB tables, S3 bucket, Lambda function)"
    echo "  - USE_MOCK_AWS=false for production"
    echo ""
    read -p "Press Enter to edit .env now, or Ctrl+C to exit and edit manually..."
    nano backend/.env
else
    echo "✓ backend/.env already exists"
fi

echo ""
echo "Step 6: Setting up systemd service..."
sudo cp deployment/train-booking.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable train-booking.service
echo "✓ Service installed and enabled"

echo ""
echo "Step 7: Setting up Nginx..."
sudo cp deployment/nginx.conf /etc/nginx/sites-available/train-booking
sudo ln -sf /etc/nginx/sites-available/train-booking /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx
echo "✓ Nginx configured and running"

echo ""
echo "Step 8: Starting application..."
sudo systemctl start train-booking.service
sleep 3
sudo systemctl status train-booking.service --no-pager

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "Next steps:"
echo "  1. Seed train data: cd ~/gemini/backend && source ../venv/bin/activate && python seed_trains.py"
echo "  2. Verify deployment: bash ~/gemini/deployment/verify_deployment.sh"
echo "  3. Check logs: tail -f /var/log/train-booking/error.log"
echo "  4. Access app: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo 'YOUR_EC2_IP')"
echo ""
