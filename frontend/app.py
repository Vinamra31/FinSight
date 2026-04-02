import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import date

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Expense Analyzer", page_icon="💸", layout="wide")
st.title("💸 Expense Analyzer")

# ── Sidebar: Add Expense ──────────────────────────────────────────────────────
with st.sidebar:
    st.header("Add Expense")

    categories = requests.get(f"{API_URL}/categories").json()

    exp_date = st.date_input("Date", value=date.today())
    category = st.selectbox("Category", categories)
    amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0, format="%.2f")
    note = st.text_input("Note (optional)")

    if st.button("Add Expense", use_container_width=True):
        if amount <= 0:
            st.error("Amount must be greater than 0")
        else:
            res = requests.post(f"{API_URL}/expenses", json={
                "date": str(exp_date),
                "category": category,
                "amount": amount,
                "note": note,
            })
            if res.status_code == 200:
                st.success("Expense added!")
                st.rerun()
            else:
                st.error("Failed to add expense")

# ── Fetch data ────────────────────────────────────────────────────────────────
expenses = requests.get(f"{API_URL}/expenses").json()
summary = requests.get(f"{API_URL}/summary").json()

if not expenses:
    st.info("No expenses yet. Add your first expense from the sidebar!")
    st.stop()

df = pd.DataFrame(expenses)
df["amount"] = df["amount"].astype(float)
df["date"] = pd.to_datetime(df["date"])

# ── Summary Cards ─────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("Total Spent", f"₹{summary['total']:,.2f}")
col2.metric("No. of Expenses", len(expenses))
top_cat = max(summary["by_category"], key=summary["by_category"].get) if summary["by_category"] else "-"
col3.metric("Top Category", top_cat)

st.divider()

# ── Charts ────────────────────────────────────────────────────────────────────
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Spending by Category")
    cat_df = pd.DataFrame(
        list(summary["by_category"].items()),
        columns=["Category", "Amount"]
    )
    fig_bar = px.bar(
        cat_df, x="Category", y="Amount",
        color="Category", text_auto=".2f",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_bar.update_layout(showlegend=False, margin=dict(t=20))
    st.plotly_chart(fig_bar, use_container_width=True)

with chart_col2:
    st.subheader("Category Breakdown")
    fig_pie = px.pie(
        cat_df, names="Category", values="Amount",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        hole=0.4
    )
    fig_pie.update_layout(margin=dict(t=20))
    st.plotly_chart(fig_pie, use_container_width=True)

st.subheader("Spending Over Time")
date_df = df.groupby("date")["amount"].sum().reset_index()
fig_line = px.line(
    date_df, x="date", y="amount",
    markers=True, labels={"amount": "Amount (₹)", "date": "Date"},
    color_discrete_sequence=["#636EFA"]
)
fig_line.update_layout(margin=dict(t=20))
st.plotly_chart(fig_line, use_container_width=True)

st.divider()

# ── Expense Table ─────────────────────────────────────────────────────────────
st.subheader("All Expenses")

display_df = df[["id", "date", "category", "amount", "note"]].copy()
display_df["date"] = display_df["date"].dt.strftime("%Y-%m-%d")
display_df.columns = ["ID", "Date", "Category", "Amount (₹)", "Note"]

st.dataframe(display_df, use_container_width=True, hide_index=True)

# Delete expense
with st.expander("Delete an Expense"):
    expense_ids = [int(e["id"]) for e in expenses]
    del_id = st.selectbox("Select Expense ID to delete", expense_ids)
    if st.button("Delete", type="primary"):
        res = requests.delete(f"{API_URL}/expenses/{del_id}")
        if res.status_code == 200:
            st.success("Deleted!")
            st.rerun()
        else:
            st.error("Failed to delete")

st.divider()

# ── LLM Chat ──────────────────────────────────────────────────────────────────
st.subheader("🤖 Ask About Your Expenses")
st.caption("Powered by Ollama (Qwen 2.5)")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Ask something like: Where am I overspending? Summarize this month...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            res = requests.post(f"{API_URL}/chat", json={"question": user_input})
            answer = res.json().get("response", "No response.")
        st.write(answer)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})