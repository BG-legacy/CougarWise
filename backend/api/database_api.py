"""
Database API endpoints for CougarWise backend.
This module provides API endpoints for database operations including:
- User management (create, retrieve)
- Transaction management (create, retrieve)
- Financial goal management (create, retrieve, update)

These endpoints serve as the interface between the frontend application
and the MongoDB database, handling data validation and error handling.
"""
from fastapi import APIRouter, HTTPException, Depends  # FastAPI components for routing and error handling
from pydantic import BaseModel  # For data validation and settings management
from typing import List, Dict, Any, Optional  # Type hints for better code documentation
from datetime import datetime  # For handling date and time
from bson import ObjectId, json_util  # For MongoDB ObjectId handling and JSON serialization
import json  # For JSON manipulation

# Import database models - Using absolute imports for better reliability
from Database.models import User, Transaction, FinancialGoal  # Database model classes
from Database.database import get_db, close_db_connection  # Database connection utilities

# Create router with prefix and tags for API documentation
router = APIRouter(
    prefix="/db",  # All endpoints will start with /db
    tags=["database"],  # For API documentation grouping
    responses={404: {"description": "Not found"}},  # Default response for 404 errors
)

# Request and response models
# These Pydantic models define the structure of request and response data
# They provide automatic validation and documentation

class UserCreate(BaseModel):
    """
    Model for creating a new user.
    Contains all required fields for user creation.
    """
    username: str  # Unique username for the user
    email: str  # User's email address
    password: str  # User's password (will be hashed before storage)
    name: str  # User's full name

class UserResponse(BaseModel):
    """
    Model for user response data.
    Contains user information returned to the client.
    Note: password is not included for security.
    """
    id: str  # User's unique ID
    username: str  # User's username
    email: str  # User's email address
    name: str  # User's full name
    createdAt: str  # When the user account was created

class TransactionCreate(BaseModel):
    """
    Model for creating a new financial transaction.
    Contains all fields needed to record a financial transaction.
    """
    userId: str  # ID of the user who made the transaction
    amount: float  # Amount of money involved in the transaction
    category: str  # Category of the transaction (e.g., Food, Housing)
    description: str  # Description of the transaction
    date: Optional[datetime] = None  # Date of the transaction (optional, defaults to current time)

class TransactionResponse(BaseModel):
    """
    Model for transaction response data.
    Contains transaction information returned to the client.
    """
    id: str  # Transaction's unique ID
    userId: str  # ID of the user who made the transaction
    amount: float  # Amount of money involved
    category: str  # Category of the transaction
    description: str  # Description of the transaction
    date: str  # Date of the transaction (as string)

class FinancialGoalCreate(BaseModel):
    """
    Model for creating a new financial goal.
    Contains all fields needed to define a financial goal.
    """
    userId: str  # ID of the user who created the goal
    targetAmount: float  # Target amount to save/earn
    currentAmount: float  # Current progress towards the goal
    category: str  # Category of the goal (e.g., Emergency Fund, Vacation)
    name: str  # Name of the financial goal
    deadline: datetime  # Deadline for achieving the goal

class FinancialGoalResponse(BaseModel):
    """
    Model for financial goal response data.
    Contains goal information returned to the client.
    """
    id: str  # Goal's unique ID
    userId: str  # ID of the user who created the goal
    targetAmount: float  # Target amount
    currentAmount: float  # Current progress
    category: str  # Category of the goal
    name: str  # Name of the financial goal
    deadline: str  # Deadline for the goal (as string)

class FinancialGoalUpdate(BaseModel):
    """
    Model for updating a financial goal.
    All fields are optional since updates may be partial.
    """
    targetAmount: Optional[float] = None  # New target amount (optional)
    currentAmount: Optional[float] = None  # New current amount (optional)
    category: Optional[str] = None  # New category (optional)
    name: Optional[str] = None  # New name (optional)
    deadline: Optional[datetime] = None  # New deadline (optional)

# Database dependency
def get_db_dependency():
    """
    Get database dependency for FastAPI dependency injection.
    This function is used as a dependency in route functions to get the database connection.
    
    Returns:
        MongoDB database connection
    """
    return get_db()

# User endpoints
@router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, db=Depends(get_db_dependency)):
    """
    Create a new user in the database.
    
    This endpoint:
    1. Validates the user data using the UserCreate model
    2. Checks if the username or email already exists
    3. Creates the user in the database
    4. Returns the created user information
    
    Args:
        user: User data from request body
        db: Database connection from dependency
        
    Returns:
        Created user information
        
    Raises:
        HTTPException: If username or email already exists
    """
    # Check if user exists by username
    existing_user = User.find_by_username(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Check if user exists by email
    existing_email = User.find_by_email(user.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user in database
    user_data = user.model_dump()  # Convert Pydantic model to dictionary
    created_user = User.create(user_data)  # Create user using model class
    
    # Convert ObjectId to string for response
    # MongoDB ObjectId is not JSON serializable, so we convert it to string
    response_data = json.loads(json_util.dumps(created_user.model_dump()))
    if '_id' in response_data:
        response_data["id"] = str(response_data["_id"])  # Add id field with string value
        del response_data["_id"]  # Remove _id field
    
    # Remove password from response for security
    if "password" in response_data:
        del response_data["password"]
    
    # Convert datetime to string for JSON serialization
    if "createdAt" in response_data and isinstance(response_data["createdAt"], dict) and "$date" in response_data["createdAt"]:
        response_data["createdAt"] = response_data["createdAt"]["$date"]
    
    return response_data

@router.get("/users/{username}", response_model=UserResponse)
async def get_user(username: str, db=Depends(get_db_dependency)):
    """
    Get a user by username.
    
    This endpoint:
    1. Looks up the user by username
    2. Returns the user information if found
    3. Returns a 404 error if not found
    
    Args:
        username: Username of the user to retrieve
        db: Database connection from dependency
        
    Returns:
        User information
        
    Raises:
        HTTPException: If user not found
    """
    # Find user by username
    user = User.find_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Convert ObjectId to string for response
    response_data = json.loads(json_util.dumps(user.model_dump()))
    if '_id' in response_data:
        response_data["id"] = str(response_data["_id"])
        del response_data["_id"]
    
    # Remove password from response for security
    if "password" in response_data:
        del response_data["password"]
    
    # Convert datetime to string for JSON serialization
    if "createdAt" in response_data and isinstance(response_data["createdAt"], dict) and "$date" in response_data["createdAt"]:
        response_data["createdAt"] = response_data["createdAt"]["$date"]
    
    return response_data

# Transaction endpoints
@router.post("/transactions", response_model=TransactionResponse)
async def create_transaction(transaction: TransactionCreate, db=Depends(get_db_dependency)):
    """
    Create a new financial transaction.
    
    This endpoint:
    1. Validates the transaction data
    2. Checks if the user exists
    3. Creates the transaction in the database
    4. Returns the created transaction information
    
    Args:
        transaction: Transaction data from request body
        db: Database connection from dependency
        
    Returns:
        Created transaction information
        
    Raises:
        HTTPException: If user not found
    """
    # Check if user exists
    user = User.find_by_username(transaction.userId)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create transaction in database
    transaction_data = transaction.model_dump()
    # Set date to current time if not provided
    if transaction_data.get("date") is None:
        transaction_data["date"] = datetime.now()
    
    # Create transaction using model class
    created_transaction = Transaction.create(transaction_data)
    
    # Convert ObjectId to string for response
    response_data = json.loads(json_util.dumps(created_transaction.model_dump()))
    response_data["id"] = str(response_data["_id"])
    del response_data["_id"]
    
    # Convert datetime to string for JSON serialization
    if "date" in response_data and isinstance(response_data["date"], dict) and "$date" in response_data["date"]:
        response_data["date"] = response_data["date"]["$date"]
    
    return response_data

@router.get("/transactions/user/{user_id}", response_model=List[TransactionResponse])
async def get_user_transactions(user_id: str, db=Depends(get_db_dependency)):
    """
    Get all transactions for a specific user.
    
    This endpoint:
    1. Retrieves all transactions for the specified user
    2. Returns a list of transactions
    
    Args:
        user_id: ID of the user whose transactions to retrieve
        db: Database connection from dependency
        
    Returns:
        List of transactions for the user
    """
    # Find all transactions for the user
    transactions = Transaction.find_by_user(user_id)
    
    # Convert ObjectId to string for response
    response_data = []
    for transaction in transactions:
        # Convert transaction to dictionary and handle MongoDB-specific types
        transaction_dict = json.loads(json_util.dumps(transaction.model_dump()))
        transaction_dict["id"] = str(transaction_dict["_id"])
        del transaction_dict["_id"]
        
        # Convert datetime to string for JSON serialization
        if "date" in transaction_dict and isinstance(transaction_dict["date"], dict) and "$date" in transaction_dict["date"]:
            transaction_dict["date"] = transaction_dict["date"]["$date"]
        
        response_data.append(transaction_dict)
    
    return response_data

# Financial Goal endpoints
@router.post("/goals", response_model=FinancialGoalResponse)
async def create_goal(goal: FinancialGoalCreate, db=Depends(get_db_dependency)):
    """
    Create a new financial goal.
    
    This endpoint:
    1. Validates the goal data
    2. Checks if the user exists
    3. Creates the goal in the database
    4. Returns the created goal information
    
    Args:
        goal: Goal data from request body
        db: Database connection from dependency
        
    Returns:
        Created goal information
        
    Raises:
        HTTPException: If user not found
    """
    # Check if user exists
    user = User.find_by_username(goal.userId)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create goal in database
    goal_data = goal.model_dump()
    created_goal = FinancialGoal.create(goal_data)
    
    # Convert ObjectId to string for response
    response_data = json.loads(json_util.dumps(created_goal.model_dump()))
    response_data["id"] = str(response_data["_id"])
    del response_data["_id"]
    
    # Convert datetime to string for JSON serialization
    if "deadline" in response_data and isinstance(response_data["deadline"], dict) and "$date" in response_data["deadline"]:
        response_data["deadline"] = response_data["deadline"]["$date"]
    
    return response_data

@router.get("/goals/user/{user_id}", response_model=List[FinancialGoalResponse])
async def get_user_goals(user_id: str, db=Depends(get_db_dependency)):
    """
    Get all financial goals for a specific user.
    
    This endpoint:
    1. Retrieves all goals for the specified user
    2. Returns a list of goals
    
    Args:
        user_id: ID of the user whose goals to retrieve
        db: Database connection from dependency
        
    Returns:
        List of financial goals for the user
    """
    # Find all goals for the user
    goals = FinancialGoal.find_by_user(user_id)
    
    # Convert ObjectId to string for response
    response_data = []
    for goal in goals:
        # Convert goal to dictionary and handle MongoDB-specific types
        goal_dict = json.loads(json_util.dumps(goal.model_dump()))
        goal_dict["id"] = str(goal_dict["_id"])
        del goal_dict["_id"]
        
        # Convert datetime to string for JSON serialization
        if "deadline" in goal_dict and isinstance(goal_dict["deadline"], dict) and "$date" in goal_dict["deadline"]:
            goal_dict["deadline"] = goal_dict["deadline"]["$date"]
        
        response_data.append(goal_dict)
    
    return response_data

@router.put("/goals/{goal_id}", response_model=FinancialGoalResponse)
async def update_goal(goal_id: str, goal_update: FinancialGoalUpdate, db=Depends(get_db_dependency)):
    """
    Update a financial goal.
    
    This endpoint:
    1. Validates the update data
    2. Checks if the goal exists
    3. Updates the goal in the database
    4. Returns the updated goal information
    
    Args:
        goal_id: ID of the goal to update
        goal_update: Goal update data from request body
        db: Database connection from dependency
        
    Returns:
        Updated goal information
        
    Raises:
        HTTPException: If goal not found or update fails
    """
    # Check if goal exists
    goal = db["FinancialGoals"].find_one({"_id": ObjectId(goal_id)})
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    # Update goal in database
    # Only include fields that are not None in the update
    update_data = {k: v for k, v in goal_update.model_dump().items() if v is not None}
    success = FinancialGoal.update_goal(goal_id, update_data)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update goal")
    
    # Get updated goal from database
    updated_goal = db["FinancialGoals"].find_one({"_id": ObjectId(goal_id)})
    
    # Convert ObjectId to string for response
    response_data = json.loads(json_util.dumps(updated_goal))
    response_data["id"] = str(response_data["_id"])
    del response_data["_id"]
    
    # Convert datetime to string for JSON serialization
    if "deadline" in response_data and isinstance(response_data["deadline"], dict) and "$date" in response_data["deadline"]:
        response_data["deadline"] = response_data["deadline"]["$date"]
    
    return response_data 