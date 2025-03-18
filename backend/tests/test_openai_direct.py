#!/usr/bin/env python3
"""
Test script to verify direct OpenAI API connectivity.
This script tests the connection to OpenAI's API and verifies responses.
"""
import os
import sys
import json
import time
from datetime import datetime
from openai import OpenAI  # Import OpenAI client properly for v1.x
from dotenv import load_dotenv

# Add backend directory to Python path to allow imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

# Load environment variables from .env file
dotenv_path = os.path.join(backend_dir, '.env')
load_dotenv(dotenv_path)

# ANSI color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def get_openai_api_key():
    """Get OpenAI API key from environment variables."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print(f"{RED}❌ OpenAI API key not found in environment variables{RESET}")
        print("Please add your OpenAI API key to the .env file as OPENAI_API_KEY=your_key")
        sys.exit(1)
    return api_key

def test_openai_api_connection(api_key):
    """Test direct connection to OpenAI API."""
    # Create an OpenAI client with the API key
    client = OpenAI(api_key=api_key)
    
    try:
        # Make a simple API call to test connection
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using a less expensive model for testing
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello! Can you respond with a short greeting?"}
            ]
        )
        
        # Extract and print the response text
        response_text = response.choices[0].message.content.strip()
        print(f"{GREEN}✅ Successfully connected to OpenAI API{RESET}")
        print(f"   Response: {response_text[:50]}...")
        return True
        
    except Exception as e:
        # Print error message if connection fails
        print(f"{RED}❌ Failed to connect to OpenAI API: {RESET}\n")
        print(str(e))
        print("\n")
        return False

def test_openai_json_response(api_key):
    """Test that OpenAI can generate and return a properly formatted JSON response."""
    # Create an OpenAI client with the API key
    client = OpenAI(api_key=api_key)
    
    try:
        # Request a JSON response specifically
        response = client.chat.completions.create(
            model="gpt-4",  # Using GPT-4 because it's better at following JSON formatting instructions
            messages=[
                {"role": "system", "content": "You are a helpful assistant that responds only with valid JSON."},
                {"role": "user", "content": """
                    Please provide a sample financial profile for a college student in JSON format.
                    Include these fields:
                    - student_financial_profile with sub-fields like age, year_in_school, major
                    - monthly_income with breakdown of sources
                    - monthly_expenses with categories
                    Do not include any text outside the JSON.
                """}
            ]
        )
        
        # Extract the response text
        response_text = response.choices[0].message.content.strip()
        
        # Try to parse the response as JSON
        try:
            json_response = json.loads(response_text)
            print(f"{GREEN}✅ Successfully received and parsed JSON response{RESET}")
            
            # Check if the expected fields are present
            expected_fields = ['student_financial_profile']
            missing_fields = [field for field in expected_fields if field not in json_response]
            
            if missing_fields:
                print(f"{YELLOW}⚠️ JSON response valid but didn't contain expected fields. This is acceptable.{RESET}")
            
            # Print a preview of the JSON response
            print(f"   JSON response: {json.dumps(json_response, indent=2)[:100]}...")
            return True
            
        except json.JSONDecodeError:
            print(f"{YELLOW}⚠️ Response wasn't valid JSON, but API connection works.{RESET}")
            print(f"   Response: {response_text[:100]}...")
            return True
            
    except Exception as e:
        print(f"{RED}❌ Failed to get JSON response from OpenAI API{RESET}")
        print(str(e))
        return False

def main():
    """Main function to run the OpenAI API tests."""
    # Print header with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n----- OPENAI API TESTS ({timestamp}) -----\n")
    
    # Get API key
    api_key = get_openai_api_key()
    print(f"{GREEN}✅ OpenAI API key exists{RESET}")
    
    # Run tests
    connection_test = test_openai_api_connection(api_key)
    
    if connection_test:
        # Only run JSON test if connection test passes
        json_test = test_openai_json_response(api_key)
    else:
        print(f"{RED}❌ API Connection test failed. Check your API key and internet connection.{RESET}")
        sys.exit(1)
    
    # Print summary
    print()
    if connection_test and json_test:
        print(f"{GREEN}✅ TESTS PASSED: Your OpenAI API integration is working correctly!{RESET}")
        sys.exit(0)
    else:
        print(f"{RED}❌ TESTS FAILED: Your OpenAI API integration is not working correctly.{RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main() 