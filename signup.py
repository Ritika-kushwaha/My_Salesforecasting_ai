import os
import requests
import streamlit as st

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")


def show():
    st.markdown("<h2 style='text-align: center;'>🚀 Create Your SalesGenie Account</h2>", unsafe_allow_html=True)
    st.caption("<p style='text-align: center;'>Get started with AI-driven B2B sales intelligence.</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])

    with col2:
        # --- GOOGLE SIGNUP ---
        st.markdown("### 🌐 Fast Signup")
        if st.button("🔴 Sign Up with Google", use_container_width=True, type="secondary"):
            with st.spinner("Creating account with Google..."):
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
                        st.success("Account created & logged in!")
                        st.rerun()
                    else:
                        st.error(f"Google signup failed (Error {res.status_code}): {res.text}")
                except Exception as e:
                    st.error(f"Error connecting to server: {e}")

        st.markdown("<div style='text-align: center; margin: 15px 0;'><strong>— OR —</strong></div>", unsafe_allow_html=True)

        # --- MANUAL EMAIL SIGNUP ---
        with st.form("signup_form"):
            st.markdown("### 📧 Create Account")
            name = st.text_input("Full Name *", placeholder="Jane Doe").strip()
            email = st.text_input("Email Address *", placeholder="jane@company.com").strip().lower()
            password = st.text_input("Password *", type="password", placeholder="At least 4 characters").strip()
            submit_btn = st.form_submit_button("✨ Create Account & Log In", type="primary", use_container_width=True)

        if submit_btn:
            if not name or not email or not password:
                st.error("Name, Email, and Password are required.")
            elif len(password) < 4:
                st.error("Password must be at least 4 characters.")
            else:
                with st.spinner("Creating account..."):
                    try:
                        res = requests.post(
                            f"{API_URL}/signup",
                            json={"name": name, "email": email, "password": password},
                            timeout=10
                        )
                        if res.status_code == 200:
                            user_info = res.json().get("user", {})
                            st.session_state["user"] = user_info
                            st.session_state["user_id"] = user_info.get("id", 1)
                            st.session_state["logged_in"] = True
                            st.session_state["authenticated"] = True
                            st.success("🎉 Account created & logged in!")
                            st.rerun()
                        else:
                            detail = res.json().get("detail", "Failed to create account.")
                            st.error(detail)
                    except Exception as e:
                        st.error(f"Error connecting to backend API: {e}")

        # --- SWITCH TO LOGIN ---
        st.markdown("---")
        st.write("Already have an account?")
        if st.button("🔐 Back to Login", use_container_width=True):
            st.session_state["page"] = "login"
            st.rerun()


if __name__ == "__main__":
    show()