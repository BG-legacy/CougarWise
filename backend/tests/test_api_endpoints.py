"""
Tests for the API endpoints.

This file contains test classes and methods for testing the CougarWise API endpoints.
It verifies that the API behaves correctly for various scenarios including:
- Creating, retrieving, and validating users
- Creating and retrieving transactions
- Creating, retrieving, and updating financial goals

These tests use pytest fixtures defined in conftest.py to set up test data and clients.
"""
import pytest  # Testing framework
import json  # For JSON manipulation
from bson import ObjectId  # MongoDB's unique identifier type
from datetime import datetime, timedelta  # For date and time operations

from tests.conftest import create_test_user, create_test_transaction, create_test_goal  # Helper functions for test data

class TestUserEndpoints:
    """
    Tests for the user endpoints.
    
    This class contains tests for the user-related API endpoints:
    - POST /db/users (create user)
    - GET /db/users/{username} (get user)
    
    These tests verify that users can be created and retrieved correctly,
    and that appropriate error responses are returned for invalid requests.
    """
    
    def test_create_user(self, client, test_user_data):
        """
        Test creating a user.
        
        This test verifies that attempting to create a user with data that
        already exists in the database returns a 400 error with an appropriate
        message.
        
        Args:
            client: FastAPI test client from fixture
            test_user_data: Test user data from fixture
        """
        # Create user
        response = client.post("/db/users", json=test_user_data)
        
        # Check response
        # We expect a 400 error because the user already exists in the database
        # (created by the test_user_data fixture)
        assert response.status_code == 400  # Expect 400 because the user already exists in the database
        assert "Username already registered" in response.json()["detail"]
    
    def test_create_duplicate_user(self, client, db, test_user_data):
        """
        Test creating a user with a duplicate username.
        
        This test verifies that attempting to create a user with a username
        that already exists returns a 400 error with an appropriate message.
        
        Args:
            client: FastAPI test client from fixture
            db: Test database from fixture
            test_user_data: Test user data from fixture
        """
        # Create user in the database directly (not through the API)
        create_test_user(db)
        
        # Try to create duplicate user through the API
        response = client.post("/db/users", json=test_user_data)
        
        # Check response
        assert response.status_code == 400  # Expect 400 Bad Request
        assert "Username already registered" in response.json()["detail"]  # Check error message
    
    def test_get_user(self, client, db):
        """
        Test getting a user by username.
        
        This test verifies that a user can be retrieved by username,
        and that the response contains the expected user data.
        
        Args:
            client: FastAPI test client from fixture
            db: Test database from fixture
        """
        # Create user in the database directly (not through the API)
        user_data = create_test_user(db)
        
        # Get user through the API
        response = client.get(f"/db/users/{user_data['username']}")
        
        # Check response
        assert response.status_code == 200  # Expect 200 OK
        data = response.json()
        # Verify user data in response
        assert data["username"] == user_data["username"]  # Check username
        assert data["email"] == user_data["email"]  # Check email
        assert data["name"] == user_data["name"]  # Check name
        assert "password" not in data  # Password should not be returned for security
    
    def test_get_nonexistent_user(self, client):
        """
        Test getting a user that doesn't exist.
        
        This test verifies that attempting to retrieve a user that doesn't exist
        returns a 404 error with an appropriate message.
        
        Args:
            client: FastAPI test client from fixture
        """
        # Get user that doesn't exist
        response = client.get("/db/users/nonexistentuser")
        
        # Check response
        assert response.status_code == 404  # Expect 404 Not Found
        assert "User not found" in response.json()["detail"]  # Check error message

class TestTransactionEndpoints:
    """
    Tests for the transaction endpoints.
    
    This class contains tests for the transaction-related API endpoints:
    - POST /db/transactions (create transaction)
    - GET /db/transactions/user/{user_id} (get user transactions)
    
    These tests verify that transactions can be created and retrieved correctly,
    and that appropriate error responses are returned for invalid requests.
    """
    
    def test_create_transaction(self, client, db, test_transaction_data):
        """
        Test creating a transaction.
        
        This test verifies that a transaction can be created successfully,
        and that the response contains the expected transaction data.
        
        Args:
            client: FastAPI test client from fixture
            db: Test database from fixture
            test_transaction_data: Test transaction data from fixture
        """
        # Create user in the database directly (not through the API)
        create_test_user(db)
        
        # Create transaction through the API
        response = client.post("/db/transactions", json=test_transaction_data)
        
        # Check response
        assert response.status_code == 200  # Expect 200 OK
        data = response.json()
        # Verify transaction data in response
        assert data["userId"] == test_transaction_data["userId"]  # Check user ID
        assert data["amount"] == test_transaction_data["amount"]  # Check amount
        assert data["category"] == test_transaction_data["category"]  # Check category
        assert data["description"] == test_transaction_data["description"]  # Check description
        assert "id" in data  # ID should be returned
    
    def test_create_transaction_nonexistent_user(self, client, test_transaction_data):
        """
        Test creating a transaction for a user that doesn't exist.
        
        This test verifies that attempting to create a transaction for a user
        that doesn't exist returns a 404 error with an appropriate message.
        
        Args:
            client: FastAPI test client from fixture
            test_transaction_data: Test transaction data from fixture
        """
        # Modify transaction data to use a nonexistent user
        test_transaction_data["userId"] = "nonexistentuser"
        
        # Create transaction through the API
        response = client.post("/db/transactions", json=test_transaction_data)
        
        # Check response
        assert response.status_code == 404  # Expect 404 Not Found
        assert "User not found" in response.json()["detail"]  # Check error message
    
    def test_get_user_transactions(self, client, db):
        """
        Test getting all transactions for a user.
        
        This test verifies that all transactions for a user can be retrieved,
        and that the response contains the expected transaction data.
        
        Args:
            client: FastAPI test client from fixture
            db: Test database from fixture
        """
        # Create user in the database directly (not through the API)
        create_test_user(db)
        
        # Create a transaction in the database directly
        transaction_data = create_test_transaction(db)
        
        # Create another transaction in the database directly
        db["Transactions"].insert_one({
            "userId": transaction_data["userId"],
            "amount": 25.00,
            "category": "Transport",
            "description": "Bus fare",
            "date": datetime.now()
        })
        
        # Get transactions through the API
        response = client.get(f"/db/transactions/user/{transaction_data['userId']}")
        
        # Check response
        assert response.status_code == 200  # Expect 200 OK
        data = response.json()
        assert len(data) >= 2  # Should have at least 2 transactions
        # Verify transaction data in response
        assert data[0]["userId"] == transaction_data["userId"]  # Check user ID in first transaction
        assert data[1]["userId"] == transaction_data["userId"]  # Check user ID in second transaction

class TestFinancialGoalEndpoints:
    """
    Tests for the financial goal endpoints.
    
    This class contains tests for the financial goal-related API endpoints:
    - POST /db/goals (create goal)
    - GET /db/goals/user/{user_id} (get user goals)
    - PUT /db/goals/{goal_id} (update goal)
    
    These tests verify that financial goals can be created, retrieved, and updated correctly,
    and that appropriate error responses are returned for invalid requests.
    """
    
    def test_create_goal(self, client, db, test_goal_data):
        """
        Test creating a financial goal.
        
        This test verifies that a financial goal can be created successfully,
        and that the response contains the expected goal data.
        
        Args:
            client: FastAPI test client from fixture
            db: Test database from fixture
            test_goal_data: Test goal data from fixture
        """
        # Create user in the database directly (not through the API)
        create_test_user(db)
        
        # Create goal through the API
        response = client.post("/db/goals", json=test_goal_data)
        
        # Check response
        assert response.status_code == 200  # Expect 200 OK
        data = response.json()
        # Verify goal data in response
        assert data["userId"] == test_goal_data["userId"]  # Check user ID
        assert data["targetAmount"] == test_goal_data["targetAmount"]  # Check target amount
        assert data["currentAmount"] == test_goal_data["currentAmount"]  # Check current amount
        assert data["category"] == test_goal_data["category"]  # Check category
        assert "id" in data  # ID should be returned
    
    def test_create_goal_nonexistent_user(self, client, test_goal_data):
        """
        Test creating a goal for a user that doesn't exist.
        
        This test verifies that attempting to create a goal for a user
        that doesn't exist returns a 404 error with an appropriate message.
        
        Args:
            client: FastAPI test client from fixture
            test_goal_data: Test goal data from fixture
        """
        # Modify goal data to use a nonexistent user
        test_goal_data["userId"] = "nonexistentuser"
        
        # Create goal through the API
        response = client.post("/db/goals", json=test_goal_data)
        
        # Check response
        assert response.status_code == 404  # Expect 404 Not Found
        assert "User not found" in response.json()["detail"]  # Check error message
    
    def test_get_user_goals(self, client, db):
        """
        Test getting all goals for a user.
        
        This test verifies that all goals for a user can be retrieved,
        and that the response contains the expected goal data.
        
        Args:
            client: FastAPI test client from fixture
            db: Test database from fixture
        """
        # Create user in the database directly (not through the API)
        create_test_user(db)
        
        # Create a goal in the database directly
        goal_data = create_test_goal(db)
        
        # Create another goal in the database directly
        db["FinancialGoals"].insert_one({
            "userId": goal_data["userId"],
            "targetAmount": 5000.00,
            "currentAmount": 1000.00,
            "category": "Education",
            "deadline": datetime.now() + timedelta(days=365)
        })
        
        # Get goals through the API
        response = client.get(f"/db/goals/user/{goal_data['userId']}")
        
        # Check response
        assert response.status_code == 200  # Expect 200 OK
        data = response.json()
        assert len(data) >= 2  # Should have at least 2 goals
        # Verify goal data in response
        assert data[0]["userId"] == goal_data["userId"]  # Check user ID in first goal
        assert data[1]["userId"] == goal_data["userId"]  # Check user ID in second goal
    
    def test_update_goal(self, client, db):
        """
        Test updating a financial goal.
        
        This test verifies that a financial goal can be updated successfully,
        and that the response contains the updated goal data.
        
        Args:
            client: FastAPI test client from fixture
            db: Test database from fixture
        """
        # Create user in the database directly (not through the API)
        create_test_user(db)
        
        # Create a goal in the database directly
        goal_data = create_test_goal(db)
        
        # Update data for the goal
        update_data = {
            "currentAmount": 500.00,  # New current amount
            "targetAmount": 1500.00  # New target amount
        }
        
        # Update goal through the API
        response = client.put(f"/db/goals/{str(goal_data['_id'])}", json=update_data)
        
        # Check response
        assert response.status_code == 200  # Expect 200 OK
        data = response.json()
        # Verify updated goal data in response
        assert data["userId"] == goal_data["userId"]  # User ID should not change
        assert data["currentAmount"] == update_data["currentAmount"]  # Current amount should be updated
        assert data["targetAmount"] == update_data["targetAmount"]  # Target amount should be updated
        assert data["category"] == goal_data["category"]  # Category should not change
    
    def test_update_nonexistent_goal(self, client):
        """
        Test updating a goal that doesn't exist.
        
        This test verifies that attempting to update a goal that doesn't exist
        returns a 404 error with an appropriate message.
        
        Args:
            client: FastAPI test client from fixture
        """
        # Generate a random ObjectId that doesn't exist in the database
        nonexistent_id = str(ObjectId())
        
        # Update data for a nonexistent goal
        update_data = {
            "currentAmount": 500.00,
            "targetAmount": 1500.00
        }
        
        # Update nonexistent goal through the API
        response = client.put(f"/db/goals/{nonexistent_id}", json=update_data)
        
        # Check response
        assert response.status_code == 404  # Expect 404 Not Found
        assert "Goal not found" in response.json()["detail"]  # Check error message 