import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
from datetime import date, datetime
from streamlit_calendar import calendar

# --- PAGE CONFIG ---
st.set_page_config(page_title="Personal Planner", layout="wide")

# --- AUTHENTICATION SETUP ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("Welcome Aravindhan Uvaraj")
    st.write("Please enter your 4-digit PIN to access your Personal Planner.")

    pin = st.text_input("Enter PIN", type="password", max_chars=4)
    if st.button("Unlock"):
        if pin == "1320":
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect PIN. Please try again.")
    st.stop()  # Stops the rest of the app from loading until unlocked

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
        st.error(f"Failed to connect: {response.status_code}")
        return {
            "monthly_expenses": {},
            "trips": [],
            "goals": {},
            "daily_logs": {}
        }


def save_data(data_dict):
    payload = {
        "files": {
            "planner_data.json": {
                "content": json.dumps(data_dict, indent=4)
            }
        }
    }
    response = requests.patch(GIST_URL, headers=HEADERS, json=payload)
    return response.status_code == 200


# --- MAIN APP INTERFACE ---
st.title("Personal Planner")
st.caption("Welcome back, Aravindhan Uvaraj")

data = load_data()

tab1, tab2, tab3, tab4 = st.tabs(
    ["Monthly Budget Tracker", "Trip Calendar", "Financial Goals", "Full-Year Grid Tracker"])

# ==========================================
# TAB 1: MONTHLY BUDGET TRACKER
# ==========================================
with tab1:
    st.header("Monthly Income & Expense Tracker")
    st.write("Select a month, enter your salary and category breakdowns, and view yearly trends.")

    months_list = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]

    selected_month = st.selectbox("Select Month", months_list, index=datetime.now().month - 1)

    if "monthly_expenses" not in data:
        data["monthly_expenses"] = {}

    month_data = data["monthly_expenses"].get(selected_month, {
        "Salary": 2591.0,
        "Rent": 600.0,
        "Utilities": 100.0,
        "Groceries": 300.0,
        "Transportation": 90.0,
        "Luxury": 0.0,
        "Family": 0.0,
        "Savings": 400.0,
        "Trip": 450.0
    })

    col_input, col_graph = st.columns([1, 1])

    with col_input:
        st.subheader(f"Data for {selected_month}")

        salary = st.number_input("Salary (€)", value=float(month_data.get("Salary", 2591)), step=50.0)
        rent = st.number_input("Rent (€)", value=float(month_data.get("Rent", 600)), step=10.0)
        utilities = st.number_input("Utilities (€)", value=float(month_data.get("Utilities", 100)), step=10.0)
        groceries = st.number_input("Groceries (€)", value=float(month_data.get("Groceries", 300)), step=10.0)
        transportation = st.number_input("Transportation (€)", value=float(month_data.get("Transportation", 90)),
                                         step=10.0)
        luxury = st.number_input("Luxury (€)", value=float(month_data.get("Luxury", 0)), step=10.0)
        family = st.number_input("Family (€)", value=float(month_data.get("Family", 0)), step=10.0)
        savings = st.number_input("Savings (€)", value=float(month_data.get("Savings", 400)), step=10.0)
        trip = st.number_input("Trip (€)", value=float(month_data.get("Trip", 450)), step=10.0)

        total_expenses = rent + utilities + groceries + transportation + luxury + family

        st.info(f"**Total Expenses:** €{total_expenses}")

        if st.button(f"Save {selected_month} Data"):
            data["monthly_expenses"][selected_month] = {
                "Salary": salary,
                "Rent": rent,
                "Utilities": utilities,
                "Groceries": groceries,
                "Transportation": transportation,
                "Luxury": luxury,
                "Family": family,
                "Savings": savings,
                "Trip": trip,
                "Total Expenses": total_expenses
            }
            if save_data(data):
                st.success(f"Successfully saved data for {selected_month}!")

    with col_graph:
        st.subheader("Current Month Breakdown")
        cat_df = pd.DataFrame({
            "Category": ["Rent", "Utilities", "Groceries", "Transportation", "Luxury", "Family", "Savings", "Trip"],
            "Amount (€)": [rent, utilities, groceries, transportation, luxury, family, savings, trip]
        })
        fig_pie = px.pie(cat_df, values="Amount (€)", names="Category", hole=0.3,
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.divider()
    st.subheader("Year-Round Monthly Trend Graph")

    saved_months_data = data.get("monthly_expenses", {})
    if saved_months_data:
        yearly_rows = []
        for m in months_list:
            if m in saved_months_data:
                row = saved_months_data[m].copy()
                row["Month"] = m
                yearly_rows.append(row)

        if yearly_rows:
            df_year = pd.DataFrame(yearly_rows)
            fig_bar = px.bar(df_year, x="Month", y=["Salary", "Total Expenses", "Savings", "Trip"],
                             barmode="group", title="Income vs Expenses vs Savings by Month")
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Save data for at least one month to see the yearly trend graph.")
    else:
        st.info("No monthly expense records found yet.")

# ==========================================
# TAB 2: TRIP CALENDAR
# ==========================================
with tab2:
    st.header("Travel Calendar")
    with st.form("add_trip_form"):
        st.subheader("Plan a New Trip")
        col_t1, col_t2, col_t3 = st.columns(3)
        trip_name = col_t1.text_input("Destination", placeholder="e.g., Tenerife or Chongqing")
        start_date = col_t2.date_input("Start Date")
        end_date = col_t3.date_input("End Date")

        if st.form_submit_button("Add Trip to Calendar"):
            new_trip = {"title": trip_name, "start": str(start_date), "end": str(end_date),
                        "backgroundColor": "#FF6C6C"}
            if "trips" not in data:
                data["trips"] = []
            data["trips"].append(new_trip)
            if save_data(data):
                st.success(f"{trip_name} added to database!")

    st.divider()
    calendar_options = {"headerToolbar": {"left": "today prev,next", "center": "title", "right": "dayGridMonth"},
                        "initialView": "dayGridMonth"}
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
        data["goals"] = {"ef_current": ef_current, "ef_target": ef_target, "inv_current": inv_current,
                         "inv_target": inv_target}
        if save_data(data):
            st.success("Financial goals updated in database!")

# ==========================================
# TAB 4: FULL-YEAR GRID TRACKER
# ==========================================
with tab4:
    st.header("Full-Year Grid Tracker")
    st.write("Select a date, write your log entry, and see it populate your yearly grid view.")

    col_input1, col_input2 = st.columns([1, 2])
    with col_input1:
        log_date = st.date_input("Entry Date", value=date.today())
    with col_input2:
        daily_logs = data.get("daily_logs", {})
        current_note = daily_logs.get(str(log_date), "")
        note_input = st.text_input("Log Entry / Note", value=current_note)

    if st.button("Save Entry to Grid"):
        daily_logs[str(log_date)] = note_input
        data["daily_logs"] = daily_logs
        if save_data(data):
            st.success(f"Saved entry for {log_date}!")

    st.divider()


    def render_month_grid(year, month_num, month_name, logs):
        st.subheader(month_name)
        first_day = date(year, month_num, 1)
        if month_num == 12:
            last_day = date(year + 1, 1, 1) - pd.Timedelta(days=1)
        else:
            last_day = date(year, month_num + 1, 1) - pd.Timedelta(days=1)

        curr = first_day
        days_dict = {}
        while curr <= last_day:
            wk = curr.isocalendar()[1]
            w_day = curr.strftime("%a")
            date_key = str(curr)
            marker = "🟢" if date_key in logs and logs[date_key] != "" else str(curr.day)

            if wk not in days_dict:
                days_dict[wk] = {"Wk": wk, "Mon": "", "Tue": "", "Wed": "", "Thu": "", "Fri": "", "Sat": "", "Sun": ""}

            if w_day == "Mon":
                days_dict[wk]["Mon"] = marker
            elif w_day == "Tue":
                days_dict[wk]["Tue"] = marker
            elif w_day == "Wed":
                days_dict[wk]["Wed"] = marker
            elif w_day == "Thu":
                days_dict[wk]["Thu"] = marker
            elif w_day == "Fri":
                days_dict[wk]["Fri"] = marker
            elif w_day == "Sat":
                days_dict[wk]["Sat"] = marker
            elif w_day == "Sun":
                days_dict[wk]["Sun"] = marker

            curr += pd.Timedelta(days=1)

        df_month = pd.DataFrame(list(days_dict.values()))
        st.dataframe(df_month, hide_index=True, use_container_width=True)


    current_year = date.today().year
    months = [
        (1, "January"), (2, "February"), (3, "March"), (4, "April"),
        (5, "May"), (6, "June"), (7, "July"), (8, "August"),
        (9, "September"), (10, "October"), (11, "November"), (12, "December")
    ]

    for i in range(0, 12, 3):
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            render_month_grid(current_year, months[i][0], months[i][1], daily_logs)
        with col_m2:
            render_month_grid(current_year, months[i + 1][0], months[i + 1][1], daily_logs)
        with col_m3:
            render_month_grid(current_year, months[i + 2][0], months[i + 2][1], daily_logs)
        st.write("---")
