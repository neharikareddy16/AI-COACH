import firebase_admin
from firebase_admin import credentials, firestore
import os
import streamlit as st

def initialize_firebase():
    if not firebase_admin._apps:
        cred_path = os.getenv(
            "FIREBASE_CREDENTIALS_PATH",
            "serviceAccountKey.json"
        )

        if os.path.exists(cred_path):
            try:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            except Exception:
                return None

        elif "firebase" in st.secrets:
            try:
                firebase_secrets = dict(st.secrets["firebase"])

                if "private_key" in firebase_secrets:
                    firebase_secrets["private_key"] = firebase_secrets["private_key"].replace("\\n", "\n")

                cred = credentials.Certificate(firebase_secrets)
                firebase_admin.initialize_app(cred)
            except Exception:
                return None

        else:
            return None

    return firestore.client()


def save_user_profile(db, user_id, profile_data):
    if db:
        db.collection("users").document(user_id).set(profile_data, merge=True)

def get_user_profile(db, user_id):
    if db:
        doc = db.collection("users").document(user_id).get()
        if doc.exists:
            return doc.to_dict()
    return None

def save_diet_plan(db, user_id, plan):
    if db:
        db.collection("users").document(user_id).collection("plans").document("diet").set({"plan": plan})

def get_diet_plan(db, user_id):
    if db:
        doc = db.collection("users").document(user_id).collection("plans").document("diet").get()
        if doc.exists:
            return doc.to_dict().get("plan")
    return None

def save_exercise_plan(db, user_id, plan):
    if db:
        db.collection("users").document(user_id).collection("plans").document("exercise").set({"plan": plan})

def get_exercise_plan(db, user_id):
    if db:
        doc = db.collection("users").document(user_id).collection("plans").document("exercise").get()
        if doc.exists:
            return doc.to_dict().get("plan")
    return None

def log_exercise(db, user_id, date, exercise_details):
    if db:
        db.collection("users").document(user_id).collection("exercise_logs").document(date).set(
            {"completed": True, "details": exercise_details}, merge=True
        )

def get_exercise_logs(db, user_id):
    logs = {}
    if db:
        docs = db.collection("users").document(user_id).collection("exercise_logs").stream()
        for doc in docs:
            logs[doc.id] = doc.to_dict()
    return logs
