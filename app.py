import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
from streamlit_calendar import calendar

# --- DATABASE SETUP ---
# Pull the secrets securely
GIST_ID = st.secrets["GIST_ID"]
TOKEN = st.secrets["GITHUB_TOKEN"]

# Set up the API connection
GIST_URL = f"https://api.github.com/gists/{GIST_ID}"
HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}


def load_data():
    """Reads the data from your secret Gist."""
    response = requests.get(GIST_URL, headers=HEADERS)
    if response.status_code == 200:
        content = response.json()["files"]["planner_data.json"]["content"]
        return json.loads(content)
    else:
        st.error(f"Failed to connect: {response.status_code}")
        # Return empty template if it fails
        return {"salary_split": {"needs": 50, "wants": 30, "savings": 20}, "trips": [], "goals": {}}


def save_data(data_dict):
    """Overwrites the Gist with your updated JSON data."""
    payload = {
        "files": {
            "planner_data.json": {
                "content": json.dumps(data_dict, indent=4)
            }
        }
    }
    response = requests.patch(GIST_URL, headers=HEADERS, json=payload)
    return response.status_code == 200


# --- USER INTERFACE ---
st.set_page_config(page_title="Personal Planner", layout="wide")
st.title("Personal Planner")

# Load the database once
data = load_data()

# Create 3 tabs for organization
tab1, tab2, tab3 = st.tabs(["Salary Strategy", "Trip Calendar", "Financial Goals"])

# ==========================================
# TAB 1: SALARY STRATEGY
# ==========================================
with tab1:
    st.header("Monthly Salary Allocation")
    salary = st.number_input("Enter Monthly Salary (€)", value=4000, step=100)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Adjust Split")
        # Pull starting values from database, default to 50/30 if missing
        split_data = data.get("salary_split", {"needs": 50, "wants": 30, "savings": 20})

        needs = st.slider("Needs (%)", 0, 100, split_data.get("needs", 50))
        wants = st.slider("Wants (%)", 0, 100, split_data.get("wants", 30))
        savings = 100 - (needs + wants)

        st.metric("Savings Allocation", f"{savings}%")

        if st.button("Save Strategy"):
            if savings < 0:
                st.error("Your split totals more than 100%!")
            else:
                data["salary_split"] = {"needs": needs, "wants": wants, "savings": savings}
                if save_data(data):
                    st.success("Strategy saved to database!")

    with col2:
        if savings >= 0:
            df = pd.DataFrame({
                "Category": ["Needs", "Wants", "Savings"],
                "Amount (€)": [salary * (needs / 100), salary * (wants / 100), salary * (savings / 100)]
            })
            fig = px.pie(df, values="Amount (€)", names="Category", hole=0.4,
                         color_discrete_sequence=["#FF6C6C", "#3b82f6", "#10b981"])
            st.plotly_chart(fig, use_container_width=True)

# ==========================================
# TAB 2: TRIP CALENDAR
# ==========================================
with tab2:
    st.header("Travel Calendar")

    # Form to add a new trip
    with st.form("add_trip_form"):
        st.subheader("Plan a New Trip")
        col_t1, col_t2, col_t3 = st.columns(3)
        trip_name = col_t1.text_input("Destination", placeholder="e.g., Tenerife or Chongqing")
        start_date = col_t2.date_input("Start Date")
        end_date = col_t3.date_input("End Date")

        if st.form_submit_button("Add Trip to Calendar"):
            new_trip = {
                "title": trip_name,
                "start": str(start_date),
                "end": str(end_date),
                "backgroundColor": "#FF6C6C"  # Red color for trips
            }
            if "trips" not in data:
                data["trips"] = []

            data["trips"].append(new_trip)
            if save_data(data):
                st.success(f"{trip_name} added to database!")

    st.divider()

    # Display the calendar
    calendar_options = {
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek",
        },
        "initialView": "dayGridMonth"
    }

    calendar(events=data.get("trips", []), options=calendar_options)

# ==========================================
# TAB 3: YEARLY FINANCIAL GOALS
# ==========================================
with tab3:
    st.header("Yearly Financial Goals")

    col_g1, col_g2 = st.columns(2)
    goals_data = data.get("goals", {})

    with col_g1:
        st.subheader("Emergency Fund")
        ef_current = st.number_input("Current Saved (€)", value=goals_data.get("ef_current", 5000), step=100)
        ef_target = st.number_input("Target Amount (€)", value=goals_data.get("ef_target", 15000), step=1000)

        ef_progress = min(ef_current / ef_target, 1.0) if ef_target > 0 else 0.0
        st.progress(ef_progress, text=f"{int(ef_progress * 100)}% to Emergency Fund Goal")

    with col_g2:
        st.subheader("Stock Investments (Tech/Semiconductors)")
        inv_current = st.number_input("Current Portfolio Value (€)", value=goals_data.get("inv_current", 2000),
                                      step=100)
        inv_target = st.number_input("End of Year Target (€)", value=goals_data.get("inv_target", 10000), step=1000)

        inv_progress = min(inv_current / inv_target, 1.0) if inv_target > 0 else 0.0
        st.progress(inv_progress, text=f"{int(inv_progress * 100)}% to Portfolio Goal")

    st.divider()
    if st.button("Save Financial Goals"):
        data["goals"] = {
            "ef_current": ef_current,
            "ef_target": ef_target,
            "inv_current": inv_current,
            "inv_target": inv_target
        }
        if save_data(data):
            st.success("Financial goals updated in database!")