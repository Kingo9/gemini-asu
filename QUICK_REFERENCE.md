# Quick Reference Guide

Fast reference for deploying and managing the Train Booking Platform on EC2.

---

## 🚀 One-Line Deployment

```bash
# After cloning repo on EC2, run:
cd ~/gemini && bash deployment/quick_setup.sh
```

---

## 📝 Environment Variables (backend/.env)

```bash
# Generate SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Minimal production .env
APP_ENV=production
USE_MOCK_AWS=false
SECRET_KEY=<paste-generated-secret>
AWS_REGION=us-east-1
DYNAMODB_TABLE_TRAINS=trains
DYNAMODB_TABLE_BOOKINGS=bookings
DYNAMODB_TABLE_USERS=users
S3_BUCKET_NAME=train-booking-receipts
LAMBDA_FUNCTION_NAME=send-booking-notification
BOOTSTRAP_ADMIN_EMAIL=admin@yourdomain.com
```

---

## 🗄️ DynamoDB Schema Quick Reference

### Trains Table
```
Primary Key: TrainID (String)
```

### Bookings Table
```
Primary Key: BookingID (String)
GSI: UserIdIndex
  - Partition Key: UserID (String)
```

### Users Table
```
Primary Key: UserID (String)
GSI: UsernameLowerIndex
  - Partition Key: UsernameLower (String)
GSI: EmailLowerIndex
  - Partition Key: EmailLower (String)
```

---

## 🔧 Common Commands

### Service Management
```bash
# Start/Stop/Restart
sudo systemctl start train-booking.service
sudo systemctl stop train-booking.service
sudo systemctl restart train-booking.service

# Check status
sudo systemctl status train-booking.service

# View logs
sudo journalctl -u train-booking.service -f
```

### Application Logs
```bash
# Error log (live)
tail -f /var/log/train-booking/error.log

# Access log (live)
tail -f /var/log/train-booking/access.log

# View last 50 errors
tail -50 /var/log/train-booking/error.log
```

### Nginx
```bash
# Test configuration
sudo nginx -t

# Reload configuration
sudo systemctl reload nginx

# Restart
sudo systemctl restart nginx

# View logs
tail -f /var/log/nginx/train-booking-error.log
```

### Code Updates
```bash
cd ~/gemini
git pull origin main
source venv/bin/activate
pip install -r backend/requirements.txt
sudo systemctl restart train-booking.service
```

---

## 🌱 Seed Train Data

```bash
cd ~/gemini/backend
source ../venv/bin/activate
python seed_trains.py
```

---

## 🔍 Health Checks

```bash
# Local health check
curl http://localhost/health

# Public health check
curl http://YOUR_EC2_PUBLIC_IP/health

# Expected response
{"status":"ok"}
```

---

## 🐛 Quick Troubleshooting

### App won't start
```bash
# Check logs for errors
sudo journalctl -u train-booking.service -n 50

# Test manually
cd ~/gemini/backend
source ../venv/bin/activate
gunicorn --bind 127.0.0.1:5001 wsgi:app
```

### DynamoDB errors
```bash
# Verify IAM role
aws sts get-caller-identity

# Test DynamoDB access
aws dynamodb describe-table --table-name trains
```

### 502 Bad Gateway
```bash
# Check if Gunicorn is running
sudo systemctl status train-booking.service

# Check if port 5001 is listening
sudo netstat -tulpn | grep 5001

# Check Nginx logs
tail -20 /var/log/nginx/train-booking-error.log
```

---

## 📊 File Locations

```
Application Code:     ~/gemini/
Virtual Environment:  ~/gemini/venv/
Environment Config:   ~/gemini/backend/.env
Application Logs:     /var/log/train-booking/
Nginx Config:         /etc/nginx/sites-available/train-booking
Systemd Service:      /etc/systemd/system/train-booking.service
Nginx Logs:           /var/log/nginx/
```

---

## 🔒 Security Checklist

- [ ] SECRET_KEY is set to random value (not default)
- [ ] USE_MOCK_AWS=false in production
- [ ] IAM role attached to EC2 (no hardcoded credentials)
- [ ] HTTPS configured with valid certificate
- [ ] SESSION_COOKIE_SECURE=true when using HTTPS
- [ ] SSH restricted to your IP in Security Group
- [ ] Nginx HTTP-to-HTTPS redirect enabled
- [ ] Regular security updates: `sudo apt update && sudo apt upgrade`

---

## 🔗 Important Links

- [Full Deployment Guide](deployment/EC2_DEPLOYMENT_GUIDE.md)
- [Production Readiness Checklist](PRODUCTION_READINESS.md)
- [Environment Template](backend/.env.example)
- [Serverless Schema](backend/serverless.yml)

---

## 🆘 Emergency Commands

### Restart Everything
```bash
sudo systemctl restart train-booking.service
sudo systemctl restart nginx
```

### Check All Services
```bash
bash ~/gemini/deployment/verify_deployment.sh
```

### View All Logs
```bash
# Application
tail -f /var/log/train-booking/error.log &
# Nginx
tail -f /var/log/nginx/train-booking-error.log &
# System
sudo journalctl -u train-booking.service -f
```

---

**Pro Tip**: Bookmark this file on your EC2 instance for quick reference!
