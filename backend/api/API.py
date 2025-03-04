from fastapi import FastAPI
from pydantic import BaseModel
import sys
import os
from fastapi import FastAPI, APIRouter, Request, Body, HTTPException
from bson import ObjectId
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from fastapi.middleware.cors import CORSMiddleware

# Add path to backend directory to import AI modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from AI.website_ai_assistant import WebsiteAIAssistant

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize AI assistant
ai_assistant = WebsiteAIAssistant()

class Student(BaseModel):
    firstname: str | None = None        
    lastname: str | None = None
    username: str | None = None
    email: str | None = None

class UserQuery(BaseModel):
    query: str
    user_context: Dict[str, Any] = None

class UserProfile(BaseModel):
    year_in_school: str
    major: str
    monthly_income: float
    financial_aid: float
    age: Optional[int] = None
    gender: Optional[str] = None
    preferred_payment_method: Optional[str] = None

class FinancialGoals(BaseModel):
    goals: List[str]
    user_context: Dict[str, Any]

newuser = Student()

def create_user(email, username, firstname, lastname):
    newuser.lastname  = lastname
    newuser.username = username
    newuser.email  = email
    newuser.first_name = firstname

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
    return {"message": "Hello World"}

@app.get("/get-student/{student_id}")
def get_student(student_id: int):
    return students[student_id]

@app.get("/items/{item_id}")
async def read_item(item_id):
    return {"item_id": item_id}

# Signup endpoint with the POST method
@app.post("/signup/{email}/{username}")
def addUser(email, username: str):
    user_exists = False
    data = create_user(email, username)

    # Covert data to dict so it can be easily inserted to MongoDB
    dict(data)

    # Checks if an email exists from the collection of users
    if connection.db.users.find(
        {'email': data['email']}
        ).count() > 0:
        user_exists = True
        print("Customer Exists")
        return {"message":"Customer Exists"}
    # If the email doesn't exist, create the user
    elif user_exists == False:
        connection.db.users.insert_one(data)
        return {"message":"User Created","email": data['email'], "name": data['name']}



@app.post("/")
async def create_item(request: Request, student: Student):
    db = request.app.mongodb["collection_name"]
    result = await db.insert_one(student.dict())
    return {"id": str(result.inserted_id)}

@app.put("/{id}")
async def update_item(request: Request, id: str, student: Student):
    db = request.app.mongodb["collection_name"]
    result = await db.update_one({"_id": ObjectId(id)}, {"$set": student.dict()})
    return {"updated_count": result.modified_count}

#Real one - Put/update email
@app.put("/customer/{email}")
async def update_item(request: Request, email: str, student: Student):
    db = request.app.mongodb["collection_name"] #change collection name to DB name
    result = await db.update_one({"email": email}, {"$set": student.dict()})
    return {"updated_count": result.modified_count}


#Real one - Put/update firstname
@app.put("/{firstname}") #add httpexectpion
async def update_item(request: Request, firstname: str, student: Student):
    db = request.app.mongodb["collection_name"] #change collection name to DB name
    result = await db.update_one({"firstname": firstname}, {"$set": student.dict()})
    return {"updated_count": result.modified_count}


@app.put("/{lastname}")#add httpexecption
async def update_item(request: Request, lastname: str, student: Student):
    db = request.app.mongodb["collection_name"] #change collection name to DB name
    result = await db.update_one({"lastname": lastname}, {"$set": student.dict()})
    return {"updated_count": result.modified_count}    


@app.put("/{username}")#add httpexpection
async def update_item(request: Request, username: str, student: Student):
    db = request.app.mongodb["collection_name"] #change collection name to DB name
    result = await db.update_one({"username": str}, {"$set": student.dict()})
    return {"updated_count": result.modified_count}


# the one I base it off of
@app.put("/{id}")
async def update_item(request: Request, id: str, student: Student):
    db = request.app.mongodb["collection_name"]
    result = await db.update_one({"_id": ObjectId(id)}, {"$set": student.dict()})
    return {"updated_count": result.modified_count}


#########################################################################################################
########################################  ALL OF THE GETS   #############################################
#########################################################################################################
@app.get("/{username}")
async def read_items(request: Request, username: str):
    db = request.app.mongodb["collection_name"] #change to name of collection
    items = await db.find_one({"username": username})
  #  if items is None:
     #   raise HTTPExeption(status_code=404, detail="Person not found")
    return items


@app.get("/{lastname}")
async def read_items(request: Request, lastname: str):
    db = request.app.mongodb["collection_name"] #change to name of collection
    items = await db.find_one({"lastname": lastname})
   # if items is None:
     #   raise HTTPExeption(status_code=404, detail="Person not found")
    return items


@app.get("/{firstname}")
async def read_items(request: Request, firstname: str):
    db = request.app.mongodb["collection_name"] #change to name of collection
    items = await db.find_one({"firstname": firstname})
   # if items is None:
    #    raise HTTPExeption(status_code=404, detail="Person not found")
    return items


@app.get("/{email}")
async def read_items(request: Request, email: str):
    db = request.app.mongodb["collection_name"] #change to name of collection
    items = await db.find_one({"email": email})
   # if items is None:
    #    raise HTTPExeption(status_code=404, detail="Person not found")
    return items


@app.get("/{id}")
async def read_items(request: Request, id: str):
    db = request.app.mongodb["collection_name"] #change to name of collection
    items = await db.find_one({"id": id})
   # if items is None:
    #    raise HTTPExeption(status_code=404, detail="Person not found")
    return items


@app.get("/")
async def read_items(request: Request):
    db = request.app.mongodb["collection_name"]#change collection name
    items = await db.find({}).to_list(100)
    for item in items:
        item["_custid"] = str(item["_custid"])
    return items






@app.delete("/{id}")
async def delete_item(request: Request, id: str):
    db = request.app.mongodb["collection_name"]
    result = await db.delete_one({"_id": ObjectId(id)})
    return {"deleted_count": result.deleted_count}


@app.delete("/{username}")
async def delete_item(request: Request, username: str):
    db = request.app.mongodb["collection_name"]
    result = await db.delete_one({"username": str})
    return {"deleted_count": result.deleted_count}

# AI Assistant Endpoints

@app.post("/ai/query")
async def process_query(user_query: UserQuery):
    """
    Process a user query using the AI assistant
    """
    try:
        result = ai_assistant.process_user_query(user_query.query, user_query.user_context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/ai/spending-advice")
async def get_spending_advice(user_data: UserProfile):
    """
    Get personalized spending advice based on user profile
    """
    try:
        result = ai_assistant.get_spending_advice(user_data.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating spending advice: {str(e)}")

@app.post("/ai/budget-template")
async def get_budget_template(user_profile: UserProfile):
    """
    Generate a personalized budget template
    """
    try:
        result = ai_assistant.get_budget_template(user_profile.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating budget template: {str(e)}")

@app.post("/ai/analyze-goals")
async def analyze_financial_goals(goals_data: FinancialGoals):
    """
    Analyze and provide feedback on financial goals
    """
    try:
        result = ai_assistant.analyze_financial_goals(goals_data.goals, goals_data.user_context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing financial goals: {str(e)}")

