import streamlit as st
import pandas as pd
import plotly.express as px

# Page settings
st.set_page_config(
    page_title="Personal Finance Analytics",
    page_icon="💰",
    layout="wide"
)

# Dashboard title
st.title("💰 Personal Finance Analytics")
st.write("Understand your money. Control your spending.")

# Sample financial data
data = {
    "Category": ["Food", "Travel", "Shopping", "Bills", "Education"],
    "Amount": [3500, 2000, 4500, 1500, 2500]
}

df = pd.DataFrame(data)

# Financial summary
total_expenses = df["Amount"].sum()

col1, col2 = st.columns(2)

with col1:
    st.metric("Total Expenses", f"₹{total_expenses:,}")

with col2:
    st.metric("Categories", len(df))

# Expense chart
st.subheader("Spending by Category")

fig = px.pie(
    df,
    names="Category",
    values="Amount",
    hole=0.4
)

st.plotly_chart(fig, use_container_width=True)

# Expense table
st.subheader("Expense Details")
st.dataframe(df, use_container_width=True)
