#!/usr/bin/env python3
"""
Python script for testing the CougarWise API.
This script uses the requests library to test various API endpoints.
"""
import requests
import json
import sys
import os
from datetime import datetime

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

# Base URL for the API
BASE_URL = "http://localhost:8000"

# ANSI colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_response(response):
    """Print a formatted API response"""
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    print()

def test_endpoint(name, method, endpoint, data=None, params=None):
    """Test an API endpoint and print the result"""
    url = f"{BASE_URL}{endpoint}"
    print(f"{BLUE}Testing: {name}{RESET}")
    print(f"URL: {url}")
    print(f"Method: {method}")
    
    if data:
        print(f"Data: {json.dumps(data, indent=2)}")
    
    if params:
        print(f"Params: {params}")
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, params=params)
        elif method.upper() == "POST":
            response = requests.post(url, json=data)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url)
        else:
            print(f"{RED}Unsupported method: {method}{RESET}")
            return None
        
        print_response(response)
        return response
    except Exception as e:
        print(f"{RED}Error: {str(e)}{RESET}")
        return None

def main():
    """Main test function"""
    print(f"{BLUE}CougarWise API Test Script{RESET}")
    print("============================")
    print()
    
    # Test root endpoint
    test_endpoint("Root Endpoint", "GET", "/")
    
    # Test user registration
    register_data = {
        "username": f"testuser_{int(datetime.now().timestamp())}",  # Unique username
        "email": f"test_{int(datetime.now().timestamp())}@example.com",  # Unique email
        "password": "password123",
        "name": "Test User"
    }
    register_response = test_endpoint("User Registration", "POST", "/api/auth/register", register_data)
    
    if not register_response or not register_response.json().get("success", False):
        print(f"{RED}Registration failed. Cannot continue with user-specific tests.{RESET}")
        return
    
    # Get user ID from registration response
    user_id = register_response.json().get("user_id")
    username = register_response.json().get("username")
    
    # Test user login
    login_data = {
        "username": username,
        "password": "password123"
    }
    login_response = test_endpoint("User Login", "POST", "/api/auth/login", login_data)
    
    # Test creating a transaction
    transaction_data = {
        "user_id": user_id,
        "amount": -50.00,
        "category": "Food",
        "description": "Grocery shopping"
    }
    transaction_response = test_endpoint("Create Transaction", "POST", "/api/transactions", transaction_data)
    
    # Test getting user transactions
    test_endpoint("Get User Transactions", "GET", f"/api/transactions/user/{user_id}")
    
    # Test creating a budget
    budget_data = {
        "user_id": user_id,
        "category": "Food",
        "amount": 300.00,
        "period": "monthly"
    }
    budget_response = test_endpoint("Create Budget", "POST", "/api/budgets", budget_data)
    
    # Test getting user budgets
    test_endpoint("Get User Budgets", "GET", f"/api/budgets/user/{user_id}")
    
    # Test getting spending analysis
    test_endpoint("Get Spending Analysis", "GET", f"/api/analysis/spending/{user_id}", params={"period": "monthly"})
    
    # Test getting spending insights
    test_endpoint("Get Spending Insights", "GET", f"/api/analysis/insights/{user_id}")
    
    # Test AI query endpoint
    ai_query_data = {
        "query": "How can I save money on groceries?",
        "user_context": {
            "year_in_school": "Sophomore"
        }
    }
    test_endpoint("AI Query", "POST", "/ai/query", ai_query_data)
    
    print(f"{GREEN}All tests completed!{RESET}")

if __name__ == "__main__":
    main() 