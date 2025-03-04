#!/usr/bin/env python3
"""
Main entry point for the CougarWise backend.
This script sets up the Python path correctly and runs the API server.
"""
import os
import sys
import uvicorn
from dotenv import load_dotenv

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

# Load environment variables
dotenv_path = os.path.join(backend_dir, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    print("Warning: .env file not found. Using default values.")
    print(f"Expected location: {dotenv_path}")
    print("You can copy .env.example to .env and fill in your values.")

# Get port from environment or use default
port = int(os.getenv('API_PORT', 8000))

if __name__ == "__main__":
    print(f"Starting CougarWise API server on port {port}...")
    print(f"Python path: {sys.path}")
    uvicorn.run("api.API:app", host="0.0.0.0", port=port, reload=True) 