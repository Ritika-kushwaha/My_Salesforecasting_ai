import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

def signup():

    st.title("Create Account")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Sign Up"):

        response = requests.post(
            f"{API_URL}/signup",
            json={
                "email": email,
                "password": password
            }
        )

        st.write(response.json())