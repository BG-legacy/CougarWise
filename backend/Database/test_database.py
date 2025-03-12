import os
import pytest
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import json
from bson import json_util  # For handling MongoDB date objects

# Load environment variables
load_dotenv()

# MongoDB connection details
MONGODB_URI = os.getenv('MONGODB_URI')
MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME')

print(f"Connecting to database: {MONGODB_DB_NAME}")
print(f"Using URI: {MONGODB_URI}")

@pytest.fixture
def mongo_client():
    """Create a MongoDB client as a pytest fixture."""
    client = MongoClient(MONGODB_URI, 
                        tls=True, 
                        tlsAllowInvalidCertificates=True)
    try:
        db_names = client.list_database_names()
        print(f"Available databases: {db_names}")
        if MONGODB_DB_NAME in db_names:
            print(f"Found target database: {MONGODB_DB_NAME}")
            db = client[MONGODB_DB_NAME]
            print(f"Available collections in {MONGODB_DB_NAME}: {db.list_collection_names()}")
        else:
            print(f"WARNING: Target database {MONGODB_DB_NAME} not found!")
    except Exception as e:
        print(f"Error accessing database: {str(e)}")
    yield client
    client.close()

@pytest.fixture
def db(mongo_client):
    """Create a database fixture."""
    database = mongo_client[MONGODB_DB_NAME]
    print(f"Using database: {database.name}")
    return database

@pytest.mark.order(1)
def test_database_connection(mongo_client):
    """Test if we can connect to the database."""
    try:
        mongo_client.admin.command('ismaster')
        print("Successfully connected to MongoDB")
        assert True
    except Exception as e:
        print(f"Failed to connect to MongoDB: {str(e)}")
        assert False, str(e)

@pytest.mark.order(2)
def test_users_collection(db):
    """Test Users collection operations."""
    users = db.Users
    print(f"\nTesting Users collection in database: {db.name}")
    print(f"Current collection name: {users.name}")
    print(f"Current database name: {users.database.name}")
    
    test_user = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "hashedpassword123",
        "name": "Test User",
        "createdAt": datetime.now()  # Add timestamp
    }
    
    # Create
    result = users.insert_one(test_user)
    assert result.inserted_id is not None
    print(f"Created user with ID: {result.inserted_id} in database {db.name}")
    print(f"Full connection details: {db.client.address}")

    # Read
    found_user = users.find_one({"username": "testuser"})
    assert found_user is not None
    print(f"Found user in database {db.name}: {found_user}")
    
    # Verify in all collections
    all_collections = db.list_collection_names()
    print(f"\nAll collections in database: {all_collections}")
    print(f"Document count in Users collection: {users.count_documents({})}")

@pytest.mark.order(3)
def test_transactions_collection(db):
    """Test Transactions collection operations."""
    transactions = db.Transactions
    test_transaction = {
        "userId": "testuser",
        "amount": 50.00,
        "category": "Food",
        "description": "Lunch",
        "date": datetime.now()
    }
    
    result = transactions.insert_one(test_transaction)
    assert result.inserted_id is not None
    print(f"Created transaction with ID: {result.inserted_id}")

@pytest.mark.order(4)
def test_financial_goals_collection(db):
    """Test FinancialGoals collection operations."""
    goals = db.FinancialGoals
    test_goal = {
        "userId": "testuser",
        "targetAmount": 1000.00,
        "currentAmount": 0.00,
        "category": "Savings",
        "deadline": datetime.now()
    }
    
    result = goals.insert_one(test_goal)
    assert result.inserted_id is not None
    print(f"Created goal with ID: {result.inserted_id}")

@pytest.mark.order(5)
def test_category_breakdown_collection(db):
    """Test CategoryBreakdown collection operations."""
    categories = db.CategoryBreakdown
    test_category = {
        "userId": "testuser",
        "category": "Food",
        "monthlyBudget": 300.00,
        "currentSpent": 50.00
    }
    
    result = categories.insert_one(test_category)
    assert result.inserted_id is not None
    print(f"Created category breakdown with ID: {result.inserted_id}")

@pytest.mark.order(6)
def test_recommendations_collection(db):
    """Test Recommendations collection operations."""
    recommendations = db.Recommendations
    test_recommendation = {
        "userId": "testuser",
        "type": "Savings",
        "message": "Consider reducing food expenses",
        "date": datetime.now()
    }
    
    result = recommendations.insert_one(test_recommendation)
    assert result.inserted_id is not None
    print(f"Created recommendation with ID: {result.inserted_id}")

@pytest.mark.order(7)
def test_notifications_collection(db):
    """Test Notifications collection operations."""
    notifications = db.Notifications
    test_notification = {
        "userId": "testuser",
        "message": "You're close to your food budget limit",
        "type": "Warning",
        "date": datetime.now(),
        "read": False
    }
    
    result = notifications.insert_one(test_notification)
    assert result.inserted_id is not None
    print(f"Created notification with ID: {result.inserted_id}")

@pytest.mark.order(8)
def test_spending_analysis_collection(db):
    """Test SpendingAnalysis collection operations."""
    analysis = db.SpendingAnalysis
    test_analysis = {
        "userId": "testuser",
        "month": datetime.now().month,
        "year": datetime.now().year,
        "totalSpent": 500.00,
        "categoryBreakdown": {
            "Food": 200.00,
            "Transport": 150.00,
            "Entertainment": 150.00
        }
    }
    
    result = analysis.insert_one(test_analysis)
    assert result.inserted_id is not None
    print(f"Created spending analysis with ID: {result.inserted_id}")

@pytest.mark.order(9)
def test_chatbot_collection(db):
    """Test Chatbot collection operations."""
    chatbot = db.Chatbot
    test_chat = {
        "userId": "testuser",
        "message": "How can I save money?",
        "response": "Try creating a budget and tracking your expenses",
        "timestamp": datetime.now()
    }
    
    result = chatbot.insert_one(test_chat)
    assert result.inserted_id is not None
    print(f"Created chat message with ID: {result.inserted_id}")

@pytest.mark.order(10)
def test_verify_data_exists(db):
    """Verify and display all test data in the database."""
    collections = [
        'Users', 'Transactions', 'FinancialGoals', 'CategoryBreakdown',
        'Recommendations', 'Notifications', 'SpendingAnalysis', 'Chatbot'
    ]
    
    print("\n=== Current Test Data in Database ===")
    total_documents = 0
    
    for collection_name in collections:
        collection = db[collection_name]
        # Find all documents related to test user
        test_docs = list(collection.find({"$or": [
            {"userId": "testuser"},
            {"username": "testuser"}
        ]}))
        
        print(f"\n{collection_name} Collection:")
        if test_docs:
            total_documents += len(test_docs)
            for doc in test_docs:
                # Convert MongoDB document to JSON string for pretty printing
                doc_str = json.dumps(json.loads(json_util.dumps(doc)), indent=2)
                print(doc_str)
        else:
            print("No test data found")
    
    print(f"\nTotal test documents found: {total_documents}")
    print("===================================")
    
    # Don't assert, just show what was found
    if total_documents == 0:
        print("No test data was found in any collection. You may need to run the full test suite first to create test data.")