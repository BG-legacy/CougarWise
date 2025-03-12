"""
Database connection module for CougarWise backend.
This module provides a MongoDB connection and database access for the application.

Key components:
- Database class: Singleton pattern for managing MongoDB connections
- Collections class: Constants for collection names
- Helper functions: Simplified access to database and collections
"""
import os  # For accessing environment variables
from pymongo import MongoClient  # MongoDB client library
from dotenv import load_dotenv  # For loading environment variables from .env file
import logging  # For logging database operations and errors
from typing import Optional  # Type hints for better code documentation

# Configure logging to track database operations and errors
# This helps with debugging and monitoring the application
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)  # Get a logger for this module

# Load environment variables from .env file
# This allows configuration without changing code
load_dotenv()

# MongoDB connection details from environment variables
# Default values are provided as fallbacks if environment variables are not set
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')  # MongoDB connection string
MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'cougarwise')  # Database name

class Database:
    """
    Database connection manager for CougarWise application.
    
    This class implements the Singleton pattern to ensure only one database
    connection is maintained throughout the application. This helps with
    performance and resource management.
    
    Key features:
    - Automatic connection management
    - Support for switching databases (useful for testing)
    - Collection access
    - Connection cleanup
    """
    
    # Singleton instance and connection variables
    _instance = None  # Single instance of the Database class
    _client = None  # MongoDB client connection
    _db = None  # Database reference
    
    @classmethod
    def get_instance(cls):
        """
        Singleton pattern to ensure only one database connection is created.
        
        This method returns the existing Database instance if one exists,
        or creates a new instance if none exists yet.
        
        Returns:
            Database: The singleton Database instance
        """
        if cls._instance is None:
            cls._instance = Database()  # Create new instance if none exists
        return cls._instance
    
    def __init__(self):
        """
        Initialize the database connection.
        
        This constructor is private and should not be called directly.
        Use get_instance() instead to get the singleton instance.
        
        Raises:
            RuntimeError: If constructor is called directly instead of get_instance()
        """
        if Database._instance is not None:
            raise RuntimeError("Use get_instance() instead of constructor")
        self.connect()  # Establish database connection
    
    def connect(self):
        """
        Connect to the MongoDB database.
        
        This method:
        1. Gets the database name from environment variables
        2. Creates a MongoDB client connection
        3. Gets a reference to the specified database
        4. Logs available collections
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Get the database name from environment variable (may be updated by tests)
            db_name = os.getenv('MONGODB_DB_NAME', MONGODB_DB_NAME)
            
            # Log connection attempt
            logger.info(f"Connecting to MongoDB at {MONGODB_URI}")
            
            # Create MongoDB client with TLS settings
            # TLS (Transport Layer Security) encrypts the connection
            # tlsAllowInvalidCertificates=True allows self-signed certificates (not recommended for production)
            self._client = MongoClient(MONGODB_URI, 
                                      tls=True, 
                                      tlsAllowInvalidCertificates=True)
            
            # Get reference to the specified database
            self._db = self._client[db_name]
            logger.info(f"Connected to database: {db_name}")
            
            # Log available collections for debugging
            collections = self._db.list_collection_names()
            logger.info(f"Available collections: {collections}")
            
            return True
        except Exception as e:
            # Log any connection errors
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            return False
    
    def get_db(self):
        """
        Get the database instance.
        
        This method:
        1. Connects to the database if not already connected
        2. Checks if the database name has changed (useful for testing)
        3. Returns the database reference
        
        Returns:
            pymongo.database.Database: The MongoDB database instance
        """
        if self._db is None:
            # Connect if not already connected
            self.connect()
        else:
            # Check if the database name has changed (for tests)
            # This allows tests to use a different database without restarting the application
            db_name = os.getenv('MONGODB_DB_NAME', MONGODB_DB_NAME)
            if self._db.name != db_name:
                # Switch to the new database
                self._db = self._client[db_name]
                logger.info(f"Switched to database: {db_name}")
        return self._db
    
    def get_collection(self, collection_name: str):
        """
        Get a specific collection from the database.
        
        Collections in MongoDB are similar to tables in relational databases.
        This method ensures we're connected before accessing a collection.
        
        Args:
            collection_name (str): Name of the collection to retrieve
            
        Returns:
            pymongo.collection.Collection: The specified MongoDB collection
        """
        if self._db is None:
            # Connect if not already connected
            self.connect()
        return self._db[collection_name]
    
    def close(self):
        """
        Close the database connection.
        
        This method:
        1. Closes the MongoDB client connection if it exists
        2. Logs the closure
        3. Resets the client and database references
        
        This helps free up resources when the application is shutting down.
        """
        if self._client:
            self._client.close()
            logger.info("Database connection closed")
            self._client = None
            self._db = None

# Collection names
class Collections:
    """
    Collection names for the CougarWise database.
    
    This class provides constants for collection names to ensure consistency
    throughout the application. Using these constants instead of hardcoded strings
    helps prevent typos and makes it easier to rename collections if needed.
    
    Each constant represents a different type of data stored in the database.
    """
    USERS = "Users"  # User accounts and profiles
    TRANSACTIONS = "Transactions"  # Financial transactions
    FINANCIAL_GOALS = "FinancialGoals"  # Savings goals and targets
    CATEGORY_BREAKDOWN = "CategoryBreakdown"  # Spending by category
    RECOMMENDATIONS = "Recommendations"  # Financial advice and recommendations
    NOTIFICATIONS = "Notifications"  # User notifications
    SPENDING_ANALYSIS = "SpendingAnalysis"  # Spending pattern analysis
    CHATBOT = "Chatbot"  # Chatbot conversation history

# Helper functions for common database operations
# These functions simplify database access throughout the application

def get_db():
    """
    Get the database instance.
    
    This helper function provides a simplified way to access the database
    without directly interacting with the Database class.
    
    Returns:
        pymongo.database.Database: The MongoDB database instance
    """
    return Database.get_instance().get_db()

def get_collection(collection_name: str):
    """
    Get a specific collection from the database.
    
    This helper function provides a simplified way to access a collection
    without directly interacting with the Database class.
    
    Args:
        collection_name (str): Name of the collection to retrieve
        
    Returns:
        pymongo.collection.Collection: The specified MongoDB collection
    """
    return Database.get_instance().get_collection(collection_name)

def close_db_connection():
    """
    Close the database connection.
    
    This helper function provides a simplified way to close the database connection
    without directly interacting with the Database class.
    
    This should be called when the application is shutting down to free up resources.
    """
    Database.get_instance().close() 