import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Finance Analytics",
    page_icon="💰",
    layout="wide"
)

# Custom styling
st.markdown("""
<style>
.stApp {
    background-color: #0E1117;
}
h1, h2, h3, p, label {
    color: #FFFFFF;
}
</style>
""", unsafe_allow_html=True)

# Dashboard heading
st.title("💰 Personal Finance Analytics")
st.caption("Your money. Your decisions. Your future.")

st.divider()


# Transaction data
st.subheader("📂 Upload Your Financial Data")

uploaded_file = st.file_uploader(
    "Upload a CSV file",
    type=["csv"]
)

# Default sample data
sample_data = {
    "Date": [
        "2026-11-01",
        "2026-11-02",
        "2026-11-03",
        "2026-11-04",
        "2026-11-05",
        "2026-11-06"
    ],
    "Type": [
        "Income", "Expense", "Expense",
        "Expense", "Income", "Expense"
    ],
    "Category": [
        "Salary", "Food", "Travel",
        "Shopping", "Freelance", "Bills"
    ],
    "Amount": [25000, 3500, 2000, 4500, 5000, 1500]
}

if uploaded_file is not None:
    transactions = pd.read_csv(uploaded_file)
else:
    transactions = pd.DataFrame(sample_data)


# Clean column names
transactions.columns = (
    transactions.columns
    .astype(str)
    .str.replace("\ufeff", "", regex=False)
    .str.strip()
    .str.title()
)

# Required columns
required_columns = ["Date", "Type", "Category", "Amount"]

# Check uploaded data
if not all(column in transactions.columns for column in required_columns):
    st.error("Missing required columns!")
    st.write("Columns detected:", transactions.columns.tolist())
    st.stop()


if not all(column in transactions.columns for column in required_columns):
    st.error("Your CSV must contain Date, Type, Category and Amount columns.")
    st.stop()

# Clean and prepare the data
transactions["Type"] = transactions["Type"].astype(str).str.strip().str.title()
transactions["Category"] = transactions["Category"].astype(str).str.strip()
transactions["Amount"] = pd.to_numeric(transactions["Amount"], errors="coerce")

transactions = transactions.dropna(
    subset=["Date", "Type", "Category", "Amount"]
)

transactions = transactions[
    transactions["Type"].isin(["Income", "Expense"])
    & (transactions["Amount"] >= 0)
]

if transactions.empty:
    st.warning("No valid transactions found.")
    st.stop()

# Calculate financial figures automatically
income = transactions.loc[
    transactions["Type"] == "Income", "Amount"
].sum()

expenses = transactions.loc[
    transactions["Type"] == "Expense", "Amount"
].sum()

savings = income - expenses

savings_rate = (savings / income * 100) if income > 0 else 0

# Prepare expense data for charts
df = transactions[
    transactions["Type"] == "Expense"
].groupby("Category", as_index=False)["Amount"].sum()


# Summary cards
st.subheader("Financial Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Income", f"₹{income:,}")
col2.metric("Total Expenses", f"₹{expenses:,}")
col3.metric("Net Savings", f"₹{savings:,}")
col4.metric("Savings Rate", f"{savings_rate:.1f}%")

st.divider()

# Charts section
left, right = st.columns(2)

with left:
    st.subheader("Expense Breakdown")

    fig = px.pie(
        df,
        names="Category",
        values="Amount",
        hole=0.55,
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Spending by Category")

    fig2 = px.bar(
        df,
        x="Category",
        y="Amount",
        color="Amount",
        template="plotly_dark"
    )

    st.plotly_chart(fig2, use_container_width=True)

# Expense details
st.divider()
st.subheader("Expense Details")

st.dataframe(
    transactions,
    use_container_width=True,
    hide_index=True
)

st.caption("Personal Finance Analytics | Version 2.0")