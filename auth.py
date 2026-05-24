import pandas as pd
import streamlit as st
import os

USER_FILE = "users.csv"


if not os.path.exists(USER_FILE):
    df = pd.DataFrame(columns=["username", "password", "email"])
    df.to_csv(USER_FILE, index=False)


def load_users():
    return pd.read_csv(USER_FILE)

def save_user(username, password, email):

    users = load_users()

    new_user = pd.DataFrame({
        "username": [username],
        "password": [password],
        "email": [email]
    })

    users = pd.concat([users, new_user], ignore_index=True)

    users.to_csv(USER_FILE, index=False)

def register():

    st.subheader("📝 Register")

    username = st.text_input("Create Username")
    email = st.text_input("Enter Email")
    password = st.text_input(
        "Create Password",
        type="password"
    )

    if st.button("Register"):

        users = load_users()

        if username in users["username"].values:
            st.error("Username already exists")

        else:
            save_user(username, password, email)
            st.success("Registration Successful")


def login():

    st.subheader("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        users = load_users()

        user = users[
            (users["username"] == username)
            &
            (users["password"] == password)
        ]

        if not user.empty:

            st.session_state.email_logged_in = True
            st.session_state.username = username

            st.success("Login Successful")
            st.rerun()

        else:
            st.error("Invalid Username or Password")


def logout():

    st.session_state.logged_in = False

    if st.button("Logout"):
        st.success("Logged Out")