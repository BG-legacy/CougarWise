"""
Database models for CougarWise backend.
This module provides database models for the application.

Key components:
- PyObjectId: Custom ObjectId type for Pydantic models
- MongoBaseModel: Base model with MongoDB integration
- User: Model for user accounts and profiles
- Transaction: Model for financial transactions
- FinancialGoal: Model for savings goals and targets
"""
from datetime import datetime  # For handling dates and times
from typing import Dict, List, Optional, Any, Union  # Type hints for better code documentation
from bson import ObjectId  # MongoDB's unique identifier type
from pydantic import BaseModel, Field, validator  # For data validation and settings management
from .database import get_collection, Collections  # Database connection utilities

class PyObjectId(ObjectId):
    """
    Custom ObjectId type for Pydantic models.
    
    This class extends MongoDB's ObjectId to make it compatible with Pydantic models.
    It provides validation and serialization methods to handle ObjectId properly
    in request/response models.
    
    This is necessary because MongoDB uses ObjectId for document IDs, but these
    are not directly compatible with JSON serialization used by FastAPI.
    """
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        """
        Return a schema dict for the ObjectId type for Pydantic v2.
        
        This method is called by Pydantic during model creation to understand
        how to validate and serialize this custom type.
        
        Args:
            _source_type: The source type
            _handler: The schema handler
            
        Returns:
            A schema dict for the ObjectId type
        """
        from pydantic_core import core_schema
        
        return core_schema.union_schema(
            [
                # Accept existing ObjectId instances directly
                core_schema.is_instance_schema(ObjectId),
                # Or convert strings to ObjectId through validation
                core_schema.chain_schema(
                    [
                        core_schema.str_schema(),
                        core_schema.no_info_plain_validator_function(cls.validate),
                    ]
                ),
            ]
        )
    
    @classmethod
    def validate(cls, v, info=None):
        """
        Validate the ObjectId.
        
        This method checks if a string is a valid ObjectId and converts it
        to an ObjectId instance if it is.
        
        Args:
            v: The value to validate
            info: Additional validation information
            
        Returns:
            ObjectId: The validated ObjectId
            
        Raises:
            ValueError: If the value is not a valid ObjectId
        """
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    
    @classmethod
    def __get_pydantic_json_schema__(cls, _schema_generator):
        """
        Return a schema dict for the ObjectId type for Pydantic v2.
        
        This method defines how the ObjectId should be represented in JSON schema,
        which is used for API documentation.
        
        Args:
            _schema_generator: The schema generator
            
        Returns:
            Dict: A schema dict for the ObjectId type
        """
        return {"type": "string"}

# Base model for MongoDB documents
class MongoBaseModel(BaseModel):
    """
    Base model for MongoDB documents.
    
    This class provides common functionality for all MongoDB document models:
    - ID field handling (converting between MongoDB's _id and Pydantic's id)
    - Configuration for MongoDB types
    - JSON serialization for MongoDB-specific types
    
    All other models inherit from this base class to ensure consistent behavior.
    """
    id: Optional[PyObjectId] = Field(alias="_id", default=None)  # MongoDB document ID
    
    # Pydantic model configuration
    model_config = {
        "populate_by_name": True,  # Allow populating by field name or alias
        "arbitrary_types_allowed": True,  # Allow custom types like ObjectId
        "json_encoders": {
            ObjectId: str,  # Convert ObjectId to string for JSON
            datetime: lambda dt: dt.isoformat()  # Convert datetime to ISO format string
        }
    }
    
    def model_dump(self, **kwargs):
        """
        Override model_dump to preserve _id field.
        
        This method ensures that the MongoDB _id field is included in the
        dictionary representation of the model, which is important for
        database operations.
        
        Args:
            **kwargs: Additional arguments for model_dump
            
        Returns:
            Dict: Dictionary representation of the model
        """
        exclude = kwargs.pop('exclude', set())
        data = super().model_dump(**kwargs)
        # Ensure _id is included in the output
        if self.id is not None and '_id' not in data:
            data['_id'] = self.id
        return data

# User model
class User(MongoBaseModel):
    """
    User model for the application.
    
    This model represents a user account in the CougarWise application.
    It includes personal information, authentication details, and methods
    for user-related database operations.
    
    Fields:
    - username: Unique identifier for the user
    - email: User's email address
    - password: User's password (should be hashed)
    - name: User's full name
    - createdAt: When the user account was created
    """
    username: str  # Unique username for the user
    email: str  # User's email address
    password: str  # User's password (should be hashed for security)
    name: str  # User's full name
    createdAt: datetime = Field(default_factory=datetime.now)  # Account creation timestamp
    
    @classmethod
    def create(cls, user_data: Dict) -> 'User':
        """
        Create a new user in the database.
        
        This method:
        1. Takes user data as a dictionary
        2. Inserts it into the Users collection
        3. Returns a User model instance with the inserted data
        
        Args:
            user_data (Dict): Dictionary containing user information
            
        Returns:
            User: The created user model instance
        """
        collection = get_collection(Collections.USERS)
        result = collection.insert_one(user_data)
        user_data["_id"] = result.inserted_id  # Add the generated ID to the data
        return cls(**user_data)  # Create a User instance with the data
    
    @classmethod
    def find_by_username(cls, username: str) -> Optional['User']:
        """
        Find a user by username.
        
        This method:
        1. Searches the Users collection for a user with the given username
        2. Returns a User model instance if found, None otherwise
        
        Args:
            username (str): The username to search for
            
        Returns:
            Optional[User]: The found user or None
        """
        collection = get_collection(Collections.USERS)
        user_data = collection.find_one({"username": username})
        if user_data:
            return cls(**user_data)  # Create a User instance with the found data
        return None
    
    @classmethod
    def find_by_email(cls, email: str) -> Optional['User']:
        """
        Find a user by email.
        
        This method:
        1. Searches the Users collection for a user with the given email
        2. Returns a User model instance if found, None otherwise
        
        Args:
            email (str): The email to search for
            
        Returns:
            Optional[User]: The found user or None
        """
        collection = get_collection(Collections.USERS)
        user_data = collection.find_one({"email": email})
        if user_data:
            return cls(**user_data)  # Create a User instance with the found data
        return None

# Transaction model
class Transaction(MongoBaseModel):
    """
    Transaction model for the application.
    
    This model represents a financial transaction in the CougarWise application.
    It includes details about the transaction amount, category, and user.
    
    Fields:
    - userId: ID of the user who made the transaction
    - amount: Amount of money involved in the transaction
    - category: Category of the transaction (e.g., Food, Housing)
    - description: Description of the transaction
    - date: When the transaction occurred
    """
    userId: str  # ID of the user who made the transaction
    amount: float  # Amount of money involved (positive for income, negative for expense)
    category: str  # Category of the transaction (e.g., Food, Housing)
    description: str  # Description of what the transaction was for
    date: datetime = Field(default_factory=datetime.now)  # When the transaction occurred
    
    @classmethod
    def create(cls, transaction_data: Dict) -> 'Transaction':
        """
        Create a new transaction in the database.
        
        This method:
        1. Takes transaction data as a dictionary
        2. Inserts it into the Transactions collection
        3. Returns a Transaction model instance with the inserted data
        
        Args:
            transaction_data (Dict): Dictionary containing transaction information
            
        Returns:
            Transaction: The created transaction model instance
        """
        collection = get_collection(Collections.TRANSACTIONS)
        result = collection.insert_one(transaction_data)
        transaction_data["_id"] = result.inserted_id  # Add the generated ID to the data
        return cls(**transaction_data)  # Create a Transaction instance with the data
    
    @classmethod
    def find_by_user(cls, user_id: str) -> List['Transaction']:
        """
        Find all transactions for a user.
        
        This method:
        1. Searches the Transactions collection for all transactions with the given user ID
        2. Returns a list of Transaction model instances
        
        Args:
            user_id (str): The ID of the user whose transactions to find
            
        Returns:
            List[Transaction]: List of transactions for the user
        """
        collection = get_collection(Collections.TRANSACTIONS)
        transactions = collection.find({"userId": user_id})
        return [cls(**transaction) for transaction in transactions]  # Create Transaction instances for each result
    
    @classmethod
    def find_by_category(cls, user_id: str, category: str) -> List['Transaction']:
        """
        Find all transactions for a user in a specific category.
        
        This method:
        1. Searches the Transactions collection for transactions with the given user ID and category
        2. Returns a list of Transaction model instances
        
        Args:
            user_id (str): The ID of the user whose transactions to find
            category (str): The category to filter by
            
        Returns:
            List[Transaction]: List of transactions for the user in the specified category
        """
        collection = get_collection(Collections.TRANSACTIONS)
        transactions = collection.find({"userId": user_id, "category": category})
        return [cls(**transaction) for transaction in transactions]  # Create Transaction instances for each result

# Financial Goal model
class FinancialGoal(MongoBaseModel):
    """
    Financial Goal model for the application.
    
    This model represents a financial goal in the CougarWise application.
    It includes details about the goal amount, progress, and deadline.
    
    Fields:
    - userId: ID of the user who created the goal
    - targetAmount: Target amount to save/earn
    - currentAmount: Current progress towards the goal
    - category: Category of the goal (e.g., Emergency Fund, Vacation)
    - deadline: Deadline for achieving the goal
    """
    userId: str  # ID of the user who created the goal
    targetAmount: float  # Target amount to save/earn
    currentAmount: float  # Current progress towards the goal
    category: str  # Category of the goal (e.g., Emergency Fund, Vacation)
    deadline: datetime  # Deadline for achieving the goal
    
    @classmethod
    def create(cls, goal_data: Dict) -> 'FinancialGoal':
        """
        Create a new financial goal in the database.
        
        This method:
        1. Takes goal data as a dictionary
        2. Inserts it into the FinancialGoals collection
        3. Returns a FinancialGoal model instance with the inserted data
        
        Args:
            goal_data (Dict): Dictionary containing goal information
            
        Returns:
            FinancialGoal: The created financial goal model instance
        """
        collection = get_collection(Collections.FINANCIAL_GOALS)
        result = collection.insert_one(goal_data)
        goal_data["_id"] = result.inserted_id  # Add the generated ID to the data
        return cls(**goal_data)  # Create a FinancialGoal instance with the data
    
    @classmethod
    def find_by_user(cls, user_id: str) -> List['FinancialGoal']:
        """
        Find all financial goals for a user.
        
        This method:
        1. Searches the FinancialGoals collection for all goals with the given user ID
        2. Returns a list of FinancialGoal model instances
        
        Args:
            user_id (str): The ID of the user whose goals to find
            
        Returns:
            List[FinancialGoal]: List of financial goals for the user
        """
        collection = get_collection(Collections.FINANCIAL_GOALS)
        goals = collection.find({"userId": user_id})
        return [cls(**goal) for goal in goals]  # Create FinancialGoal instances for each result
    
    @classmethod
    def update_goal(cls, goal_id: str, update_data: Dict) -> bool:
        """
        Update a financial goal.
        
        This method:
        1. Takes goal ID and update data
        2. Updates the goal in the FinancialGoals collection
        3. Returns whether the update was successful
        
        Args:
            goal_id (str): The ID of the goal to update
            update_data (Dict): Dictionary containing fields to update
            
        Returns:
            bool: True if the update was successful, False otherwise
        """
        collection = get_collection(Collections.FINANCIAL_GOALS)
        result = collection.update_one(
            {"_id": ObjectId(goal_id)},  # Find the goal by ID
            {"$set": update_data}  # Update the specified fields
        )
        return result.modified_count > 0  # Return True if at least one document was modified 