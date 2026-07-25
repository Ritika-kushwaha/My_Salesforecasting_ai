import os
import requests
import streamlit as st

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")


def render_signup_page():
    st.markdown("## 📝 Create a SalesGenie Account")
    st.caption("Join SalesGenie AI to manage leads and automate sales outreach.")

    with st.form("signup_form", clear_on_submit=False):
        name = st.text_input("Full Name", placeholder="John Doe").strip()
        email = st.text_input("Email Address", placeholder="name@company.com").strip()
        password = st.text_input("Password", type="password", placeholder="••••••••").strip()
        
        submit_btn = st.form_submit_button(
            "🚀 Sign Up", type="primary", use_container_width=True
        )

    if submit_btn:
        if not name or not email or not password:
            st.warning("⚠️ Please fill in all required fields.")
            return

        payload = {
            "name": name,
            "email": email,
            "password": password,
        }

        try:
            response = requests.post(
                f"{API_URL}/signup",
                json=payload,
                timeout=10,
            )

            if response.status_code in [200, 201]:
                st.success("🎉 Signup Successful! Redirecting to login...")
                st.session_state["page"] = "login"
                st.rerun()
            else:
                error_msg = response.json().get("detail", response.text)
                st.error(f"Signup Failed ({response.status_code}): {error_msg}")

        except requests.exceptions.ConnectionError:
            st.error(
                f"Cannot connect to FastAPI backend at `{API_URL}`. Make sure Uvicorn server is running."
            )
        except Exception as e:
            st.error(f"An error occurred during signup: {e}")

    st.markdown("---")
    st.markdown("Already have an account?")
    if st.button("🔐 Back to Login", type="secondary", use_container_width=True):
        st.session_state["page"] = "login"
        st.rerun()


# Function Aliases for flexible calling from main.py
def show():
    render_signup_page()


def signup():
    render_signup_page()