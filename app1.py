import os
import tempfile
import streamlit as st
from dotenv import load_dotenv

from workout_generator import generate_workout, generate_diet_plan, analyze_diet_image
from chat_agent import create_conversation, chat_with_ai

load_dotenv()

st.set_page_config(
    page_title="FitAI",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a, #111827, #1e293b);
    color: white;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}

.hero {
    background: linear-gradient(90deg, rgba(59,130,246,0.25), rgba(16,185,129,0.20));
    border: 1px solid rgba(255,255,255,0.08);
    padding: 28px;
    border-radius: 24px;
    margin-bottom: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.20);
}

.hero h1 {
    margin: 0;
    font-size: 2.5rem;
    color: white;
}

.hero p {
    margin-top: 8px;
    color: #cbd5e1;
    font-size: 1.05rem;
}

.card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(10px);
    border-radius: 22px;
    padding: 22px;
    margin-bottom: 18px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.18);
}

.section-title {
    font-size: 1.35rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 14px;
}

.stButton > button {
    width: 100%;
    border: none;
    border-radius: 14px;
    padding: 0.8rem 1rem;
    font-weight: 700;
    font-size: 1rem;
    color: white;
    background: linear-gradient(90deg, #2563eb, #06b6d4);
    box-shadow: 0 8px 20px rgba(37,99,235,0.35);
    transition: 0.2s ease-in-out;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 26px rgba(6,182,212,0.35);
}

.stTextInput > div > div > input,
.stNumberInput input,
.stTextArea textarea {
    background-color: rgba(255,255,255,0.08) !important;
    color: white !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
}

.stSelectbox div[data-baseweb="select"] > div {
    background-color: rgba(255,255,255,0.08) !important;
    color: white !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
}

div[data-baseweb="radio"] > div {
    color: white !important;
}

[data-testid="stFileUploader"],
[data-testid="stCameraInput"] {
    background: rgba(255,255,255,0.04);
    border: 1px dashed rgba(255,255,255,0.18);
    border-radius: 18px;
    padding: 16px;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    background: rgba(255,255,255,0.04);
    padding: 10px;
    border-radius: 18px;
}

.stTabs [data-baseweb="tab"] {
    height: 52px;
    border-radius: 14px;
    padding: 0 20px;
    color: white;
    font-weight: 600;
    background: rgba(255,255,255,0.05);
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg, #2563eb, #14b8a6) !important;
    color: white !important;
}

.metric-card {
    background: rgba(255,255,255,0.05);
    border-radius: 18px;
    padding: 18px;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.08);
}

[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 10px 14px;
    margin-bottom: 10px;
}

[data-testid="stChatInput"] {
    background: rgba(255,255,255,0.05);
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.10);
}

hr {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.08);
    margin: 1rem 0;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------- HERO ----------
st.markdown("""
<div class="hero">
    <h1>🔥 FitAI Planner</h1>
    <p>Create workout plans, build diet plans, analyze meal photos, and chat with your AI fitness coach.</p>
</div>
""", unsafe_allow_html=True)

# ---------- TOP METRICS ----------
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown('<div class="metric-card"><h3>🏋️ Workout</h3><p>Custom plans by goal</p></div>', unsafe_allow_html=True)
with m2:
    st.markdown('<div class="metric-card"><h3>🥗 Diet</h3><p>Daily goal-based meals</p></div>', unsafe_allow_html=True)
with m3:
    st.markdown('<div class="metric-card"><h3>📸 Scan Meals</h3><p>Upload or click images</p></div>', unsafe_allow_html=True)
with m4:
    st.markdown('<div class="metric-card"><h3>💬 Coach</h3><p>Ask fitness questions</p></div>', unsafe_allow_html=True)

st.write("")

# ---------- TABS ----------
tab1, tab2, tab3, tab4 = st.tabs([
    "🏋️ Workout Planner",
    "🥗 Diet Planner",
    "📸 Diet Image Analyzer",
    "💬 AI Fitness Coach"
])

# ---------- WORKOUT TAB ----------
with tab1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Personalized Workout Generator</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        fitness_level = st.selectbox(
            "Fitness Level",
            ["Beginner", "Intermediate", "Advanced"]
        )
        workout_goal = st.selectbox(
            "Goal",
            ["Weight Loss", "Muscle Gain", "Maintenance", "Strength", "Endurance"]
        )

    with c2:
        duration = st.number_input(
            "Workout Duration (minutes)",
            min_value=10,
            max_value=180,
            value=30
        )
        equipment = st.selectbox(
            "Equipment",
            ["Bodyweight", "Dumbbells", "Resistance Bands", "Gym Equipment", "Mixed"]
        )

    if st.button("Generate Workout Plan", key="workout_btn"):
        with st.spinner("Generating your workout plan..."):
            result = generate_workout(
                fitness_level=fitness_level,
                goal=workout_goal,
                duration=duration,
                equipment=equipment
            )

        st.success("Workout plan generated successfully.")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Your Workout Plan")
        st.write(result)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- DIET TAB ----------
with tab2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Daily Diet Planner</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        diet_goal = st.selectbox(
            "Goal",
            ["Weight Loss", "Muscle Gain", "Maintenance"]
        )
        weight = st.number_input("Weight (kg)", min_value=20, max_value=250, value=70)
        height = st.number_input("Height (cm)", min_value=100, max_value=250, value=170)
        age = st.number_input("Age", min_value=10, max_value=100, value=25)

    with col2:
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        activity_level = st.selectbox(
            "Activity Level",
            ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"]
        )
        diet_preference = st.selectbox(
            "Diet Preference",
            ["Vegetarian", "Non-Vegetarian", "Vegan", "Eggetarian", "Mixed"]
        )
        meals_per_day = st.number_input("Meals Per Day", min_value=2, max_value=8, value=4)

    if st.button("Generate Diet Plan", key="diet_btn"):
        with st.spinner("Building your diet plan..."):
            result = generate_diet_plan(
                diet_goal,
                weight,
                height,
                age,
                gender,
                activity_level,
                diet_preference,
                meals_per_day
            )

        st.success("Diet plan generated successfully.")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Your Diet Plan")
        st.write(result)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- IMAGE ANALYZER TAB ----------
with tab3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Analyze Food by Upload or Camera</div>', unsafe_allow_html=True)
    st.info("You can upload a food image or click a photo directly using your camera.")

    option = st.radio(
        "Choose input method",
        ["Upload Image", "Use Camera"],
        horizontal=True
    )

    image_file = None

    if option == "Upload Image":
        uploaded_file = st.file_uploader(
            "Upload a food image",
            type=["jpg", "jpeg", "png"]
        )
        if uploaded_file:
            image_file = uploaded_file
            st.image(image_file, caption="Uploaded Image", use_container_width=True)

    elif option == "Use Camera":
        camera_photo = st.camera_input("Take a picture")
        if camera_photo:
            image_file = camera_photo
            st.image(image_file, caption="Captured Image", use_container_width=True)

    if image_file and st.button("Analyze Food Image", key="image_btn"):
        with st.spinner("Analyzing your meal..."):
            try:
                suffix = ".jpg"
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                    tmp_file.write(image_file.read())
                    temp_path = tmp_file.name

                result = analyze_diet_image(temp_path)

                if os.path.exists(temp_path):
                    os.remove(temp_path)

                st.success("Image analyzed successfully.")
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("Food Intake Details")
                st.write(result)
                st.markdown('</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- CHAT TAB ----------
with tab4:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">AI Fitness Coach</div>', unsafe_allow_html=True)
    st.caption("Ask about workouts, diet plans, calories, recovery, muscle gain, or fat loss.")

    if "conversation" not in st.session_state:
        st.session_state.conversation = create_conversation()

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {
                "role": "assistant",
                "content": "Hey! I’m your AI fitness coach. Ask me anything about workouts, diet, calories, muscle gain, or weight loss."
            }
        ]

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask your fitness question here...")

    if prompt:
        st.session_state.chat_messages.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                reply = chat_with_ai(st.session_state.conversation, prompt)
                st.markdown(reply)

        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": reply
        })

    c1, c2 = st.columns([1, 2])

    with c1:
        if st.button("Clear Chat", key="clear_chat_btn"):
            st.session_state.conversation = create_conversation()
            st.session_state.chat_messages = [
                {
                    "role": "assistant",
                    "content": "Chat cleared. I’m ready to help with your fitness goals."
                }
            ]
            st.rerun()

    with c2:
        st.info("Try: 'Give me a high-protein vegetarian meal plan' or 'Suggest a 20-minute home workout for fat loss'.")

    st.markdown('</div>', unsafe_allow_html=True)