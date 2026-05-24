import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

from sklearn.linear_model import LinearRegression
from streamlit_oauth import OAuth2Component

from auth import login, register
from email_alert import send_email


 # ==================================================
# SESSION STATES
# ==================================================

if "auth_method" not in st.session_state:
    st.session_state["auth_method"] = None

if "email_logged_in" not in st.session_state:
    st.session_state["email_logged_in"] = False

if "google_logged_in" not in st.session_state:
    st.session_state["google_logged_in"] = False


# ==================================================
# GOOGLE OAUTH
# ==================================================

from streamlit_oauth import OAuth2Component

CLIENT_ID = st.secrets["CLIENT_ID"]

CLIENT_SECRET = st.secrets["CLIENT_SECRET"]

AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/auth"

TOKEN_URL = "https://oauth2.googleapis.com/token"

oauth2 = OAuth2Component(
    CLIENT_ID,
    CLIENT_SECRET,
    AUTHORIZE_URL,
    TOKEN_URL,
    TOKEN_URL
)


# ==================================================
# SIDEBAR AUTH
# ==================================================

st.sidebar.title("Authentication")

if st.sidebar.button("Email Login"):
    st.session_state.auth_method = "email"

if st.sidebar.button("Google Login"):
    st.session_state.auth_method = "google"


# ==================================================
# EMAIL LOGIN
# ==================================================

if st.session_state.auth_method == "email":

    menu = ["Login", "Register"]

    choice = st.sidebar.selectbox(
        "Menu",
        menu
    )

    if not st.session_state.email_logged_in:

        if choice == "Login":
            login()

        else:
            register()

        st.stop()

    st.sidebar.success(
        f"Welcome {st.session_state.username}"
    )


# ==================================================
# GOOGLE LOGIN
# ==================================================

if st.session_state.auth_method == "google":

    if "google_auth" not in st.session_state:

        result = oauth2.authorize_button(
            name="Continue with Google",
            icon="https://www.google.com/favicon.ico",
            redirect_uri="http://localhost:8501",
            scope="openid email profile",
            key="google",
            extras_params={
                "prompt": "consent",
                "access_type": "offline"
            },
            pkce='S256',
            use_container_width=True
        )

        if result and "token" in result:

            st.session_state["google_auth"] = result

            st.session_state["google_logged_in"] = True

            st.success("Google Login Successful")

            st.rerun()

    else:

        st.session_state["google_logged_in"] = True


# ==================================================
# NO LOGIN SELECTED
# ==================================================

if (
    not st.session_state.email_logged_in
    and
    not st.session_state.google_logged_in
):

    st.warning("Please Login First")

    st.stop()


# ==================================================
# TITLE
# ==================================================

st.title("💰 Financial Expense Tracking & Analytics")


# ==================================================
# LOAD DATA
# ==================================================

file_path = "personal_transactions_dashboard_ready (2).xlsx"

try:

    df = pd.read_excel(file_path)

except FileNotFoundError:

    st.error("Dataset file not found")

    st.stop()


# ==================================================
# DATA PREPROCESSING
# ==================================================

df['Date'] = pd.to_datetime(df['Date'])

df['Month'] = df['Date'].dt.to_period('M').astype(str)

expense_df = df[
    df['Transaction Type'].str.lower() == 'debit'
]


# ==================================================
# SIDEBAR FILTER
# ==================================================

st.sidebar.header("Filter Options")

selected_month = st.sidebar.selectbox(
    "Select Month",
    sorted(expense_df['Month'].unique())
)

month_df = expense_df[
    expense_df['Month'] == selected_month
]


# ==================================================
# METRICS
# ==================================================

total_expense = month_df['Amount'].sum()

avg_expense = month_df['Amount'].mean()

max_expense = month_df['Amount'].max()

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Expense",
    f"₹ {total_expense:,.2f}"
)

col2.metric(
    "Average Expense",
    f"₹ {avg_expense:,.2f}"
)

col3.metric(
    "Highest Expense",
    f"₹ {max_expense:,.2f}"
)


# ==================================================
# PIE CHART
# ==================================================

st.subheader("📊 Category Wise Spending")

category_data = month_df.groupby(
    'Category'
)['Amount'].sum().reset_index()

pie_chart = px.pie(
    category_data,
    values='Amount',
    names='Category',
    title='Expense Distribution'
)

st.plotly_chart(
    pie_chart,
    use_container_width=True
)


# ==================================================
# LINE CHART
# ==================================================

st.subheader("📉 Monthly Expense Trend")

monthly_expense = expense_df.groupby(
    'Month'
)['Amount'].sum().reset_index()

line_chart = px.line(
    monthly_expense,
    x='Month',
    y='Amount',
    markers=True,
    title='Monthly Spending Trend'
)

st.plotly_chart(
    line_chart,
    use_container_width=True
)


# ==================================================
# BUDGET ANALYSIS
# ==================================================

st.subheader("💵 Budget Analysis")

budget = st.number_input(
    "Enter Monthly Budget",
    min_value=1000,
    value=20000
)

if total_expense > budget:

    st.error(
        f"⚠ Budget Exceeded by ₹ {total_expense - budget:,.2f}"
    )

else:

    st.success(
        f"✅ You Saved ₹ {budget - total_expense:,.2f}"
    )


# ==================================================
# MONTH COMPARISON
# ==================================================

st.subheader("📅 Previous vs Current Month Analysis")

months = sorted(monthly_expense['Month'].unique())

if len(months) >= 2:

    current_month = months[-1]

    previous_month = months[-2]

    current_total = monthly_expense[
        monthly_expense['Month'] == current_month
    ]['Amount'].values[0]

    previous_total = monthly_expense[
        monthly_expense['Month'] == previous_month
    ]['Amount'].values[0]

    compare_col1, compare_col2 = st.columns(2)

    compare_col1.metric(
        f"Previous Month ({previous_month})",
        f"₹ {previous_total:,.2f}"
    )

    compare_col2.metric(
        f"Current Month ({current_month})",
        f"₹ {current_total:,.2f}"
    )

    receiver_email = st.text_input(
        "Enter Email for Alert"
    )

    if st.button("Send Monthly Report"):

        if current_total < previous_total:

            status = "decreased"

            message = (
                f"Great Job! Your expenses decreased "
                f"from ₹{previous_total:,.2f} "
                f"to ₹{current_total:,.2f}."
            )

            color = "green"

        else:

            status = "increased"

            message = (
                f"Warning! Your expenses increased "
                f"from ₹{previous_total:,.2f} "
                f"to ₹{current_total:,.2f}."
            )

            color = "red"

        send_email(
            receiver_email,
            previous_total,
            current_total,
            status,
            color,
            message
        )

        st.success("Email Sent Successfully")


# ==================================================
# ML PREDICTION
# ==================================================

st.subheader("🤖 Future Expense Prediction")

monthly_expense['Month_Number'] = np.arange(
    len(monthly_expense)
)

X = monthly_expense[['Month_Number']]

y = monthly_expense['Amount']

model = LinearRegression()

model.fit(X, y)

next_month = [[len(monthly_expense)]]

predicted_expense = model.predict(next_month)[0]

st.info(
    f"Predicted Next Month Expense: "
    f"₹ {predicted_expense:,.2f}"
)


# ==================================================
# TRANSACTION TABLE
# ==================================================

st.subheader("📄 Transaction Details")

st.dataframe(month_df)


# ==================================================
# DOWNLOAD BUTTON
# ==================================================

csv = month_df.to_csv(index=False).encode('utf-8')

st.download_button(
    label="Download Report",
    data=csv,
    file_name='expense_report.csv',
    mime='text/csv'
)