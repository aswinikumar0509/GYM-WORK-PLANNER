import os
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from logger import log_message

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env")

llm = ChatOpenAI(model="gpt-4", temperature=0.7, openai_api_key=OPENAI_API_KEY)

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
    

if __name__=="__main__":
    testworkout = generate_workout("Beginner","Weight Loss","30","Bodyweight")
    print("Generated plan",testworkout)
