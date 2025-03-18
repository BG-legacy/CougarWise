#!/bin/bash
# Test script for OpenAI integration in CougarWise
# This script runs all OpenAI-related tests to verify the functionality

# Set terminal colors for better readability
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
# Get the backend directory (parent of tests)
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${CYAN}======================================================${NC}"
echo -e "${CYAN}       CougarWise OpenAI Integration Tests           ${NC}"
echo -e "${CYAN}======================================================${NC}"
echo

# Step 1: Check if OpenAI API key exists
echo -e "${CYAN}[1/5] Checking OpenAI API Key...${NC}"
if [ -f "$BACKEND_DIR/.env" ]; then
    if grep -q "OPENAI_API_KEY" "$BACKEND_DIR/.env"; then
        echo -e "${GREEN}✓ OpenAI API key found in .env file${NC}"
    else
        echo -e "${RED}✗ OpenAI API key not found in .env file${NC}"
        echo "Please add your OpenAI API key to $BACKEND_DIR/.env as OPENAI_API_KEY=your_key"
        exit 1
    fi
else
    echo -e "${RED}✗ .env file not found${NC}"
    echo "Please create a .env file in $BACKEND_DIR with your OpenAI API key as OPENAI_API_KEY=your_key"
    exit 1
fi

# Step 2: Check if Python and required packages are installed
echo
echo -e "${CYAN}[2/5] Checking Python environment...${NC}"
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✓ Python 3 found${NC}"
    
    # Check required packages
    REQUIRED_PACKAGES=("openai" "pytest" "pytest-mock" "python-dotenv")
    MISSING_PACKAGES=()
    
    for package in "${REQUIRED_PACKAGES[@]}"; do
        if ! python3 -c "import $package" &> /dev/null; then
            MISSING_PACKAGES+=("$package")
        fi
    done
    
    if [ ${#MISSING_PACKAGES[@]} -eq 0 ]; then
        echo -e "${GREEN}✓ All required Python packages are installed${NC}"
    else
        echo -e "${YELLOW}! Some required packages are missing:${NC} ${MISSING_PACKAGES[*]}"
        echo -n "Do you want to install them now? (y/n): "
        read -r install_packages
        
        if [ "$install_packages" = "y" ] || [ "$install_packages" = "Y" ]; then
            python3 -m pip install "${MISSING_PACKAGES[@]}"
            echo -e "${GREEN}✓ Packages installed${NC}"
        else
            echo -e "${RED}✗ Missing packages required for testing${NC}"
            exit 1
        fi
    fi
else
    echo -e "${RED}✗ Python 3 not found${NC}"
    echo "Please install Python 3 to run the tests"
    exit 1
fi

# Track test results
DIRECT_TESTS_PASSED=false
COMPONENT_TESTS_PASSED=false
API_TESTS_PASSED=false

# Step 3: Run the direct OpenAI tests
echo
echo -e "${CYAN}[3/5] Running direct OpenAI API tests...${NC}"
python3 "$SCRIPT_DIR/test_openai_direct.py"
if [ $? -ne 0 ]; then
    echo -e "\n${RED}✗ Direct OpenAI API tests failed${NC}"
    echo "This indicates an issue with your OpenAI API key or connection."
    echo "Please check the error messages above and fix the issues before continuing."
else
    DIRECT_TESTS_PASSED=true
fi

# Step 4: Run AI component tests
echo
echo -e "${CYAN}[4/5] Running AI component tests...${NC}"
pytest "$SCRIPT_DIR/test_ai_components.py::TestOpenAIIntegration" -v
if [ $? -ne 0 ]; then
    echo -e "\n${YELLOW}! Some AI component tests failed${NC}"
    echo "This may indicate issues with the implementation of the OpenAI API in your components."
else
    echo -e "\n${GREEN}✓ All AI component tests passed${NC}"
    COMPONENT_TESTS_PASSED=true
fi

# Step 5: Run AI API endpoint tests
echo
echo -e "${CYAN}[5/5] Running AI API endpoint tests...${NC}"
pytest "$SCRIPT_DIR/test_ai_api_endpoints.py::TestOpenAIConfigBehavior" -v
if [ $? -ne 0 ]; then
    echo -e "\n${YELLOW}! Some AI API endpoint tests failed${NC}"
    echo "This may indicate issues with the implementation of the OpenAI API in your API endpoints."
else
    echo -e "\n${GREEN}✓ All AI API endpoint tests passed${NC}"
    API_TESTS_PASSED=true
fi

echo
echo -e "${CYAN}======================================================${NC}"
echo -e "${CYAN}          OpenAI Integration Tests Results           ${NC}"
echo -e "${CYAN}======================================================${NC}"
echo

# Display detailed summary
echo -e "Direct API Tests: $(if $DIRECT_TESTS_PASSED; then echo -e "${GREEN}PASSED${NC}"; else echo -e "${RED}FAILED${NC}"; fi)"
echo -e "Component Tests: $(if $COMPONENT_TESTS_PASSED; then echo -e "${GREEN}PASSED${NC}"; else echo -e "${RED}FAILED${NC}"; fi)"
echo -e "API Endpoint Tests: $(if $API_TESTS_PASSED; then echo -e "${GREEN}PASSED${NC}"; else echo -e "${RED}FAILED${NC}"; fi)"
echo

# Overall assessment
if $DIRECT_TESTS_PASSED && $COMPONENT_TESTS_PASSED && $API_TESTS_PASSED; then
    echo -e "${GREEN}✅ ALL TESTS PASSED: Your OpenAI integration is working correctly!${NC}"
    exit 0
elif $DIRECT_TESTS_PASSED; then
    echo -e "${YELLOW}⚠️ PARTIAL SUCCESS: Your OpenAI API connection works, but there are issues with the implementation.${NC}"
    echo "Review the failed tests and fix the integration issues in your code."
    exit 1
else
    echo -e "${RED}❌ TESTS FAILED: There are fundamental issues with your OpenAI API integration.${NC}"
    echo "Make sure your API key is valid and that you have proper internet connectivity."
    exit 1
fi 