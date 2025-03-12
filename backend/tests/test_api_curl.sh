#!/bin/bash
# Test script for CougarWise API endpoints using curl

# Set the base URL
BASE_URL="http://localhost:8000"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}CougarWise API Test Script${NC}"
echo "=============================="
echo ""

# Function to run a test
run_test() {
    local test_name=$1
    local command=$2
    
    echo -e "${BLUE}Testing: ${test_name}${NC}"
    echo "Command: $command"
    echo "Response:"
    eval $command
    echo ""
    echo "------------------------------"
}

# 1. Test the root endpoint
run_test "Root Endpoint" "curl -s ${BASE_URL}/"

# 2. Test user registration
run_test "User Registration" "curl -s -X POST ${BASE_URL}/api/auth/register \
  -H \"Content-Type: application/json\" \
  -d '{\"username\": \"testuser\", \"email\": \"test@example.com\", \"password\": \"password123\", \"name\": \"Test User\"}'"

# 3. Test user login
run_test "User Login" "curl -s -X POST ${BASE_URL}/api/auth/login \
  -H \"Content-Type: application/json\" \
  -d '{\"username\": \"testuser\", \"password\": \"password123\"}'"

# Store user ID for subsequent tests (you'll need to manually set this after running the login test)
USER_ID="replace_with_actual_user_id_from_login_response"

# 4. Test creating a transaction
run_test "Create Transaction" "curl -s -X POST ${BASE_URL}/api/transactions \
  -H \"Content-Type: application/json\" \
  -d '{\"user_id\": \"${USER_ID}\", \"amount\": -50.00, \"category\": \"Food\", \"description\": \"Grocery shopping\"}'"

# 5. Test getting user transactions
run_test "Get User Transactions" "curl -s ${BASE_URL}/api/transactions/user/${USER_ID}"

# 6. Test creating a budget
run_test "Create Budget" "curl -s -X POST ${BASE_URL}/api/budgets \
  -H \"Content-Type: application/json\" \
  -d '{\"user_id\": \"${USER_ID}\", \"category\": \"Food\", \"amount\": 300.00, \"period\": \"monthly\"}'"

# 7. Test getting user budgets
run_test "Get User Budgets" "curl -s ${BASE_URL}/api/budgets/user/${USER_ID}"

# 8. Test getting spending analysis
run_test "Get Spending Analysis" "curl -s \"${BASE_URL}/api/analysis/spending/${USER_ID}?period=monthly\""

# 9. Test getting spending insights
run_test "Get Spending Insights" "curl -s ${BASE_URL}/api/analysis/insights/${USER_ID}"

# 10. Test AI query endpoint
run_test "AI Query" "curl -s -X POST ${BASE_URL}/ai/query \
  -H \"Content-Type: application/json\" \
  -d '{\"query\": \"How can I save money on groceries?\", \"user_context\": {\"year_in_school\": \"Sophomore\"}}'"

echo -e "${GREEN}All tests completed!${NC}"
echo "Note: Some tests may have failed if the server is not running or if the USER_ID is not set correctly."
echo "Please update the USER_ID variable in this script after registering/logging in a user." 