#!/bin/bash
# Quick deployment check script for EC2 instances
# Run this after deployment to verify everything is working

echo "=== Train Booking Platform - Deployment Verification ==="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_service() {
    if systemctl is-active --quiet $1; then
        echo -e "${GREEN}✓${NC} $1 is running"
        return 0
    else
        echo -e "${RED}✗${NC} $1 is NOT running"
        return 1
    fi
}

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} File exists: $1"
        return 0
    else
        echo -e "${RED}✗${NC} File missing: $1"
        return 1
    fi
}

check_env_var() {
    if grep -q "^$1=" ~/gemini/backend/.env 2>/dev/null; then
        value=$(grep "^$1=" ~/gemini/backend/.env | cut -d'=' -f2)
        if [ -n "$value" ] && [ "$value" != "replace-with-strong-random-value" ]; then
            echo -e "${GREEN}✓${NC} $1 is set"
            return 0
        else
            echo -e "${YELLOW}⚠${NC} $1 needs to be configured"
            return 1
        fi
    else
        echo -e "${RED}✗${NC} $1 is not set"
        return 1
    fi
}

echo "1. Checking required files..."
check_file ~/gemini/backend/.env
check_file ~/gemini/backend/wsgi.py
check_file ~/gemini/backend/app.py
echo ""

echo "2. Checking environment configuration..."
check_env_var "SECRET_KEY"
check_env_var "USE_MOCK_AWS"
check_env_var "DYNAMODB_TABLE_TRAINS"
check_env_var "S3_BUCKET_NAME"
echo ""

echo "3. Checking services..."
check_service "train-booking"
check_service "nginx"
echo ""

echo "4. Checking network ports..."
if netstat -tuln | grep -q ":5001 "; then
    echo -e "${GREEN}✓${NC} Gunicorn is listening on port 5001"
else
    echo -e "${RED}✗${NC} Gunicorn is NOT listening on port 5001"
fi

if netstat -tuln | grep -q ":80 "; then
    echo -e "${GREEN}✓${NC} Nginx is listening on port 80"
else
    echo -e "${RED}✗${NC} Nginx is NOT listening on port 80"
fi
echo ""

echo "5. Testing health endpoint..."
health_response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/health 2>/dev/null)
if [ "$health_response" = "200" ]; then
    echo -e "${GREEN}✓${NC} Health endpoint returned 200 OK"
else
    echo -e "${RED}✗${NC} Health endpoint returned $health_response"
fi
echo ""

echo "6. Checking IAM role (AWS CLI required)..."
if command -v aws &> /dev/null; then
    if aws sts get-caller-identity &> /dev/null; then
        echo -e "${GREEN}✓${NC} AWS credentials are configured"
        role_arn=$(aws sts get-caller-identity --query Arn --output text 2>/dev/null)
        echo "   Role: $role_arn"
    else
        echo -e "${RED}✗${NC} AWS credentials not found or invalid"
    fi
else
    echo -e "${YELLOW}⚠${NC} AWS CLI not installed (optional but recommended)"
fi
echo ""

echo "7. Recent application logs..."
echo "Last 5 lines from error.log:"
if [ -f /var/log/train-booking/error.log ]; then
    tail -5 /var/log/train-booking/error.log
else
    echo -e "${YELLOW}⚠${NC} Log file not found"
fi
echo ""

echo "=== Verification Complete ==="
echo ""
echo "Next steps:"
echo "  - Visit http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo 'YOUR_EC2_IP') in your browser"
echo "  - Register a new user"
echo "  - Search for trains"
echo "  - Monitor logs: tail -f /var/log/train-booking/error.log"
