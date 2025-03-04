import uvicorn
import os
import sys
from dotenv import load_dotenv

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Load environment variables
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(backend_dir, '.env')
load_dotenv(dotenv_path)

# Get port from environment or use default
port = int(os.getenv('API_PORT', 8000))

if __name__ == "__main__":
    print(f"Starting CougarWise API server on port {port}...")
    uvicorn.run("API:app", host="0.0.0.0", port=port, reload=True)
    print("Server started successfully!") 