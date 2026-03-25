import os
import base64
from mimetypes import guess_type

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from logger import log_message

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env")

# Use a model that can handle both text and image inputs
llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0.7,
    max_tokens=500,
    openai_api_key=OPENAI_API_KEY
)

# ---------------- WORKOUT PROMPT ----------------
workout_prompt = PromptTemplate(
    input_variables=["fitness_level", "goal", "duration", "equipment"],
    template=(
        "Create a personalized workout plan for a {fitness_level} individual "
        "whose goal is {goal}. The workout should last {duration} minutes "
        "and use {equipment} equipment. Provide step-by-step exercises."
    ),
)

def generate_workout(fitness_level, goal, duration, equipment):
    prompt = workout_prompt.format(
        fitness_level=fitness_level,
        goal=goal,
        duration=duration,
        equipment=equipment
    )
    try:
        response = llm.invoke(prompt)
        log_message("Workout plan generated successfully.")
        return response.content
    except Exception as e:
        log_message(f"Workout generation failed: {str(e)}", "error")
        return f"Error: {str(e)}"


# ---------------- IMAGE ANALYSIS HELPERS ----------------
def encode_image_to_data_url(image_path: str) -> str:
    """Convert local image to base64 data URL."""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    mime_type, _ = guess_type(image_path)
    if mime_type is None:
        mime_type = "image/jpeg"

    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")

    return f"data:{mime_type};base64,{base64_image}"


def analyze_diet_image(image_path: str):
    """
    Analyze a food/diet image and return food intake details.
    """
    try:
        image_data_url = encode_image_to_data_url(image_path)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a nutrition assistant. Analyze the meal image carefully. "
                    "Identify visible food items and estimate nutrition."
                ),
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Look at this meal image and provide:\n"
                            "1. List of visible food items\n"
                            "2. Estimated portion size of each item\n"
                            "3. Estimated calories\n"
                            "4. Approximate protein, carbs, and fats\n"
                            "5. Whether the meal supports weight loss, muscle gain, or maintenance\n"
                            "6. Suggestions for improvement\n\n"
                            "Be clear that values are estimates if uncertain."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_data_url
                        },
                    },
                ],
            },
        ]

        response = llm.invoke(messages)
        log_message("Diet image analyzed successfully.")
        return response.content

    except Exception as e:
        log_message(f"Diet image analysis failed: {str(e)}", "error")
        return f"Error: {str(e)}"


# ---------------- DIET PLAN PROMPT ----------------
diet_prompt = PromptTemplate(
    input_variables=[
        "goal",
        "weight",
        "height",
        "age",
        "gender",
        "activity_level",
        "diet_preference",
        "meals_per_day"
    ],
    template=(
        "Create a one-day personalized diet plan for a person with the following details:\n"
        "Goal: {goal}\n"
        "Weight: {weight} kg\n"
        "Height: {height} cm\n"
        "Age: {age}\n"
        "Gender: {gender}\n"
        "Activity level: {activity_level}\n"
        "Diet preference: {diet_preference}\n"
        "Meals per day: {meals_per_day}\n\n"
        "Please provide:\n"
        "1. Total daily calorie target\n"
        "2. Suggested macro split (protein, carbs, fats)\n"
        "3. Breakfast\n"
        "4. Lunch\n"
        "5. Dinner\n"
        "6. Snacks\n"
        "7. Portion guidance\n"
        "8. Simple tips to follow the diet plan\n\n"
        "Keep the plan practical, easy to follow, and aligned with the goal."
    ),
)

def generate_diet_plan(goal, weight, height, age, gender, activity_level, diet_preference, meals_per_day):
    """
    Generate a daily diet plan according to user's goal.
    """
    prompt = diet_prompt.format(
        goal=goal,
        weight=weight,
        height=height,
        age=age,
        gender=gender,
        activity_level=activity_level,
        diet_preference=diet_preference,
        meals_per_day=meals_per_day
    )

    try:
        response = llm.invoke(prompt)
        log_message("Diet plan generated successfully.")
        return response.content
    except Exception as e:
        log_message(f"Diet plan generation failed: {str(e)}", "error")
        return f"Error: {str(e)}"


if __name__ == "__main__":
    # testworkout = generate_workout("Beginner", "Weight Loss", "30", "Bodyweight")
    # print("Generated workout plan:\n", testworkout)

    # testdiet = analyze_diet_image("diet.jpg")  # replace with your image path
    # print("\nDiet image analysis:\n", testdiet)

    daily_diet = generate_diet_plan(
        goal="Weight Loss",
        weight=70,
        height=170,
        age=25,
        gender="Male",
        activity_level="Moderately Active",
        diet_preference="Vegetarian",
        meals_per_day=4
    )
    print("\nGenerated daily diet plan:\n", daily_diet)