from fastapi import FastAPI, Depends, HTTPException,UploadFile, File
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from workout_generator import generate_workout,generate_diet_plan,analyze_diet_image
from chat_agent import chat_with_ai,clear_conversation
from logger import log_message
from database2 import Base, engine, get_db, User,init_db,save_workout,get_user_by_username
from auth import hash_password, verify_password, create_access_token
import tempfile
import sys
import os

app = FastAPI()

@app.on_event("startup")
def startup():
    init_db()

Base.metadata.create_all(bind=engine)


class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    age: int | None = None
    fitness_level: str | None = None
    goal: str | None = None
    equipment: str | None = None


class LoginRequest(BaseModel):
    username_or_email: str
    password: str


@app.get("/")
def home():
    return {"message": "Diet Tracker API is running"}


@app.post("/signup")
def signup(user: SignupRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    hashed_password = hash_password(user.password)

    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        age=user.age,
        fitness_level=user.fitness_level,
        goal=user.goal,
        equipment=user.equipment
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User created successfully",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email
        }
    }


@app.post("/login")
def login(user: LoginRequest, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(
        (User.username == user.username_or_email) |
        (User.email == user.username_or_email)
    ).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid username/email or password")

    if not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username/email or password")

    access_token = create_access_token(
        data={
            "sub": db_user.username,
            "email": db_user.email,
            "user_id": db_user.id
        }
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer"
    }


#-----------------------------------workoutplan----------------------------------------

class workoutRequest(BaseModel):
    fitness_level:str
    goal:str
    duration:int
    equipment:str

@app.post("/workout/{username}")
def get_user_workout(data: workoutRequest,username:str):
    user = get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    
    workout = generate_workout(
        fitness_level=data.fitness_level,
        goal=data.goal,
        duration=data.duration,
        equipment=data.equipment
    )

    save_workout(user_id=user.id,workout_plan=workout)
    return {
            "message":"Workout Plan generated successfully",
            "workout_plan":workout
    }

#------------------Generate Diet Plan -------------------------------

class DietPlanRequest(BaseModel):
    goal:str
    weight:float
    height:float
    age:int
    gender:str
    activity_level:str
    diet_preference:str
    meals_per_day:int


@app.post("/diet_plan{username}")
def create_diet_paln(data:DietPlanRequest,username:str):
    try:
        user = get_user_by_username(username)
        if not user:
            raise HTTPException(status_code=404,detail="User not found")
        
        plan = generate_diet_plan(
            goal=data.goal,
            weight=data.weight,
            height=data.height,
            age=data.age,
            gender=data.gender,
            activity_level=data.activity_level,
            diet_preference=data.diet_preference,
            meals_per_day=data.meals_per_day
        )
        save_workout(user_id=user.id , workout_plan=plan)

        return {
            "message":"Diet Plan generated successfully",
            "diet_plan":plan
        }
    except Exception as e:
        log_message(f"Diet plan API error: {str(e)}", "error")
        raise HTTPException(status_code=500, detail=str(e))
    

#-------------------------- Analyzing the food ------------------------------

@app.post("/analyze_food_image/{username}")
async def analyze_food_image_api(username: str, file: UploadFile = File(...)):
    user = get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    temp_path = None
    try:
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Please upload a valid image file")

        suffix = os.path.splitext(file.filename)[1] if file.filename else ".jpg"

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            contents = await file.read()
            tmp.write(contents)
            temp_path = tmp.name

        result = analyze_diet_image(temp_path)
        save_workout(user_id=user.id,workout_plan=result)

        return {
            "message": f"Food image analyzed successfully for {username}",
            "filename": file.filename,
            "analysis": result
        }

    except HTTPException:
        raise
    except Exception as e:
        log_message(f"Food image API error: {str(e)}", "error")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

#-------------------Chat_with_Coach-------------------------------

class ChatRequest(BaseModel):
    session_id:str
    message:str

class ChatResponse(BaseModel):
    session_id:str
    reply:str

@app.post("/chat{username}",response_model=ChatResponse)
def chat_endpoint(data:ChatRequest,username):
    user = get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    
    try:
        reply = chat_with_ai(data.session_id,data.message)
        save_workout(user_id=user.id,workout_plan=reply)
        return {
            "session_id":data.session_id,
            "reply":reply
        }
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    

@app.delete("/chat/{session_id}")
def clear_chat_endpoint(session_id:str):
    try:
        clear_conversation(session_id)
        return {"message":f"Chat cleared for session {session_id}"}
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))