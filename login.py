import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

def login():

    st.title("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        response = requests.post(
            f"{API_URL}/login",
            json={
                "email": email,
                "password": password
            }
        )

        if response.status_code == 200:
            st.success("Login Successful")
            user = response.json()["user"]
            st.session_state.logged_in = True
            st.session_state.user = user
            st.rerun()

        else:
            st.error(response.json()["detail"])

    st.write("Don't have an account?")

    if st.button("Create Account"):
        st.session_state.page = "signup"
        st.rerun()