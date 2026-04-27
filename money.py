import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import os

st.set_page_config(page_title="Budget Planner", layout="wide")

# ------------------ FILE ------------------
FILE_NAME = "data.csv"

# ------------------ LOAD DATA ------------------
if "data" not in st.session_state:
    if os.path.exists(FILE_NAME):
        st.session_state.data = pd.read_csv(FILE_NAME)
    else:
        st.session_state.data = pd.DataFrame(columns=["Date","Type","Category","Amount"])

if "budget" not in st.session_state:
    st.session_state.budget = 0

if "goal" not in st.session_state:
    st.session_state.goal = 0

# ------------------ UI STYLE ------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to right, #141E30, #243B55);
    color: white;
}
h1, h2 {
    color: #00ffcc;
    text-align: center;
}
.stButton>button {
    background-color: #00ffcc;
    color: black;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title("💰 Smart Budget Planner")

# ------------------ SIDEBAR ------------------
st.sidebar.header("⚙️ Settings")
st.session_state.budget = st.sidebar.number_input("Monthly Budget", min_value=0)
st.session_state.goal = st.sidebar.number_input("Saving Goal", min_value=0)

# ------------------ ADD TRANSACTION ------------------
st.header("➕ Add Transaction")

col1, col2, col3 = st.columns(3)

with col1:
    date = st.date_input("Date", datetime.date.today())

with col2:
    trans_type = st.selectbox("Type", ["Income", "Expense"])

with col3:
    amount = st.number_input("Amount", min_value=0)

category = st.text_input("Category")

if st.button("Add Transaction"):
    if category != "" and amount > 0:
        new_row = pd.DataFrame([[date, trans_type, category, amount]],
                               columns=["Date","Type","Category","Amount"])
        st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)

        # SAVE DATA
        st.session_state.data.to_csv(FILE_NAME, index=False)

        st.success("✅ Added Successfully!")
    else:
        st.warning("⚠️ Enter valid details")

# ------------------ DATA PREP ------------------
data = st.session_state.data.copy()

if not data.empty:
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")

# ------------------ FILTER ------------------
st.header("📅 Filter by Month")

if not data.empty:
    selected_month = st.selectbox("Select Month", range(1,13))
    filtered_data = data[data["Date"].dt.month == selected_month]
else:
    filtered_data = data

# ------------------ DISPLAY ------------------
st.header("📊 Transactions")
st.dataframe(filtered_data)

# ------------------ CALCULATIONS ------------------
income = filtered_data[filtered_data["Type"]=="Income"]["Amount"].sum()
expense = filtered_data[filtered_data["Type"]=="Expense"]["Amount"].sum()
balance = income - expense

col4, col5, col6 = st.columns(3)
col4.metric("💵 Income", f"₹{income}")
col5.metric("💸 Expense", f"₹{expense}")
col6.metric("🏦 Balance", f"₹{balance}")

# ------------------ CHART ------------------
st.header("📉 Expense Breakdown")

expense_data = filtered_data[filtered_data["Type"]=="Expense"]

if not expense_data.empty:
    category_sum = expense_data.groupby("Category", as_index=False)["Amount"].sum()

    fig, ax = plt.subplots()
    ax.pie(category_sum["Amount"], labels=category_sum["Category"], autopct="%1.1f%%")
    ax.set_title("Expenses by Category")

    st.pyplot(fig)
else:
    st.info("No expense data")

# ------------------ ALERT ------------------
st.header("🚨 Budget Alert")

if st.session_state.budget > 0:
    if expense > st.session_state.budget:
        st.error("💥 Budget Exceeded!")
    elif expense > 0.8 * st.session_state.budget:
        st.warning("⚠️ Near limit")
    else:
        st.success("✅ Within budget")

# ------------------ GOAL ------------------
st.header("🎯 Goal Tracker")

if st.session_state.goal > 0:
    progress = min(balance / st.session_state.goal, 1.0)
    st.progress(progress)

    if balance >= st.session_state.goal:
        st.success("🏆 Goal Achieved!")
    else:
        st.info("Keep saving 🚀")
