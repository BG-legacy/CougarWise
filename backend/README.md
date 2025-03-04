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