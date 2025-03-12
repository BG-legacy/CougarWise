# CougarWise Database Module

This module provides database connection and models for the CougarWise application.

## Overview

The database module consists of the following components:

1. **database.py**: Provides a MongoDB connection manager and helper functions.
2. **models.py**: Provides Pydantic models for database entities.
3. **test_database.py**: Contains tests for the database connection and operations.

## Database Connection

The database connection is managed by the `Database` class in `database.py`. It uses a singleton pattern to ensure only one database connection is created.

```python
from Database.database import get_db, get_collection, Collections

# Get the database instance
db = get_db()

# Get a specific collection
users_collection = get_collection(Collections.USERS)
```

## Database Models

The database models are defined in `models.py`. They provide a convenient way to interact with the database.

```python
from Database.models import User, Transaction, FinancialGoal

# Create a new user
user_data = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "hashedpassword123",
    "name": "Test User"
}
user = User.create(user_data)

# Find a user by username
user = User.find_by_username("testuser")

# Create a new transaction
transaction_data = {
    "userId": "testuser",
    "amount": 50.00,
    "category": "Food",
    "description": "Lunch"
}
transaction = Transaction.create(transaction_data)

# Find all transactions for a user
transactions = Transaction.find_by_user("testuser")
```

## API Endpoints

The database API endpoints are defined in `api/database_api.py`. They provide a RESTful interface to the database.

### User Endpoints

- `POST /db/users`: Create a new user
- `GET /db/users/{username}`: Get a user by username

### Transaction Endpoints

- `POST /db/transactions`: Create a new transaction
- `GET /db/transactions/user/{user_id}`: Get all transactions for a user

### Financial Goal Endpoints

- `POST /db/goals`: Create a new financial goal
- `GET /db/goals/user/{user_id}`: Get all financial goals for a user
- `PUT /db/goals/{goal_id}`: Update a financial goal

## Database Schema

The database schema consists of the following collections:

1. **Users**: Stores user information
2. **Transactions**: Stores user transactions
3. **FinancialGoals**: Stores user financial goals
4. **CategoryBreakdown**: Stores user category budgets
5. **Recommendations**: Stores AI-generated recommendations
6. **Notifications**: Stores user notifications
7. **SpendingAnalysis**: Stores user spending analysis
8. **Chatbot**: Stores chatbot conversations

## Environment Variables

The database connection requires the following environment variables:

- `MONGODB_URI`: The MongoDB connection URI
- `MONGODB_DB_NAME`: The MongoDB database name

These can be set in the `.env` file in the backend directory.

## Testing

The database connection and operations can be tested using the `test_database.py` file:

```bash
cd backend
pytest Database/test_database.py -v
``` 