import os
import requests
import streamlit as st

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")


def render_login_page():
    st.markdown("## 🔐 Login to SalesGenie AI")
    st.caption("Enter your credentials to access your sales workspace.")

    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Email Address", placeholder="name@company.com").strip()
        password = st.text_input("Password", type="password", placeholder="••••••••").strip()
        
        submit_btn = st.form_submit_button(
            "🔓 Log In", type="primary", use_container_width=True
        )

    if submit_btn:
        if not email or not password:
            st.warning("⚠️ Please fill in both email and password.")
            return

        try:
            res = requests.post(
                f"{API_URL}/login",
                json={"email": email, "password": password},
                timeout=10,
            )

            if res.status_code == 200:
                data = res.json()
                st.session_state["logged_in"] = True
                st.session_state["user"] = data.get("user", {})
                st.session_state["active_tab"] = "Dashboard"
                st.success("✅ Login Successful!")
                st.rerun()
            elif res.status_code == 401:
                st.error("❌ Invalid email or password.")
            else:
                st.error(f"Error ({res.status_code}): {res.text}")

        except requests.exceptions.ConnectionError:
            st.error(
                f"Cannot connect to FastAPI backend at `{API_URL}`. Make sure Uvicorn server is running."
            )
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

    st.markdown("---")
    st.markdown("Don't have an account yet?")
    if st.button("📝 Create an Account", type="secondary", use_container_width=True):
        st.session_state["page"] = "signup"
        st.rerun()


# Function Aliases for flexible calling from main.py
def show():
    render_login_page()


def login():
    render_login_page()