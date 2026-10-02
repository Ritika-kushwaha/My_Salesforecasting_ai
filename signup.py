import os
import requests
import streamlit as st

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")


def apply_auth_theme():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}

        /* Centered Glass Card */
        .auth-card {
            background: rgba(15, 23, 42, 0.85);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 24px;
            padding: 36px 32px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(20px);
        }

        /* Inputs & Buttons */
        .stTextInput>div>div>input {
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.04) !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            color: #F8FAFC !important;
            padding: 10px 14px;
        }
        .stTextInput>div>div>input:focus {
            border-color: #6366F1 !important;
            box-shadow: 0 0 0 1px #6366F1 !important;
        }
        .stButton>button {
            border-radius: 12px;
            font-weight: 700;
            padding: 10px 20px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show():
    apply_auth_theme()

    # Centered Column Layout
    st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)
    _, col_center, _ = st.columns([1, 1.25, 1])

    with col_center:
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 24px;">
                <div style="background: linear-gradient(135deg, #10B981, #6366F1); width: 48px; height: 48px; border-radius: 14px; display: inline-flex; align-items: center; justify-content: center; font-size: 24px; box-shadow: 0 10px 25px -5px rgba(16, 185, 129, 0.4); margin-bottom: 12px;">🚀</div>
                <h1 style="font-size: 1.85rem; font-weight: 800; margin: 0; letter-spacing: -0.02em;">Create Workspace</h1>
                <p style="color: #94A3B8; font-size: 0.9rem; margin-top: 4px;">Set up your enterprise account in 60 seconds</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="auth-card">', unsafe_allow_html=True)

        with st.form("signup_form", clear_on_submit=False):
            full_name = st.text_input("Full Name *", placeholder="e.g. Alex Morgan").strip()
            email = st.text_input("Work Email Address *", placeholder="alex@company.com").strip()
            company_name = st.text_input("Company / Organization *", placeholder="e.g. Acme Tech").strip()
            password = st.text_input("Create Password *", type="password", placeholder="Minimum 6 characters").strip()

            agree = st.checkbox("I agree to the Terms of Service", value=True)

            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            create_btn = st.form_submit_button("✨ Launch Workspace", type="primary", use_container_width=True)

            if create_btn:
                if not full_name or not email or not password or not company_name:
                    st.error("Please fill in all required fields.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters.")
                elif not agree:
                    st.error("Please agree to the Terms of Service.")
                else:
                    with st.spinner("Creating workspace..."):
                        try:
                            payload = {
                                "email": email,
                                "name": full_name,
                                "company": company_name,
                                "avatar": "",
                            }
                            res = requests.post(f"{API_URL}/auth/sync-user", json=payload, timeout=8)
                            if res.status_code == 200:
                                user_data = res.json()
                            else:
                                user_data = {"id": 1, "email": email, "name": full_name}
                        except Exception:
                            user_data = {"id": 1, "email": email, "name": full_name}

                        st.session_state["authenticated"] = True
                        st.session_state["logged_in"] = True
                        st.session_state["user"] = user_data
                        st.session_state["user_id"] = user_data.get("id", 1)
                        st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

        # Switch back to Login
        sw_c1, sw_c2 = st.columns([1.2, 1])
        with sw_c1:
            st.caption("Already have an account?")
        with sw_c2:
            if st.button("Sign In Instead 🔑", use_container_width=True):
                st.session_state["page"] = "login"
                st.rerun()


if __name__ == "__main__":
    show()