# Train Booking Platform - Backend

This is a consolidated backend application for the Train Booking Platform. All functionality has been consolidated into a single `app.py` file for easy deployment and maintenance.

## Features

- **Train Search**: Search for trains by route
- **User Authentication**: Registration, login, and profile management
- **Booking System**: Complete booking flow with passenger details and payment
- **Booking History**: View past and upcoming bookings
- **Admin Dashboard**: Administrative functions for managing the platform
- **Receipt Generation**: Automatic receipt generation and storage

## Architecture

The entire backend is contained in `app.py` with the following components:

- **DatabaseService**: Handles all data operations (trains, bookings)
- **UserService**: Manages user authentication and profiles
- **S3Service**: Handles receipt storage (mock/local or real S3)
- **LambdaService**: Manages notifications (mock or real AWS Lambda)
- **Flask Routes**: All web routes and API endpoints
- **Authentication Decorators**: Login and admin requirement decorators

## Configuration

The application can run in two modes:
- **Mock Mode** (default): Uses local file system and in-memory storage
- **Real AWS Mode**: Connects to actual AWS services

Toggle between modes using the `USE_MOCK_AWS` constant in `app.py`.

## Running the Application

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Access the application at `http://localhost:5001`

## AWS Deployment

When ready for AWS deployment:
1. Change `USE_MOCK_AWS = False` in `app.py`
2. Ensure AWS credentials are configured
3. Deploy using Serverless Framework:
```bash
serverless deploy --stage prod
```

The application includes a `lambda_handler` function that makes it compatible with AWS Lambda and API Gateway.