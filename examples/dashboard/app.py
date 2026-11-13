import html

import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Finance Analytics",
    page_icon="💰",
    layout="wide"
)

# ---------------------------------------------------------------------------
# Design system
# ---------------------------------------------------------------------------
ACCENT = "#7C83FF"     # indigo
POSITIVE = "#2DD4BF"   # teal
NEGATIVE = "#FB7185"   # rose
WARNING = "#FBBF24"    # amber
CARD_BG = "#121826"

CATEGORY_COLORS = [
    "#7C83FF", "#2DD4BF", "#FBBF24", "#FB7185",
    "#38BDF8", "#A78BFA", "#34D399", "#F472B6",
]

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #0B0F19;
    --card: #121826;
    --card-2: #171F31;
    --border: rgba(255, 255, 255, 0.07);
    --text: #F3F5FA;
    --muted: #8A94AD;
    --accent: #7C83FF;
}

/* Base */
.stApp {
    background:
        radial-gradient(900px 500px at 10% -10%, rgba(124, 131, 255, 0.14), transparent 60%),
        radial-gradient(800px 500px at 100% 0%, rgba(45, 212, 191, 0.08), transparent 55%),
        var(--bg);
    color: var(--text);
}
.stApp, .stMarkdown, p, label, input, button, textarea,
h1, h2, h3, h4, [data-testid="stCaptionContainer"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
h1, h2, h3, p, label {
    color: var(--text);
}
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
.block-container {
    padding-top: 2.2rem;
    padding-bottom: 3rem;
    max-width: 1240px;
}

/* Hero */
.fin-hero {
    display: flex;
    align-items: center;
    gap: 18px;
    padding: 6px 0 22px 0;
}
.fin-logo {
    width: 54px; height: 54px;
    border-radius: 16px;
    display: flex; align-items: center; justify-content: center;
    font-size: 26px;
    background: linear-gradient(135deg, #7C83FF 0%, #2DD4BF 100%);
    box-shadow: 0 10px 30px rgba(124, 131, 255, 0.35);
    flex-shrink: 0;
}
.fin-eyebrow {
    font-size: 12px; font-weight: 600;
    letter-spacing: 0.14em; text-transform: uppercase;
    color: var(--accent);
}
.fin-title {
    font-size: 30px; font-weight: 800; line-height: 1.15;
    letter-spacing: -0.02em; color: var(--text);
    margin: 2px 0;
}
.fin-tagline { font-size: 14px; color: var(--muted); }

/* Section headers */
.fin-section { margin: 34px 0 14px 0; }
.fin-section-title {
    font-size: 18px; font-weight: 700; letter-spacing: -0.01em;
    color: var(--text); margin: 0;
}
.fin-section-sub { font-size: 13px; color: var(--muted); margin-top: 2px; }

/* Upload card */
.fin-upload {
    background: linear-gradient(145deg, var(--card-2), var(--card));
    border: 1px solid var(--border);
    border-radius: 20px 20px 0 0;
    border-bottom: none;
    padding: 22px 24px 8px 24px;
}
.fin-upload-head {
    display: flex; align-items: center; justify-content: space-between;
    gap: 12px; flex-wrap: wrap;
}
.fin-upload-title { font-size: 17px; font-weight: 700; color: var(--text); }
.fin-upload-sub { font-size: 13px; color: var(--muted); margin-top: 2px; }
.fin-badge {
    font-size: 12px; font-weight: 600;
    padding: 5px 12px; border-radius: 999px;
    border: 1px solid var(--border);
    background: rgba(255, 255, 255, 0.04);
    color: var(--muted);
    white-space: nowrap;
}
.fin-badge.live {
    color: #2DD4BF;
    background: rgba(45, 212, 191, 0.10);
    border-color: rgba(45, 212, 191, 0.30);
}
.fin-chips { display: flex; flex-wrap: wrap; gap: 8px; margin: 14px 0 6px 0; }
.fin-chip {
    font-size: 12px; font-weight: 500; color: #C9D1E3;
    padding: 4px 10px; border-radius: 8px;
    background: rgba(124, 131, 255, 0.10);
    border: 1px solid rgba(124, 131, 255, 0.22);
}
[data-testid="stFileUploader"] {
    background: var(--card);
    border: 1px solid var(--border);
    border-top: none;
    border-radius: 0 0 20px 20px;
    padding: 8px 24px 22px 24px;
    margin-top: -1px;
}
[data-testid="stFileUploaderDropzone"] {
    background: rgba(124, 131, 255, 0.05);
    border: 1.5px dashed rgba(124, 131, 255, 0.38);
    border-radius: 16px;
    padding: 26px;
    transition: all 0.2s ease;
}
[data-testid="stFileUploaderDropzone"]:hover {
    background: rgba(124, 131, 255, 0.10);
    border-color: rgba(124, 131, 255, 0.75);
}
[data-testid="stFileUploaderDropzone"] button {
    border-radius: 10px;
    border: 1px solid rgba(124, 131, 255, 0.45);
    background: rgba(124, 131, 255, 0.12);
    color: var(--text);
    font-weight: 600;
}

/* Inputs */
[data-testid="stSelectbox"] label p {
    font-size: 12px; font-weight: 600;
    letter-spacing: 0.06em; text-transform: uppercase;
    color: var(--muted);
}
[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    min-height: 46px;
}

/* Metric cards */
.fin-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 16px;
}
.fin-card {
    position: relative;
    overflow: hidden;
    background: linear-gradient(145deg, var(--card-2) 0%, var(--card) 100%);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 20px 22px;
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}
.fin-card::before {
    content: "";
    position: absolute; top: -60px; right: -60px;
    width: 160px; height: 160px; border-radius: 50%;
    background: radial-gradient(circle, var(--accent) 0%, transparent 70%);
    opacity: 0.18;
}
.fin-card:hover {
    transform: translateY(-3px);
    border-color: rgba(255, 255, 255, 0.16);
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.35);
}
.fin-card-top {
    display: flex; align-items: center; justify-content: space-between;
}
.fin-card-label {
    font-size: 12px; font-weight: 600;
    letter-spacing: 0.08em; text-transform: uppercase;
    color: var(--muted);
}
.fin-card-icon {
    width: 34px; height: 34px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px;
    background: rgba(255, 255, 255, 0.06);
}
.fin-card-value {
    font-size: 30px; font-weight: 800; letter-spacing: -0.02em;
    color: var(--text); margin: 14px 0 4px 0;
    word-break: break-word;
}
.fin-card-sub { font-size: 13px; color: var(--muted); }
.fin-bar { height: 4px; border-radius: 4px; background: rgba(255,255,255,0.07); margin-top: 14px; }
.fin-bar > div { height: 100%; border-radius: 4px; background: var(--accent); }

/* Insight card */
.fin-insight {
    display: flex; align-items: center; gap: 18px; flex-wrap: wrap;
    background: linear-gradient(120deg, rgba(251, 191, 36, 0.10), rgba(251, 113, 133, 0.06) 60%, var(--card));
    border: 1px solid rgba(251, 191, 36, 0.22);
    border-radius: 20px;
    padding: 20px 24px;
}
.fin-insight-icon {
    width: 48px; height: 48px; border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px; background: rgba(251, 191, 36, 0.14);
    flex-shrink: 0;
}
.fin-insight-body { flex: 1; min-width: 180px; }
.fin-insight-label {
    font-size: 12px; font-weight: 600;
    letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted);
}
.fin-insight-name { font-size: 22px; font-weight: 700; color: var(--text); margin-top: 2px; }
.fin-insight-amount { text-align: right; }
.fin-insight-amount .amt { font-size: 24px; font-weight: 800; color: #FBBF24; }
.fin-insight-amount .share { font-size: 12px; color: var(--muted); }
.fin-empty {
    padding: 18px 22px; border-radius: 16px;
    background: var(--card); border: 1px dashed var(--border);
    color: var(--muted); font-size: 14px;
}

/* Charts */
div[data-testid="stPlotlyChart"] {
    background: linear-gradient(145deg, var(--card-2), var(--card));
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 12px 14px 4px 14px;
    overflow: hidden;
}

/* Table */
div[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 16px;
    overflow: hidden;
}

/* Download button */
.stDownloadButton button {
    background: linear-gradient(135deg, #7C83FF 0%, #5B63F0 100%);
    color: #FFFFFF;
    font-weight: 600;
    border: none;
    border-radius: 12px;
    padding: 10px 22px;
    box-shadow: 0 8px 24px rgba(124, 131, 255, 0.30);
    transition: all 0.2s ease;
}
.stDownloadButton button:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 30px rgba(124, 131, 255, 0.45);
    color: #FFFFFF;
}

/* Alerts */
[data-testid="stAlert"] { border-radius: 14px; }

/* Footer */
.fin-footer {
    margin-top: 44px; padding-top: 18px;
    border-top: 1px solid var(--border);
    text-align: center; font-size: 12px; color: var(--muted);
}

/* Responsive */
@media (max-width: 768px) {
    .block-container { padding: 1.2rem 1rem 2.5rem 1rem; }
    .fin-title { font-size: 23px; }
    .fin-logo { width: 44px; height: 44px; font-size: 21px; border-radius: 13px; }
    .fin-card { padding: 16px 18px; border-radius: 16px; }
    .fin-card-value { font-size: 25px; }
    .fin-grid { gap: 12px; grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .fin-section { margin-top: 26px; }
    .fin-upload { padding: 18px 16px 6px 16px; }
    [data-testid="stFileUploader"] { padding: 6px 16px 18px 16px; }
    .fin-insight { padding: 16px 18px; }
    .fin-insight-amount { text-align: left; }
}
@media (max-width: 420px) {
    .fin-grid { grid-template-columns: 1fr; }
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# UI helpers (presentation only)
# ---------------------------------------------------------------------------
def section(title, sub=""):
    sub_html = f'<div class="fin-section-sub">{sub}</div>' if sub else ""
    st.markdown(
        f'<div class="fin-section"><div class="fin-section-title">{title}</div>{sub_html}</div>',
        unsafe_allow_html=True
    )


def metric_card(label, value, sub, accent, icon, progress=None):
    bar = ""
    if progress is not None:
        width = max(0, min(100, progress))
        bar = f'<div class="fin-bar"><div style="width:{width:.0f}%"></div></div>'
    return (
        f'<div class="fin-card" style="--accent:{accent}">'
        f'<div class="fin-card-top"><span class="fin-card-label">{label}</span>'
        f'<span class="fin-card-icon">{icon}</span></div>'
        f'<div class="fin-card-value">{value}</div>'
        f'<div class="fin-card-sub">{sub}</div>{bar}</div>'
    )


def style_fig(fig, height=380, top=56):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#C9D1E3", size=13),
        title=dict(font=dict(size=16, color="#F3F5FA"), x=0.01),
        margin=dict(l=8, r=8, t=top, b=8),
        height=height,
        legend=dict(
            orientation="h", y=1.14, x=1, xanchor="right", title_text=""
        ),
        hoverlabel=dict(
            bgcolor="#1B2236", font_size=13,
            bordercolor="rgba(255,255,255,0.12)"
        ),
    )
    fig.update_xaxes(
        showgrid=False, title_text="",
        linecolor="rgba(255,255,255,0.10)"
    )
    fig.update_yaxes(
        gridcolor="rgba(255,255,255,0.06)", zeroline=False,
        title_text="", tickprefix="₹"
    )
    return fig


# Dashboard heading
st.markdown("""
<div class="fin-hero">
    <div class="fin-logo">💰</div>
    <div>
        <div class="fin-eyebrow">Finance Analytics</div>
        <div class="fin-title">Personal Finance Analytics</div>
        <div class="fin-tagline">Your money. Your decisions. Your future.</div>
    </div>
</div>
""", unsafe_allow_html=True)


# Transaction data
section("Upload Your Financial Data", "Drop in a CSV export or an HDFC statement PDF to analyse your own transactions.")

upload_badge_slot = st.empty()

uploaded_file = st.file_uploader(
    "Upload a CSV or PDF file",
    type=["csv", "pdf"],
    label_visibility="collapsed"
)

if uploaded_file is not None:
    badge = f'<span class="fin-badge live">● {html.escape(uploaded_file.name)}</span>'
else:
    badge = '<span class="fin-badge">Showing sample data</span>'

# The card header is rendered above the uploader using the reserved slot
upload_badge_slot.markdown(
    '<div class="fin-upload">'
    '<div class="fin-upload-head"><div>'
    '<div class="fin-upload-title">📂 Transaction file</div>'
    '<div class="fin-upload-sub">CSV or HDFC statement PDF · your data is processed in this session</div>'
    f'</div>{badge}</div>'
    '<div class="fin-chips">'
    '<span class="fin-chip">Date</span><span class="fin-chip">Type</span>'
    '<span class="fin-chip">Category</span><span class="fin-chip">Amount</span>'
    '</div></div>',
    unsafe_allow_html=True
)

# PDF statements may be password protected
is_pdf = uploaded_file is not None and uploaded_file.name.lower().endswith(".pdf")
pdf_password = None
if is_pdf:
    pdf_password = st.text_input(
        "PDF password (leave empty if the PDF has none)", type="password"
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

# Read the uploaded file safely
if is_pdf:
    try:
        from open_finance_toolkit import (
            OpenFinanceError,
            categorize,
            load_pdf_transactions,
        )
    except ImportError:
        st.error(
            "PDF support needs the open-finance-toolkit package. "
            'Install it with: pip install "open-finance-toolkit[pdf]"'
        )
        st.stop()
    try:
        transactions = categorize(
            load_pdf_transactions(uploaded_file, password=pdf_password or None)
        )
    except OpenFinanceError as error:
        st.error(str(error))
        st.stop()
elif uploaded_file is not None:
    try:
        transactions = pd.read_csv(uploaded_file)
    except pd.errors.EmptyDataError:
        st.error("Your CSV file is empty. Please upload a file with data.")
        st.stop()
    except (pd.errors.ParserError, UnicodeDecodeError):
        st.error("Unable to read this CSV. Please check its format.")
        st.stop()
else:
    transactions = pd.DataFrame(sample_data)


# Clean column names
transactions.columns = (
    transactions.columns.astype(str)
    .str.replace("\ufeff", "", regex=False)
    .str.strip()
    .str.title()
)

# Required columns
required_columns = ["Date", "Type", "Category", "Amount"]

if not all(column in transactions.columns for column in required_columns):
    st.error("CSV must contain Date, Type, Category and Amount columns.")
    st.write("Columns detected:", transactions.columns.tolist())
    st.stop()


# Clean and prepare transaction data
transactions["Type"] = (
    transactions["Type"].astype(str).str.strip().str.title()
)

transactions["Category"] = (
    transactions["Category"].astype(str).str.strip()
)

transactions["Date"] = pd.to_datetime(
    transactions["Date"],
    format="mixed",
    dayfirst=True,
    errors="coerce"
)

transactions["Amount"] = pd.to_numeric(
    transactions["Amount"]
    .astype(str)
    .str.replace(",", "", regex=False)
    .str.strip(),
    errors="coerce"
)

# Remove invalid transactions
transactions = transactions.dropna(
    subset=["Date", "Type", "Category", "Amount"]
)

transactions = transactions[
    transactions["Type"].isin(["Income", "Expense"])
    & (transactions["Amount"] >= 0)
    & (transactions["Category"] != "")
]

if transactions.empty:
    st.error("No valid transactions found. Please check your CSV.")
    st.stop()


# Monthly analysis
transactions["Month"] = transactions["Date"].dt.strftime("%B %Y")

months = sorted(
    transactions["Month"].unique(),
    key=lambda x: pd.to_datetime(x, format="%B %Y")
)

section("Report Period", "Pick a month to drill into.")

filter_col, _spacer = st.columns([1, 2])
with filter_col:
    selected_month = st.selectbox("Select Month", months)

# Keep original data for monthly comparisons
all_transactions = transactions.copy()

# Filter selected month
transactions = transactions[
    transactions["Month"] == selected_month
]


# Calculate financial figures
income = transactions.loc[
    transactions["Type"] == "Income", "Amount"
].sum()

expenses = transactions.loc[
    transactions["Type"] == "Expense", "Amount"
].sum()

savings = income - expenses

savings_rate = (savings / income * 100) if income > 0 else 0


# Prepare expense data
df = transactions[
    transactions["Type"] == "Expense"
].groupby("Category", as_index=False)["Amount"].sum()


# Summary cards
section("Financial Overview", f"Summary for {html.escape(str(selected_month))}")

cards = [
    metric_card("Total Income", f"₹{income:,.0f}", "Money in", POSITIVE, "📈"),
    metric_card("Total Expenses", f"₹{expenses:,.0f}", "Money out", NEGATIVE, "💸"),
    metric_card(
        "Net Savings", f"₹{savings:,.0f}", "Income − Expenses",
        POSITIVE if savings >= 0 else NEGATIVE, "🏦"
    ),
    metric_card(
        "Savings Rate", f"{savings_rate:.1f}%", "Of income saved",
        ACCENT if savings_rate >= 0 else NEGATIVE, "🎯",
        progress=savings_rate
    ),
]

st.markdown(
    '<div class="fin-grid">' + "".join(cards) + "</div>",
    unsafe_allow_html=True
)


# Top spending category
section("Monthly Spending Insight")

if not df.empty:
    top_category = df.loc[df["Amount"].idxmax(), "Category"]
    top_amount = df["Amount"].max()
    top_share = (top_amount / df["Amount"].sum() * 100) if df["Amount"].sum() > 0 else 0

    st.markdown(
        '<div class="fin-insight">'
        '<div class="fin-insight-icon">🔥</div>'
        '<div class="fin-insight-body">'
        '<div class="fin-insight-label">Highest Spending Category</div>'
        f'<div class="fin-insight-name">{html.escape(str(top_category))}</div>'
        '</div>'
        '<div class="fin-insight-amount">'
        f'<div class="amt">₹{top_amount:,.0f}</div>'
        f'<div class="share">{top_share:.0f}% of this month\'s expenses</div>'
        '</div></div>',
        unsafe_allow_html=True
    )
else:
    st.markdown(
        '<div class="fin-empty">No expenses recorded this month.</div>',
        unsafe_allow_html=True
    )


# Month-to-month comparison
section("Monthly Spending Comparison", "How income, expenses and savings move over time.")

monthly_summary = all_transactions.pivot_table(
    index="Month",
    columns="Type",
    values="Amount",
    aggfunc="sum",
    fill_value=0
).reset_index()

for col in ["Income", "Expense"]:
    if col not in monthly_summary.columns:
        monthly_summary[col] = 0

# Sort months chronologically
monthly_summary["_Sort"] = pd.to_datetime(
    monthly_summary["Month"], format="%B %Y"
)

monthly_summary = monthly_summary.sort_values("_Sort")

monthly_chart = px.bar(
    monthly_summary,
    x="Month",
    y=["Income", "Expense"],
    barmode="group",
    title="Income vs Expenses by Month",
    template="plotly_dark",
    color_discrete_map={"Income": POSITIVE, "Expense": NEGATIVE}
)
style_fig(monthly_chart)
monthly_chart.update_layout(bargap=0.35, bargroupgap=0.08)
monthly_chart.update_traces(
    hovertemplate="%{x}<br>%{fullData.name}: ₹%{y:,.0f}<extra></extra>"
)

st.plotly_chart(monthly_chart, use_container_width=True)


# Monthly savings trend
monthly_summary["Savings"] = (
    monthly_summary["Income"] - monthly_summary["Expense"]
)

savings_chart = px.line(
    monthly_summary,
    x="Month",
    y="Savings",
    markers=True,
    title="Monthly Savings Trend",
    template="plotly_dark"
)
style_fig(savings_chart, height=340)
savings_chart.update_traces(
    line=dict(color=POSITIVE, width=3, shape="spline"),
    marker=dict(size=10, color=POSITIVE, line=dict(color=CARD_BG, width=2)),
    fill="tozeroy",
    fillcolor="rgba(45, 212, 191, 0.12)",
    hovertemplate="%{x}<br>Savings: ₹%{y:,.0f}<extra></extra>"
)
savings_chart.update_layout(showlegend=False)

st.plotly_chart(savings_chart, use_container_width=True)


# Expense charts
section("Expense Analysis", f"Where your money went in {html.escape(str(selected_month))}.")

left, right = st.columns(2)

with left:
    st.markdown('<div class="fin-section-title" style="margin-bottom:10px">Expense Breakdown</div>', unsafe_allow_html=True)

    if not df.empty:
        fig = px.pie(
            df,
            names="Category",
            values="Amount",
            hole=0.62,
            template="plotly_dark",
            color_discrete_sequence=CATEGORY_COLORS
        )
        style_fig(fig, height=400, top=16)
        fig.update_traces(
            textposition="inside",
            textinfo="percent",
            marker=dict(line=dict(color=CARD_BG, width=3)),
            hovertemplate="%{label}<br>₹%{value:,.0f} (%{percent})<extra></extra>"
        )
        fig.update_layout(
            legend=dict(
                orientation="h", y=-0.05, x=0.5, xanchor="center", title_text=""
            ),
            annotations=[dict(
                text=f"<b>₹{df['Amount'].sum():,.0f}</b><br>Total spent",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=15, color="#F3F5FA")
            )]
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No expense data available for this month.")

with right:
    st.markdown('<div class="fin-section-title" style="margin-bottom:10px">Spending by Category</div>', unsafe_allow_html=True)

    if not df.empty:
        fig2 = px.bar(
            df,
            x="Category",
            y="Amount",
            color="Amount",
            template="plotly_dark",
            color_continuous_scale=[[0, "#3B3F8F"], [1, "#7C83FF"]]
        )
        style_fig(fig2, height=400, top=16)
        fig2.update_layout(coloraxis_showscale=False, bargap=0.35)
        fig2.update_traces(
            hovertemplate="%{x}<br>₹%{y:,.0f}<extra></extra>"
        )

        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No spending data available for this month.")


# Expense details
section("Expense Details", "Every expense transaction for the selected month.")

expense_details = transactions[
    transactions["Type"] == "Expense"
]

st.dataframe(
    expense_details,
    use_container_width=True,
    hide_index=True
)


# Download monthly report
section("Download Your Report", "Export this month's transactions as CSV.")

csv_data = transactions.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇  Download Monthly CSV",
    data=csv_data,
    file_name=f"finance_report_{selected_month}.csv",
    mime="text/csv"
)

st.markdown(
    '<div class="fin-footer">Personal Finance Analytics | Version 3.0</div>',
    unsafe_allow_html=True
)