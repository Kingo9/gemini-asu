# Simplified AWS Deployment for Lab Environment

This guide explains how to prepare your application for AWS deployment while working in a lab environment with limited access.

## Understanding the Application Structure

Your application is designed to work in two modes:
1. **Mock Mode (USE_MOCK_AWS = True)** - Uses local file system instead of AWS services
2. **Real AWS Mode (USE_MOCK_AWS = False)** - Connects to actual AWS services

Currently, the application is configured for Mock Mode which is perfect for your lab environment.

## Key Files for Lab Testing

### 1. app.py
- Contains the main Flask application
- Includes a `lambda_handler` function that makes it compatible with AWS Lambda
- Works locally with `flask run` and in AWS Lambda with the same code

### 2. database.py
- Handles all database operations
- Automatically switches between mock storage and real DynamoDB based on `USE_MOCK_AWS`
- All train data is stored in-memory when in mock mode

### 3. s3_service.py
- Handles file uploads/downloads
- Uses local file system when in mock mode
- Connects to real S3 when in AWS mode

## Running in Your Lab Environment

### To run locally in your lab:
```bash
cd backend
pip install -r requirements.txt
python app.py
```

The application will start in Mock Mode, showing:
```
Train Booking Platform - Running in MOCK MODE
AWS services are simulated using local Python operations
```

## Preparing for Actual AWS Deployment

When you have access to deploy to real AWS:

### 1. Update config.py
Change `USE_MOCK_AWS = False` to use real AWS services

### 2. Deploy using Serverless Framework
```bash
# Install serverless
npm install -g serverless

# Install Python requirements plugin
serverless plugin install --name serverless-python-requirements

# Deploy to AWS
serverless deploy --stage prod
```

## Lambda Handler Explained

The `lambda_handler` function in `app.py` is designed to:
- Receive API Gateway events from AWS
- Convert them to Flask-compatible requests
- Process them through your existing Flask app
- Format responses back for API Gateway

This means your Flask code works the same way in both environments!

## Lab Testing Checklist

- [ ] Application runs with `python app.py`
- [ ] Visit `http://localhost:5001` to test the interface
- [ ] Check that train search works
- [ ] Verify booking functionality
- [ ] Confirm you see the "MOCK MODE" message

## Files You Need to Know

- `app.py` - Main application with Lambda compatibility
- `config.py` - Controls mock vs real AWS mode
- `routes.py` - All your route handlers
- `database.py` - Data handling with mock/real AWS toggle
- `s3_service.py` - File handling with mock/real AWS toggle
- `serverless.yml` - AWS deployment configuration

## Important Notes for Lab

1. **No AWS credentials needed in mock mode** - All data is stored locally
2. **Same code works in both environments** - Just change the config flag
3. **Easy debugging** - Standard Python debugging works in mock mode
4. **Self-contained** - No external dependencies required in mock mode

## When You Have Full AWS Access

To switch to real AWS services:
1. Update `USE_MOCK_AWS = False` in config.py
2. Set up AWS credentials
3. Create necessary AWS resources (DynamoDB tables, S3 buckets)
4. Deploy using serverless framework

The application architecture is already in place - you just need to flip the switch!