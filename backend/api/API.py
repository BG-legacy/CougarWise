from fastapi import FastAPI
from pydantic import BaseModel
import sys
import os
from fastapi import FastAPI, APIRouter, Request, Body, HTTPException, Depends
from bson import ObjectId
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import json

# Add path to backend directory to import AI modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import AI modules conditionally to allow tests to run without them
try:
    from AI.website_ai_assistant import WebsiteAIAssistant
    ai_assistant = WebsiteAIAssistant()
    AI_AVAILABLE = True
except ImportError:
    print("Warning: AI modules not available. AI features will be disabled.")
    AI_AVAILABLE = False
    ai_assistant = None

# Import database API router and database connection
from .database_api import router as db_router
from Database.database import get_db, get_collection, Collections

app = FastAPI()

# Configure CORS
frontend_url = os.getenv('FRONTEND_URL', 'https://cougar-wise.vercel.app')
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],  # Allows the frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include database API router
app.include_router(db_router)

# Database dependency
def get_db_dependency():
    """
    Get database dependency for FastAPI dependency injection.
    This function is used as a dependency in route functions to get the database connection.
    
    Returns:
        MongoDB database connection
    """
    return get_db()

# Authentication models
class LoginRequest(BaseModel):
    """Model for login requests"""
    username: str
    password: str

class LoginResponse(BaseModel):
    """Model for login responses"""
    success: bool
    message: str
    user_id: Optional[str] = None
    username: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[str] = None

class Student(BaseModel):
    """
    Student data model for request/response validation.
    These fields are optional (can be None) to allow partial updates.
    """
    firstname: str | None = None        
    lastname: str | None = None
    username: str | None = None
    email: str | None = None

class UserQuery(BaseModel):
    """
    Model for AI assistant query requests.
    Contains the user's question and optional context about the user.
    """
    query: str  # The user's question or request
    user_context: Dict[str, Any] = None  # Optional context about the user (year in school, major, etc.)

class UserProfile(BaseModel):
    """
    Model for user profile data used in AI spending advice and budget templates.
    Contains information about the student's academic and financial situation.
    """
    year_in_school: str  # Freshman, Sophomore, Junior, Senior, etc.
    major: str  # Student's field of study
    monthly_income: float  # Student's monthly income
    financial_aid: float  # Amount of financial aid received
    age: Optional[int] = None  # Student's age (optional)
    gender: Optional[str] = None  # Student's gender (optional)
    preferred_payment_method: Optional[str] = None  # Preferred payment method (optional)

class FinancialGoals(BaseModel):
    """
    Model for financial goals analysis requests.
    Contains a list of goals and context about the user.
    """
    goals: List[str]  # List of financial goals as strings
    user_context: Dict[str, Any]  # Context about the user

# Financial data models
class TransactionRequest(BaseModel):
    """Model for creating a new transaction"""
    user_id: str
    amount: float
    category: str
    description: str
    date: Optional[datetime] = None

class TransactionResponse(BaseModel):
    """Model for transaction response"""
    id: Optional[str] = None
    user_id: str
    amount: float
    category: str
    description: str
    date: str

class BudgetRequest(BaseModel):
    """Model for creating or updating a budget"""
    user_id: str
    category: str
    amount: float
    period: str  # 'monthly', 'weekly', etc.

class BudgetResponse(BaseModel):
    """Model for budget response"""
    id: Optional[str] = None
    user_id: str
    category: str
    amount: float
    period: str
    spent: Optional[float] = 0
    created_at: Optional[str] = None

# Financial analysis models
class SpendingAnalysisResponse(BaseModel):
    """Model for spending analysis response"""
    total_spending: float
    category_breakdown: Dict[str, float]
    period: str
    start_date: str
    end_date: str

class SpendingInsightResponse(BaseModel):
    """Model for spending insights response"""
    insights: List[str]
    recommendations: List[str]

newuser = Student()

def create_user(email, username, firstname, lastname):
    """
    Create a user dictionary from provided information.
    
    Args:
        email: User's email address
        username: User's username
        firstname: User's first name
        lastname: User's last name
        
    Returns:
        Dictionary containing user information
    """
    newuser.lastname = lastname
    newuser.username = username
    newuser.email = email
    newuser.firstname = firstname

    return dict(newuser)


students = {
    1:{
        "name": "john",
        "age": 17,
        "class": "year 12"
    }
}

@app.get("/")
async def root():
    """
    Root endpoint that returns a simple message.
    Used as a health check to verify the API is running.
    """
    return {"message": "Hello World"}

@app.get("/get-student/{student_id}")
def get_student(student_id: int):
    """
    Get a student by ID from the sample data.
    
    Args:
        student_id: The ID of the student to retrieve
        
    Returns:
        Student information as a dictionary
    """
    return students[student_id]

@app.get("/items/{item_id}")
async def read_item(item_id):
    """
    Generic endpoint that returns the provided item ID.
    Demonstrates how path parameters work in FastAPI.
    
    Args:
        item_id: The ID of the item to retrieve
        
    Returns:
        Dictionary containing the item ID
    """
    return {"item_id": item_id}

# Signup endpoint with the POST method
@app.post("/signup/{email}/{username}/{firstname}/{lastname}")
def addUser(email, username: str, firstname: str, lastname: str):
    """
    Create a new user in the database.
    
    Args:
        email: User's email address
        username: User's username
        firstname: User's first name
        lastname: User's last name
        
    Returns:
        User information or error message
    """
    user_exists = False
    data = create_user(email, username, firstname, lastname)

    # Check if an email exists from the collection of users
    collection = get_collection(Collections.USERS)
    if collection.count_documents({'email': data['email']}) > 0:
        user_exists = True
        print("Customer Exists")
        return {"message": "Customer Exists", "detail": "User already exists"}
    
    # If user doesn't exist, create a new user
    collection.insert_one({
        "email": data['email'],
        "username": data['username'],
        "name": f"{data['firstname']} {data['lastname']}",
        "password": "defaultpassword",  # In a real app, this should be hashed
        "createdAt": datetime.now()
    })
    
    return data



@app.post("/")
async def create_item(request: Request, student: Student):
    """
    Create a new item in the database.
    Demonstrates how to use request body and MongoDB integration.
    
    Args:
        request: The HTTP request object
        student: The student data to create
        
    Returns:
        Dictionary containing the ID of the created item
    """
    db = request.app.mongodb["collection_name"]
    result = await db.insert_one(student.dict())
    return {"id": str(result.inserted_id)}

@app.put("/{id}")
async def update_item(request: Request, id: str, student: Student):
    """
    Update an item by ID.
    
    Args:
        request: The HTTP request object
        id: The ID of the item to update
        student: The updated student data
        
    Returns:
        Dictionary containing the number of updated items
    """
    db = request.app.mongodb["collection_name"]
    result = await db.update_one({"_id": ObjectId(id)}, {"$set": student.dict()})
    return {"updated_count": result.modified_count}

#Real one - Put/update email
@app.put("/customer/{email}")
async def update_item(request: Request, email: str, student: Student):
    """
    Update a customer by email.
    
    Args:
        request: The HTTP request object
        email: The email of the customer to update
        student: The updated student data
        
    Returns:
        Dictionary containing the number of updated items
    """
    db = request.app.mongodb["collection_name"] #change collection name to DB name
    result = await db.update_one({"email": email}, {"$set": student.dict()})
    return {"updated_count": result.modified_count}


#Real one - Put/update firstname
@app.put("/{firstname}") #add httpexectpion
async def update_item(request: Request, firstname: str, student: Student):
    """
    Update a user by firstname.
    
    Args:
        request: The HTTP request object
        firstname: The firstname of the user to update
        student: The updated student data
        
    Returns:
        Dictionary containing the number of updated items
    """
    db = request.app.mongodb["collection_name"] #change collection name to DB name
    result = await db.update_one({"firstname": firstname}, {"$set": student.dict()})
    return {"updated_count": result.modified_count}


@app.put("/{lastname}")#add httpexecption
async def update_item(request: Request, lastname: str, student: Student):
    """
    Update a user by lastname.
    
    Args:
        request: The HTTP request object
        lastname: The lastname of the user to update
        student: The updated student data
        
    Returns:
        Dictionary containing the number of updated items
    """
    db = request.app.mongodb["collection_name"] #change collection name to DB name
    result = await db.update_one({"lastname": lastname}, {"$set": student.dict()})
    return {"updated_count": result.modified_count}    


@app.put("/{username}")#add httpexpection
async def update_item(request: Request, username: str, student: Student):
    """
    Update a user by username.
    
    Args:
        request: The HTTP request object
        username: The username of the user to update
        student: The updated student data
        
    Returns:
        Dictionary containing the number of updated items
    """
    db = request.app.mongodb["collection_name"] #change collection name to DB name
    result = await db.update_one({"username": str}, {"$set": student.dict()})
    return {"updated_count": result.modified_count}


# the one I base it off of
@app.put("/{id}")
async def update_item(request: Request, id: str, student: Student):
    """
    Base update endpoint that other update endpoints are based on.
    
    Args:
        request: The HTTP request object
        id: The ID of the item to update
        student: The updated student data
        
    Returns:
        Dictionary containing the number of updated items
    """
    db = request.app.mongodb["collection_name"]
    result = await db.update_one({"_id": ObjectId(id)}, {"$set": student.dict()})
    return {"updated_count": result.modified_count}


#########################################################################################################
########################################  ALL OF THE GETS   #############################################
#########################################################################################################
@app.get("/{username}")
async def read_items(request: Request, username: str):
    """
    Get a user by username.
    
    Args:
        request: The HTTP request object
        username: The username of the user to retrieve
        
    Returns:
        User information or None if not found
    """
    db = request.app.mongodb["collection_name"] #change to name of collection
    items = await db.find_one({"username": username})
  #  if items is None:
     #   raise HTTPExeption(status_code=404, detail="Person not found")
    return items


@app.get("/{lastname}")
async def read_items(request: Request, lastname: str):
    """
    Get a user by lastname.
    
    Args:
        request: The HTTP request object
        lastname: The lastname of the user to retrieve
        
    Returns:
        User information or None if not found
    """
    db = request.app.mongodb["collection_name"] #change to name of collection
    items = await db.find_one({"lastname": lastname})
   # if items is None:
     #   raise HTTPExeption(status_code=404, detail="Person not found")
    return items


@app.get("/{firstname}")
async def read_items(request: Request, firstname: str):
    """
    Get a user by firstname.
    
    Args:
        request: The HTTP request object
        firstname: The firstname of the user to retrieve
        
    Returns:
        User information or None if not found
    """
    db = request.app.mongodb["collection_name"] #change to name of collection
    items = await db.find_one({"firstname": firstname})
   # if items is None:
    #    raise HTTPExeption(status_code=404, detail="Person not found")
    return items


@app.get("/{email}")
async def read_items(request: Request, email: str):
    """
    Get a user by email.
    
    Args:
        request: The HTTP request object
        email: The email of the user to retrieve
        
    Returns:
        User information or None if not found
    """
    db = request.app.mongodb["collection_name"] #change to name of collection
    items = await db.find_one({"email": email})
   # if items is None:
    #    raise HTTPExeption(status_code=404, detail="Person not found")
    return items


@app.get("/{id}")
async def read_items(request: Request, id: str):
    """
    Get a user by ID.
    
    Args:
        request: The HTTP request object
        id: The ID of the user to retrieve
        
    Returns:
        User information or None if not found
    """
    db = request.app.mongodb["collection_name"] #change to name of collection
    items = await db.find_one({"id": id})
   # if items is None:
    #    raise HTTPExeption(status_code=404, detail="Person not found")
    return items


@app.get("/")
async def read_items(request: Request):
    """
    Get all items from the collection.
    
    Args:
        request: The HTTP request object
        
    Returns:
        List of items (limited to 100)
    """
    db = request.app.mongodb["collection_name"]#change collection name
    items = await db.find({}).to_list(100)
    for item in items:
        item["_custid"] = str(item["_custid"])
    return items






@app.delete("/{id}")
async def delete_item(request: Request, id: str):
    """
    Delete an item by ID.
    
    Args:
        request: The HTTP request object
        id: The ID of the item to delete
        
    Returns:
        Dictionary containing the number of deleted items
    """
    db = request.app.mongodb["collection_name"]
    result = await db.delete_one({"_id": ObjectId(id)})
    return {"deleted_count": result.deleted_count}


@app.delete("/{username}")
async def delete_item(request: Request, username: str):
    """
    Delete a user by username.
    
    Args:
        request: The HTTP request object
        username: The username of the user to delete
        
    Returns:
        Dictionary containing the number of deleted items
    """
    db = request.app.mongodb["collection_name"]
    result = await db.delete_one({"username": str})
    return {"deleted_count": result.deleted_count}

# AI Assistant Endpoints

@app.post("/ai/query")
async def process_query(user_query: UserQuery):
    """
    Process a user query using the AI assistant.
    This endpoint takes a user's question and optional context,
    and returns a response generated by the AI assistant.
    
    Args:
        user_query: Object containing the query and user context
        
    Returns:
        AI-generated response to the query
        
    Raises:
        HTTPException: If AI features are not available or an error occurs
    """
    if not AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI features are not available")
    
    try:
        # Get user data from database if user_id is provided
        user_data = {}
        user_id = None
        if user_query.user_context and 'user_id' in user_query.user_context:
            user_id = user_query.user_context['user_id']
            # Fetch user profile data
            users_collection = get_collection(Collections.USERS)
            user = users_collection.find_one({"_id": ObjectId(user_id)})
            
            if user:
                user_data['profile'] = {
                    'name': user.get('name', ''),
                    'email': user.get('email', ''),
                    'year_in_school': user.get('year_in_school', ''),
                    'major': user.get('major', '')
                }
                
                # Fetch transaction data
                transactions_collection = get_collection(Collections.TRANSACTIONS)
                transactions = list(transactions_collection.find({"user_id": user_id}))
                
                # Calculate financial metrics
                total_income = 0
                total_expenses = 0
                
                # Categorize transactions with or without type field
                for t in transactions:
                    amount = t.get('amount', 0)
                    
                    # If transaction has a type field, use it
                    if 'type' in t:
                        if t['type'] == 'income':
                            total_income += amount
                        elif t['type'] == 'expense':
                            total_expenses += amount
                    # Otherwise infer type from amount or category
                    else:
                        # If transaction has a category, consider it an expense
                        if t.get('category', '').strip() != '':
                            total_expenses += amount
                        # If no type and no category, use amount sign (positive = income, negative = expense)
                        elif amount < 0:
                            total_expenses += abs(amount)
                        else:
                            total_income += amount
                
                # Get category breakdown
                category_spending = {}
                for t in transactions:
                    # Determine if this is an expense
                    is_expense = False
                    
                    # Check if we have a transaction type field
                    if "type" in t:
                        is_expense = t["type"].lower() == "expense"
                    # If no type field or type is not "expense", use category and amount
                    if not is_expense:
                        # Any transaction with a category is considered an expense
                        category = t.get('category', '').strip()
                        is_expense = category != ""
                    
                    # For expenses, add to the category breakdown
                    if is_expense:
                        category = t.get('category', 'Uncategorized')
                        if not category or category.strip() == "":
                            category = 'Uncategorized'
                        
                        # Convert to positive for easier understanding
                        amount = abs(t.get('amount', 0))
                        
                        if category in category_spending:
                            category_spending[category] += amount
                        else:
                            category_spending[category] = amount
                
                # Add financial data to user context
                user_data['finances'] = {
                    'total_income': total_income,
                    'total_expenses': total_expenses,
                    'category_spending': category_spending
                }
                
                # Update user_context with the retrieved data
                if not user_query.user_context:
                    user_query.user_context = {}
                user_query.user_context.update(user_data)
        
        # Check if the query is about food spending or specific categories
        query_lower = user_query.query.lower()
        spending_categories = ["food", "rent", "groceries", "dining", "housing", "transportation", 
                            "utilities", "entertainment", "education", "health", "shopping"]
        
        # Enhanced pattern matching for spending queries
        is_spending_query = any(
            pattern in query_lower 
            for category in spending_categories
            for pattern in [
                f"spent on {category}", 
                f"spending on {category}", 
                f"{category} expenses",
                f"how much {category}",
                f"how much on {category}",
                f"how much for {category}",
                f"how much did i spend on {category}",
                f"how much money i spent on {category}",
                f"how much have i spent on {category}",
                f"money spent on {category}"
            ]
        )
        
        # If this is a spending query and we have a user_id, get specific category spending data
        if is_spending_query and user_id:
            # Detect which category the user is asking about
            detected_category = None
            for category in spending_categories:
                patterns = [
                    f"spent on {category}", 
                    f"spending on {category}", 
                    f"{category} expenses",
                    f"how much {category}",
                    f"how much on {category}",
                    f"how much for {category}",
                    f"how much did i spend on {category}",
                    f"how much money i spent on {category}",
                    f"how much have i spent on {category}",
                    f"money spent on {category}"
                ]
                
                if any(pattern in query_lower for pattern in patterns):
                    detected_category = category
                    break
            
            if detected_category:
                # Get detailed spending data for this category
                spending_data = get_category_spending(user_id, detected_category)
                
                # Format a detailed response about this category
                if spending_data.get("transaction_count", 0) > 0:
                    response_text = f"Based on your transaction history, you've spent ${spending_data['total_spent']:.2f} on {detected_category.capitalize()} "
                    response_text += f"during the period {spending_data['time_period']}. "
                    response_text += f"This represents {spending_data['percentage']:.1f}% of your total expenses. "
                    
                    # Add transaction examples if available
                    if len(spending_data.get('transactions', [])) > 0:
                        response_text += f"Your {detected_category} spending includes "
                        transaction_samples = spending_data['transactions'][:3]  # Show up to 3 examples
                        examples = []
                        for t in transaction_samples:
                            date_str = t.get('date')
                            try:
                                if isinstance(date_str, str) and 'T' in date_str:
                                    date_obj = datetime.fromisoformat(date_str.split('T')[0])
                                    formatted_date = date_obj.strftime('%b %d')
                                else:
                                    formatted_date = "Unknown date"
                            except:
                                formatted_date = "Unknown date"
                                
                            examples.append(f"${abs(t.get('amount', 0)):.2f} on {t.get('description', 'Unknown')} ({formatted_date})")
                        
                        response_text += ", ".join(examples)
                        if len(spending_data['transactions']) > 3:
                            response_text += f", and {len(spending_data['transactions']) - 3} more transactions."
                        else:
                            response_text += "."
                    
                    return {
                        "status": "success",
                        "response": response_text
                    }
                else:
                    return {
                        "status": "success",
                        "response": f"Based on your transaction history, you haven't recorded any spending on {detected_category.capitalize()} yet."
                    }
        
        # For regular queries, or if no category-specific data is found, use the AI assistant
        result = ai_assistant.process_user_query(user_query.query, user_query.user_context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/ai/spending-advice")
async def get_spending_advice(user_data: UserProfile):
    """
    Get spending advice based on user profile.
    This endpoint takes a user's profile information and returns
    personalized spending advice and predictions.
    
    Args:
        user_data: User profile information
        
    Returns:
        Dictionary containing spending predictions and advice
        
    Raises:
        HTTPException: If AI features are not available or an error occurs
    """
    if not AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI features are not available")
    
    try:
        # Convert to dict for easier manipulation
        user_profile = user_data.dict()
        
        # Get user_id if provided
        user_id = user_profile.get('user_id')
        
        # If user_id is provided, fetch additional data from database
        if user_id:
            # Fetch user's transactions
            transactions_collection = get_collection(Collections.TRANSACTIONS)
            transactions = list(transactions_collection.find({"user_id": user_id}))
            
            # Calculate financial metrics
            total_income = sum(t['amount'] for t in transactions if t.get('type') == 'income')
            total_expenses = sum(t['amount'] for t in transactions if t.get('type') == 'expense')
            
            # Get category breakdown
            category_spending = {}
            for t in transactions:
                # Determine if this is an expense
                is_expense = False
                
                # Check if we have a transaction type field
                if "type" in t:
                    is_expense = t["type"].lower() == "expense"
                # If no type field or type is not "expense", use category and amount
                if not is_expense:
                    # Any transaction with a category is considered an expense
                    category = t.get('category', '').strip()
                    is_expense = category != ""
                
                # For expenses, add to the category breakdown
                if is_expense:
                    category = t.get('category', 'Uncategorized')
                    if not category or category.strip() == "":
                        category = 'Uncategorized'
                    
                    # Convert to positive for easier understanding
                    amount = abs(t.get('amount', 0))
                    
                    if category in category_spending:
                        category_spending[category] += amount
                    else:
                        category_spending[category] = amount
            
            # Get the top spending category
            top_category = max(category_spending.items(), key=lambda x: x[1]) if category_spending else ('None', 0)
            
            # Fetch budget data
            budgets_collection = get_collection(Collections.CATEGORY_BREAKDOWN)
            budgets = list(budgets_collection.find({"user_id": user_id}))
            
            # Add to user profile data
            user_profile['financial_data'] = {
                'total_income': total_income,
                'total_expenses': total_expenses,
                'category_spending': category_spending,
                'top_category': top_category[0],
                'top_category_amount': top_category[1],
                'budgets': budgets
            }
        
        result = ai_assistant.get_spending_advice(user_profile)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting spending advice: {str(e)}")

@app.post("/ai/budget-template")
async def get_budget_template(user_profile: UserProfile):
    """
    Generate a budget template based on user profile.
    This endpoint takes a user's profile information and returns
    a personalized budget template.
    
    Args:
        user_profile: User profile information
        
    Returns:
        Dictionary containing the budget template
        
    Raises:
        HTTPException: If AI features are not available or an error occurs
    """
    if not AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI features are not available")
    
    try:
        # Convert to dict for easier manipulation
        user_data = user_profile.dict()
        
        # Get user_id if provided
        user_id = user_data.get('user_id')
        
        # If user_id is provided, fetch additional data from database
        if user_id:
            # Fetch user's transactions
            transactions_collection = get_collection(Collections.TRANSACTIONS)
            transactions = list(transactions_collection.find({"user_id": user_id}))
            
            # Calculate spending by category
            category_spending = {}
            for t in transactions:
                # Determine if this is an expense
                is_expense = False
                
                # Check if we have a transaction type field
                if "type" in t:
                    is_expense = t["type"].lower() == "expense"
                # If no type field or type is not "expense", use category and amount
                if not is_expense:
                    # Any transaction with a category is considered an expense
                    category = t.get('category', '').strip()
                    is_expense = category != ""
                
                # For expenses, add to the category breakdown
                if is_expense:
                    category = t.get('category', 'Uncategorized')
                    if not category or category.strip() == "":
                        category = 'Uncategorized'
                    
                    # Convert to positive for easier understanding
                    amount = abs(t.get('amount', 0))
                    
                    if category in category_spending:
                        category_spending[category] += amount
                    else:
                        category_spending[category] = amount
            
            # Calculate income sources
            income_sources = {}
            for t in transactions:
                # Determine if this is income
                is_income = False
                
                # Check if we have a transaction type field
                if "type" in t:
                    is_income = t["type"].lower() == "income"
                # If no type field, use amount (positive = income)
                elif t.get('amount', 0) > 0 and not t.get('category', '').strip():
                    is_income = True
                
                # For income, add to the income sources
                if is_income:
                    source = t.get('category', 'Other Income')
                    if not source or source.strip() == "":
                        source = 'Other Income'
                    
                    amount = abs(t.get('amount', 0))
                    
                    if source in income_sources:
                        income_sources[source] += amount
                    else:
                        income_sources[source] = amount
            
            # Add to financial_data if it exists, or create it
            if 'financial_data' not in user_data:
                user_data['financial_data'] = {}
                
            user_data['financial_data'].update({
                'category_spending': category_spending,
                'income_sources': income_sources
            })
        
        result = ai_assistant.generate_budget_template(user_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating budget template: {str(e)}")

@app.post("/ai/analyze-goals")
async def analyze_financial_goals(goals_data: FinancialGoals):
    """
    Analyze financial goals and provide recommendations.
    This endpoint takes a list of financial goals and user context,
    and returns an analysis with recommendations.
    
    Args:
        goals_data: Object containing goals and user context
        
    Returns:
        Dictionary containing the goals analysis
        
    Raises:
        HTTPException: If AI features are not available or an error occurs
    """
    if not AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI features are not available")
    
    try:
        # Create a copy to avoid modifying the original
        goals = goals_data.goals.copy()
        user_context = goals_data.user_context.copy() if goals_data.user_context else {}
        
        # Get user_id if provided
        user_id = user_context.get('user_id')
        
        # If user_id is provided, fetch actual goals from database
        if user_id:
            # Fetch user's financial goals
            goals_collection = get_collection(Collections.FINANCIAL_GOALS)
            user_goals = list(goals_collection.find({"userId": user_id}))
            
            if user_goals:
                # Use actual goals from database
                goals = [goal.get('name', 'Unnamed Goal') for goal in user_goals]
                
                # Add goal details to context
                user_context['goal_details'] = [
                    {
                        'name': goal.get('name', 'Unnamed Goal'),
                        'target_amount': goal.get('targetAmount', 0),
                        'current_amount': goal.get('currentAmount', 0),
                        'category': goal.get('category', 'Other')
                    }
                    for goal in user_goals
                ]
                
            # Fetch user's transactions for financial context
            transactions_collection = get_collection(Collections.TRANSACTIONS)
            transactions = list(transactions_collection.find({"user_id": user_id}))
            
            # Calculate income and expenses
            total_income = sum(t['amount'] for t in transactions if t.get('type') == 'income')
            total_expenses = sum(t['amount'] for t in transactions if t.get('type') == 'expense')
            monthly_savings = total_income - total_expenses
            
            # Add financial details to context
            user_context.update({
                'monthly_income': total_income,
                'monthly_expenses': total_expenses,
                'monthly_savings': monthly_savings
            })
        
        result = ai_assistant.analyze_financial_goals(goals, user_context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing financial goals: {str(e)}")

@app.get("/your-endpoint")
async def read_items():
    """
    Example endpoint that uses MongoDB.
    
    Returns:
        Dictionary containing a message
    """
    # Use the get_collection function instead of request.app.mongodb
    collection = get_collection(Collections.USERS)
    count = collection.count_documents({})
    return {"message": f"Found {count} users in the database"}

# Authentication endpoints
@app.post("/api/auth/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """
    Authenticate a user and return a success message with user details.
    
    Args:
        login_data: Login credentials from request body
        
    Returns:
        Login response with success status and user details if successful
    """
    try:
        # Get the users collection
        users_collection = get_collection(Collections.USERS)
        
        # Find the user by username
        user = users_collection.find_one({"username": login_data.username})
        
        if not user:
            return {
                "success": False,
                "message": "Invalid username or password"
            }
        
        # Validate password (in a production app, compare hashed passwords)
        if user["password"] != login_data.password:
            return {
                "success": False,
                "message": "Invalid username or password"
            }
        
        return {
            "success": True,
            "message": "Login successful",
            "user_id": str(user["_id"]),
            "username": user["username"],
            "firstName": user.get("firstName", ""),
            "lastName": user.get("lastName", ""),
            "email": user.get("email", "")
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Login failed: {str(e)}"
        }

class RegisterRequest(BaseModel):
    """Model for user registration requests"""
    username: str
    email: str
    password: str
    firstName: str
    lastName: str

@app.post("/api/auth/register", response_model=LoginResponse)
async def register(register_data: RegisterRequest):
    """
    Register a new user and return a success message with user details.
    
    Args:
        register_data: Registration data from request body
        
    Returns:
        Login response with success status and user details if successful
    """
    try:
        # Get the users collection
        users_collection = get_collection(Collections.USERS)
        
        # Check if username already exists
        if users_collection.find_one({"username": register_data.username}):
            return {
                "success": False,
                "message": "Username already exists"
            }
        
        # Check if email already exists
        if users_collection.find_one({"email": register_data.email}):
            return {
                "success": False,
                "message": "Email already exists"
            }
        
        # Create new user document
        new_user = {
            "username": register_data.username,
            "email": register_data.email,
            "password": register_data.password,  # In production, hash the password
            "firstName": register_data.firstName,
            "lastName": register_data.lastName,
            "createdAt": datetime.now()
        }
        
        # Insert the new user
        result = users_collection.insert_one(new_user)
        
        return {
            "success": True,
            "message": "Registration successful",
            "user_id": str(result.inserted_id),
            "username": register_data.username,
            "firstName": register_data.firstName,
            "lastName": register_data.lastName,
            "email": register_data.email
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Registration failed: {str(e)}"
        }

# Financial data endpoints
@app.post("/api/transactions", response_model=TransactionResponse)
async def create_transaction(transaction: TransactionRequest):
    """
    Create a new financial transaction.
    
    Args:
        transaction: Transaction data from request body
        
    Returns:
        Created transaction information
    """
    try:
        # Get the transactions collection
        transactions_collection = get_collection(Collections.TRANSACTIONS)
        
        # Create transaction document
        transaction_data = transaction.model_dump()
        
        # Ensure we have a date (default to now if not provided)
        if transaction_data.get("date") is None:
            transaction_data["date"] = datetime.now()
        
        # Insert the transaction
        result = transactions_collection.insert_one(transaction_data)
        
        # Update associated budget if the category has a budget
        await update_budget_for_transaction(transaction_data)
        
        # Create a copy of the transaction data for response
        response_data = transaction_data.copy()
        # Add the ID of the inserted document
        response_data["id"] = str(result.inserted_id)
        # Convert date to ISO format string for JSON response
        if isinstance(response_data["date"], datetime):
            response_data["date"] = response_data["date"].isoformat()
            
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create transaction: {str(e)}")

async def update_budget_for_transaction(transaction):
    """
    Update the budget for a transaction's category.
    
    This helper function updates the appropriate budget when a transaction is created.
    It finds the budget for the transaction's category and updates the current amount.
    
    Args:
        transaction: Transaction data
        
    Returns:
        None
    """
    try:
        # Find budget with matching user ID and category
        budgets_collection = get_collection(Collections.CATEGORY_BREAKDOWN)
        budget = budgets_collection.find_one({
            "user_id": transaction["user_id"],
            "category": transaction["category"]
        })
        
        # If no budget exists for this category, there's nothing to update
        if not budget:
            return
        
        # Now we actually update the budget to maintain a running total
        # We'll add a field called 'spent' to track accumulated spending
        
        # Initialize spent field if it doesn't exist
        spent = budget.get('spent', 0)
        
        # Add the absolute amount of the transaction to the spent total
        # We use absolute value because transactions could be negative for expenses
        # Budget tracking needs positive values regardless of transaction type
        amount = abs(transaction["amount"])
        updated_spent = spent + amount
        
        # Update the budget with the new spent amount
        budgets_collection.update_one(
            {"_id": budget["_id"]},
            {"$set": {"spent": updated_spent}}
        )
        
    except Exception as e:
        # Log the error but don't fail the transaction creation
        print(f"Error updating budget for transaction: {str(e)}")

@app.get("/api/transactions/user/{user_id}", response_model=List[TransactionResponse])
async def get_user_transactions(user_id: str):
    """
    Get all transactions for a specific user.
    
    Args:
        user_id: ID of the user
        
    Returns:
        List of transactions
    """
    try:
        # Get the transactions collection
        transactions_collection = get_collection(Collections.TRANSACTIONS)
        
        # Find transactions for the user
        transactions = list(transactions_collection.find({"user_id": user_id}))
        
        # Format the response
        response_data = []
        for transaction in transactions:
            # Convert MongoDB _id to string
            transaction["id"] = str(transaction.pop("_id"))
            
            # Ensure date is in ISO format
            if isinstance(transaction["date"], datetime):
                transaction["date"] = transaction["date"].isoformat()
                
            response_data.append(transaction)
        
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get transactions: {str(e)}")

@app.post("/api/budgets", response_model=BudgetResponse)
async def create_budget(budget: BudgetRequest):
    """
    Create a new budget category for a user.
    
    Args:
        budget: Budget data from request body
        
    Returns:
        Created budget information
    """
    try:
        # Get the budgets collection (using CATEGORY_BREAKDOWN as the collection)
        budgets_collection = get_collection(Collections.CATEGORY_BREAKDOWN)
        
        # Check if budget already exists for this category and user
        existing_budget = budgets_collection.find_one({
            "user_id": budget.user_id,
            "category": budget.category,
            "period": budget.period
        })
        
        if existing_budget:
            # Update existing budget
            budgets_collection.update_one(
                {"_id": existing_budget["_id"]},
                {"$set": {"amount": budget.amount}}
            )
            
            # Format the response
            response_data = {
                "id": str(existing_budget["_id"]),
                "user_id": budget.user_id,
                "category": budget.category,
                "amount": budget.amount,
                "period": budget.period,
                "created_at": existing_budget.get("created_at", datetime.now()).isoformat()
            }
        else:
            # Create new budget document
            budget_data = budget.model_dump()
            budget_data["created_at"] = datetime.now()
            
            # Insert the budget
            result = budgets_collection.insert_one(budget_data)
            
            # Format the response
            response_data = budget_data.copy()
            response_data["id"] = str(result.inserted_id)
            response_data["created_at"] = response_data["created_at"].isoformat()
        
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create budget: {str(e)}")

@app.get("/api/budgets/user/{user_id}", response_model=List[BudgetResponse])
async def get_user_budgets(user_id: str):
    """
    Get all budgets for a specific user.
    
    Args:
        user_id: ID of the user
        
    Returns:
        List of budgets
    """
    try:
        # Get the budgets collection
        budgets_collection = get_collection(Collections.CATEGORY_BREAKDOWN)
        
        # Find budgets for the user
        budgets = list(budgets_collection.find({"user_id": user_id}))
        
        # Format the response
        response_data = []
        for budget in budgets:
            # Add spent field if it doesn't exist
            if 'spent' not in budget:
                budget['spent'] = 0
                
            budget["id"] = str(budget.pop("_id"))
            if isinstance(budget.get("created_at"), datetime):
                budget["created_at"] = budget["created_at"].isoformat()
            response_data.append(budget)
        
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get budgets: {str(e)}")

@app.put("/api/budgets/{budget_id}", response_model=BudgetResponse)
async def update_budget(budget_id: str, budget: BudgetRequest):
    """
    Update an existing budget.
    
    Args:
        budget_id: ID of the budget to update
        budget: Updated budget data from request body
        
    Returns:
        Updated budget information
    """
    try:
        # Get the budgets collection
        budgets_collection = get_collection(Collections.CATEGORY_BREAKDOWN)
        
        # Check if budget exists
        existing_budget = budgets_collection.find_one({"_id": ObjectId(budget_id)})
        if not existing_budget:
            raise HTTPException(status_code=404, detail="Budget not found")
        
        # Update budget document
        budget_data = budget.model_dump()
        
        # Update the budget
        budgets_collection.update_one(
            {"_id": ObjectId(budget_id)},
            {"$set": {
                "category": budget_data["category"],
                "amount": budget_data["amount"],
                "period": budget_data["period"],
                "updated_at": datetime.now()
            }}
        )
        
        # Get the updated budget
        updated_budget = budgets_collection.find_one({"_id": ObjectId(budget_id)})
        
        # Format the response
        response_data = {
            "id": str(updated_budget["_id"]),
            "user_id": updated_budget["user_id"],
            "category": updated_budget["category"],
            "amount": updated_budget["amount"],
            "period": updated_budget["period"],
            "created_at": updated_budget.get("created_at", datetime.now()).isoformat()
        }
        
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update budget: {str(e)}")

@app.delete("/api/budgets/{budget_id}")
async def delete_budget(budget_id: str):
    """
    Delete a budget.
    
    Args:
        budget_id: ID of the budget to delete
        
    Returns:
        Success message
    """
    try:
        # Get the budgets collection
        budgets_collection = get_collection(Collections.CATEGORY_BREAKDOWN)
        
        # Check if budget exists
        existing_budget = budgets_collection.find_one({"_id": ObjectId(budget_id)})
        if not existing_budget:
            raise HTTPException(status_code=404, detail="Budget not found")
        
        # Delete the budget
        budgets_collection.delete_one({"_id": ObjectId(budget_id)})
        
        return {"success": True, "message": "Budget deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete budget: {str(e)}")

# Financial analysis endpoints
@app.get("/api/analysis/spending/{user_id}", response_model=SpendingAnalysisResponse)
async def get_spending_analysis(
    user_id: str, 
    period: str = "monthly", 
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None
):
    """
    Get spending analysis for a user.
    
    Args:
        user_id: ID of the user
        period: Analysis period (daily, weekly, monthly, yearly)
        start_date: Start date for custom period (ISO format)
        end_date: End date for custom period (ISO format)
        
    Returns:
        Spending analysis data
    """
    try:
        # Get the transactions collection
        transactions_collection = get_collection(Collections.TRANSACTIONS)
        
        # Set date range based on period
        now = datetime.now()
        if start_date and end_date:
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
        elif period == "daily":
            start = datetime(now.year, now.month, now.day, 0, 0, 0)
            end = now
        elif period == "weekly":
            # Start from the beginning of the week (Monday)
            days_since_monday = now.weekday()
            start = datetime(now.year, now.month, now.day, 0, 0, 0) - timedelta(days=days_since_monday)
            end = now
        elif period == "yearly":
            start = datetime(now.year, 1, 1, 0, 0, 0)
            end = now
        else:  # Default to monthly
            start = datetime(now.year, now.month, 1, 0, 0, 0)
            end = now
        
        # Query transactions within the date range
        query = {
            "user_id": user_id,
            "date": {"$gte": start, "$lte": end}
        }
        
        transactions = list(transactions_collection.find(query))
        
        # Calculate total spending and category breakdown
        total_spending = 0
        category_breakdown = {}
        
        for transaction in transactions:
            amount = transaction["amount"]
            category = transaction["category"]
            
            # Determine if this is an expense based on amount, type, and category
            is_expense = False
            
            # Check if we have a transaction type field
            if "type" in transaction:
                is_expense = transaction["type"].lower() == "expense"
            # If no type field or type is not "expense", use category and amount
            if not is_expense:
                # Consider all categorized transactions as expenses
                # Changed: Any transaction with a category is considered an expense, not just negative amounts
                is_expense = category and category.strip() != ""
            
            # For expenses, add to the category breakdown
            if is_expense:
                # Convert to positive for easier understanding
                amount = abs(amount)
                total_spending += amount
                
                if category in category_breakdown:
                    category_breakdown[category] += amount
                else:
                    category_breakdown[category] = amount
        
        # Format the response
        response_data = {
            "total_spending": total_spending,
            "category_breakdown": category_breakdown,
            "period": period,
            "start_date": start.isoformat(),
            "end_date": end.isoformat()
        }
        
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get spending analysis: {str(e)}")

@app.get("/api/analysis/insights/{user_id}", response_model=SpendingInsightResponse)
async def get_spending_insights(user_id: str):
    """
    Get spending insights and recommendations for a user.
    
    Args:
        user_id: ID of the user
        
    Returns:
        Spending insights and recommendations
    """
    try:
        # Get the transactions and budgets collections
        transactions_collection = get_collection(Collections.TRANSACTIONS)
        budgets_collection = get_collection(Collections.CATEGORY_BREAKDOWN)
        
        # Get user's transactions for the current month
        now = datetime.now()
        start_of_month = datetime(now.year, now.month, 1, 0, 0, 0)
        
        transactions = list(transactions_collection.find({
            "user_id": user_id,
            "date": {"$gte": start_of_month}
        }))
        
        # Get user's budgets
        budgets = list(budgets_collection.find({"user_id": user_id}))
        
        # Calculate spending by category
        spending_by_category = {}
        for transaction in transactions:
            amount = transaction["amount"]
            category = transaction["category"]
            
            # Only count expenses (negative amounts)
            if amount < 0:
                amount = abs(amount)
                if category in spending_by_category:
                    spending_by_category[category] += amount
                else:
                    spending_by_category[category] = amount
        
        # Compare with budgets and generate insights
        insights = []
        recommendations = []
        
        # Create a dictionary of budgets by category
        budget_by_category = {budget["category"]: budget["amount"] for budget in budgets}
        
        # Check for categories where spending exceeds budget
        for category, spent in spending_by_category.items():
            if category in budget_by_category:
                budget = budget_by_category[category]
                percentage = (spent / budget) * 100
                
                if percentage > 90:
                    insights.append(f"You've spent {percentage:.1f}% of your {category} budget.")
                    
                    if percentage > 100:
                        recommendations.append(f"You've exceeded your {category} budget by ${spent - budget:.2f}. Consider adjusting your spending or increasing your budget.")
                    else:
                        recommendations.append(f"You're close to exceeding your {category} budget. Try to limit your spending in this category.")
            else:
                # No budget for this category
                insights.append(f"You've spent ${spent:.2f} on {category} without a budget.")
                recommendations.append(f"Consider creating a budget for {category} to track your spending better.")
        
        # Check for categories with budgets but no spending
        for category, budget in budget_by_category.items():
            if category not in spending_by_category:
                insights.append(f"You haven't spent anything on {category} yet this month.")
                recommendations.append(f"You have ${budget:.2f} available to spend on {category}.")
        
        # If no insights or recommendations, provide defaults
        if not insights:
            insights.append("Not enough data to generate insights.")
        
        if not recommendations:
            recommendations.append("Start by setting up budgets for your main spending categories.")
        
        return {
            "insights": insights,
            "recommendations": recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get spending insights: {str(e)}")

class UserProfileUpdateRequest(BaseModel):
    """Model for updating user profile information"""
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

class UserProfileResponse(BaseModel):
    """Model for user profile response"""
    userId: str
    username: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

class PasswordUpdateRequest(BaseModel):
    """Model for updating user password"""
    currentPassword: str
    newPassword: str

@app.get("/api/users/{user_id}/profile", response_model=UserProfileResponse)
async def get_user_profile(user_id: str):
    """
    Get profile information for a specific user.
    
    Args:
        user_id: ID of the user
        
    Returns:
        User profile information
    """
    try:
        # Get the users collection
        users_collection = get_collection(Collections.USERS)
        
        # Find the user by ID
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Split the name into first and last name if available
        name_parts = user.get("name", "").split(" ", 1)
        first_name = name_parts[0] if len(name_parts) > 0 else ""
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        # Format the response
        return {
            "userId": str(user["_id"]),
            "username": user.get("username", ""),
            "firstName": user.get("firstName", first_name),
            "lastName": user.get("lastName", last_name),
            "email": user.get("email", ""),
            "phone": user.get("phone", "")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user profile: {str(e)}")

@app.put("/api/users/{user_id}/profile", response_model=UserProfileResponse)
async def update_user_profile(user_id: str, profile_data: UserProfileUpdateRequest):
    """
    Update profile information for a specific user.
    
    Args:
        user_id: ID of the user
        profile_data: Profile data to update
        
    Returns:
        Updated user profile information
    """
    try:
        # Get the users collection
        users_collection = get_collection(Collections.USERS)
        
        # Find the user by ID
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create update document with only non-None fields
        update_data = {k: v for k, v in profile_data.model_dump().items() if v is not None}
        
        if update_data:
            # Update the user
            users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
        
        # Get the updated user
        updated_user = users_collection.find_one({"_id": ObjectId(user_id)})
        
        # Format the response
        return {
            "userId": str(updated_user["_id"]),
            "username": updated_user.get("username", ""),
            "firstName": updated_user.get("firstName", ""),
            "lastName": updated_user.get("lastName", ""),
            "email": updated_user.get("email", ""),
            "phone": updated_user.get("phone", "")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update user profile: {str(e)}")

@app.put("/api/users/{user_id}/password")
async def update_user_password(user_id: str, password_data: PasswordUpdateRequest):
    """
    Update password for a specific user.
    
    Args:
        user_id: ID of the user
        password_data: Current and new password
        
    Returns:
        Success message
    """
    try:
        # Get the users collection
        users_collection = get_collection(Collections.USERS)
        
        # Find the user by ID
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Verify current password
        if user.get("password") != password_data.currentPassword:
            return {"success": False, "message": "Current password is incorrect"}
        
        # Update the password
        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"password": password_data.newPassword}}
        )
        
        return {"success": True, "message": "Password updated successfully"}
    except Exception as e:
        return {"success": False, "message": f"Failed to update password: {str(e)}"}

# Financial Goal models
class GoalCreate(BaseModel):
    """Model for creating a new financial goal"""
    name: str
    category: str
    targetAmount: float
    currentAmount: float
    targetDate: datetime

class GoalResponse(BaseModel):
    """Model for goal response"""
    id: Optional[str] = None
    name: str
    category: str
    targetAmount: float
    currentAmount: float
    targetDate: str

# Financial Goal endpoints
@app.post("/api/goals")
async def create_goal(goal: GoalCreate, request: Request):
    """
    Create a new financial goal.
    
    Args:
        goal: Goal data from request body
        request: Request object containing authentication info
        
    Returns:
        Created goal information
    """
    try:
        # Get the goals collection
        goals_collection = get_collection(Collections.FINANCIAL_GOALS)
        
        # Create goal document with current user ID
        goal_data = goal.model_dump()
        
        # Get user ID from authentication
        # In a real app, this would come from the auth token
        # For now, we'll get it from the user stored in session or use a default
        user_id = None
        user_str = request.cookies.get("user") or request.headers.get("authorization")
        
        if user_str:
            try:
                if user_str.startswith("Bearer "):
                    user_str = user_str[7:]  # Remove "Bearer " prefix
                user_data = json.loads(user_str)
                user_id = user_data.get("id") or user_data.get("user_id")
            except:
                pass
        
        # Fallback to default user ID if not found
        if not user_id:
            user_id = "current_user_id"  # Fallback ID
            
        goal_data["userId"] = user_id
        
        # Insert the goal
        result = goals_collection.insert_one(goal_data)
        
        # Format the response - Create a new dict instead of modifying the original
        response_data = {
            "id": str(result.inserted_id),
            "name": goal_data["name"],
            "category": goal_data["category"],
            "targetAmount": goal_data["targetAmount"],
            "currentAmount": goal_data["currentAmount"],
            "userId": goal_data["userId"]
        }
        
        # Convert date to ISO format string for JSON response
        if isinstance(goal_data.get("targetDate"), datetime):
            response_data["targetDate"] = goal_data["targetDate"].isoformat()
        else:
            response_data["targetDate"] = goal_data.get("targetDate")
            
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create goal: {str(e)}")

@app.get("/api/goals")
async def get_goals(request: Request):
    """
    Get all financial goals for the current user.
    
    Args:
        request: Request object containing authentication info
        
    Returns:
        List of goals
    """
    try:
        # Get the goals collection
        goals_collection = get_collection(Collections.FINANCIAL_GOALS)
        
        # Get user ID from authentication
        # In a real app, this would come from the auth token
        # For now, we'll get it from the user stored in session or use a default
        user_id = None
        user_str = request.cookies.get("user") or request.headers.get("authorization")
        
        if user_str:
            try:
                if user_str and user_str.startswith("Bearer "):
                    user_str = user_str[7:]  # Remove "Bearer " prefix
                user_data = json.loads(user_str)
                user_id = user_data.get("id") or user_data.get("user_id")
            except:
                pass
        
        # Fallback to default user ID if not found
        if not user_id:
            user_id = "current_user_id"  # Fallback ID
        
        # Find goals for the user
        goals = list(goals_collection.find({"userId": user_id}))
        
        # Format the response
        response_data = []
        for goal in goals:
            # Create a new dict with properly converted values
            goal_data = {
                "id": str(goal["_id"]),
                "name": goal.get("name", ""),
                "category": goal.get("category", ""),
                "targetAmount": goal.get("targetAmount", 0),
                "currentAmount": goal.get("currentAmount", 0),
                "userId": goal.get("userId", "")
            }
            
            # Ensure date is in ISO format
            if isinstance(goal.get("targetDate"), datetime):
                goal_data["targetDate"] = goal["targetDate"].isoformat()
            else:
                goal_data["targetDate"] = str(goal.get("targetDate", ""))
                
            response_data.append(goal_data)
        
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get goals: {str(e)}")

@app.get("/api/goals/user/{user_id}")
async def get_user_goals(user_id: str):
    """
    Get all financial goals for a specific user.
    
    Args:
        user_id: ID of the user
        
    Returns:
        List of goals
    """
    try:
        # Validate user_id
        if not user_id or user_id.strip() == "":
            return []
        
        # Get the goals collection
        goals_collection = get_collection(Collections.FINANCIAL_GOALS)
        
        # Find goals for the user - try both with userId and user_id fields
        goals = list(goals_collection.find({"$or": [{"userId": user_id}, {"user_id": user_id}]}))
        
        # Format the response
        response_data = []
        for goal in goals:
            # Create a new dict with properly converted values
            goal_data = {
                "id": str(goal["_id"]),
                "name": goal.get("name", ""),
                "category": goal.get("category", ""),
                "targetAmount": goal.get("targetAmount", 0),
                "currentAmount": goal.get("currentAmount", 0),
                "userId": goal.get("userId", "") or goal.get("user_id", "")
            }
            
            # Ensure date is in ISO format
            if isinstance(goal.get("targetDate"), datetime):
                goal_data["targetDate"] = goal["targetDate"].isoformat()
            else:
                goal_data["targetDate"] = str(goal.get("targetDate", ""))
                
            response_data.append(goal_data)
        
        return response_data
    except Exception as e:
        # Log the error but return empty list instead of raising an exception
        print(f"Error getting user goals: {str(e)}")
        return []

@app.put("/api/goals/{goal_id}")
async def update_goal(goal_id: str, goal: GoalCreate):
    """
    Update an existing financial goal.
    
    Args:
        goal_id: ID of the goal to update
        goal: Updated goal data from request body
        
    Returns:
        Updated goal information
    """
    try:
        # Get the goals collection
        goals_collection = get_collection(Collections.FINANCIAL_GOALS)
        
        # Check if goal exists
        existing_goal = goals_collection.find_one({"_id": ObjectId(goal_id)})
        if not existing_goal:
            raise HTTPException(status_code=404, detail="Goal not found")
        
        # Update goal document
        goal_data = goal.model_dump()
        
        # Update the goal
        goals_collection.update_one(
            {"_id": ObjectId(goal_id)},
            {"$set": {
                "name": goal_data["name"],
                "category": goal_data["category"],
                "targetAmount": goal_data["targetAmount"],
                "currentAmount": goal_data["currentAmount"],
                "targetDate": goal_data["targetDate"],
                "updatedAt": datetime.now()
            }}
        )
        
        # Get the updated goal
        updated_goal = goals_collection.find_one({"_id": ObjectId(goal_id)})
        
        # Format the response with safe access to keys
        response_data = {
            "id": str(updated_goal["_id"]),
            "name": updated_goal.get("name", ""),
            "category": updated_goal.get("category", ""),
            "targetAmount": updated_goal.get("targetAmount", 0),
            "currentAmount": updated_goal.get("currentAmount", 0),
            "userId": updated_goal.get("userId", "")
        }
        
        # Handle the date format safely
        if isinstance(updated_goal.get("targetDate"), datetime):
            response_data["targetDate"] = updated_goal["targetDate"].isoformat()
        else:
            response_data["targetDate"] = str(updated_goal.get("targetDate", ""))
        
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update goal: {str(e)}")

@app.delete("/api/goals/{goal_id}")
async def delete_goal(goal_id: str):
    """
    Delete a financial goal.
    
    Args:
        goal_id: ID of the goal to delete
        
    Returns:
        Success message
    """
    try:
        # Get the goals collection
        goals_collection = get_collection(Collections.FINANCIAL_GOALS)
        
        # Check if goal exists
        existing_goal = goals_collection.find_one({"_id": ObjectId(goal_id)})
        if not existing_goal:
            raise HTTPException(status_code=404, detail="Goal not found")
        
        # Delete the goal
        goals_collection.delete_one({"_id": ObjectId(goal_id)})
        
        return {"success": True, "message": "Goal deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete goal: {str(e)}")

def get_category_spending(user_id, category='Food'):
    """
    Get spending data for a specific category from a user's transaction history.
    
    Args:
        user_id: ID of the user whose spending to analyze
        category: The spending category to analyze (default: 'Food')
        
    Returns:
        Dictionary containing:
        - total_spent: Total amount spent in the category
        - transactions: List of transactions in the category
        - percentage: Percentage of total expenses this category represents
        - time_period: Period covered by the data
    """
    try:
        # Get the transactions collection
        transactions_collection = get_collection(Collections.TRANSACTIONS)
        
        # Filter transactions for the user and category
        # NOTE: Category matching handles case variations (Food, food, FOOD)
        query = {
            "user_id": user_id,
            "$or": [
                {"category": {"$regex": f"^{category}$", "$options": "i"}},  # Exact match with case insensitivity
                {"category": {"$regex": f"{category}", "$options": "i"}}  # Contains category name
            ]
        }
        
        category_transactions = list(transactions_collection.find(query))
        
        # Calculate total spent in this category
        total_spent = sum(transaction['amount'] for transaction in category_transactions)
        
        # Get all expenses to calculate percentage - handle transactions with or without type field
        all_expenses_query = {
            "user_id": user_id,
            "$or": [
                {"type": "expense"},  # Transactions with type=expense
                {"category": {"$exists": True, "$ne": ""}}  # Transactions with a category (assumed to be expenses)
            ]
        }
        all_expenses = list(transactions_collection.find(all_expenses_query))
        
        # Sum all expenses, considering transactions with explicit type or just by category
        total_expenses = 0
        for transaction in all_expenses:
            # If the transaction has a type field and it's not 'expense', skip it
            if 'type' in transaction and transaction['type'] != 'expense':
                continue
            # Add the transaction amount to total expenses
            total_expenses += transaction['amount']
        
        # Calculate percentage of total expenses
        percentage = (total_spent / total_expenses * 100) if total_expenses > 0 else 0
        
        # Determine time period for the data (from oldest to newest transaction)
        if category_transactions:
            oldest_transaction = min(category_transactions, key=lambda t: t.get('date', datetime.now()))
            newest_transaction = max(category_transactions, key=lambda t: t.get('date', datetime.now()))
            
            if 'date' in oldest_transaction and 'date' in newest_transaction:
                oldest_date = oldest_transaction['date']
                newest_date = newest_transaction['date']
                if isinstance(oldest_date, datetime) and isinstance(newest_date, datetime):
                    time_period = f"{oldest_date.strftime('%b %d, %Y')} to {newest_date.strftime('%b %d, %Y')}"
                else:
                    time_period = "All time"
            else:
                time_period = "All time"
        else:
            time_period = "All time"
        
        # Format transaction data for response
        transactions_data = [
            {
                "description": t.get('description', 'No description'),
                "amount": t.get('amount', 0),
                "date": t.get('date').isoformat() if isinstance(t.get('date'), datetime) else str(t.get('date', '')),
                "category": t.get('category', 'Unknown')
            }
            for t in category_transactions
        ]
        
        return {
            "total_spent": total_spent,
            "transactions": transactions_data,
            "percentage": percentage,
            "time_period": time_period,
            "transaction_count": len(category_transactions)
        }
    except Exception as e:
        return {
            "error": f"Error retrieving {category} spending data: {str(e)}",
            "total_spent": 0,
            "transactions": [],
            "percentage": 0,
            "time_period": "Unknown",
            "transaction_count": 0
        }

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint for the API.
    Returns the status of the API and its dependencies.
    """
    try:
        # Check MongoDB connection
        db = get_collection(Collections.USERS)
        db.find_one({})  # Simple query to check connection
        
        return {
            "status": "healthy",
            "message": "API and database are operational",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"API check failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

