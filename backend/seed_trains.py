#!/usr/bin/env python3
"""
Seed script to populate DynamoDB Trains table with initial data.
Run this once after provisioning the Trains table.

Usage:
    python seed_trains.py
"""

import os
import sys
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
DYNAMODB_TABLE_TRAINS = os.getenv('DYNAMODB_TABLE_TRAINS', 'trains')

# Train data (same as mock_trains in app.py)
TRAIN_DATA = [
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
        "TrainID": "12261",
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


def seed_trains():
    """Seed the DynamoDB Trains table with initial data."""
    print(f"Seeding trains table: {DYNAMODB_TABLE_TRAINS} in region {AWS_REGION}")
    
    try:
        dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
        table = dynamodb.Table(DYNAMODB_TABLE_TRAINS)
        
        # Check if table exists
        try:
            table.load()
        except Exception as e:
            print(f"Error: Table '{DYNAMODB_TABLE_TRAINS}' does not exist or is not accessible.")
            print(f"Details: {e}")
            return False
        
        # Batch write items
        with table.batch_writer() as batch:
            for train in TRAIN_DATA:
                batch.put_item(Item=train)
                print(f"  ✓ Inserted train {train['TrainID']} - {train['TrainName']}")
        
        print(f"\n✓ Successfully seeded {len(TRAIN_DATA)} trains into {DYNAMODB_TABLE_TRAINS}")
        return True
    
    except Exception as e:
        print(f"Error seeding trains: {e}")
        return False


if __name__ == '__main__':
    success = seed_trains()
    sys.exit(0 if success else 1)
