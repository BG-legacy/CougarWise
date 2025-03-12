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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
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
        result = ai_assistant.get_spending_advice(user_data.dict())
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
        result = ai_assistant.generate_budget_template(user_profile.dict())
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
        result = ai_assistant.analyze_financial_goals(goals_data.goals, goals_data.user_context)
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
        
        # Check if user exists and password matches
        if user and user["password"] == login_data.password:  # In production, use proper password hashing
            return {
                "success": True,
                "message": "Login successful",
                "user_id": str(user["_id"]),
                "username": user["username"]
            }
        else:
            return {
                "success": False,
                "message": "Invalid username or password"
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
    name: str

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
            "name": register_data.name,
            "createdAt": datetime.now()
        }
        
        # Insert the new user
        result = users_collection.insert_one(new_user)
        
        return {
            "success": True,
            "message": "Registration successful",
            "user_id": str(result.inserted_id),
            "username": register_data.username
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
        if transaction_data.get("date") is None:
            transaction_data["date"] = datetime.now()
        
        # Insert the transaction
        result = transactions_collection.insert_one(transaction_data)
        
        # Format the response
        response_data = transaction_data.copy()
        response_data["id"] = str(result.inserted_id)
        response_data["date"] = response_data["date"].isoformat()
        response_data["user_id"] = response_data.pop("user_id")  # Rename to match response model
        
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create transaction: {str(e)}")

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
            transaction["id"] = str(transaction.pop("_id"))
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
            budget["id"] = str(budget.pop("_id"))
            if isinstance(budget.get("created_at"), datetime):
                budget["created_at"] = budget["created_at"].isoformat()
            response_data.append(budget)
        
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get budgets: {str(e)}")

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
            
            # Only count expenses (negative amounts) for spending analysis
            if amount < 0:
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

