"""
Tests for the database models.
"""
import pytest
from bson import ObjectId
from datetime import datetime, timedelta

from Database.models import User, Transaction, FinancialGoal
from Database.database import Collections

class TestUserModel:
    """Tests for the User model."""
    
    def test_create_user(self, db, test_user_data):
        """Test creating a user."""
        # Create user
        user = User.create(test_user_data)
        
        # Check user was created
        assert user is not None
        assert user.username == test_user_data["username"]
        assert user.email == test_user_data["email"]
        assert user.password == test_user_data["password"]
        assert user.name == test_user_data["name"]
        
        # Check user exists in database
        db_user = db[Collections.USERS].find_one({"username": test_user_data["username"]})
        assert db_user is not None
        assert db_user["username"] == test_user_data["username"]
    
    def test_find_by_username(self, db, test_user_data):
        """Test finding a user by username."""
        # Create user
        db[Collections.USERS].insert_one(test_user_data)
        
        # Find user
        user = User.find_by_username(test_user_data["username"])
        
        # Check user was found
        assert user is not None
        assert user.username == test_user_data["username"]
        assert user.email == test_user_data["email"]
    
    def test_find_by_email(self, db, test_user_data):
        """Test finding a user by email."""
        # Create user
        db[Collections.USERS].insert_one(test_user_data)
        
        # Find user
        user = User.find_by_email(test_user_data["email"])
        
        # Check user was found
        assert user is not None
        assert user.username == test_user_data["username"]
        assert user.email == test_user_data["email"]
    
    def test_find_nonexistent_user(self, db):
        """Test finding a user that doesn't exist."""
        # Find user
        user = User.find_by_username("nonexistentuser")
        
        # Check user was not found
        assert user is None

class TestTransactionModel:
    """Tests for the Transaction model."""
    
    def test_create_transaction(self, db, test_transaction_data):
        """Test creating a transaction."""
        # Create transaction
        transaction = Transaction.create(test_transaction_data)
        
        # Check transaction was created
        assert transaction is not None
        assert transaction.userId == test_transaction_data["userId"]
        assert transaction.amount == test_transaction_data["amount"]
        assert transaction.category == test_transaction_data["category"]
        assert transaction.description == test_transaction_data["description"]
        
        # Check transaction exists in database
        db_transaction = db[Collections.TRANSACTIONS].find_one({"userId": test_transaction_data["userId"]})
        assert db_transaction is not None
        assert db_transaction["userId"] == test_transaction_data["userId"]
    
    def test_find_by_user(self, db, test_transaction_data):
        """Test finding transactions by user."""
        # Clear existing transactions
        db[Collections.TRANSACTIONS].delete_many({})
        
        # Create transactions
        db[Collections.TRANSACTIONS].insert_one(test_transaction_data)
        db[Collections.TRANSACTIONS].insert_one({
            "userId": test_transaction_data["userId"],
            "amount": 25.00,
            "category": "Transport",
            "description": "Bus fare",
            "date": datetime.now()
        })
    
        # Find transactions
        transactions = Transaction.find_by_user(test_transaction_data["userId"])
    
        # Check transactions were found
        assert transactions is not None
        assert len(transactions) == 2
    
    def test_find_by_category(self, db, test_transaction_data):
        """Test finding transactions by category."""
        # Clear existing transactions
        db[Collections.TRANSACTIONS].delete_many({})
        
        # Create transactions
        db[Collections.TRANSACTIONS].insert_one(test_transaction_data)
        db[Collections.TRANSACTIONS].insert_one({
            "userId": test_transaction_data["userId"],
            "amount": 25.00,
            "category": "Transport",
            "description": "Bus fare",
            "date": datetime.now()
        })
    
        # Find transactions
        transactions = Transaction.find_by_category(test_transaction_data["userId"], test_transaction_data["category"])
    
        # Check transactions were found
        assert transactions is not None
        assert len(transactions) == 1

class TestFinancialGoalModel:
    """Tests for the FinancialGoal model."""
    
    def test_create_goal(self, db, test_goal_data):
        """Test creating a financial goal."""
        # Create goal
        goal = FinancialGoal.create(test_goal_data)
        
        # Check goal was created
        assert goal is not None
        assert goal.userId == test_goal_data["userId"]
        assert goal.targetAmount == test_goal_data["targetAmount"]
        assert goal.currentAmount == test_goal_data["currentAmount"]
        assert goal.category == test_goal_data["category"]
        
        # Check goal exists in database
        db_goal = db[Collections.FINANCIAL_GOALS].find_one({"userId": test_goal_data["userId"]})
        assert db_goal is not None
        assert db_goal["userId"] == test_goal_data["userId"]
    
    def test_find_by_user(self, db, test_goal_data):
        """Test finding goals by user."""
        # Clear existing goals
        db[Collections.FINANCIAL_GOALS].delete_many({})
        
        # Create goals
        db[Collections.FINANCIAL_GOALS].insert_one(test_goal_data)
        db[Collections.FINANCIAL_GOALS].insert_one({
            "userId": test_goal_data["userId"],
            "targetAmount": 5000.00,
            "currentAmount": 1000.00,
            "category": "Education",
            "deadline": datetime.now() + timedelta(days=365)
        })
    
        # Find goals
        goals = FinancialGoal.find_by_user(test_goal_data["userId"])
    
        # Check goals were found
        assert goals is not None
        assert len(goals) == 2
    
    def test_update_goal(self, db, test_goal_data):
        """Test updating a financial goal."""
        # Create goal
        result = db[Collections.FINANCIAL_GOALS].insert_one(test_goal_data)
        goal_id = str(result.inserted_id)
        
        # Update goal
        update_data = {
            "currentAmount": 500.00,
            "targetAmount": 1500.00
        }
        success = FinancialGoal.update_goal(goal_id, update_data)
        
        # Check goal was updated
        assert success is True
        
        # Check goal was updated in database
        db_goal = db[Collections.FINANCIAL_GOALS].find_one({"_id": ObjectId(goal_id)})
        assert db_goal is not None
        assert db_goal["currentAmount"] == update_data["currentAmount"]
        assert db_goal["targetAmount"] == update_data["targetAmount"] 