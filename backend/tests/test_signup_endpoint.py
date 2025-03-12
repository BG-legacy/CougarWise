"""
Tests for the signup endpoint.
"""
import pytest
from bson import ObjectId
from datetime import datetime

from tests.conftest import create_test_user
from Database.database import Collections

class TestSignupEndpoint:
    """Tests for the signup endpoint."""
    
    def test_signup(self, client, db):
        """Test signing up a new user."""
        # First, make sure the user doesn't exist
        email = "newuser@example.com"
        username = "newuser"
        firstname = "New"
        lastname = "User"
        
        # Delete the user if it exists
        db[Collections.USERS].delete_many({"email": email})
        
        # Signup
        response = client.post(f"/signup/{email}/{username}/{firstname}/{lastname}")
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == email
        assert data["username"] == username
        assert data["firstname"] == firstname
        assert data["lastname"] == lastname
        
        # Check user was created in database
        user = db[Collections.USERS].find_one({"email": email})
        assert user is not None
    
    def test_signup_existing_user(self, client, db):
        """Test signing up a user that already exists."""
        # Create user
        email = "test@example.com"
        username = "testuser"
        firstname = "Test"
        lastname = "User"
        db[Collections.USERS].insert_one({
            "email": email,
            "username": username,
            "name": "Test User",
            "password": "hashedpassword123"
        })
        
        # Signup
        response = client.post(f"/signup/{email}/{username}/{firstname}/{lastname}")
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Customer Exists"
        assert "detail" in data 