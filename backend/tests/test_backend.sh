#!/bin/bash
# test_backend.sh - Comprehensive Test Script for CougarWise Backend
# This script runs all backend tests, including database, API, and OpenAI integration tests

# Set terminal colors for better readability
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
# Get the backend directory (parent of tests)
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${CYAN}======================================================${NC}"
echo -e "${CYAN}         CougarWise Backend Test Suite                ${NC}"
echo -e "${CYAN}======================================================${NC}"
echo

# Define the Python command to use
if [ -d "$BACKEND_DIR/venv" ]; then
    echo -e "${CYAN}[1/7] Activating virtual environment...${NC}"
    source "$BACKEND_DIR/venv/bin/activate"
    PYTHON_CMD="python"
    echo -e "${GREEN}✓ Virtual environment activated${NC}"
else
    echo -e "${YELLOW}! Virtual environment not found at $BACKEND_DIR/venv${NC}"
    echo -e "${YELLOW}! Using system Python instead${NC}"
    PYTHON_CMD="python3"
fi

# Step 1: Check Python environment and dependencies
echo
echo -e "${CYAN}[2/7] Checking Python environment and dependencies...${NC}"
if command -v $PYTHON_CMD &> /dev/null; then
    echo -e "${GREEN}✓ Python found: $($PYTHON_CMD --version)${NC}"
    
    # Check required packages
    REQUIRED_PACKAGES=("pytest" "fastapi" "pymongo" "uvicorn" "pydantic" "openai" "python-dotenv" "requests")
    MISSING_PACKAGES=()
    
    for package in "${REQUIRED_PACKAGES[@]}"; do
        if ! $PYTHON_CMD -c "import $package" &> /dev/null; then
            MISSING_PACKAGES+=("$package")
        fi
    done
    
    if [ ${#MISSING_PACKAGES[@]} -eq 0 ]; then
        echo -e "${GREEN}✓ All required Python packages are installed${NC}"
    else
        echo -e "${YELLOW}! Some required packages are missing:${NC} ${MISSING_PACKAGES[*]}"
        echo -n "Do you want to install them using the virtual environment? (y/n): "
        read -r install_packages
        
        if [ "$install_packages" = "y" ] || [ "$install_packages" = "Y" ]; then
            # Install the packages using pip in the virtual environment
            $PYTHON_CMD -m pip install ${MISSING_PACKAGES[@]}
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✓ Packages installed successfully${NC}"
            else
                echo -e "${RED}✗ Failed to install packages${NC}"
                echo "Please install them manually using:"
                echo "$PYTHON_CMD -m pip install ${MISSING_PACKAGES[@]}"
            fi
        else
            echo -e "${YELLOW}! Missing packages may cause test failures${NC}"
        fi
    fi
else
    echo -e "${RED}✗ Python not found: $PYTHON_CMD${NC}"
    echo "Please make sure Python is installed and available in your PATH"
    exit 1
fi

# Step 2: Check if backend server is running
echo
echo -e "${CYAN}[3/7] Checking if backend server is running...${NC}"
if nc -z localhost 8000 &> /dev/null; then
    echo -e "${GREEN}✓ Backend server is running on port 8000${NC}"
    BACKEND_RUNNING=true
else
    echo -e "${YELLOW}! Backend server is not running${NC}"
    echo -n "Do you want to start the server in a new terminal? (y/n): "
    read -r start_server
    
    if [ "$start_server" = "y" ] || [ "$start_server" = "Y" ]; then
        # Use start_server.sh if it exists
        if [ -f "$BACKEND_DIR/start_server.sh" ]; then
            echo -e "${GREEN}Using existing start_server.sh script${NC}"
            # Start server in a new terminal and detach
            if [[ "$OSTYPE" == "darwin"* ]]; then
                # macOS
                osascript -e "tell app \"Terminal\" to do script \"cd $BACKEND_DIR && ./start_server.sh\""
            elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
                # Linux
                if command -v gnome-terminal &> /dev/null; then
                    gnome-terminal -- bash -c "cd $BACKEND_DIR && ./start_server.sh; exec bash"
                elif command -v xterm &> /dev/null; then
                    xterm -e "cd $BACKEND_DIR && ./start_server.sh" &
                else
                    echo -e "${YELLOW}! Could not start server automatically. Please start it manually in another terminal:${NC}"
                    echo "cd $BACKEND_DIR && ./start_server.sh"
                    BACKEND_RUNNING=false
                fi
            else
                echo -e "${YELLOW}! Unsupported OS for automatic server start. Please start it manually in another terminal:${NC}"
                echo "cd $BACKEND_DIR && ./start_server.sh"
                BACKEND_RUNNING=false
            fi
        else
            # Start using run.py
            if [[ "$OSTYPE" == "darwin"* ]]; then
                # macOS
                osascript -e "tell app \"Terminal\" to do script \"cd $BACKEND_DIR && $PYTHON_CMD run.py\""
            elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
                # Linux
                if command -v gnome-terminal &> /dev/null; then
                    gnome-terminal -- bash -c "cd $BACKEND_DIR && $PYTHON_CMD run.py; exec bash"
                elif command -v xterm &> /dev/null; then
                    xterm -e "cd $BACKEND_DIR && $PYTHON_CMD run.py" &
                else
                    echo -e "${YELLOW}! Could not start server automatically. Please start it manually in another terminal:${NC}"
                    echo "cd $BACKEND_DIR && $PYTHON_CMD run.py"
                    BACKEND_RUNNING=false
                fi
            else
                echo -e "${YELLOW}! Unsupported OS for automatic server start. Please start it manually in another terminal:${NC}"
                echo "cd $BACKEND_DIR && $PYTHON_CMD run.py"
                BACKEND_RUNNING=false
            fi
        fi
        
        # Wait for server to start
        echo "Waiting for backend server to start..."
        for i in {1..15}; do
            if nc -z localhost 8000 &> /dev/null; then
                echo -e "${GREEN}✓ Backend server started successfully${NC}"
                BACKEND_RUNNING=true
                break
            fi
            sleep 2
        done
        
        if [ "$BACKEND_RUNNING" != true ]; then
            echo -e "${YELLOW}! Backend server did not start in the expected time${NC}"
            echo "You can continue with the tests that don't require a running server"
        fi
    else
        echo -e "${YELLOW}! Some tests will be skipped without a running server${NC}"
        BACKEND_RUNNING=false
    fi
fi

# Step 3: Run database connection tests
echo
echo -e "${CYAN}[4/7] Running database connection tests...${NC}"
$PYTHON_CMD -m pytest "$SCRIPT_DIR/test_database_connection.py" -v
if [ $? -ne 0 ]; then
    echo -e "\n${RED}✗ Database connection tests failed${NC}"
    echo "Please check your MongoDB configuration and make sure MongoDB is running."
    echo "Other tests may fail if database connection is not working."
else
    echo -e "\n${GREEN}✓ Database connection tests passed${NC}"
fi

# Step 4: Run database model tests
echo
echo -e "${CYAN}[5/7] Running database model tests...${NC}"
$PYTHON_CMD -m pytest "$SCRIPT_DIR/test_database_models.py" -v
if [ $? -ne 0 ]; then
    echo -e "\n${YELLOW}! Some database model tests failed${NC}"
    echo "This may indicate issues with the database schema or model implementation."
else
    echo -e "\n${GREEN}✓ Database model tests passed${NC}"
fi

# Step 5: Run API endpoint tests if server is running
echo
echo -e "${CYAN}[6/7] Running API endpoint tests...${NC}"
if [ "$BACKEND_RUNNING" = true ]; then
    # First run the pytest API tests
    echo -e "${CYAN}[6.1/7] Running API endpoint pytest tests...${NC}"
    $PYTHON_CMD -m pytest "$SCRIPT_DIR/test_api_endpoints.py" -v
    API_TEST_RESULT=$?
    
    if [ $API_TEST_RESULT -ne 0 ]; then
        echo -e "\n${YELLOW}! Some API endpoint tests failed${NC}"
        echo "This may indicate issues with the API implementation or server configuration."
    else
        echo -e "\n${GREEN}✓ API endpoint tests passed${NC}"
    fi
    
    # Run signup endpoint tests
    echo -e "${CYAN}[6.2/7] Running signup endpoint tests...${NC}"
    $PYTHON_CMD -m pytest "$SCRIPT_DIR/test_signup_endpoint.py" -v
    
    # Run API endpoint curl tests
    echo -e "${CYAN}[6.3/7] Running API curl tests...${NC}"
    bash "$SCRIPT_DIR/test_api_curl.sh"
else
    echo -e "${YELLOW}! Skipping API endpoint tests because server is not running${NC}"
fi

# Step 6: Run OpenAI integration tests
echo
echo -e "${CYAN}[7/7] Running OpenAI integration tests...${NC}"
# First check for OpenAI API key
if [ -f "$BACKEND_DIR/.env" ] && grep -q "OPENAI_API_KEY" "$BACKEND_DIR/.env"; then
    echo -e "${GREEN}✓ OpenAI API key found in .env file${NC}"
    
    # Run the direct OpenAI tests
    echo -e "${CYAN}[7.1/7] Running direct OpenAI API tests...${NC}"
    $PYTHON_CMD "$SCRIPT_DIR/test_openai_direct.py"
    DIRECT_TEST_RESULT=$?
    
    # Run AI component tests
    echo
    echo -e "${CYAN}[7.2/7] Running AI component tests...${NC}"
    $PYTHON_CMD -m pytest "$SCRIPT_DIR/test_ai_components.py::TestOpenAIIntegration" -v
    COMPONENT_TEST_RESULT=$?
    
    # Run AI API endpoint tests if server is running
    if [ "$BACKEND_RUNNING" = true ]; then
        echo
        echo -e "${CYAN}[7.3/7] Running AI API endpoint tests...${NC}"
        $PYTHON_CMD -m pytest "$SCRIPT_DIR/test_ai_api_endpoints.py::TestOpenAIConfigBehavior" -v
        AI_API_TEST_RESULT=$?
    else
        echo -e "${YELLOW}! Skipping AI API endpoint tests because server is not running${NC}"
        AI_API_TEST_RESULT=0  # Skip this test if server is not running
    fi
    
    # Display results
    echo
    echo -e "${CYAN}OpenAI Integration Test Results:${NC}"
    echo -e "Direct API Tests: $(if [ $DIRECT_TEST_RESULT -eq 0 ]; then echo -e "${GREEN}PASSED${NC}"; else echo -e "${RED}FAILED${NC}"; fi)"
    echo -e "Component Tests: $(if [ $COMPONENT_TEST_RESULT -eq 0 ]; then echo -e "${GREEN}PASSED${NC}"; else echo -e "${RED}FAILED${NC}"; fi)"
    if [ "$BACKEND_RUNNING" = true ]; then
        echo -e "API Endpoint Tests: $(if [ $AI_API_TEST_RESULT -eq 0 ]; then echo -e "${GREEN}PASSED${NC}"; else echo -e "${RED}FAILED${NC}"; fi)"
    else
        echo -e "API Endpoint Tests: ${YELLOW}SKIPPED${NC}"
    fi
else
    echo -e "${YELLOW}! OpenAI API key not found in .env file${NC}"
    echo "OpenAI integration tests will be skipped."
    echo "To run OpenAI tests, add your OpenAI API key to $BACKEND_DIR/.env as OPENAI_API_KEY=your_key"
fi

# Summary
echo
echo -e "${CYAN}======================================================${NC}"
echo -e "${CYAN}          Backend Test Suite Results                  ${NC}"
echo -e "${CYAN}======================================================${NC}"
echo

# Try to count total tests run and passed
echo -e "${CYAN}Collecting test statistics...${NC}"
$PYTHON_CMD -m pytest "$SCRIPT_DIR" --collect-only -q > /dev/null 2>&1
if [ $? -eq 0 ]; then
    TOTAL_TESTS=$($PYTHON_CMD -m pytest "$SCRIPT_DIR" --collect-only -q | wc -l)
    # Run the tests quietly and count passed tests
    $PYTHON_CMD -m pytest "$SCRIPT_DIR" -v > pytest_output.txt 2>&1
    TESTS_PASSED=$(grep "PASSED" pytest_output.txt | wc -l)
    rm pytest_output.txt
    
    # Display summary
    echo -e "Total Tests: $TOTAL_TESTS"
    echo -e "Tests Passed: $TESTS_PASSED"
    echo
    
    if [ $TOTAL_TESTS -eq $TESTS_PASSED ]; then
        echo -e "${GREEN}✅ ALL TESTS PASSED: The CougarWise backend is working correctly!${NC}"
        exit 0
    else
        echo -e "${YELLOW}⚠️ SOME TESTS FAILED: There are issues with the CougarWise backend.${NC}"
        echo "Review the failed tests and fix the issues in your code."
        exit 1
    fi
else
    echo -e "${YELLOW}! Could not collect test statistics${NC}"
    echo "Review the test outputs above to see which tests passed or failed."
    exit 1
fi 