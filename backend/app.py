from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional
import boto3
from boto3.dynamodb.conditions import Key
from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Response
import logging
from dotenv import load_dotenv

try:
    from .config import Config
except ImportError:
    from config import Config

# Load environment variables from .env if present
load_dotenv()

# Get the base directory (project root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configuration
_config = Config()
USE_MOCK_AWS = _config.USE_MOCK_AWS
MOCK_UPLOADS_DIR = _config.MOCK_UPLOADS_DIR
AWS_REGION = _config.AWS_REGION
DYNAMODB_TABLE_TRAINS = _config.DYNAMODB_TABLE_TRAINS
DYNAMODB_TABLE_BOOKINGS = _config.DYNAMODB_TABLE_BOOKINGS
DYNAMODB_TABLE_USERS = _config.DYNAMODB_TABLE_USERS
S3_BUCKET_NAME = _config.S3_BUCKET_NAME
LAMBDA_FUNCTION_NAME = _config.LAMBDA_FUNCTION_NAME
BOOTSTRAP_ADMIN_EMAIL = _config.BOOTSTRAP_ADMIN_EMAIL

# Mock Database: In-memory storage simulating DynamoDB
# Indian Railways Train Data with Classes and Fares
mock_trains = [
    {
        "TrainID": "12951",
        "Route": "Mumbai Central - New Delhi",
        "Time": "06:15 AM",
        "TrainName": "Mumbai Rajdhani Express",
        "Classes": {
            "AC1": {"Availability": 12, "Fare": 4500},
            "AC2": {"Availability": 28, "Fare": 2800},
            "AC3": {"Availability": 45, "Fare": 1800}
        }
    },
    {
        "TrainID": "12627",
        "Route": "Bangalore - Chennai Central",
        "Time": "07:30 AM",
        "TrainName": "Bangalore Mail",
        "Classes": {
            "AC2": {"Availability": 18, "Fare": 1200},
            "AC3": {"Availability": 35, "Fare": 850},
            "SL": {"Availability": 42, "Fare": 450},
            "GN": {"Availability": 60, "Fare": 180}
        }
    },
    {
        "TrainID": "12301",
        "Route": "Howrah - New Delhi",
        "Time": "08:00 AM",
        "TrainName": "Rajdhani Express",
        "Classes": {
            "AC1": {"Availability": 15, "Fare": 4200},
            "AC2": {"Availability": 32, "Fare": 2600},
            "AC3": {"Availability": 52, "Fare": 1700}
        }
    },
    {
        "TrainID": "12259",
        "Route": "Mumbai - Ahmedabad",
        "Time": "09:15 AM",
        "TrainName": "Shatabdi Express",
        "Classes": {
            "AC Chair Car": {"Availability": 28, "Fare": 950},
            "Executive": {"Availability": 12, "Fare": 1850}
        }
    },
    {
        "TrainID": "12649",
        "Route": "Hyderabad - Bangalore",
        "Time": "10:30 AM",
        "TrainName": "Sampark Kranti Express",
        "Classes": {
            "AC2": {"Availability": 22, "Fare": 1100},
            "AC3": {"Availability": 38, "Fare": 750},
            "SL": {"Availability": 45, "Fare": 400}
        }
    },
    {
        "TrainID": "12859",
        "Route": "Pune - Mumbai",
        "Time": "11:00 AM",
        "TrainName": "Deccan Express",
        "Classes": {
            "AC2": {"Availability": 15, "Fare": 650},
            "AC3": {"Availability": 30, "Fare": 450},
            "SL": {"Availability": 42, "Fare": 250},
            "GN": {"Availability": 80, "Fare": 120}
        }
    },
    {
        "TrainID": "12431",
        "Route": "Jaipur - Delhi",
        "Time": "12:45 PM",
        "TrainName": "Shatabdi Express",
        "Classes": {
            "AC Chair Car": {"Availability": 25, "Fare": 750},
            "Executive": {"Availability": 10, "Fare": 1500}
        }
    },
    {
        "TrainID": "12655",
        "Route": "Chennai - Coimbatore",
        "Time": "02:20 PM",
        "TrainName": "Kovai Express",
        "Classes": {
            "AC2": {"Availability": 12, "Fare": 850},
            "AC3": {"Availability": 18, "Fare": 550},
            "SL": {"Availability": 24, "Fare": 300},
            "GN": {"Availability": 30, "Fare": 150}
        }
    },
    {
        "TrainID": "12953",
        "Route": "Mumbai - Surat",
        "Time": "03:30 PM",
        "TrainName": "Gujarat Mail",
        "Classes": {
            "AC2": {"Availability": 20, "Fare": 700},
            "AC3": {"Availability": 35, "Fare": 500},
            "SL": {"Availability": 45, "Fare": 280},
            "GN": {"Availability": 75, "Fare": 130}
        }
    },
    {
        "TrainID": "12621",
        "Route": "Chennai - Bangalore",
        "Time": "04:15 PM",
        "TrainName": "Brindavan Express",
        "Classes": {
            "AC2": {"Availability": 16, "Fare": 900},
            "AC3": {"Availability": 33, "Fare": 600},
            "SL": {"Availability": 38, "Fare": 350}
        }
    },
    {
        "TrainID": "12309",
        "Route": "Kolkata - Patna",
        "Time": "05:00 PM",
        "TrainName": "Rajdhani Express",
        "Classes": {
            "AC1": {"Availability": 10, "Fare": 3800},
            "AC2": {"Availability": 28, "Fare": 2400},
            "AC3": {"Availability": 48, "Fare": 1600}
        }
    },
    {
        "TrainID": "12701",
        "Route": "Secunderabad - Visakhapatnam",
        "Time": "06:30 PM",
        "TrainName": "Godavari Express",
        "Classes": {
            "AC2": {"Availability": 20, "Fare": 1000},
            "AC3": {"Availability": 35, "Fare": 700},
            "SL": {"Availability": 42, "Fare": 380},
            "GN": {"Availability": 65, "Fare": 160}
        }
    },
    {
        "TrainID": "12841",
        "Route": "Mumbai - Goa",
        "Time": "07:00 AM",
        "TrainName": "Konkan Kanya Express",
        "Classes": {
            "AC2": {"Availability": 22, "Fare": 1200},
            "AC3": {"Availability": 40, "Fare": 850},
            "SL": {"Availability": 48, "Fare": 450}
        }
    },
    {
        "TrainID": "12260",
        "Route": "Ahmedabad - Mumbai",
        "Time": "08:30 AM",
        "TrainName": "Shatabdi Express",
        "Classes": {
            "AC Chair Car": {"Availability": 30, "Fare": 900},
            "Executive": {"Availability": 14, "Fare": 1750}
        }
    },
    {
        "TrainID": "12636",
        "Route": "Chennai - Mysore",
        "Time": "09:45 AM",
        "TrainName": "Shatabdi Express",
        "Classes": {
            "AC Chair Car": {"Availability": 28, "Fare": 750},
            "Executive": {"Availability": 12, "Fare": 1400}
        }
    },
    {
        "TrainID": "12957",
        "Route": "Mumbai - Jaipur",
        "Time": "10:15 AM",
        "TrainName": "Swaraj Express",
        "Classes": {
            "AC2": {"Availability": 24, "Fare": 1800},
            "AC3": {"Availability": 42, "Fare": 1200},
            "SL": {"Availability": 50, "Fare": 600}
        }
    },
    {
        "TrainID": "12654",
        "Route": "Bangalore - Hyderabad",
        "Time": "11:30 AM",
        "TrainName": "Sampark Kranti Express",
        "Classes": {
            "AC2": {"Availability": 20, "Fare": 1100},
            "AC3": {"Availability": 36, "Fare": 750},
            "SL": {"Availability": 44, "Fare": 400}
        }
    },
    {
        "TrainID": "12302",
        "Route": "New Delhi - Howrah",
        "Time": "12:00 PM",
        "TrainName": "Rajdhani Express",
        "Classes": {
            "AC1": {"Availability": 14, "Fare": 4200},
            "AC2": {"Availability": 30, "Fare": 2600},
            "AC3": {"Availability": 50, "Fare": 1700}
        }
    },
    {
        "TrainID": "12626",
        "Route": "Chennai - New Delhi",
        "Time": "01:15 PM",
        "TrainName": "Tamil Nadu Express",
        "Classes": {
            "AC1": {"Availability": 12, "Fare": 4800},
            "AC2": {"Availability": 26, "Fare": 3000},
            "AC3": {"Availability": 45, "Fare": 2000},
            "SL": {"Availability": 52, "Fare": 900}
        }
    },
    {
        "TrainID": "12834",
        "Route": "Howrah - Mumbai",
        "Time": "02:00 PM",
        "TrainName": "Gitanjali Express",
        "Classes": {
            "AC2": {"Availability": 28, "Fare": 2200},
            "AC3": {"Availability": 48, "Fare": 1500},
            "SL": {"Availability": 55, "Fare": 750}
        }
    },
    {
        "TrainID": "12213",
        "Route": "Mumbai - Delhi",
        "Time": "03:45 PM",
        "TrainName": "Duronto Express",
        "Classes": {
            "AC2": {"Availability": 32, "Fare": 2900},
            "AC3": {"Availability": 55, "Fare": 1900},
            "SL": {"Availability": 60, "Fare": 950}
        }
    },
    {
        "TrainID": "12639",
        "Route": "Bangalore - Coimbatore",
        "Time": "04:30 PM",
        "TrainName": "Intercity Express",
        "Classes": {
            "AC Chair Car": {"Availability": 35, "Fare": 650},
            "SL": {"Availability": 45, "Fare": 320}
        }
    },
    {
        "TrainID": "12952",
        "Route": "New Delhi - Mumbai Central",
        "Time": "05:15 PM",
        "TrainName": "Mumbai Rajdhani Express",
        "Classes": {
            "AC1": {"Availability": 13, "Fare": 4500},
            "AC2": {"Availability": 29, "Fare": 2800},
            "AC3": {"Availability": 46, "Fare": 1800}
        }
    },
    {
        "TrainID": "12628",
        "Route": "Chennai Central - Bangalore",
        "Time": "06:00 PM",
        "TrainName": "Bangalore Mail",
        "Classes": {
            "AC2": {"Availability": 19, "Fare": 1200},
            "AC3": {"Availability": 36, "Fare": 850},
            "SL": {"Availability": 43, "Fare": 450},
            "GN": {"Availability": 62, "Fare": 180}
        }
    },
    {
        "TrainID": "12728",
        "Route": "Hyderabad - Chennai",
        "Time": "07:20 PM",
        "TrainName": "Charminar Express",
        "Classes": {
            "AC2": {"Availability": 21, "Fare": 950},
            "AC3": {"Availability": 38, "Fare": 650},
            "SL": {"Availability": 46, "Fare": 350},
            "GN": {"Availability": 68, "Fare": 140}
        }
    },
    {
        "TrainID": "12324",
        "Route": "New Delhi - Howrah",
        "Time": "08:00 PM",
        "TrainName": "Poorva Express",
        "Classes": {
            "AC2": {"Availability": 25, "Fare": 2500},
            "AC3": {"Availability": 44, "Fare": 1650},
            "SL": {"Availability": 52, "Fare": 800}
        }
    },
    {
        "TrainID": "12658",
        "Route": "Mumbai - Chennai",
        "Time": "09:30 PM",
        "TrainName": "Mumbai Mail",
        "Classes": {
            "AC2": {"Availability": 27, "Fare": 2100},
            "AC3": {"Availability": 48, "Fare": 1400},
            "SL": {"Availability": 56, "Fare": 700}
        }
    },
    {
        "TrainID": "12284",
        "Route": "New Delhi - Lucknow",
        "Time": "10:15 PM",
        "TrainName": "Shatabdi Express",
        "Classes": {
            "AC Chair Car": {"Availability": 0, "Fare": 850},
            "Executive": {"Availability": 0, "Fare": 1600}
        }
    },
    {
        "TrainID": "12616",
        "Route": "Mumbai - Bangalore",
        "Time": "11:00 PM",
        "TrainName": "Mumbai Express",
        "Classes": {
            "AC2": {"Availability": 23, "Fare": 1800},
            "AC3": {"Availability": 42, "Fare": 1200},
            "SL": {"Availability": 50, "Fare": 600}
        }
    },
    {
        "TrainID": "12509",
        "Route": "Gorakhpur - New Delhi",
        "Time": "11:45 PM",
        "TrainName": "Gorakhpur Express",
        "Classes": {
            "AC2": {"Availability": 20, "Fare": 1500},
            "AC3": {"Availability": 38, "Fare": 1000},
            "SL": {"Availability": 45, "Fare": 500},
            "GN": {"Availability": 72, "Fare": 200}
        }
    },
    {
        "TrainID": "12870",
        "Route": "Bhubaneswar - New Delhi",
        "Time": "12:30 AM",
        "TrainName": "Bhubaneswar Rajdhani",
        "Classes": {
            "AC1": {"Availability": 11, "Fare": 4000},
            "AC2": {"Availability": 26, "Fare": 2500},
            "AC3": {"Availability": 44, "Fare": 1650}
        }
    },
    {
        "TrainID": "12618",
        "Route": "Mumbai - Coimbatore",
        "Time": "01:00 AM",
        "TrainName": "Mumbai Express",
        "Classes": {
            "AC2": {"Availability": 24, "Fare": 1900},
            "AC3": {"Availability": 43, "Fare": 1300},
            "SL": {"Availability": 51, "Fare": 650}
        }
    },
    {
        "TrainID": "12260",
        "Route": "Mumbai - Ahmedabad",
        "Time": "02:15 AM",
        "TrainName": "Gujarat Sampark Kranti",
        "Classes": {
            "AC2": {"Availability": 22, "Fare": 1100},
            "AC3": {"Availability": 40, "Fare": 750},
            "SL": {"Availability": 48, "Fare": 400}
        }
    },
    {
        "TrainID": "12722",
        "Route": "Hyderabad - Tirupati",
        "Time": "03:00 AM",
        "TrainName": "Tirupati Express",
        "Classes": {
            "AC2": {"Availability": 10, "Fare": 800},
            "AC3": {"Availability": 15, "Fare": 550},
            "SL": {"Availability": 20, "Fare": 300},
            "GN": {"Availability": 25, "Fare": 150}
        }
    },
    {
        "TrainID": "12659",
        "Route": "Mumbai - Pune",
        "Time": "04:30 AM",
        "TrainName": "Deccan Express",
        "Classes": {
            "AC2": {"Availability": 16, "Fare": 650},
            "AC3": {"Availability": 31, "Fare": 450},
            "SL": {"Availability": 41, "Fare": 250},
            "GN": {"Availability": 78, "Fare": 120}
        }
    }
]

mock_users = []
mock_bookings = []

# Counter for generating unique booking IDs and PNR
booking_id_counter = 10000
pnr_counter = 8000000000  # PNR numbers are 10 digits


class DatabaseService:
    """Service class for database operations"""
    
    def __init__(self):
        self.use_mock = USE_MOCK_AWS
        
        if not self.use_mock:
            # Initialize DynamoDB client when USE_MOCK_AWS = False
            self.dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
            self.trains_table = self.dynamodb.Table(DYNAMODB_TABLE_TRAINS)
            self.bookings_table = self.dynamodb.Table(DYNAMODB_TABLE_BOOKINGS)
    
    def search_trains(self, route_query: str = None) -> List[Dict]:
        """
        Search for trains by route
        Args:
            route_query: Optional search term to filter routes
        Returns:
            List of train dictionaries matching the search
        """
        if self.use_mock:
            # Mock implementation: Filter trains from in-memory list
            if route_query:
                route_query_lower = route_query.lower()
                results = [
                    train for train in mock_trains
                    if route_query_lower in train["Route"].lower()
                ]
                return results
            return mock_trains.copy()
        
        else:
            # Real DynamoDB implementation
            try:
                if route_query:
                    response = self.trains_table.scan(
                        FilterExpression=Key('Route').contains(route_query)
                    )
                else:
                    response = self.trains_table.scan()
                
                return response.get('Items', [])
            except Exception as e:
                print(f"Error searching trains in DynamoDB: {str(e)}")
                return []
    
    def get_train_by_id(self, train_id: str) -> Optional[Dict]:
        """
        Get a specific train by TrainID
        Args:
            train_id: The TrainID to search for
        Returns:
            Train dictionary or None if not found
        """
        if self.use_mock:
            # Mock implementation: Search in-memory list
            for train in mock_trains:
                if train["TrainID"] == train_id:
                    return train.copy()
            return None
        
        else:
            # Real DynamoDB implementation
            try:
                response = self.trains_table.get_item(
                    Key={'TrainID': train_id}
                )
                return response.get('Item')
            except Exception as e:
                print(f"Error getting train from DynamoDB: {str(e)}")
                return None
    
    def update_train_availability(self, train_id: str, class_name: str, seats_to_reserve: int) -> bool:
        """
        Decrement train availability when booking seats for a specific class
        Args:
            train_id: The TrainID to update
            class_name: The class name (AC1, AC2, AC3, SL, GN, etc.)
            seats_to_reserve: Number of seats to reserve
        Returns:
            True if successful, False if insufficient availability
        """
        if self.use_mock:
            # Mock implementation: Update in-memory list
            for train in mock_trains:
                if train["TrainID"] == train_id:
                    if "Classes" in train and class_name in train["Classes"]:
                        if train["Classes"][class_name]["Availability"] >= seats_to_reserve:
                            train["Classes"][class_name]["Availability"] -= seats_to_reserve
                            return True
                    return False
            return False
        
        else:
            # Real DynamoDB implementation
            try:
                self.trains_table.update_item(
                    Key={'TrainID': train_id},
                    UpdateExpression='SET #classes.#class.#availability = #classes.#class.#availability - :seats',
                    ExpressionAttributeNames={
                        '#classes': 'Classes',
                        '#class': class_name,
                        '#availability': 'Availability'
                    },
                    ExpressionAttributeValues={':seats': seats_to_reserve},
                    ConditionExpression='#classes.#class.#availability >= :seats',
                    ReturnValues='UPDATED_NEW'
                )
                return True
            except self.dynamodb.meta.client.exceptions.ClientError as e:
                if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                    print(f"Insufficient availability for train {train_id}, class {class_name}")
                else:
                    print(f"Error updating train availability in DynamoDB: {str(e)}")
                return False
    
    def generate_pnr(self) -> str:
        """Generate a 10-digit PNR number"""
        global pnr_counter
        pnr_counter += 1
        return str(pnr_counter)
    
    def allocate_berth(self, class_name: str, seats: int) -> list:
        """
        Allocate berth/seat numbers based on class
        Args:
            class_name: The class name
            seats: Number of seats
        Returns:
            List of berth/seat allocations
        """
        import random
        
        berths = []
        berth_types = ["Lower", "Middle", "Upper", "Side Lower", "Side Upper"]
        coach_prefixes = {
            "AC1": "A",
            "AC2": "B",
            "AC3": "C",
            "SL": "S",
            "GN": "G",
            "AC Chair Car": "CC",
            "Executive": "E"
        }
        
        prefix = coach_prefixes.get(class_name, "X")
        
        for i in range(seats):
            coach_num = random.randint(1, 10)
            berth_num = random.randint(1, 72)
            berth_type = random.choice(berth_types) if class_name in ["AC2", "AC3", "SL"] else "Seat"
            berths.append({
                "Coach": f"{prefix}{coach_num}",
                "Berth": f"{berth_num}",
                "Type": berth_type
            })
        
        return berths
    
    def create_booking(self, train_id: str, route: str, time: str, seats: int, 
                       passenger_name: str, train_name: str = None, class_name: str = None,
                       journey_date: str = None, passengers: list = None, berth_preference: str = None,
                       user_id: str = None) -> Dict:
        """
        Create a new booking record with IRCTC-style details
        Args:
            train_id: The TrainID
            route: The route name
            time: Departure time
            seats: Number of seats booked
            passenger_name: Name of the passenger
            train_name: Optional train name
            class_name: Train class (AC1, AC2, AC3, SL, GN, etc.)
            journey_date: Date of journey
            passengers: List of passenger details (name, age, gender)
            berth_preference: Berth preference (Lower, Middle, Upper, etc.)
        Returns:
            Booking dictionary with BookingID and PNR
        """
        global booking_id_counter
        
        if self.use_mock:
            # Mock implementation: Add to in-memory list
            booking_id_counter += 1
            pnr = self.generate_pnr()
            
            # Get fare for the class
            fare_per_seat = 0
            for train in mock_trains:
                if train["TrainID"] == train_id and "Classes" in train:
                    if class_name and class_name in train["Classes"]:
                        fare_per_seat = train["Classes"][class_name]["Fare"]
                        break
            
            total_fare = fare_per_seat * seats
            
            # Allocate berths
            berth_allocations = self.allocate_berth(class_name, seats) if class_name else []
            
            booking = {
                "BookingID": str(booking_id_counter),
                "PNR": pnr,
                "TrainID": train_id,
                "Route": route,
                "Time": time,
                "Seats": seats,
                "PassengerName": passenger_name,
                "BookingDate": datetime.now().isoformat(),
                "Status": "Confirmed",
                "Class": class_name or "GN",
                "JourneyDate": journey_date or datetime.now().strftime("%Y-%m-%d"),
                "TotalFare": total_fare,
                "FarePerSeat": fare_per_seat,
                "BerthAllocations": berth_allocations,
                "BerthPreference": berth_preference or "No Preference",
                "UserID": user_id
            }
            
            if train_name:
                booking["TrainName"] = train_name
            
            if passengers:
                booking["Passengers"] = passengers
            else:
                # Default passenger if not provided
                booking["Passengers"] = [{
                    "Name": passenger_name,
                    "Age": "N/A",
                    "Gender": "N/A"
                }]
            
            mock_bookings.append(booking)
            return booking
        
        else:
            # Real DynamoDB implementation
            import uuid
            booking_id = f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:8].upper()}"
            pnr = self.generate_pnr()
            
            # Get fare for the class
            train_details = self.get_train_by_id(train_id)
            fare_per_seat = 0
            if train_details and "Classes" in train_details:
                if class_name and class_name in train_details["Classes"]:
                    fare_per_seat = train_details["Classes"][class_name]["Fare"]
            
            total_fare = fare_per_seat * seats
            
            # Allocate berths
            berth_allocations = self.allocate_berth(class_name, seats) if class_name else []
            
            booking = {
                "BookingID": booking_id,
                "PNR": pnr,
                "TrainID": train_id,
                "Route": route,
                "Time": time,
                "Seats": seats,
                "PassengerName": passenger_name,
                "BookingDate": datetime.now().isoformat(),
                "Status": "Confirmed",
                "Class": class_name or "GN",
                "JourneyDate": journey_date or datetime.now().strftime("%Y-%m-%d"),
                "TotalFare": total_fare,
                "FarePerSeat": fare_per_seat,
                "BerthAllocations": berth_allocations,
                "BerthPreference": berth_preference or "No Preference",
                "UserID": user_id
            }
            
            if train_name:
                booking["TrainName"] = train_name
            
            if passengers:
                booking["Passengers"] = passengers
            else:
                # Default passenger if not provided
                booking["Passengers"] = [{
                    "Name": passenger_name,
                    "Age": "N/A",
                    "Gender": "N/A"
                }]
            
            try:
                self.bookings_table.put_item(Item=booking)
                return booking
            except Exception as e:
                print(f"Error creating booking in DynamoDB: {str(e)}")
                return {}
    
    def get_booking_by_id(self, booking_id: str) -> Optional[Dict]:
        """
        Get a booking by BookingID
        Args:
            booking_id: The BookingID to search for
        Returns:
            Booking dictionary or None if not found
        """
        if self.use_mock:
            # Mock implementation: Search in-memory list
            for booking in mock_bookings:
                if booking["BookingID"] == booking_id:
                    return booking.copy()
            return None
    
    def get_bookings_by_user_id(self, user_id: str) -> List[Dict]:
        """
        Get all bookings for a specific user
        Args:
            user_id: The UserID to search for
        Returns:
            List of booking dictionaries
        """
        if self.use_mock:
            # Mock implementation: Filter bookings by user_id
            user_bookings = [
                booking.copy() for booking in mock_bookings
                if booking.get("UserID") == user_id
            ]
            # Sort by booking date (newest first)
            user_bookings.sort(key=lambda x: x.get("BookingDate", ""), reverse=True)
            return user_bookings
        
        else:
            # Real DynamoDB implementation
            try:
                response = self.bookings_table.query(
                    IndexName='UserIdIndex',
                    KeyConditionExpression=Key('UserID').eq(user_id)
                )
                user_bookings = response.get('Items', [])
                # Sort by booking date (newest first)
                user_bookings.sort(key=lambda x: x.get("BookingDate", ""), reverse=True)
                return user_bookings
            except Exception as e:
                print(f"Error getting bookings by user ID from DynamoDB: {str(e)}")
                return []


# Global instance for easy import
db_service = DatabaseService()


class UserService:
    """Service class for user authentication and management"""

    def __init__(self):
        self.use_mock = USE_MOCK_AWS
        if not self.use_mock:
            self.dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
            self.users_table = self.dynamodb.Table(DYNAMODB_TABLE_USERS)

    def _normalize_user(self, user: Optional[Dict]) -> Optional[Dict]:
        if not user:
            return None

        if 'user_id' in user:
            user_copy = user.copy()
            user_copy.pop('password_hash', None)
            return user_copy

        return {
            'user_id': user.get('UserID'),
            'username': user.get('Username'),
            'email': user.get('Email'),
            'full_name': user.get('FullName'),
            'phone': user.get('Phone'),
            'created_at': user.get('CreatedAt'),
            'bookings': user.get('Bookings', []),
            'is_admin': user.get('IsAdmin', False)
        }

    def _get_user_by_username_or_email(self, login_value: str) -> Optional[Dict]:
        if self.use_mock:
            for user in mock_users:
                if user['username'] == login_value or user['email'] == login_value:
                    return user.copy()
            return None

        login_value = (login_value or '').strip().lower()
        if not login_value:
            return None

        try:
            response = self.users_table.query(
                IndexName='UsernameLowerIndex',
                KeyConditionExpression=Key('UsernameLower').eq(login_value)
            )
            items = response.get('Items', [])
            if items:
                return items[0]
        except Exception:
            pass

        try:
            response = self.users_table.query(
                IndexName='EmailLowerIndex',
                KeyConditionExpression=Key('EmailLower').eq(login_value)
            )
            items = response.get('Items', [])
            if items:
                return items[0]
        except Exception:
            pass

        return None
    
    def register_user(self, username: str, email: str, password: str, full_name: str, phone: str = None) -> Dict:
        """
        Register a new user
        Args:
            username: Unique username
            email: User email
            password: Plain text password
            full_name: Full name of user
            phone: Optional phone number
        Returns:
            User dictionary or None if registration failed
        """
        if self.use_mock:
            # Check if username or email already exists
            for user in mock_users:
                if user['username'] == username or user['email'] == email:
                    return None

            # First user becomes admin in mock mode (simple bootstrap)
            is_admin = len(mock_users) == 0

            # Create new user
            user_id = str(uuid.uuid4())
            user = {
                'user_id': user_id,
                'username': username,
                'email': email,
                'password_hash': generate_password_hash(password),
                'full_name': full_name,
                'phone': phone or '',
                'created_at': datetime.now().isoformat(),
                'bookings': [],
                'is_admin': is_admin
            }

            mock_users.append(user)
            return self._normalize_user(user)

        username_lower = (username or '').strip().lower()
        email_lower = (email or '').strip().lower()

        if self._get_user_by_username_or_email(username_lower) or self._get_user_by_username_or_email(email_lower):
            return None

        is_admin = bool(BOOTSTRAP_ADMIN_EMAIL and email_lower == BOOTSTRAP_ADMIN_EMAIL)

        user_id = str(uuid.uuid4())
        user = {
            'UserID': user_id,
            'Username': username,
            'Email': email,
            'UsernameLower': username_lower,
            'EmailLower': email_lower,
            'PasswordHash': generate_password_hash(password),
            'FullName': full_name,
            'Phone': phone or '',
            'CreatedAt': datetime.now().isoformat(),
            'Bookings': [],
            'IsAdmin': is_admin
        }

        try:
            self.users_table.put_item(Item=user)
        except Exception:
            return None

        return self._normalize_user(user)
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """
        Authenticate a user
        Args:
            username: Username or email
            password: Plain text password
        Returns:
            User dictionary if authenticated, None otherwise
        """
        user = self._get_user_by_username_or_email(username)
        if not user:
            return None

        if self.use_mock:
            password_hash = user.get('password_hash')
        else:
            password_hash = user.get('PasswordHash')

        if password_hash and check_password_hash(password_hash, password):
            return self._normalize_user(user)

        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """
        Get user by user_id
        Args:
            user_id: User ID
        Returns:
            User dictionary or None
        """
        if self.use_mock:
            for user in mock_users:
                if user['user_id'] == user_id:
                    return self._normalize_user(user)
            return None

        try:
            response = self.users_table.get_item(Key={'UserID': user_id})
            item = response.get('Item')
            if not item:
                return None
            return self._normalize_user(item)
        except Exception:
            return None
    
    def update_user_profile(self, user_id: str, full_name: str = None, email: str = None, phone: str = None) -> bool:
        """
        Update user profile
        Args:
            user_id: User ID
            full_name: New full name
            email: New email
            phone: New phone
        Returns:
            True if updated, False otherwise
        """
        if self.use_mock:
            for user in mock_users:
                if user['user_id'] == user_id:
                    if full_name:
                        user['full_name'] = full_name
                    if email:
                        # Check if email already exists for another user
                        for other_user in mock_users:
                            if other_user['user_id'] != user_id and other_user['email'] == email:
                                return False
                        user['email'] = email
                    if phone:
                        user['phone'] = phone
                    return True
            return False

        updates = []
        names = {}
        values = {}

        if full_name:
            updates.append('#full_name = :full_name')
            names['#full_name'] = 'FullName'
            values[':full_name'] = full_name

        if email:
            email_lower = email.strip().lower()
            existing = self._get_user_by_username_or_email(email_lower)
            if existing and existing.get('UserID') != user_id:
                return False
            updates.append('#email = :email')
            updates.append('#email_lower = :email_lower')
            names['#email'] = 'Email'
            names['#email_lower'] = 'EmailLower'
            values[':email'] = email
            values[':email_lower'] = email_lower

        if phone:
            updates.append('#phone = :phone')
            names['#phone'] = 'Phone'
            values[':phone'] = phone

        if not updates:
            return True

        try:
            self.users_table.update_item(
                Key={'UserID': user_id},
                UpdateExpression='SET ' + ', '.join(updates),
                ExpressionAttributeNames=names,
                ExpressionAttributeValues=values
            )
            return True
        except Exception:
            return False
    
    def add_booking_to_user(self, user_id: str, booking_id: str):
        """
        Add booking ID to user's booking list
        Args:
            user_id: User ID
            booking_id: Booking ID
        """
        if self.use_mock:
            for user in mock_users:
                if user['user_id'] == user_id:
                    if booking_id not in user['bookings']:
                        user['bookings'].append(booking_id)
                    break
            return

        try:
            self.users_table.update_item(
                Key={'UserID': user_id},
                UpdateExpression='SET #bookings = list_append(if_not_exists(#bookings, :empty), :new)',
                ExpressionAttributeNames={'#bookings': 'Bookings'},
                ExpressionAttributeValues={
                    ':empty': [],
                    ':new': [booking_id]
                }
            )
        except Exception:
            return


# Global instance
user_service = UserService()


class S3Service:
    """Service class for S3 storage operations"""
    
    def __init__(self):
        self.use_mock = USE_MOCK_AWS
        
        if self.use_mock:
            # Get absolute path for uploads directory
            # Get the base directory (project root)
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.uploads_dir = os.path.join(base_dir, MOCK_UPLOADS_DIR)
            # Ensure the uploads directory exists for mock storage
            os.makedirs(self.uploads_dir, exist_ok=True)
        
        else:
            # Initialize S3 client when USE_MOCK_AWS = False
            self.s3_client = boto3.client('s3', region_name=AWS_REGION)
    
    def save_receipt(self, booking_data: dict) -> Optional[str]:
        """
        Save a booking receipt as a text file
        Args:
            booking_data: Dictionary containing booking information
        Returns:
            File path/URL of the saved receipt, or None if failed
        """
        if self.use_mock:
            # Mock implementation: Save to local file system
            try:
                booking_id = booking_data.get('BookingID', 'unknown')
                filename = f"receipt_{booking_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                filepath = os.path.join(self.uploads_dir, filename)
                
                # Generate receipt content
                receipt_content = self._generate_receipt_content(booking_data)
                
                # Write to file
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(receipt_content)
                
                # Return relative path for download link
                return f"static/uploads/{filename}"
            
            except Exception as e:
                print(f"[MOCK S3] Error saving receipt: {e}")
                return None
        
        else:
            # Real S3 implementation
            try:
                booking_id = booking_data.get('BookingID', 'unknown')
                filename = f"receipt_{booking_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                key = f"receipts/{filename}"
                
                # Generate receipt content
                receipt_content = self._generate_receipt_content(booking_data)
                
                # Upload to S3
                self.s3_client.put_object(
                    Bucket=S3_BUCKET_NAME,
                    Key=key,
                    Body=receipt_content.encode('utf-8'),
                    ContentType='text/plain'
                )
                
                # Generate presigned URL for download (valid for 1 hour)
                url = self.s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': S3_BUCKET_NAME, 'Key': key},
                    ExpiresIn=3600
                )
                
                return url

            except Exception as e:
                print(f"[S3] Error saving receipt: {e}")
                return None
    
    def _generate_receipt_content(self, booking_data: dict) -> str:
        """
        Generate the text content for a receipt
        Args:
            booking_data: Dictionary containing booking information
        Returns:
            Formatted receipt string
        """
        train_name_line = ""
        if booking_data.get('TrainName'):
            train_name_line = f"Train Name:        {booking_data.get('TrainName', 'N/A')}\n"
        
        pnr_line = ""
        if booking_data.get('PNR'):
            pnr_line = f"PNR Number:        {booking_data.get('PNR', 'N/A')}\n"
        
        class_line = ""
        if booking_data.get('Class'):
            class_line = f"Class:             {booking_data.get('Class', 'N/A')}\n"
        
        journey_date_line = ""
        if booking_data.get('JourneyDate'):
            journey_date_line = f"Journey Date:      {booking_data.get('JourneyDate', 'N/A')}\n"
        
        fare_line = ""
        if booking_data.get('TotalFare'):
            fare_line = f"Total Fare:        ₹{booking_data.get('TotalFare', 0)}\n"
        
        # Passenger details
        passengers_section = ""
        if booking_data.get('Passengers'):
            passengers_section = "\nPassenger Details:\n"
            for i, p in enumerate(booking_data.get('Passengers', []), 1):
                passengers_section += f"  {i}. {p.get('Name', 'N/A')} (Age: {p.get('Age', 'N/A')}, Gender: {p.get('Gender', 'N/A')})\n"
        
        # Berth allocations
        berth_section = ""
        if booking_data.get('BerthAllocations'):
            berth_section = "\nSeat/Berth Allocations:\n"
            for i, b in enumerate(booking_data.get('BerthAllocations', []), 1):
                berth_section += f"  {i}. Coach: {b.get('Coach', 'N/A')}, Berth: {b.get('Berth', 'N/A')}, Type: {b.get('Type', 'N/A')}\n"
        
        receipt = f"""
╔═══════════════════════════════════════════════════════════╗
║         INDIAN RAILWAYS BOOKING RECEIPT                   ║
╚═══════════════════════════════════════════════════════════╝

{pnr_line}Booking ID:        {booking_data.get('BookingID', 'N/A')}
Train Number:      {booking_data.get('TrainID', 'N/A')}
{train_name_line}Route:             {booking_data.get('Route', 'N/A')}
{journey_date_line}Departure Time:    {booking_data.get('Time', 'N/A')}
{class_line}Number of Seats:   {booking_data.get('Seats', 'N/A')}
{fare_line}{passengers_section}{berth_section}
Booking Date:      {booking_data.get('BookingDate', 'N/A')}
Status:            {booking_data.get('Status', 'N/A')}

╔═══════════════════════════════════════════════════════════╗
║  Thank you for choosing Indian Railways!                  ║
║  Please arrive at least 30 minutes before departure.     ║
║  Keep your PNR number safe for future reference.        ║
╚═══════════════════════════════════════════════════════════╝
"""
        return receipt.strip()
    
    def get_receipt_url(self, booking_id: str) -> Optional[str]:
        """
        Get the URL/path to a receipt file
        Args:
            booking_id: The BookingID
        Returns:
            File path/URL or None if not found
        """
        if self.use_mock:
            # Mock implementation: Search for file in uploads directory
            try:
                for filename in os.listdir(self.uploads_dir):
                    if booking_id in filename and filename.startswith('receipt_'):
                        return f"static/uploads/{filename}"
                return None
            except Exception as e:
                print(f"[MOCK S3] Error finding receipt: {e}")
                return None
        
        else:
            # Real S3 implementation
            try:
                # List objects with prefix
                response = self.s3_client.list_objects_v2(
                    Bucket=S3_BUCKET_NAME,
                    Prefix=f"receipts/receipt_{booking_id}_"
                )
                
                if 'Contents' in response and len(response['Contents']) > 0:
                    key = response['Contents'][0]['Key']
                    url = self.s3_client.generate_presigned_url(
                        'get_object',
                        Params={'Bucket': S3_BUCKET_NAME, 'Key': key},
                        ExpiresIn=3600
                    )
                    return url
                
                return None

            except Exception as e:
                print(f"[S3] Error getting receipt URL: {e}")
                return None


class LambdaService:
    """Service class for Lambda/SNS notification operations"""
    
    def __init__(self):
        self.use_mock = USE_MOCK_AWS
        
        if not self.use_mock:
            # Initialize Lambda client when USE_MOCK_AWS = False
            self.lambda_client = boto3.client('lambda', region_name=AWS_REGION)
            
            # Alternative: Use SNS for notifications
            # self.sns_client = boto3.client('sns', region_name=AWS_REGION)
            # self.sns_topic_arn = 'arn:aws:sns:us-east-1:123456789012:booking-notifications'
    
    def send_booking_notification(self, booking_data: dict) -> bool:
        """
        Send a notification about a new booking
        Args:
            booking_data: Dictionary containing booking information
        Returns:
            True if successful, False otherwise
        """
        if self.use_mock:
            # Mock implementation: Print to console simulating SNS/Lambda
            try:
                notification_payload = {
                    "event": "booking_confirmed",
                    "booking_id": booking_data.get('BookingID'),
                    "train_id": booking_data.get('TrainID'),
                    "route": booking_data.get('Route'),
                    "passenger_name": booking_data.get('PassengerName'),
                    "seats": booking_data.get('Seats'),
                    "timestamp": booking_data.get('BookingDate')
                }
                
                print("\n" + "="*60)
                print("[MOCK SNS] Email sent for Booking ID:", booking_data.get('BookingID'))
                print("[MOCK SNS] Notification Payload:")
                print(json.dumps(notification_payload, indent=2))
                print("="*60 + "\n")
                
                return True
            
            except Exception as e:
                print(f"[MOCK SNS] Error sending notification: {e}")
                return False
        
        else:
            # Real Lambda invocation implementation
            try:
                payload = {
                    "event": "booking_confirmed",
                    "booking_id": booking_data.get('BookingID'),
                    "train_id": booking_data.get('TrainID'),
                    "route": booking_data.get('Route'),
                    "passenger_name": booking_data.get('PassengerName'),
                    "seats": booking_data.get('Seats'),
                    "timestamp": booking_data.get('BookingDate')
                }
                
                response = self.lambda_client.invoke(
                    FunctionName=LAMBDA_FUNCTION_NAME,
                    InvocationType='Event',  # Async invocation
                    Payload=json.dumps(payload)
                )
                
                return response['StatusCode'] == 202
            except Exception as e:
                print(f"Error sending Lambda notification: {str(e)}")
                return False


# Global instances
s3_service = S3Service()
lambda_service = LambdaService()


# Initialize Flask app
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'frontend', 'templates'),
    static_folder=os.path.join(BASE_DIR, 'frontend', 'static')
)

# App configuration
app.secret_key = _config.SECRET_KEY
app.config.update(
    ENV=_config.APP_ENV,
    DEBUG=_config.DEBUG,
    SESSION_COOKIE_SECURE=_config.SESSION_COOKIE_SECURE,
    SESSION_COOKIE_HTTPONLY=_config.SESSION_COOKIE_HTTPONLY,
    SESSION_COOKIE_SAMESITE=_config.SESSION_COOKIE_SAMESITE
)

if not app.secret_key and _config.APP_ENV == 'production':
    raise RuntimeError('SECRET_KEY must be set in production')

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)

# Initialize app on startup
if USE_MOCK_AWS:
    print("\n" + "="*60)
    print("Train Booking Platform - Running in MOCK MODE")
    print("AWS services are simulated using local Python operations")
    print("="*60 + "\n")
    
    # Ensure uploads directory exists
    uploads_dir = os.path.join(BASE_DIR, MOCK_UPLOADS_DIR)
    os.makedirs(uploads_dir, exist_ok=True)
    print(f"[INIT] Created/verified uploads directory: {uploads_dir}")

def login_required(f):
    """
    Decorator to require user login for routes
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'error')
            return redirect(url_for('login'))
        # Verify user still exists
        current_user = get_current_user()
        if current_user is None:
            flash('Session expired. Please login again.', 'error')
            session.clear()
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Decorator to require admin access for routes.
    In mock mode: the first registered user is admin.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'error')
            return redirect(url_for('login'))
        user = user_service.get_user_by_id(session['user_id'])
        if not user or not user.get('is_admin'):
            flash('Admin access required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """
    Get current logged-in user
    Returns:
        User dictionary or None
    """
    if 'user_id' in session:
        return user_service.get_user_by_id(session['user_id'])
    return None


# Register all routes
# We'll define all routes in this file since we're consolidating everything

@app.route('/')
def index():
    """Home page with train search form"""
    current_user = get_current_user()
    return render_template('index.html', current_user=current_user)

@app.route('/search', methods=['GET', 'POST'])
def search():
    """Search for trains by route"""
    if request.method == 'POST':
        route_query = request.form.get('route', '').strip()
    else:
        # GET request - check for query parameter
        route_query = request.args.get('route', '').strip()
    
    # Search trains
    trains = db_service.search_trains(route_query)
    current_user = get_current_user()
    
    return render_template('results.html', trains=trains, search_query=route_query, current_user=current_user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        
        # Validation
        if not all([username, email, password, full_name]):
            flash('Please fill in all required fields.', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('register.html')
        
        # Register user
        user = user_service.register_user(username, email, password, full_name, phone)
        
        if user:
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username or email already exists.', 'error')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash('Please enter both username and password.', 'error')
            return render_template('login.html')
        
        user = user_service.authenticate_user(username, password)
        
        if user:
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            flash(f'Welcome back, {user["full_name"]}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid username or password.', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    current_user = get_current_user()
    if current_user is None:
        flash('User not found. Please login again.', 'error')
        return redirect(url_for('login'))
    
    # Get user booking stats
    bookings = db_service.get_bookings_by_user_id(current_user['user_id'])
    user_stats = {
        "total_bookings": len(bookings),
        "latest_booking": bookings[0] if bookings else None,
    }
    return render_template('profile.html', user=current_user, current_user=current_user, user_stats=user_stats)

@app.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    current_user = get_current_user()
    full_name = request.form.get('full_name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    
    success = user_service.update_user_profile(
        current_user['user_id'],
        full_name=full_name or None,
        email=email or None,
        phone=phone or None
    )
    
    if success:
        flash('Profile updated successfully!', 'success')
    else:
        flash('Failed to update profile. Email may already be in use.', 'error')
    
    return redirect(url_for('profile'))

@app.route('/history')
@login_required
def booking_history():
    """User booking history page"""
    current_user = get_current_user()
    if current_user is None:
        flash('User not found. Please login again.', 'error')
        return redirect(url_for('login'))
    bookings = db_service.get_bookings_by_user_id(current_user['user_id'])
    return render_template('history.html', bookings=bookings, user=current_user, current_user=current_user)

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard (enterprise landing after login)."""
    current_user = get_current_user()
    if current_user is None:
        flash('User not found. Please login again.', 'error')
        return redirect(url_for('login'))
    bookings = db_service.get_bookings_by_user_id(current_user['user_id'])
    stats = {
        "total_bookings": len(bookings),
        "latest_booking": bookings[0] if bookings else None,
    }
    return render_template('dashboard.html', current_user=current_user, stats=stats, bookings=bookings[:5])

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard (mock)."""
    current_user = get_current_user()
    if current_user is None:
        flash('User not found. Please login again.', 'error')
        return redirect(url_for('login'))
    # Basic operational data for capstone/demo (mock)
    trains = db_service.search_trains("")
    # compute sold-out trains (all classes 0)
    sold_out = []
    for t in trains:
        classes = t.get("Classes", {}) or {}
        total = sum(c.get("Availability", 0) for c in classes.values())
        if total <= 0:
            sold_out.append(t)
    return render_template(
        'admin.html',
        current_user=current_user,
        trains=trains,
        sold_out_trains=sold_out
    )

@app.route('/booking/<train_id>', methods=['GET', 'POST'])
@login_required
def booking(train_id):
    """Passenger details step (stores pending booking; proceeds to payment)."""
    # Get train details
    train = db_service.get_train_by_id(train_id)
    
    if not train:
        flash('Train not found!', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Process booking
        try:
            seats = int(request.form.get('seats', 0))
            passenger_name = request.form.get('passenger_name', '').strip()
            class_name = request.form.get('class_name', '').strip()
            journey_date = request.form.get('journey_date', '').strip()
            berth_preference = request.form.get('berth_preference', 'No Preference').strip()
            
            # Validate input
            if seats <= 0:
                flash('Please enter a valid number of seats.', 'error')
                return render_template('booking.html', train=train)
            
            if not passenger_name:
                flash('Please enter passenger name.', 'error')
                return render_template('booking.html', train=train)
            
            if not class_name:
                flash('Please select a class.', 'error')
                return render_template('booking.html', train=train)
            
            if not journey_date:
                flash('Please select journey date.', 'error')
                return render_template('booking.html', train=train)
            
            # Check availability for selected class
            if 'Classes' not in train or class_name not in train['Classes']:
                flash('Invalid class selected.', 'error')
                return render_template('booking.html', train=train)
            
            class_availability = train['Classes'][class_name]['Availability']
            if class_availability < seats:
                flash(f'Only {class_availability} seats available in {class_name}. Please select fewer seats.', 'error')
                return render_template('booking.html', train=train)
            
            # Collect passenger details
            passengers = []
            for i in range(seats):
                p_name = request.form.get(f'passenger_name_{i}', passenger_name if i == 0 else '').strip()
                p_age = request.form.get(f'passenger_age_{i}', '').strip()
                p_gender = request.form.get(f'passenger_gender_{i}', '').strip()
                
                if not p_name:
                    p_name = passenger_name if i == 0 else f"Passenger {i+1}"
                
                passengers.append({
                    "Name": p_name,
                    "Age": p_age or "N/A",
                    "Gender": p_gender or "N/A"
                })
            
            # Get current user
            current_user = get_current_user()

            # Store pending booking in session (Payment step will finalize + decrement availability)
            session['pending_booking'] = {
                "train_id": train_id,
                "route": train['Route'],
                "time": train['Time'],
                "train_name": train.get('TrainName'),
                "seats": seats,
                "primary_passenger_name": passenger_name,
                "class_name": class_name,
                "journey_date": journey_date,
                "passengers": passengers,
                "berth_preference": berth_preference,
                "user_id": current_user['user_id']
            }

            return redirect(url_for('payment'))
        
        except ValueError:
            flash('Invalid input. Please enter valid numbers.', 'error')
            return render_template('booking.html', train=train)
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')
            return render_template('booking.html', train=train)
        
    # GET request - show booking form
    current_user = get_current_user()
    return render_template('booking.html', train=train, current_user=current_user)

@app.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    """
    Payment step (mock).
    Confirms payment and finalizes booking: availability decrement, booking creation, receipt, notification.
    """
    current_user = get_current_user()
    pending = session.get('pending_booking')
    if not pending:
        flash('No pending booking found. Please start a new booking.', 'error')
        return redirect(url_for('index'))

    train = db_service.get_train_by_id(pending['train_id'])
    if not train:
        flash('Train not found.', 'error')
        return redirect(url_for('index'))

    class_name = pending['class_name']
    seats = int(pending['seats'])
    if 'Classes' not in train or class_name not in train['Classes']:
        flash('Selected class is no longer available.', 'error')
        return redirect(url_for('booking', train_id=pending['train_id']))

    fare_per_seat = train['Classes'][class_name]['Fare']
    total_fare = fare_per_seat * seats

    if request.method == 'POST':
        payment_method = request.form.get('payment_method', 'UPI').strip()
        reference = request.form.get('payment_reference', '').strip()

        # Basic mock validation
        if not payment_method:
            flash('Please select a payment method.', 'error')
            return render_template('payment.html', current_user=current_user, pending=pending, train=train, total_fare=total_fare)

        # Decrement availability (final check)
        success = db_service.update_train_availability(pending['train_id'], class_name, seats)
        if not success:
            flash('Payment received but seats are no longer available. Please try again.', 'error')
            return redirect(url_for('booking', train_id=pending['train_id']))

        # Create booking
        booking_data = db_service.create_booking(
            train_id=pending['train_id'],
            route=pending['route'],
            time=pending['time'],
            seats=seats,
            passenger_name=pending['primary_passenger_name'],
            train_name=pending.get('train_name'),
            class_name=class_name,
            journey_date=pending['journey_date'],
            passengers=pending['passengers'],
            berth_preference=pending.get('berth_preference'),
            user_id=pending['user_id']
        )
        booking_data["Payment"] = {
            "Method": payment_method,
            "Reference": reference or "MOCK-PAYMENT",
            "Amount": total_fare,
            "Currency": "INR",
            "Status": "PAID"
        }

        user_service.add_booking_to_user(current_user['user_id'], booking_data['BookingID'])

        # Receipt + notification
        s3_service.save_receipt(booking_data)
        lambda_service.send_booking_notification(booking_data)

        # Clear pending booking
        session.pop('pending_booking', None)

        return redirect(url_for('booking_success', booking_id=booking_data['BookingID']))

    return render_template('payment.html', current_user=current_user, pending=pending, train=train, total_fare=total_fare)

@app.route('/booking/success/<booking_id>')
@login_required
def booking_success(booking_id):
    """Success page after booking confirmation"""
    current_user = get_current_user()
    # Get booking details
    booking = db_service.get_booking_by_id(booking_id)
    
    if not booking:
        flash('Booking not found!', 'error')
        return redirect(url_for('index'))
    
    # Verify booking belongs to current user
    if booking.get('UserID') != current_user['user_id']:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('index'))
    
    # Get receipt URL/path
    receipt_path = s3_service.get_receipt_url(booking_id)
    
    return render_template('success.html', booking=booking, receipt_path=receipt_path, current_user=current_user)

@app.route('/api/trains', methods=['GET'])
def api_trains():
    """API endpoint to get all trains (for AJAX/future use)"""
    route_query = request.args.get('route', '').strip()
    trains = db_service.search_trains(route_query)
    return jsonify(trains)

@app.route('/api/train/<train_id>', methods=['GET'])
def api_train(train_id):
    """API endpoint to get a specific train"""
    train = db_service.get_train_by_id(train_id)
    if train:
        return jsonify(train)
    return jsonify({'error': 'Train not found'}), 404

@app.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint for load balancers."""
    return jsonify({'status': 'ok'}), 200


# Lambda handler function
def lambda_handler(event, context):
    """AWS Lambda handler for API Gateway"""
    from werkzeug.test import EnvironBuilder
    from werkzeug.wrappers import Request, Response
    import json
    import logging
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    try:
        # Log the incoming event
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Extract components from API Gateway event
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        query_params = event.get('queryStringParameters', {}) or {}
        headers = event.get('headers', {}) or {}
        body = event.get('body', '')
        
        # Handle base64 encoded body
        if event.get('isBase64Encoded', False) and body:
            import base64
            body = base64.b64decode(body)
        
        # Create environ using EnvironBuilder
        builder = EnvironBuilder(
            method=http_method,
            path=path,
            query_string=query_params,
            headers=headers,
            data=body
        )
        environ = builder.get_environ()
        
        # Process request through Flask app
        response = Response.from_app(app, environ)
        
        # Prepare response for API Gateway
        api_gateway_response = {
            'statusCode': response.status_code,
            'headers': dict(response.headers),
            'body': response.get_data(as_text=True)
        }
        
        logger.info(f"Returning response with status {response.status_code}")
        return api_gateway_response
        
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }


if __name__ == '__main__':
    # Run the Flask development server
    app.run(debug=_config.DEBUG, host=_config.HOST, port=_config.PORT)
