import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
from datetime import date, datetime
from streamlit_calendar import calendar

# --- PAGE CONFIG ---
st.set_page_config(page_title="Personal Planner", layout="wide")

# --- CUSTOM BACKGROUND STYLING ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #090d16 100%);
        background-attachment: fixed;
    }
    div.stButton > button {
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background: linear-gradient(90deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# --- AUTHENTICATION SETUP ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1.5, 1, 1.5])
    with col_l2:
        st.markdown("### 🔒 Locked")
        st.write("Welcome Aravindhan Uvaraj")
        pin = st.text_input("Enter PIN", type="password", max_chars=4)
        if st.button("Unlock Planner", use_container_width=True):
            if pin == "1320":
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Incorrect PIN.")
    st.stop()

# --- DATABASE SETUP ---
GIST_ID = st.secrets["GIST_ID"]
TOKEN = st.secrets["GITHUB_TOKEN"]

GIST_URL = f"https://api.github.com/gists/{GIST_ID}"
HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def load_data():
    response = requests.get(GIST_URL, headers=HEADERS)
    if response.status_code == 200:
        content = response.json()["files"]["planner_data.json"]["content"]
        return json.loads(content)
    else:
        return {"monthly_expenses": {}, "trips": [], "trip_itineraries": {}, "goals": {}, "daily_logs": {}}

def save_data(data_dict):
    payload = {"files": {"planner_data.json": {"content": json.dumps(data_dict, indent=4)}}}
    response = requests.patch(GIST_URL, headers=HEADERS, json=payload)
    return response.status_code == 200

# --- MAIN APP HEADER ---
col_head1, col_head2 = st.columns([5, 1])
with col_head1:
    st.title("Personal Planner")
    st.caption("Welcome back, Aravindhan Uvaraj")
with col_head2:
    st.write("") 
    if st.button("🔒 Lock"):
        st.session_state["authenticated"] = False
        st.rerun()

data = load_data()

# Added back as a tab for full-page view
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Monthly Budget Tracker", "Trip Calendar", "Financial Goals", "Full-Year Grid Tracker", "ℹ️ About Me"])

# ... [Tabs 1, 2, 3, 4 remain exactly as before] ...

# ==========================================
# TAB 5: ABOUT ME (Full Page)
# ==========================================
with tab5:
    st.header("About Me")
    col_bio_img, col_bio_txt = st.columns([1, 2])
    with col_bio_img:
        st.image("aravindhan.jpg.jpg", caption="Aravindhan Uvaraj", use_container_width=True)
    with col_bio_txt:
        st.subheader("Aravindhan Uvaraj")
        st.write("Hello! I'm an engineer passionate about technology, semiconductor manufacturing, videography, and building custom digital tools from scratch.")

    st.divider()
    st.subheader("➕ Family & Pet Details")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.subheader("My Wife")
        st.image("wife.jpg.JPG", caption="Partner & Companion", use_container_width=True)
        st.write("My wonderful travel partner and companion.")
    with col_f2:
        st.subheader("Our Cat")
        st.image("cat.jpg.jpeg", caption="The Boss of the House", use_container_width=True)
        st.write("Our adorable feline friend who keeps the home lively!")
