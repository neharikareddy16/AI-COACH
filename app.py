import streamlit as st
import os
from dotenv import load_dotenv
import firebase_setup
import ai_coach
from datetime import date

# Load environment variables (like API keys)
load_dotenv()

st.set_page_config(page_title="AI Fitness Coach", page_icon="💪", layout="centered")

# Initialize external services
db = firebase_setup.initialize_firebase()
ai_model = ai_coach.initialize_ai()

# Session State Initialization
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {}

def login_ui():
    st.title("💪 AI Fitness Coach")
    st.subheader("Login / Sign Up")
    
    st.info("For this prototype, just enter a unique username to act as your user ID.")
    username = st.text_input("Username")
    
    if st.button("Enter"):
        if username:
            st.session_state.user_id = username
            # Fetch profile
            profile = firebase_setup.get_user_profile(db, username)
            if profile:
                st.session_state.user_profile = profile
                st.success(f"Welcome back, {username}!")
            else:
                st.session_state.user_profile = {"username": username}
                firebase_setup.save_user_profile(db, username, st.session_state.user_profile)
                st.success(f"Account created for {username}!")
            st.rerun()
        else:
            st.error("Please enter a username")

def profile_ui():
    st.header("Profile Setup")
    
    with st.form("profile_form"):
        age = st.number_input("Age", min_value=10, max_value=120, value=st.session_state.user_profile.get("age", 25))
        weight = st.number_input("Weight (kg)", min_value=30, max_value=300, value=st.session_state.user_profile.get("weight", 70))
        goal = st.selectbox("Goal", ["Lose Weight", "Build Muscle", "Maintain", "Improve Endurance"], index=0)
        fitness_level = st.selectbox("Fitness Level", ["Beginner", "Intermediate", "Advanced"], index=0)
        
        submitted = st.form_submit_button("Save Profile")
        if submitted:
            st.session_state.user_profile.update({
                "age": age,
                "weight": weight,
                "goal": goal,
                "fitness_level": fitness_level
            })
            firebase_setup.save_user_profile(db, st.session_state.user_id, st.session_state.user_profile)
            st.success("Profile saved!")

def diet_plan_ui():
    st.header("🥗 Diet Plan")
    
    current_plan = firebase_setup.get_diet_plan(db, st.session_state.user_id)
    if current_plan:
        st.markdown(current_plan)
    else:
        st.info("No diet plan found.")
        
    st.subheader("Analyze Current Diet")
    current_diet = st.text_area("What do you typically eat in a day?")
    if st.button("Analyze & Suggest Plan"):
        if not ai_model:
            st.error("AI Model not initialized. Check your GEMINI_API_KEY.")
            return
        with st.spinner("Analyzing..."):
            suggestion = ai_coach.analyze_and_suggest_diet(ai_model, current_diet, st.session_state.user_profile)
            st.markdown(suggestion)
            
            if st.button("Save this Plan"):
                firebase_setup.save_diet_plan(db, st.session_state.user_id, suggestion)
                st.success("Plan saved!")
                st.rerun()

def exercise_plan_ui():
    st.header("🏋️ Exercise Plan")
    
    current_plan = firebase_setup.get_exercise_plan(db, st.session_state.user_id)
    if current_plan:
        st.markdown(current_plan)
    else:
        st.info("No exercise plan found.")
        
    if st.button("Generate New Exercise Plan"):
        if not ai_model:
            st.error("AI Model not initialized. Check your GEMINI_API_KEY.")
            return
        with st.spinner("Generating..."):
            suggestion = ai_coach.generate_exercise_plan(ai_model, st.session_state.user_profile)
            st.markdown(suggestion)
            
            # Auto save for simplicity
            firebase_setup.save_exercise_plan(db, st.session_state.user_id, suggestion)
            st.success("Plan saved! Refresh to see it permanently.")

def tracking_ui():
    st.header("📅 Schedule Monitor")
    
    today = str(date.today())
    logs = firebase_setup.get_exercise_logs(db, st.session_state.user_id)
    
    st.subheader("Log Today's Exercise")
    details = st.text_input("What did you do today?")
    if st.button("Log Exercise"):
        firebase_setup.log_exercise(db, st.session_state.user_id, today, details)
        st.success("Logged successfully!")
        st.rerun()
        
    st.subheader("Past Logs")
    if logs:
        for d, data in logs.items():
            st.write(f"**{d}**: {data.get('details', 'Completed')}")
    else:
        st.write("No logs yet. Get started!")

def chat_ui():
    st.header("💬 Chat with Coach")
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.chat_message("user").markdown(message["parts"][0])
        else:
            st.chat_message("assistant").markdown(message["parts"][0])
            
    # Input
    user_input = st.chat_input("Ask me anything about fitness...")
    if user_input:
        st.chat_message("user").markdown(user_input)
        
        # Prepare history for Gemini
        formatted_history = []
        for msg in st.session_state.chat_history:
            formatted_history.append({"role": msg["role"], "parts": msg["parts"]})
            
        with st.spinner("Typing..."):
            try:
                response_text, new_history = ai_coach.chat_with_coach(
                    ai_model, formatted_history, user_input, str(st.session_state.user_profile)
                )
                
                st.chat_message("assistant").markdown(response_text)
                
                # Update history in session state
                st.session_state.chat_history.append({"role": "user", "parts": [user_input]})
                st.session_state.chat_history.append({"role": "model", "parts": [response_text]})
            except Exception as e:
                st.error(f"Error chatting with AI: {e}")

# Main App Routing
if not st.session_state.user_id:
    login_ui()
else:
    st.sidebar.title(f"Hello, {st.session_state.user_id}!")
    
    if st.sidebar.button("Logout"):
        st.session_state.user_id = None
        st.session_state.chat_history = []
        st.rerun()
        
    tab = st.sidebar.radio("Navigation", ["Profile", "Diet Plan", "Exercise Plan", "Track Schedule", "Chat"])
    
    if tab == "Profile":
        profile_ui()
    elif tab == "Diet Plan":
        diet_plan_ui()
    elif tab == "Exercise Plan":
        exercise_plan_ui()
    elif tab == "Track Schedule":
        tracking_ui()
    elif tab == "Chat":
        chat_ui()
