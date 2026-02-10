# File Structure - Production Ready

Complete file structure with production deployment files.

```
gemini/
├── README.md                              # Updated with deployment section
├── PRODUCTION_READINESS.md                # Complete readiness checklist [NEW]
├── QUICK_REFERENCE.md                     # Command quick reference [NEW]
├── .gitignore                             # Updated for production
│
├── backend/
│   ├── __init__.py
│   ├── app.py                             # Refactored with env config
│   ├── config.py                          # Environment-driven config [REFACTORED]
│   ├── wsgi.py                            # WSGI entrypoint for Gunicorn [NEW]
│   ├── seed_trains.py                     # DynamoDB seeding script [NEW]
│   ├── requirements.txt                   # Added gunicorn
│   ├── .env.example                       # Production env template [NEW]
│   ├── serverless.yml                     # Updated with all 3 tables
│   ├── README.md
│   └── SIMPLIFIED_DEPLOYMENT.md
│
├── deployment/                            # [NEW] Deployment automation
│   ├── EC2_DEPLOYMENT_GUIDE.md           # [NEW] Complete deployment manual
│   ├── train-booking.service             # [NEW] Systemd service file
│   ├── nginx.conf                        # [NEW] Nginx reverse proxy config
│   ├── quick_setup.sh                    # [NEW] Automated EC2 setup
│   └── verify_deployment.sh              # [NEW] Health check script
│
└── frontend/
    ├── static/
    │   ├── css/
    │   │   ├── modern.css
    │   │   └── style.css
    │   └── uploads/                       # Receipt storage (local mock)
    │       └── *.txt
    └── templates/
        ├── admin.html
        ├── booking.html
        ├── dashboard.html
        ├── history.html
        ├── index.html
        ├── login.html
        ├── navbar.html
        ├── payment.html
        ├── profile.html
        ├── register.html
        ├── results.html
        └── success.html
```

## New Files Created (11 files)

1. **backend/wsgi.py** - WSGI entrypoint for production servers
2. **backend/seed_trains.py** - Populate DynamoDB with train data
3. **backend/.env.example** - Environment variable template
4. **deployment/EC2_DEPLOYMENT_GUIDE.md** - Step-by-step deployment instructions
5. **deployment/train-booking.service** - Systemd service configuration
6. **deployment/nginx.conf** - Nginx reverse proxy setup
7. **deployment/quick_setup.sh** - Automated deployment script
8. **deployment/verify_deployment.sh** - Post-deployment health checks
9. **PRODUCTION_READINESS.md** - Complete readiness documentation
10. **QUICK_REFERENCE.md** - Command reference guide
11. **File_Structure.md** - This file

## Modified Files (6 files)

1. **backend/config.py** - Complete refactor to environment-driven config
2. **backend/app.py** - 
   - Import Config class
   - DynamoDB user persistence
   - Fixed availability update expression
   - Added health endpoint
   - Session security configuration
3. **backend/serverless.yml** - 
   - Added Users table with GSIs
   - Added Trains table
   - Fixed schema attribute naming (PascalCase)
4. **backend/requirements.txt** - Added gunicorn
5. **README.md** - Added production deployment section
6. **.gitignore** - Enhanced for production

## Executable Scripts (3 files)

All scripts have execute permissions set:
- `deployment/quick_setup.sh`
- `deployment/verify_deployment.sh`
- `backend/seed_trains.py`

## Key Changes Summary

### Configuration
- Environment-driven (12 env vars)
- Production mode detection
- Safe secret key handling

### Data Persistence
- DynamoDB Users table
- DynamoDB-backed authentication
- Fixed schema alignment

### Production Server
- Gunicorn WSGI server
- Systemd service (auto-restart)
- Nginx reverse proxy
- Health check endpoint

### Deployment
- Automated setup script
- Comprehensive documentation
- Seeding utilities

## Deployment Workflow

1. **Provision AWS Resources** → DynamoDB, S3, Lambda, IAM
2. **Launch EC2** → With IAM role attached
3. **Clone Repo** → `git clone ...`
4. **Run Setup** → `bash deployment/quick_setup.sh`
5. **Configure** → Edit `backend/.env`
6. **Seed Data** → `python backend/seed_trains.py`
7. **Verify** → `bash deployment/verify_deployment.sh`
8. **Access** → `http://YOUR_EC2_IP`

## Documentation Hierarchy

```
Quick Start:     QUICK_REFERENCE.md (commands & troubleshooting)
                           ↓
Full Guide:      deployment/EC2_DEPLOYMENT_GUIDE.md (step-by-step)
                           ↓
Checklist:       PRODUCTION_READINESS.md (all tasks & requirements)
```

## AWS Resources Required

1. **EC2 Instance** with IAM role
2. **DynamoDB Tables**: trains, bookings, users (with GSIs)
3. **S3 Bucket**: train-booking-receipts
4. **Lambda Function**: send-booking-notification (optional)
5. **IAM Policies**: DynamoDB, S3, Lambda permissions

## Environment Variables

12 required/optional variables in `backend/.env`:

**Required:**
- SECRET_KEY
- USE_MOCK_AWS=false
- DYNAMODB_TABLE_TRAINS
- DYNAMODB_TABLE_BOOKINGS
- DYNAMODB_TABLE_USERS
- S3_BUCKET_NAME

**Optional:**
- AWS_REGION
- LAMBDA_FUNCTION_NAME
- BOOTSTRAP_ADMIN_EMAIL
- SESSION_COOKIE_SECURE
- More...

## Next Steps After Deployment

1. Configure HTTPS (certbot)
2. Set SESSION_COOKIE_SECURE=true
3. Create admin user
4. Set up CloudWatch logging
5. Configure backups
6. Test booking flow end-to-end
