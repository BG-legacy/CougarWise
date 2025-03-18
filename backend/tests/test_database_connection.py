"""
Tests for the database connection.
"""
import pytest
from pymongo import MongoClient

from Database.database import Database, get_db, get_collection, Collections, close_db_connection

class TestDatabaseConnection:
    """Tests for the database connection."""
    
    def test_singleton_pattern(self):
        """Test that the Database class follows the singleton pattern."""
        # Get instance
        db1 = Database.get_instance()
        db2 = Database.get_instance()
        
        # Check that they are the same instance
        assert db1 is db2
    
    def test_get_db(self):
        """Test getting the database."""
        # Get database
        db = get_db()
        
        # Check database
        assert db is not None
        assert db.name == "CougarWise"
    
    def test_get_collection(self):
        """Test getting a collection."""
        # Get collection
        collection = get_collection(Collections.USERS)
        
        # Check collection
        assert collection is not None
        assert collection.name == Collections.USERS
    
    def test_close_connection(self):
        """Test closing the database connection."""
        # Get database
        db_instance = Database.get_instance()
        
        # Close connection
        close_db_connection()
        
        # Check connection is closed
        assert db_instance._client is None
        assert db_instance._db is None
    
    def test_reconnect_after_close(self):
        """Test reconnecting after closing the connection."""
        # Close connection
        close_db_connection()
        
        # Get database again
        db = get_db()
        
        # Check database
        assert db is not None
        assert db.name == "CougarWise" 