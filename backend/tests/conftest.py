"""
Pytest configuration file for CougarWise backend tests.
This file contains fixtures and configuration for pytest.

Key components:
- Test client fixture for FastAPI
- MongoDB test database setup and teardown
- Test data fixtures for users, transactions, and goals
- Helper functions for creating test data
"""
import os  # For accessing environment variables and file paths
import pytest  # The testing framework
from fastapi.testclient import TestClient  # For testing FastAPI applications
from pymongo import MongoClient  # MongoDB client library
from bson import ObjectId  # MongoDB's unique identifier type
from datetime import datetime, timedelta  # For handling dates and times

# Add backend directory to path to allow imports from parent directory
# This is necessary because the tests are in a subdirectory
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import app and database using absolute imports
# These are the main components we'll be testing
from api.API import app  # The FastAPI application
from Database.database import Database, get_db, get_collection, Collections  # Database utilities

# Test client fixture
@pytest.fixture
def client():
    """
    Create a test client for the FastAPI app.
    
    This fixture provides a test client that can be used to make requests
    to the FastAPI application without running a server. It's used in tests
    to simulate HTTP requests and check responses.
    
    The 'with' statement ensures proper cleanup after tests.
    
    Returns:
        TestClient: A FastAPI test client
    """
    with TestClient(app) as test_client:
        yield test_client  # Yield the client to the test, then clean up after

# MongoDB test database fixture
@pytest.fixture(scope="session")
def mongo_client():
    """
    Create a MongoDB client for testing.
    
    This fixture:
    1. Sets up a separate test database to avoid affecting the production database
    2. Clears the test database before tests to ensure a clean state
    3. Provides the MongoDB client to tests
    4. Cleans up the test database after all tests are complete
    
    The 'scope="session"' means this fixture is created once per test session,
    rather than for each test function, improving performance.
    
    Returns:
        MongoClient: A MongoDB client connected to the test database
    """
    # Use a test database with a different name from the production database
    test_db_name = "cougarwise_test"
    mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    
    # Override the database instance for testing
    # This ensures tests use the test database instead of the production database
    Database._instance = None  # Reset the singleton instance
    os.environ["MONGODB_DB_NAME"] = test_db_name  # Set environment variable for test DB
    
    # Create MongoDB client
    client = MongoClient(mongo_uri, tls=True, tlsAllowInvalidCertificates=True)
    
    # Clear test database before tests to ensure a clean state
    client.drop_database(test_db_name)
    
    # Provide the client to tests
    yield client
    
    # Clean up after tests
    # This ensures tests don't leave data behind that could affect future test runs
    client.drop_database(test_db_name)  # Remove the test database
    client.close()  # Close the connection

@pytest.fixture
def db(mongo_client):
    """
    Get the test database.
    
    This fixture provides the test database to tests. It depends on the
    mongo_client fixture, which sets up the MongoDB client.
    
    Args:
        mongo_client: The MongoDB client from the mongo_client fixture
        
    Returns:
        Database: The test MongoDB database
    """
    return mongo_client[os.getenv('MONGODB_DB_NAME', 'cougarwise_test')]

# Test data fixtures
# These fixtures provide consistent test data for tests to use

@pytest.fixture
def test_user_data():
    """
    Create test user data.
    
    This fixture provides a dictionary with test user data that can be used
    to create a user in tests. Using a fixture ensures consistent test data
    across tests.
    
    Returns:
        dict: Dictionary containing test user data
    """
    return {
        "username": "testuser",  # Test username
        "email": "test@example.com",  # Test email
        "password": "hashedpassword123",  # Test password (would be hashed in production)
        "name": "Test User"  # Test name
    }

@pytest.fixture
def test_transaction_data():
    """
    Create test transaction data.
    
    This fixture provides a dictionary with test transaction data that can be
    used to create a transaction in tests. The date is converted to ISO format
    for JSON serialization.
    
    Returns:
        dict: Dictionary containing test transaction data
    """
    return {
        "userId": "testuser",  # User who made the transaction
        "amount": 50.00,  # Transaction amount
        "category": "Food",  # Transaction category
        "description": "Lunch",  # Transaction description
        "date": datetime.now().isoformat()  # Current time in ISO format for JSON
    }

@pytest.fixture
def test_goal_data():
    """
    Create test financial goal data.
    
    This fixture provides a dictionary with test financial goal data that can be
    used to create a goal in tests. The deadline is set to 30 days from now
    and converted to ISO format for JSON serialization.
    
    Returns:
        dict: Dictionary containing test financial goal data
    """
    return {
        "userId": "testuser",  # User who created the goal
        "targetAmount": 1000.00,  # Target amount to save
        "currentAmount": 0.00,  # Current progress (starting at 0)
        "category": "Savings",  # Goal category
        "deadline": (datetime.now() + timedelta(days=30)).isoformat()  # 30 days from now in ISO format
    }

# Helper functions for creating test data in the database
# These functions are used by tests to set up test data

def create_test_user(db):
    """
    Create a test user in the database.
    
    This helper function creates a test user directly in the database,
    bypassing the API. This is useful for setting up test data for other tests.
    
    Args:
        db: The test database from the db fixture
        
    Returns:
        dict: The created user data, including the generated _id
    """
    # Create user data
    user_data = {
        "username": "testuser",  # Username
        "email": "test@example.com",  # Email
        "password": "hashedpassword123",  # Password (would be hashed in production)
        "name": "Test User",  # Full name
        "createdAt": datetime.now()  # Creation timestamp
    }
    
    # Insert user into database
    result = db[Collections.USERS].insert_one(user_data)
    
    # Add the generated ID to the user data
    user_data["_id"] = result.inserted_id
    
    return user_data

def create_test_transaction(db):
    """
    Create a test transaction in the database.
    
    This helper function creates a test transaction directly in the database,
    bypassing the API. This is useful for setting up test data for other tests.
    
    Args:
        db: The test database from the db fixture
        
    Returns:
        dict: The created transaction data, including the generated _id
    """
    # Create transaction data
    transaction_data = {
        "userId": "testuser",  # User who made the transaction
        "amount": 50.00,  # Transaction amount
        "category": "Food",  # Transaction category
        "description": "Lunch",  # Transaction description
        "date": datetime.now()  # Current time
    }
    
    # Insert transaction into database
    result = db[Collections.TRANSACTIONS].insert_one(transaction_data)
    
    # Add the generated ID to the transaction data
    transaction_data["_id"] = result.inserted_id
    
    return transaction_data

def create_test_goal(db):
    """
    Create a test financial goal in the database.
    
    This helper function creates a test financial goal directly in the database,
    bypassing the API. This is useful for setting up test data for other tests.
    
    Args:
        db: The test database from the db fixture
        
    Returns:
        dict: The created goal data, including the generated _id
    """
    # Create goal data
    goal_data = {
        "userId": "testuser",  # User who created the goal
        "targetAmount": 1000.00,  # Target amount to save
        "currentAmount": 0.00,  # Current progress (starting at 0)
        "category": "Savings",  # Goal category
        "deadline": datetime.now() + timedelta(days=30)  # 30 days from now
    }
    
    # Insert goal into database
    result = db[Collections.FINANCIAL_GOALS].insert_one(goal_data)
    
    # Add the generated ID to the goal data
    goal_data["_id"] = result.inserted_id
    
    return goal_data 