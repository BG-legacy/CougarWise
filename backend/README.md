# CougarWise Backend

This is the backend for the CougarWise application, which includes a FastAPI server and AI components for student financial assistance.

## Setup

1. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Then edit the `.env` file with your actual values, especially the OpenAI API key.

4. Verify the student spending data file:
   Make sure the `student_spending.csv` file exists in the `backend/AI/` directory. This file is required for training the spending analysis model.

## Running the API Server

To start the API server, run from the backend directory:

```bash
python run.py
```

Alternatively, you can run it directly from the api directory:

```bash
cd api
python run_server.py
```

The server will start on the port specified in your `.env` file (default: 8000).

## Troubleshooting

### Import Errors

If you encounter import errors:

1. Make sure you're running the server from the correct directory (backend or api)
2. Check that you have `__init__.py` files in both the `api` and `AI` directories
3. Verify that your Python path includes the backend directory

### Model Training Errors

If you see a warning about not being able to train the spending model:

1. Check that the `student_spending.csv` file exists in the `backend/AI/` directory
2. Verify that the path in your `.env` file is correct (should be `STUDENT_DATA_PATH=AI/student_spending.csv`)
3. If using a custom path, make sure it's either an absolute path or relative to the backend directory
4. Check the file permissions to ensure the application can read the file

The API will still work without the trained model, but the spending analysis features will be limited.

## API Endpoints

### Authentication Endpoints

- **POST /api/auth/register**: Register a new user
  ```json
  {
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "name": "Test User"
  }
  ```

- **POST /api/auth/login**: Login with username and password
  ```json
  {
    "username": "testuser",
    "password": "password123"
  }
  ```

### Transaction Endpoints

- **POST /api/transactions**: Create a new transaction
  ```json
  {
    "user_id": "user_id_here",
    "amount": -50.00,
    "category": "Food",
    "description": "Grocery shopping"
  }
  ```

- **GET /api/transactions/user/{user_id}**: Get all transactions for a user

### Budget Endpoints

- **POST /api/budgets**: Create or update a budget category
  ```json
  {
    "user_id": "user_id_here",
    "category": "Food",
    "amount": 300.00,
    "period": "monthly"
  }
  ```

- **GET /api/budgets/user/{user_id}**: Get all budgets for a user

### Financial Analysis Endpoints

- **GET /api/analysis/spending/{user_id}**: Get spending analysis for a user
  - Query parameters:
    - `period`: Analysis period (daily, weekly, monthly, yearly)
    - `start_date`: Start date for custom period (ISO format)
    - `end_date`: End date for custom period (ISO format)

- **GET /api/analysis/insights/{user_id}**: Get spending insights and recommendations for a user

### AI Assistant Endpoints

- **POST /ai/query**: Process a general user query
  ```json
  {
    "query": "What are some good budgeting tips for college students?",
    "user_context": {
      "year_in_school": "Sophomore",
      "major": "Computer Science",
      "monthly_income": 1200,
      "financial_aid": 5000
    }
  }
  ```

- **POST /ai/spending-advice**: Get personalized spending advice
  ```json
  {
    "year_in_school": "Sophomore",
    "major": "Computer Science",
    "monthly_income": 1200,
    "financial_aid": 5000
  }
  ```

- **POST /ai/budget-template**: Generate a personalized budget template
  ```json
  {
    "year_in_school": "Sophomore",
    "major": "Computer Science",
    "monthly_income": 1200,
    "financial_aid": 5000
  }
  ```

- **POST /ai/analyze-goals**: Analyze financial goals
  ```json
  {
    "goals": [
      "Save $5000 for summer study abroad",
      "Reduce food spending by 15%",
      "Start an emergency fund"
    ],
    "user_context": {
      "year_in_school": "Sophomore",
      "major": "Computer Science",
      "monthly_income": 1200
    }
  }
  ```

## Testing the API

You can test the API using curl, Postman, or by visiting the interactive documentation at `http://localhost:8000/docs` when the server is running.

### Using the Test Scripts

We provide two test scripts to help you test the API:

1. **Bash script with curl commands**:
   ```bash
   cd tests
   ./test_api_curl.sh
   ```

2. **Python test script**:
   ```bash
   cd tests
   ./test_api.py
   ```

See the `tests/README.md` file for more detailed testing instructions. 