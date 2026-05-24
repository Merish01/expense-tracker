import smtplib
import streamlit as st

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(
    receiver_email,
    previous_total,
    current_total,
    status,
    color,
    message
):

    sender_email = st.secrets["EMAIL"]
    sender_password = st.secrets["EMAIL_PASSWORD"]

    subject = "Monthly Expense Report"

    html = f"""
    <html>
    <body>

        <h2 style='color:{color};'>
            Monthly Expense Analysis
        </h2>

        <p>{message}</p>

        <table border='1' cellpadding='10'>

            <tr>
                <th>Previous Month</th>
                <th>Current Month</th>
            </tr>

            <tr>
                <td>₹ {previous_total:,.2f}</td>
                <td>₹ {current_total:,.2f}</td>
            </tr>

        </table>

        <br>

        <p>Thank You</p>

    </body>
    </html>
    """

    msg = MIMEMultipart()

    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg.attach(
        MIMEText(html, 'html')
    )

    server = smtplib.SMTP(
        'smtp.gmail.com',
        587
    )

    server.starttls()

    server.login(
        sender_email,
        sender_password
    )

    server.send_message(msg)

    server.quit()