from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from database import get_user, add_user, save_workout
from workout_generator import generate_workout,generate_diet_plan,analyze_diet_image
from chat_agent import chat_with_ai
from logger import log_message
import tempfile
import sys
import os

app = FastAPI()

class UserRequest(BaseModel):
    name:str
    age:int
    fitness_level:str
    goal:str
    equipment:str


@app.get("/")
def root():
    return {"message":"Welcome to the AI Fitness Coach API "}

@app.post("/user")
def register_user(user:UserRequest):
    if get_user(user.name):
        raise HTTPException(status_code=400, detail="User already exist")
    
    add_user(
        name=user.name,
        age=user.age,
        fitness_level=user.fitness_level,
        goal=user.goal,
        equipment=user.equipment
    )

    return {"message":f"User '{user.name}' register successfully"}


#---------------Generate workoutplan -------------------------

@app.get("/workout/{username}")
def get_user_workout(username:str):
    user = get_user(username)
    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    
    workout = generate_workout(
        fitness_level=user.fitness_level,
        goal=user.goal,
        duration=30,
        equipment=user.equipment
    )

    save_workout(user_id=user.id,workout_plan=workout)
    return {
        "username":user.name,
        "goal":user.goal,
        "fitness_level":user.fitness_level,
        "equipment":user.equipment,
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
        user = get_user(username)
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
    user = get_user(username)
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
