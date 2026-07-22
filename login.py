import os
import streamlit as st
import requests

API_URL = os.getenv(
    "SALESGENIE_API_URL",
    "http://127.0.0.1:8000"
)

def login():

    st.title("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if not email or not password:
            st.warning("Please enter email and password.")
            return

        try:
            response = requests.post(
                f"{API_URL}/login",
                json={
                    "email": email,
                    "password": password
                },
                timeout=10
            )

            if response.status_code == 200:
                st.success("Login Successful")

                st.session_state.logged_in = True
                st.session_state.user = response.json()["user"]

                st.rerun()

            else:
                st.error(response.json()["detail"])

        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to backend.")

        except Exception as e:
            st.error(str(e))

    st.markdown("---")
    st.write("Don't have an account?")

    if st.button("Create Account"):
        st.session_state.page = "signup"
        st.rerun()