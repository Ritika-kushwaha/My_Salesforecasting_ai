import os
import requests
import streamlit as st
from urllib.parse import urlencode

# -------------------------------------------------------------------
# 1. LOAD CREDENTIALS
# -------------------------------------------------------------------
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")

CLIENT_ID = os.getenv(
    "GOOGLE_CLIENT_ID",
    "802596462436-vtfnim58h3j7mo706b4bs8dko80cdmb1.apps.googleusercontent.com"
).strip()

CLIENT_SECRET = os.getenv(
    "GOOGLE_CLIENT_SECRET",
    "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"
).strip()

REDIRECT_URI = "http://localhost:8501/"


def show():
    st.markdown("<h2 style='text-align: center;'>🔐 Log In to SalesGenie</h2>", unsafe_allow_html=True)
    st.caption("<p style='text-align: center;'>Access your AI-powered B2B sales workspace.</p>", unsafe_allow_html=True)

    # -------------------------------------------------------------------
    # 2. RECEIVE GOOGLE OAUTH REDIRECT CODE
    # -------------------------------------------------------------------
    query_params = st.query_params
    auth_code = query_params.get("code")

    if auth_code:
        with st.spinner("Authenticating with Google..."):
            try:
                res = requests.post(
                    f"{API_URL}/auth/google",
                    json={"token": auth_code},
                    timeout=10
                )
                if res.status_code == 200:
                    user_data = res.json().get("user", {})
                    st.session_state["user"] = user_data
                    st.session_state["user_id"] = user_data.get("id", 1)
                    st.session_state["logged_in"] = True
                    st.session_state["authenticated"] = True
                    st.query_params.clear()  # Clean URL bar
                    st.success(f"Welcome back, {user_data.get('name', 'User')}!")
                    st.rerun()
                else:
                    st.error("Google authentication failed on backend.")
            except Exception as e:
                st.error(f"Error connecting to backend server: {e}")

    col1, col2, col3 = st.columns([1, 1.5, 1])

    with col2:
        st.markdown("### 🌐 Fast Auth")

        # -------------------------------------------------------------------
        # 3. DIRECT GOOGLE OAUTH URL
        # -------------------------------------------------------------------
        oauth_params = {
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "prompt": "select_account",
            "access_type": "online"
        }
        google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(oauth_params)}"

        # Custom HTML link button for reliable redirection
        st.markdown(
            f"""
            <a href="{google_auth_url}" target="_self" style="text-decoration: none;">
                <div style="
                    background-color: #4285F4;
                    color: white;
                    padding: 12px 20px;
                    border-radius: 8px;
                    text-align: center;
                    font-weight: bold;
                    font-size: 16px;
                    margin-bottom: 15px;
                    box-shadow: 0px 2px 4px rgba(0,0,0,0.2);
                    cursor: pointer;">
                    🔴 Select Google Account
                </div>
            </a>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<div style='text-align: center; margin: 15px 0;'><strong>— OR —</strong></div>", unsafe_allow_html=True)

        # -------------------------------------------------------------------
        # 4. MANUAL EMAIL FORM
        # -------------------------------------------------------------------
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
                            timeout=25
                        )
                        if res.status_code == 200:
                            user_data = res.json().get("user", {})
                            st.session_state["user"] = user_data
                            st.session_state["user_id"] = user_data.get("id", 1)
                            st.session_state["logged_in"] = True
                            st.session_state["authenticated"] = True
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("Invalid email or password.")
                    except Exception as e:
                        st.error(f"Error connecting to backend API: {e}")

        st.markdown("---")
        st.write("Don't have an account yet?")
        if st.button("✨ Create New Account", use_container_width=True):
            st.session_state["page"] = "signup"
            st.rerun()


if __name__ == "__main__":
    show()