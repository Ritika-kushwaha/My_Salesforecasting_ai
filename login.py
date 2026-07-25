import os
import requests
import streamlit as st

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")


def render_login_page():
    st.markdown("## 🔐 Login to SalesGenie AI")

    with st.form("login_form"):
        email = st.text_input("Email", placeholder="name@company.com")
        password = st.text_input("Password", type="password")
        submit_btn = st.form_submit_button(
            "🔓 Log In", type="primary", use_container_width=True
        )

    if submit_btn:
        if not email.strip() or not password.strip():
            st.warning("⚠️ Please fill in both email and password.")
            return

        try:
            res = requests.post(
                f"{API_URL}/login",
                json={"email": email.strip(), "password": password.strip()},
                timeout=10,
            )

            if res.status_code == 200:
                data = res.json()
                st.session_state["logged_in"] = True
                st.session_state["user"] = data.get("user", {})
                st.success("✅ Login Successful!")
                st.rerun()
            elif res.status_code == 401:
                st.error("❌ Invalid email or password.")
            else:
                st.error(f"Error {res.status_code}: {res.text}")

        except requests.exceptions.ConnectionError:
            st.error(
                f"Cannot connect to FastAPI backend at `{API_URL}`. Make sure Uvicorn is running."
            )
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")


# Map all possible caller function names so main.py never throws an AttributeError
login = render_login_page
show = render_login_page

if __name__ == "__main__":
    render_login_page()