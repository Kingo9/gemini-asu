"""
Configuration for Train Booking Platform.
All values are environment-driven to support production deployments.
"""

import os


def _parse_bool(value: str, default: bool = False) -> bool:
	if value is None:
		return default
	return value.strip().lower() in {"1", "true", "yes", "y", "on"}


class Config:
	def __init__(self) -> None:
		app_env = os.getenv("APP_ENV", "development").strip().lower()
		self.APP_ENV = app_env
		self.DEBUG = _parse_bool(os.getenv("FLASK_DEBUG"), default=(app_env != "production"))

		# Toggle mock/real AWS services
		default_mock = app_env != "production"
		self.USE_MOCK_AWS = _parse_bool(os.getenv("USE_MOCK_AWS"), default=default_mock)

		# Flask
		self.SECRET_KEY = os.getenv("SECRET_KEY", "")
		self.SESSION_COOKIE_SECURE = _parse_bool(os.getenv("SESSION_COOKIE_SECURE"), default=(app_env == "production"))
		self.SESSION_COOKIE_HTTPONLY = True
		self.SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")

		# Server
		self.HOST = os.getenv("HOST", "0.0.0.0")
		self.PORT = int(os.getenv("PORT", "5001"))

		# AWS
		self.AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
		self.DYNAMODB_TABLE_TRAINS = os.getenv("DYNAMODB_TABLE_TRAINS", "trains")
		self.DYNAMODB_TABLE_BOOKINGS = os.getenv("DYNAMODB_TABLE_BOOKINGS", "bookings")
		self.DYNAMODB_TABLE_USERS = os.getenv("DYNAMODB_TABLE_USERS", "users")
		self.S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "train-booking-receipts")
		self.LAMBDA_FUNCTION_NAME = os.getenv("LAMBDA_FUNCTION_NAME", "send-booking-notification")

		# Optional admin bootstrap
		self.BOOTSTRAP_ADMIN_EMAIL = os.getenv("BOOTSTRAP_ADMIN_EMAIL", "").strip().lower()

		# Local Mock Configuration
		self.MOCK_UPLOADS_DIR = os.getenv("MOCK_UPLOADS_DIR", "frontend/static/uploads")
		self.MOCK_DB_FILE = os.getenv("MOCK_DB_FILE", "mock_database.json")
