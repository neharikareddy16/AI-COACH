import google.generativeai as genai
import os

import streamlit as st

def initialize_ai():
    # Try environment variable first, then Streamlit secrets
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key and "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
        
    if not api_key:
        print("Warning: GEMINI_API_KEY not found in env or secrets.")
        return None
    genai.configure(api_key=api_key)
    # Using the standard gemini-1.5-pro model
    model = genai.GenerativeModel('gemini-1.5-pro')
    return model

def analyze_and_suggest_diet(model, current_diet, user_profile):
    prompt = f"""
    You are an expert personal fitness coach and nutritionist.
    User Profile: {user_profile}
    Current Diet: {current_diet}
    
    Please analyze this diet, point out any flaws based on their goals, and suggest an optimal diet plan.
    Format your response in Markdown.
    """
    response = model.generate_content(prompt)
    return response.text

def generate_exercise_plan(model, user_profile):
    prompt = f"""
    You are an expert personal fitness coach.
    User Profile: {user_profile}
    
    Please generate a weekly exercise plan tailored to their goals, fitness level, and preferences.
    Format your response in Markdown. Include specific days, exercises, sets, and reps.
    """
    response = model.generate_content(prompt)
    return response.text

def chat_with_coach(model, chat_history, user_message, user_profile):
    # Initialize a chat session with history if possible, or just build a prompt
    # Since we are using standard generate_content, we can construct the history manually or use chat sessions.
    # We will use ChatSession for a conversational feel.
    
    system_instruction = f"You are a helpful, motivating personal fitness coach. You know this about the user: {user_profile}. Answer their questions concisely."
    
    # In Gemini API, we can pass history to start_chat.
    # To keep it simple, we will just send a combined prompt if we aren't maintaining the chat object in memory.
    
    chat = model.start_chat(history=chat_history)
    response = chat.send_message(f"System instruction: {system_instruction}\n\nUser: {user_message}")
    
    # We return the new message text and the updated history
    return response.text, chat.history
