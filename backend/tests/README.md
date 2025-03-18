# CougarWise Backend Tests

This directory contains tests for the CougarWise backend.

## Overview

The tests are organized into the following files:

1. **conftest.py**: Contains pytest fixtures and configuration.
2. **test_database_connection.py**: Tests for the database connection.
3. **test_database_models.py**: Tests for the database models.
4. **test_api_endpoints.py**: Tests for the API endpoints.
5. **test_signup_endpoint.py**: Tests for the signup endpoint.

## Running Tests

To run all tests:

```bash
cd backend
pytest tests/
```

To run a specific test file:

```bash
cd backend
pytest tests/test_database_models.py
```

To run a specific test:

```bash
cd backend
pytest tests/test_database_models.py::TestUserModel::test_create_user
```

## Test Database

The tests use a separate test database (`cougarwise_test`) to avoid affecting the production database. The test database is created and dropped for each test session.

## Test Coverage

To run tests with coverage:

```bash
cd backend
pytest --cov=. tests/
```

## Continuous Integration

These tests can be integrated into a CI/CD pipeline to ensure code quality and prevent regressions.

## Adding New Tests

When adding new features to the backend, please add corresponding tests to ensure the feature works as expected and to prevent regressions in the future.

# Testing the CougarWise API

This directory contains tools and scripts for testing the CougarWise API.

## Using the Curl Test Script

The `test_api_curl.sh` script provides a convenient way to test all the API endpoints using curl commands. This is useful for quick verification of API functionality without needing a frontend client.

### Prerequisites

- The CougarWise backend server must be running
- Curl must be installed on your system
- Bash shell environment

### Running the Test Script

1. Make sure the backend server is running:
   ```bash
   cd ../
   python run.py
   ```

2. In a new terminal, run the test script:
   ```bash
   cd tests
   ./test_api_curl.sh
   ```

3. After running the registration and login tests, you'll need to update the `USER_ID` variable in the script with the actual user ID returned from the login response.

### Manual Testing with Curl

If you prefer to test individual endpoints manually, here are some example curl commands:

#### Authentication

**Register a new user:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "password123", "name": "Test User"}'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "password123"}'
```

#### Transactions

**Create a transaction:**
```bash
curl -X POST http://localhost:8000/api/transactions \
  -H "Content-Type: application/json" \
  -d '{"user_id": "YOUR_USER_ID", "amount": -50.00, "category": "Food", "description": "Grocery shopping"}'
```

**Get user transactions:**
```bash
curl http://localhost:8000/api/transactions/user/YOUR_USER_ID
```

#### Budgets

**Create a budget:**
```bash
curl -X POST http://localhost:8000/api/budgets \
  -H "Content-Type: application/json" \
  -d '{"user_id": "YOUR_USER_ID", "category": "Food", "amount": 300.00, "period": "monthly"}'
```

**Get user budgets:**
```bash
curl http://localhost:8000/api/budgets/user/YOUR_USER_ID
```

#### Financial Analysis

**Get spending analysis:**
```bash
curl "http://localhost:8000/api/analysis/spending/YOUR_USER_ID?period=monthly"
```

**Get spending insights:**
```bash
curl http://localhost:8000/api/analysis/insights/YOUR_USER_ID
```

#### AI Features

**Get AI advice:**
```bash
curl -X POST http://localhost:8000/ai/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How can I save money on groceries?", "user_context": {"year_in_school": "Sophomore"}}'
```

## Troubleshooting

- If you get connection refused errors, make sure the backend server is running
- If you get 404 errors, check that the endpoint URL is correct
- If you get 500 errors, check the server logs for more details
- If you get authentication errors, make sure you're using the correct credentials

## OpenAI Integration Testing

The CougarWise project uses OpenAI's API for various AI-powered features. To ensure proper integration and handling of the OpenAI API, we have created several test files specifically for OpenAI functionality:

### New OpenAI Test Files

1. **TestOpenAIIntegration** (in `test_ai_components.py`)
   - Tests direct integration with OpenAI API in our components
   - Verifies correct parameter passing, response parsing, and error handling

2. **TestOpenAIConfigBehavior** (in `test_ai_api_endpoints.py`)
   - Tests API endpoint behavior based on OpenAI configuration
   - Verifies graceful handling when AI services are unavailable
   - Tests error handling for missing API keys and rate limits

3. **test_openai_direct.py**
   - Standalone script that tests direct connection to OpenAI API
   - Verifies API key existence, connection, and JSON response formatting
   - Can be run independently to troubleshoot OpenAI connectivity issues

4. **test_openai.sh**
   - Shell script to run all OpenAI-related tests in one command
   - Checks environment setup, dependencies, and API connectivity
   - Provides clear, color-coded output for test results

### Running OpenAI Tests

To run all OpenAI-related tests:

```bash
# From the tests directory
./test_openai.sh
```

To run specific OpenAI test components:

```bash
# Test direct OpenAI API connection
python test_openai_direct.py

# Test OpenAI integration in components
pytest test_ai_components.py::TestOpenAIIntegration -v

# Test OpenAI behavior in API endpoints
pytest test_ai_api_endpoints.py::TestOpenAIConfigBehavior -v
```

### Setting Up OpenAI API Key

To run the OpenAI tests, you need a valid OpenAI API key:

1. Create a `.env` file in the backend directory
2. Add your OpenAI API key: `OPENAI_API_KEY=your_key_here`

The tests will automatically detect and use this key. 