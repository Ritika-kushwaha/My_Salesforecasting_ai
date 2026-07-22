import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

def signup():

    st.title("Create Account")

    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Sign Up"):

        payload = {
            "name": name,
            "email": email,
            "password": password
        }

        response = requests.post(
            f"{API_URL}/signup",
            json=payload
        )

        if response.status_code == 200:
            st.success("Signup Successful!")

            st.session_state.page = "login"
            st.rerun()

        else:
            st.error(response.text)

    st.write("Already have an account?")

    if st.button("Login Here"):
        st.session_state.page = "login"
        st.rerun()