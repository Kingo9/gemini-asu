# Indian Railways Booking Platform

A full-stack Flask-based train booking platform for Indian Railways, designed for production deployment on AWS EC2 with DynamoDB, S3, and Lambda/SNS integration.

## 🎯 Project Overview

This platform allows users to:
- Search for trains by route or city
- View train availability and details
- Book train tickets with passenger information
- Receive booking confirmations and downloadable receipts
- Get notifications for booking confirmations

## 🏗️ Architecture

**Production Mode (AWS)**
- **DynamoDB**: User authentication, train data, and booking persistence
- **S3**: Receipt storage with presigned URLs
- **Lambda/SNS**: Booking notifications
- **EC2 + Nginx + Gunicorn**: Application hosting

**Development Mode (Mock)**
- **Mock DynamoDB**: In-memory Python lists/dictionaries
- **Mock S3**: Local file system (`frontend/static/uploads/`)
- **Mock Lambda/SNS**: Console print statements

Toggle between modes using `USE_MOCK_AWS` environment variable.

## 📁 Project Structure

```
train-booking-capstone/
├── backend/
│   ├── __init__.py          # Package initialization
│   ├── app.py               # Main Flask application
│   ├── config.py            # Configuration (USE_MOCK_AWS toggle)
│   ├── routes.py            # API endpoints (Search, Booking)
│   ├── database.py          # Database logic (Mock vs Real DynamoDB)
│   ├── s3_service.py        # Storage logic (Local File vs S3)
│   ├── lambda_service.py    # Notification logic (Print vs Lambda/SNS)
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css    # Main stylesheet
│   │   └── uploads/          # Mock S3: Receipt storage
│   └── templates/
│       ├── index.html        # Home page (search)
│       ├── results.html      # Search results
│       ├── booking.html      # Booking form
│       └── success.html      # Booking confirmation
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd train-booking-capstone
   ```

2. **Install dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Verify the project structure:**
   Ensure the `frontend/static/uploads/` directory exists (it will be created automatically on first run).

### Running the Application

**Option 1: Using Python module (Recommended)**
```bash
python -m backend.app
```

**Option 2: Using Flask CLI**
```bash
# Set Flask app environment variable
export FLASK_APP=backend.app  # On Windows: set FLASK_APP=backend.app

# Run Flask
flask run
```

**Option 3: Direct Python execution**
```bash
python backend/app.py
```

The application will start on `http://localhost:5000` (or `http://127.0.0.1:5000`).

### Accessing the Application

Open your web browser and navigate to:
```
http://localhost:5000
```

## 📊 Mock Data

The application comes pre-loaded with Indian Railways train data including popular routes:

| Train Number | Train Name | Route | Time | Availability |
|--------------|------------|-------|------|---------------|
| 12951 | Mumbai Rajdhani Express | Mumbai Central - New Delhi | 06:15 AM | 45 seats |
| 12627 | Bangalore Mail | Bangalore - Chennai Central | 07:30 AM | 38 seats |
| 12301 | Rajdhani Express | Howrah - New Delhi | 08:00 AM | 52 seats |
| 12259 | Shatabdi Express | Mumbai - Ahmedabad | 09:15 AM | 28 seats |
| 12649 | Sampark Kranti Express | Hyderabad - Bangalore | 10:30 AM | 35 seats |
| 12859 | Deccan Express | Pune - Mumbai | 11:00 AM | 42 seats |
| 12431 | Shatabdi Express | Jaipur - Delhi | 12:45 PM | 30 seats |
| 12655 | Kovai Express | Chennai - Coimbatore | 02:20 PM | 25 seats |
| 12953 | Gujarat Mail | Mumbai - Surat | 03:30 PM | 40 seats |
| 12621 | Brindavan Express | Chennai - Bangalore | 04:15 PM | 33 seats |
| 12309 | Rajdhani Express | Kolkata - Patna | 05:00 PM | 48 seats |
| 12701 | Godavari Express | Secunderabad - Visakhapatnam | 06:30 PM | 22 seats |

**Note:** Bookings start as an empty list and are stored in memory during the session.

## 🔄 Workflow

1. **Search**: User enters a route (e.g., "New York") → System filters trains
2. **Select**: User clicks "Book Now" on a train → Redirects to booking page
3. **Book**: User enters passenger name and seat count → System validates availability
4. **Confirm**: 
   - Availability is decremented
   - Booking record is created
   - Receipt is saved to `frontend/static/uploads/` (mock S3)
   - Notification is printed to console (mock SNS)
5. **Success**: User sees confirmation page with booking details and receipt download link

## 🔧 Configuration

### Switching to Real AWS Services

To enable real AWS services:

1. **Edit `backend/config.py`:**
   ```python
   USE_MOCK_AWS = False  # Change from True to False
   ```

2. **Configure AWS credentials:**
   - Set up AWS credentials via `~/.aws/credentials` or environment variables
   - Ensure you have appropriate IAM permissions for DynamoDB, S3, and Lambda/SNS

3. **Uncomment AWS code:**
   - In `backend/database.py`: Uncomment DynamoDB code blocks
   - In `backend/s3_service.py`: Uncomment S3 code blocks
   - In `backend/lambda_service.py`: Uncomment Lambda/SNS code blocks

4. **Update AWS resource names:**
   - Edit `DYNAMODB_TABLE_TRAINS`, `DYNAMODB_TABLE_BOOKINGS` in `config.py`
   - Edit `S3_BUCKET_NAME` in `config.py`
   - Edit `LAMBDA_FUNCTION_NAME` or SNS topic ARN in `config.py`

## 📝 Code Comments

All files contain extensive comments explaining:
- How mock implementations work
- Where real AWS code is located (marked with `# TODO:`)
- How to enable real AWS services
- Function parameters and return values

## 🧪 Testing the Application

### Test Scenarios

1. **Search All Trains:**
   - Go to home page
   - Click "Search Trains" without entering a route
   - Should see both T100 and T101

2. **Search by Route:**
   - Enter "New York" in search
   - Should see only T100

3. **Book a Train:**
   - Select a train
   - Enter passenger name and seats
   - Complete booking
   - Check console for mock notification
   - Download receipt from success page

4. **Test Availability:**
   - Book more seats than available
   - Should see error message

## 📦 Dependencies

- **Flask 3.0.0**: Web framework
- **boto3 1.34.0**: AWS SDK (included but unused in mock mode)
- **Werkzeug 3.0.1**: WSGI utilities (Flask dependency)

## 🎨 Frontend Features

- Responsive design (mobile-friendly)
- Modern UI with gradient styling
- Flash messages for user feedback
- Clean, intuitive navigation
- Downloadable receipts

## 🔍 API Endpoints

- `GET /` - Home page
- `POST /search` - Search trains
- `GET /booking/<train_id>` - Booking form
- `POST /booking/<train_id>` - Process booking
- `GET /booking/success/<booking_id>` - Success page
- `GET /api/trains?route=<query>` - JSON API for trains
- `GET /api/train/<train_id>` - JSON API for specific train

## 🐛 Troubleshooting

### Issue: ModuleNotFoundError
**Solution:** Ensure you're running from the project root directory, not from inside the `backend` folder.

### Issue: Template not found
**Solution:** Verify the `frontend/templates/` directory exists and contains all HTML files.

### Issue: Receipts not saving
**Solution:** Check that `frontend/static/uploads/` directory exists and has write permissions.

### Issue: Port already in use
**Solution:** Change the port in `backend/app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Use different port
```

## 📚 Production Deployment on AWS EC2

This application is production-ready for deployment on AWS EC2.

### Quick Start

1. **Provision AWS Resources:**
   - Create DynamoDB tables (Users, Trains, Bookings) - see [serverless.yml](backend/serverless.yml) for schema
   - Create S3 bucket for receipts
   - Create Lambda function or SNS topic for notifications (optional)
   - Attach IAM role to EC2 with DynamoDB, S3, and Lambda permissions

2. **Deploy to EC2:**
   - Clone this repository on your EC2 instance
   - Follow the comprehensive guide: [EC2 Deployment Guide](deployment/EC2_DEPLOYMENT_GUIDE.md)
   - Or use quick setup script: `bash deployment/quick_setup.sh`

3. **Seed Initial Data:**
   ```bash
   cd backend
   source ../venv/bin/activate
   python seed_trains.py
   ```

4. **Verify Deployment:**
   ```bash
   bash deployment/verify_deployment.sh
   ```

### Key Files for Production

- [backend/.env.example](backend/.env.example) - Environment variable template
- [deployment/EC2_DEPLOYMENT_GUIDE.md](deployment/EC2_DEPLOYMENT_GUIDE.md) - Complete deployment instructions
- [deployment/train-booking.service](deployment/train-booking.service) - Systemd service configuration
- [deployment/nginx.conf](deployment/nginx.conf) - Nginx reverse proxy configuration
- [backend/seed_trains.py](backend/seed_trains.py) - DynamoDB data seeding script

## 📄 License

This project is created for educational/capstone purposes.

## 👤 Author

Senior Full-Stack Cloud Engineer & AWS Solutions Architect

---

**Note:** This application runs entirely offline in mock mode. No AWS credentials are required to run or test the application. The platform uses Indian Railways train data for realistic booking scenarios.
#   g e m i n i - a s u  
 