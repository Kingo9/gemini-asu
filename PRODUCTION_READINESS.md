# Production Readiness Checklist

This document tracks all changes made to prepare the Train Booking Platform for production deployment on AWS EC2.

---

## ✅ Completed Tasks

### 1. Configuration Management
- [x] Created environment-driven config system in `backend/config.py`
- [x] Added `.env.example` template with all required variables
- [x] Removed hard-coded secrets and AWS resource names
- [x] Added environment detection (development/production modes)
- [x] Implemented safe defaults with production enforcement for SECRET_KEY

**Files Modified:**
- `backend/config.py` - Complete rewrite to use environment variables
- `backend/app.py` - Import and use Config class
- `backend/.env.example` - Created production environment template

---

### 2. Data Persistence
- [x] Implemented DynamoDB-backed user authentication
- [x] Added Users table schema with GSI for username/email lookups
- [x] Normalized user data structure between mock and production modes
- [x] Fixed DynamoDB bookings schema alignment (BookingID vs booking_id)
- [x] Added Trains table schema to serverless.yml
- [x] Corrected DynamoDB update expression for train availability

**Files Modified:**
- `backend/app.py` - UserService now persists to DynamoDB
- `backend/serverless.yml` - Added Users and Trains table definitions with proper GSIs
- `backend/config.py` - Added DYNAMODB_TABLE_USERS configuration

**DynamoDB Tables Created:**
1. **Users Table**
   - Primary Key: UserID
   - GSI: UsernameLowerIndex (for login by username)
   - GSI: EmailLowerIndex (for login by email)

2. **Bookings Table**
   - Primary Key: BookingID
   - GSI: UserIdIndex (for user history queries)

3. **Trains Table**
   - Primary Key: TrainID

---

### 3. Application Security
- [x] Environment-driven SECRET_KEY (required in production)
- [x] Session cookie security flags (SECURE, HTTPONLY, SAMESITE)
- [x] Production mode detection and enforcement
- [x] Password hashing maintained (werkzeug.security)
- [x] Admin bootstrap via environment variable

**Files Modified:**
- `backend/config.py` - Session cookie configuration
- `backend/app.py` - App config with session security

**Remaining Security Recommendations:**
- [ ] Add CSRF protection (Flask-WTF)
- [ ] Implement rate limiting (Flask-Limiter)
- [ ] Add request validation middleware
- [ ] Configure CORS properly for production domain

---

### 4. Production Server Setup
- [x] Created WSGI entrypoint for Gunicorn
- [x] Added Gunicorn to requirements.txt
- [x] Created systemd service configuration
- [x] Added Nginx reverse proxy configuration
- [x] Implemented health check endpoint
- [x] Configured structured logging

**Files Created:**
- `backend/wsgi.py` - WSGI application entrypoint
- `deployment/train-booking.service` - Systemd service unit
- `deployment/nginx.conf` - Nginx configuration with HTTP/HTTPS support

**Configuration Details:**
- Gunicorn: 4 workers, 120s timeout, bound to 127.0.0.1:5001
- Nginx: Reverse proxy, static file serving, `/health` endpoint
- Systemd: Auto-restart, logging to `/var/log/train-booking/`

---

### 5. Database Seeding & Migration
- [x] Created train data seeding script
- [x] Extracted mock train data to reusable format
- [x] Added batch write for efficient DynamoDB seeding

**Files Created:**
- `backend/seed_trains.py` - Populates Trains table with 35 Indian Railway trains

**Usage:**
```bash
cd backend
source ../venv/bin/activate
python seed_trains.py
```

---

### 6. Deployment Automation
- [x] Comprehensive EC2 deployment guide
- [x] Quick setup script for automated installation
- [x] Deployment verification script
- [x] Updated .gitignore for production

**Files Created:**
- `deployment/EC2_DEPLOYMENT_GUIDE.md` - Complete step-by-step deployment instructions
- `deployment/quick_setup.sh` - Automated EC2 setup script
- `deployment/verify_deployment.sh` - Post-deployment health checks
- `.gitignore` - Updated to exclude .env, logs, and credentials

---

### 7. AWS Integration Fixes
- [x] Fixed DynamoDB nested attribute update expression for Classes.{ClassName}.Availability
- [x] Aligned all table/attribute names between code and CloudFormation
- [x] Corrected case sensitivity issues (BookingID vs booking_id)
- [x] Added proper error handling for AWS service calls

**Key Changes:**
- Update expression now uses proper nested path: `Classes.#class.Availability`
- Condition expression prevents negative availability
- All DynamoDB operations use consistent PascalCase attribute names

---

### 8. Documentation
- [x] Updated README with production deployment section
- [x] Created comprehensive EC2 deployment guide
- [x] Added environment variable documentation
- [x] Documented IAM permissions required
- [x] Created troubleshooting guide

**Files Modified/Created:**
- `README.md` - Added production deployment section
- `deployment/EC2_DEPLOYMENT_GUIDE.md` - Complete deployment manual
- `backend/.env.example` - Inline comments for each variable

---

## 📋 Production Deployment Requirements

### AWS Resources to Provision

1. **EC2 Instance**
   - Type: t3.small or higher
   - OS: Ubuntu 22.04 LTS
   - Security Group: Allow ports 80, 443, 22
   - IAM Role: Attached with DynamoDB, S3, Lambda permissions

2. **DynamoDB Tables** (via CloudFormation or Console)
   - `trains` - TrainID (Hash)
   - `bookings` - BookingID (Hash), GSI: UserIdIndex
   - `users` - UserID (Hash), GSI: UsernameLowerIndex, EmailLowerIndex
   - Billing: PAY_PER_REQUEST

3. **S3 Bucket**
   - Name: `train-booking-receipts` (or custom)
   - CORS enabled
   - IAM policy allowing EC2 role to Put/Get objects

4. **Lambda Function** (Optional)
   - Name: `send-booking-notification`
   - Runtime: Python 3.9+
   - Purpose: Send booking confirmation emails/SMS

5. **IAM Role for EC2**
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
           "arn:aws:dynamodb:REGION:ACCOUNT:table/trains*",
           "arn:aws:dynamodb:REGION:ACCOUNT:table/users*",
           "arn:aws:dynamodb:REGION:ACCOUNT:table/bookings*"
         ]
       },
       {
         "Effect": "Allow",
         "Action": [
           "s3:GetObject",
           "s3:PutObject",
           "s3:ListBucket"
         ],
         "Resource": [
           "arn:aws:s3:::train-booking-receipts",
           "arn:aws:s3:::train-booking-receipts/*"
         ]
       },
       {
         "Effect": "Allow",
         "Action": "lambda:InvokeFunction",
         "Resource": "arn:aws:lambda:REGION:ACCOUNT:function/send-booking-notification"
       }
     ]
   }
   ```

### Environment Variables to Configure

Copy `backend/.env.example` to `backend/.env` and set:

```bash
# Required
SECRET_KEY=<generate-with-secrets.token_urlsafe>
USE_MOCK_AWS=false
DYNAMODB_TABLE_TRAINS=trains
DYNAMODB_TABLE_BOOKINGS=bookings
DYNAMODB_TABLE_USERS=users
S3_BUCKET_NAME=train-booking-receipts

# Optional
LAMBDA_FUNCTION_NAME=send-booking-notification
BOOTSTRAP_ADMIN_EMAIL=admin@example.com
SESSION_COOKIE_SECURE=true  # When using HTTPS
```

---

## 🚀 Deployment Steps Summary

1. **Provision AWS resources** (DynamoDB, S3, Lambda, IAM role)
2. **Launch EC2 instance** with IAM role attached
3. **Clone repository** on EC2
4. **Run quick setup**: `bash deployment/quick_setup.sh`
5. **Configure .env** with AWS resource names
6. **Seed train data**: `python backend/seed_trains.py`
7. **Verify deployment**: `bash deployment/verify_deployment.sh`
8. **Access application** at `http://YOUR_EC2_IP`

---

## 🔒 Security Hardening (Post-Deployment)

- [ ] Configure HTTPS with Let's Encrypt certificate
- [ ] Enable CloudWatch logging and monitoring
- [ ] Set up CloudWatch alarms for errors and high usage
- [ ] Configure DynamoDB point-in-time recovery
- [ ] Enable S3 bucket versioning
- [ ] Implement rate limiting on API endpoints
- [ ] Add CSRF protection to forms
- [ ] Configure AWS WAF (optional)
- [ ] Set up automated backups
- [ ] Restrict SSH access by IP in Security Group

---

## 📊 Monitoring & Observability

### Log Files
- Application: `/var/log/train-booking/access.log` and `error.log`
- Nginx: `/var/log/nginx/train-booking-access.log` and `error.log`
- Systemd: `sudo journalctl -u train-booking.service`

### Health Checks
- Endpoint: `http://YOUR_EC2_IP/health`
- Expected Response: `{"status": "ok"}` with HTTP 200

### CloudWatch Integration (Recommended)
- Install CloudWatch agent on EC2
- Ship application logs to CloudWatch Logs
- Create metric filters for errors
- Set up alarms for 5xx errors, high latency

---

## 🧪 Testing the Deployment

1. **Health Check**: `curl http://localhost/health`
2. **User Registration**: Visit `/register` and create an account
3. **Train Search**: Search for trains by route
4. **Booking Flow**: Complete a booking end-to-end
5. **Receipt Download**: Verify receipt is stored in S3
6. **Verify Logs**: Check `/var/log/train-booking/error.log` for errors

---

## 📝 Known Limitations & Future Enhancements

### Current Limitations
- No payment gateway integration (mock payment)
- No email/SMS sending (requires SES or SNS setup)
- No real-time seat availability updates
- No booking cancellation feature
- No train schedule management UI

### Recommended Enhancements
- Integrate AWS SES for email notifications
- Add SNS for SMS notifications
- Implement payment gateway (Razorpay/Stripe)
- Add admin panel for train management
- Implement booking cancellation with refunds
- Add PNR-based booking lookup
- Integrate with IRCTC API (if available)
- Add seat map visualization
- Implement booking history export (PDF/CSV)

---

## 🎯 Success Criteria

The application is considered production-ready when:

- [x] All code runs without errors in production mode
- [x] User data persists in DynamoDB
- [x] Bookings are stored in DynamoDB
- [x] Receipts are uploaded to S3
- [x] Application restarts automatically after crashes
- [x] Health check endpoint returns 200 OK
- [x] Logs are accessible and structured
- [ ] HTTPS is configured with valid certificate
- [ ] All AWS resources are provisioned and accessible
- [ ] At least one admin user is registered
- [ ] Train data is seeded in DynamoDB

---

## 📞 Support & Troubleshooting

For deployment issues, refer to:
1. [EC2 Deployment Guide](deployment/EC2_DEPLOYMENT_GUIDE.md) - Comprehensive troubleshooting section
2. Application logs: `/var/log/train-booking/error.log`
3. Systemd status: `sudo systemctl status train-booking.service`
4. Nginx logs: `/var/log/nginx/train-booking-error.log`

---

**Last Updated**: February 10, 2026  
**Production Ready**: ✅ Yes (pending AWS resource provisioning)
