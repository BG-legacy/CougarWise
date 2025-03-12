#!/bin/bash
# Script to start the CougarWise backend server

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting CougarWise Backend Server${NC}"
echo "======================================"

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source venv/bin/activate
else
    echo -e "${GREEN}Creating virtual environment...${NC}"
    python -m venv venv
    source venv/bin/activate
    echo -e "${GREEN}Installing dependencies...${NC}"
    pip install -r requirements.txt
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${GREEN}Creating .env file from example...${NC}"
    cp .env.example .env
    echo "Please edit the .env file with your actual values, especially the OpenAI API key."
fi

# Start the server
echo -e "${GREEN}Starting the API server...${NC}"
python run.py 