# EC2 Deployment Guide - Train Booking Platform

Complete guide to deploy the Train Booking Platform on an AWS EC2 instance.

---

## Prerequisites

### 1. AWS Resources Provisioned

Ensure you have created the following AWS resources:

#### **DynamoDB Tables**
- **Trains Table**: `trains` (or your custom name)
  - Primary Key: `TrainID` (String)
  
- **Bookings Table**: `bookings` (or your custom name)
  - Primary Key: `BookingID` (String)
  - GSI: `UserIdIndex` with partition key `UserID` (String)

- **Users Table**: `users` (or your custom name)
  - Primary Key: `UserID` (String)
  - GSI: `UsernameLowerIndex` with partition key `UsernameLower` (String)
  - GSI: `EmailLowerIndex` with partition key `EmailLower` (String)

#### **S3 Bucket**
- Bucket name: `train-booking-receipts` (or your custom name)
- CORS configuration enabled for uploads
- Bucket policy allowing EC2 IAM role to PutObject/GetObject

#### **Lambda Function** (Optional for notifications)
- Function name: `send-booking-notification` (or your custom name)
- Runtime: Python 3.9+

#### **SNS Topic** (Alternative to Lambda)
- Topic ARN for booking notifications

### 2. EC2 Instance Setup

**Recommended Instance Type**: `t3.small` or higher

**Operating System**: Ubuntu 22.04 LTS (or Amazon Linux 2023)

**Security Group**: Allow inbound traffic
- Port 80 (HTTP)
- Port 443 (HTTPS)
- Port 22 (SSH - restrict to your IP)

**IAM Role**: Attach an IAM role with the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:BatchWriteItem"
      ],
      "Resource": [
        "arn:aws:dynamodb:REGION:ACCOUNT_ID:table/trains",
        "arn:aws:dynamodb:REGION:ACCOUNT_ID:table/bookings",
        "arn:aws:dynamodb:REGION:ACCOUNT_ID:table/users",
        "arn:aws:dynamodb:REGION:ACCOUNT_ID:table/trains/index/*",
        "arn:aws:dynamodb:REGION:ACCOUNT_ID:table/bookings/index/*",
        "arn:aws:dynamodb:REGION:ACCOUNT_ID:table/users/index/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::train-booking-receipts",
        "arn:aws:s3:::train-booking-receipts/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "lambda:InvokeFunction"
      ],
      "Resource": "arn:aws:lambda:REGION:ACCOUNT_ID:function/send-booking-notification"
    }
  ]
}
```

---

## Deployment Steps

### Step 1: Connect to EC2 Instance

```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

### Step 2: Install System Dependencies

```bash
# Update package index
sudo apt update && sudo apt upgrade -y

# Install Python, pip, nginx, and git
sudo apt install -y python3 python3-pip python3-venv nginx git

# Create log directories
sudo mkdir -p /var/log/train-booking
sudo chown ubuntu:ubuntu /var/log/train-booking
```

### Step 3: Clone Repository

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git gemini
cd gemini
```

### Step 4: Set Up Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### Step 5: Configure Environment Variables

```bash
# Copy environment template
cp backend/.env.example backend/.env

# Edit environment file with your AWS resource names
nano backend/.env
```

**Set the following required values in `.env`:**

```bash
APP_ENV=production
USE_MOCK_AWS=false
SECRET_KEY=REPLACE_WITH_STRONG_RANDOM_SECRET_KEY_HERE
HOST=0.0.0.0
PORT=5001
FLASK_DEBUG=false

SESSION_COOKIE_SECURE=false  # Set to true when using HTTPS
SESSION_COOKIE_SAMESITE=Lax

AWS_REGION=us-east-1  # Your AWS region
DYNAMODB_TABLE_TRAINS=trains  # Your trains table name
DYNAMODB_TABLE_BOOKINGS=bookings  # Your bookings table name
DYNAMODB_TABLE_USERS=users  # Your users table name
S3_BUCKET_NAME=train-booking-receipts  # Your S3 bucket name
LAMBDA_FUNCTION_NAME=send-booking-notification  # Your Lambda function name

# Optional: First user with this email becomes admin
BOOTSTRAP_ADMIN_EMAIL=admin@example.com
```

**Generate a strong SECRET_KEY:**

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 6: Seed Train Data into DynamoDB

```bash
cd ~/gemini/backend
source ../venv/bin/activate
python seed_trains.py
```

**Expected output:**
```
Seeding trains table: trains in region us-east-1
  ✓ Inserted train 12951 - Mumbai Rajdhani Express
  ✓ Inserted train 12627 - Bangalore Mail
  ...
✓ Successfully seeded 35 trains into trains
```

### Step 7: Set Up Systemd Service

```bash
# Copy service file
sudo cp ~/gemini/deployment/train-booking.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable train-booking.service

# Start service
sudo systemctl start train-booking.service

# Check status
sudo systemctl status train-booking.service
```

**Service should show "active (running)"**

### Step 8: Configure Nginx

```bash
# Copy nginx configuration
sudo cp ~/gemini/deployment/nginx.conf /etc/nginx/sites-available/train-booking

# Create symbolic link
sudo ln -s /etc/nginx/sites-available/train-booking /etc/nginx/sites-enabled/

# Remove default site (optional)
sudo rm /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx

# Enable nginx to start on boot
sudo systemctl enable nginx
```

### Step 9: Verify Deployment

```bash
# Check if Gunicorn is running
sudo systemctl status train-booking.service

# Check if Nginx is running
sudo systemctl status nginx

# Test health endpoint locally
curl http://localhost/health

# Test from browser
# Open: http://YOUR_EC2_PUBLIC_IP
```

---

## Post-Deployment Configuration

### Optional: Set Up HTTPS with Let's Encrypt

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate (replace with your domain)
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

After SSL is configured:
- Update `backend/.env`: Set `SESSION_COOKIE_SECURE=true`
- Restart service: `sudo systemctl restart train-booking.service`

### Create First Admin User

1. Visit: `http://YOUR_EC2_IP/register`
2. Register with the email matching `BOOTSTRAP_ADMIN_EMAIL`
3. This user will have admin privileges

### Monitor Logs

```bash
# Application logs
tail -f /var/log/train-booking/access.log
tail -f /var/log/train-booking/error.log

# Nginx logs
tail -f /var/log/nginx/train-booking-access.log
tail -f /var/log/nginx/train-booking-error.log

# Systemd service logs
sudo journalctl -u train-booking.service -f
```

---

## Maintenance Commands

### Restart Application

```bash
sudo systemctl restart train-booking.service
```

### Update Code from Git

```bash
cd ~/gemini
git pull origin main
source venv/bin/activate
pip install -r backend/requirements.txt
sudo systemctl restart train-booking.service
```

### View Service Status

```bash
sudo systemctl status train-booking.service
```

### Stop/Start Services

```bash
# Stop application
sudo systemctl stop train-booking.service

# Start application
sudo systemctl start train-booking.service

# Restart Nginx
sudo systemctl restart nginx
```

---

## Troubleshooting

### Application Won't Start

```bash
# Check logs
sudo journalctl -u train-booking.service -n 50

# Verify environment variables
cat ~/gemini/backend/.env

# Test manually
cd ~/gemini/backend
source ../venv/bin/activate
gunicorn --bind 127.0.0.1:5001 wsgi:app
```

### DynamoDB Access Denied

- Verify IAM role is attached to EC2 instance
- Check IAM policy includes correct table ARNs and region
- Ensure table names in `.env` match actual table names

### S3 Access Errors

- Verify IAM role has S3 permissions
- Check bucket name in `.env` matches actual bucket
- Ensure bucket policy allows EC2 role access

### 502 Bad Gateway (Nginx)

- Check if Gunicorn is running: `sudo systemctl status train-booking.service`
- Verify port 5001 is listening: `sudo netstat -tulpn | grep 5001`
- Check Gunicorn logs: `tail -f /var/log/train-booking/error.log`

---

## Security Hardening Checklist

- [ ] Use HTTPS with valid SSL certificate
- [ ] Set `SESSION_COOKIE_SECURE=true` in production
- [ ] Restrict SSH access to specific IPs in Security Group
- [ ] Use strong, randomly-generated `SECRET_KEY`
- [ ] Enable CloudWatch logging for EC2, DynamoDB, and Lambda
- [ ] Configure automatic security updates
- [ ] Set up CloudWatch alarms for high CPU/memory usage
- [ ] Implement regular DynamoDB backups
- [ ] Use AWS Systems Manager Session Manager instead of SSH (optional)

---

## Architecture Summary

```
Internet
    ↓
Nginx (Port 80/443) - Reverse Proxy + Static Files
    ↓
Gunicorn (Port 5001) - WSGI Server
    ↓
Flask App (app.py) - Application Logic
    ↓
AWS Services:
    - DynamoDB (Users, Trains, Bookings)
    - S3 (Receipts)
    - Lambda/SNS (Notifications)
```

---

## Support

For issues or questions, refer to:
- Application logs: `/var/log/train-booking/`
- System logs: `sudo journalctl -u train-booking.service`
- AWS CloudWatch Logs (if configured)
