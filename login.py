import os
import requests
import streamlit as st

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")


def show():
    st.markdown("<h2 style='text-align: center;'>🔐 Log In to SalesGenie</h2>", unsafe_allow_html=True)
    st.caption("<p style='text-align: center;'>Access your AI-powered B2B sales workspace.</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])

    with col2:
        # --- GOOGLE AUTHENTICATION ---
        st.markdown("### 🌐 Fast Auth")
        if st.button("🔴 Continue with Google", use_container_width=True, type="secondary"):
            with st.spinner("Logging in with Google..."):
                try:
                    res = requests.post(
                        f"{API_URL}/auth/google",
                        json={"email": "google.user@salesgenie.ai", "name": "Google User"},
                        timeout=10
                    )
                    if res.status_code == 200:
                        user_info = res.json().get("user", {})
                        st.session_state["user"] = user_info
                        st.session_state["user_id"] = user_info.get("id", 1)
                        st.session_state["logged_in"] = True
                        st.session_state["authenticated"] = True
                        st.success(f"Welcome back, {user_info.get('name', 'User')}!")
                        st.rerun()
                    else:
                        st.error(f"Google auth failed (Error {res.status_code}): {res.text}")
                except Exception as e:
                    st.error(f"Could not connect to backend server ({API_URL}): {e}")

        st.markdown("<div style='text-align: center; margin: 15px 0;'><strong>— OR —</strong></div>", unsafe_allow_html=True)

        # --- MANUAL EMAIL LOGIN ---
        with st.form("login_form"):
            st.markdown("### 📧 Email Credentials")
            email = st.text_input("Email Address", placeholder="user@company.com").strip().lower()
            password = st.text_input("Password", type="password", placeholder="••••••••").strip()
            submit_btn = st.form_submit_button("🚀 Log In", type="primary", use_container_width=True)

        if submit_btn:
            if not email or not password:
                st.error("Please enter both email and password.")
            else:
                with st.spinner("Authenticating..."):
                    try:
                        res = requests.post(
                            f"{API_URL}/login",
                            json={"email": email, "password": password},
                            timeout=10
                        )
                        if res.status_code == 200:
                            user_info = res.json().get("user", {})
                            st.session_state["user"] = user_info
                            st.session_state["user_id"] = user_info.get("id", 1)
                            st.session_state["logged_in"] = True
                            st.session_state["authenticated"] = True
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("Invalid email or password.")
                    except Exception as e:
                        st.error(f"Error connecting to server: {e}")

        # --- SWITCH TO SIGNUP ---
        st.markdown("---")
        st.write("Don't have an account yet?")
        if st.button("✨ Create New Account", use_container_width=True):
            st.session_state["page"] = "signup"
            st.rerun()


if __name__ == "__main__":
    show()