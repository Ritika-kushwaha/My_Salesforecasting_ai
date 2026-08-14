import os
import streamlit as st

# Page Setup
st.set_page_config(
    page_title="SalesGenie AI | B2B Sales Automation",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inline Custom Theme Function
def apply_custom_theme():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Glassmorphic KPI Cards */
        .kpi-card {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(12px);
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
            transition: all 0.2s ease-in-out;
            margin-bottom: 12px;
        }
        .kpi-card:hover {
            transform: translateY(-2px);
            border-color: rgba(99, 102, 241, 0.4);
            box-shadow: 0 20px 25px -5px rgba(99, 102, 241, 0.12);
        }
        .kpi-label {
            font-size: 0.8rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #94A3B8;
            margin-bottom: 6px;
        }
        .kpi-value {
            font-size: 1.9rem;
            font-weight: 800;
            color: #6366F1;
            line-height: 1.1;
        }

        /* Sidebar User Profile Card */
        .user-profile-badge {
            display: flex;
            align-items: center;
            gap: 12px;
            background: rgba(99, 102, 241, 0.08);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 12px;
            padding: 12px 14px;
            margin-top: 15px;
            margin-bottom: 12px;
        }
        .user-avatar {
            width: 38px;
            height: 38px;
            border-radius: 50%;
            background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 700;
            font-size: 1.05rem;
            flex-shrink: 0;
        }
        .user-info {
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .user-name {
            font-size: 0.9rem;
            font-weight: 700;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .user-email {
            font-size: 0.72rem;
            color: #94A3B8;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        /* Modernized Buttons */
        .stButton>button {
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.15s ease-in-out;
        }
        .stButton>button:hover {
            transform: scale(1.01);
        }

        /* Clean Table Corners */
        [data-testid="stDataFrame"] {
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Apply global styles
apply_custom_theme()

# Auth modules
import login
import signup

# Feature modules
from modules import module1_leads as leads
from modules import module2_company as company
from modules import module3_outreach as outreach
from modules import module4_scoring as scoring
from modules import module5_conversation as conversation
from modules import module6_dashboard as dashboard

# Session defaults
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_id" not in st.session_state:
    st.session_state["user_id"] = 1
if "user" not in st.session_state:
    st.session_state["user"] = {}


def render_sidebar():
    with st.sidebar:
        # App Branding Header
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 10px; padding: 10px 0 18px 0;">
                <div style="background: linear-gradient(135deg, #6366F1, #8B5CF6); width: 38px; height: 38px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px;">⚡</div>
                <div>
                    <h2 style="margin: 0; font-size: 1.25rem; font-weight: 800; letter-spacing: -0.02em;">SalesGenie</h2>
                    <p style="margin: 0; font-size: 0.72rem; color: #94A3B8; font-weight: 600;">AI B2B WORKSPACE</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Navigation Options
        nav_options = [
            "📊 Executive Dashboard",
            "📋 Lead Pipeline",
            "🏢 Company Intelligence",
            "✍️ AI Outreach Generator",
            "🎯 Lead Scoring & Qualification",
            "🎙️ Conversation Intelligence",
        ]

        if "current_page" not in st.session_state:
            st.session_state["current_page"] = nav_options[0]

        selected_page = st.radio("Navigation", nav_options, label_visibility="collapsed")
        st.session_state["current_page"] = selected_page

        st.markdown("<div style='flex-grow: 1; height: 20vh;'></div>", unsafe_allow_html=True)
        st.markdown("---")

        # Dynamic User Profile Card
        user = st.session_state.get("user", {})
        user_name = user.get("name") or "Sales Rep"
        user_email = user.get("email") or "user@salesgenie.ai"
        initial = user_name[0].upper() if user_name else "U"

        st.markdown(
            f"""
            <div class="user-profile-badge">
                <div class="user-avatar">{initial}</div>
                <div class="user-info">
                    <span class="user-name">{user_name}</span>
                    <span class="user-email">{user_email}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("🚪 Log Out", use_container_width=True, type="secondary"):
            st.session_state.clear()
            st.rerun()


# Page Routing Logic
if not st.session_state.get("authenticated", False):
    page = st.session_state.get("page", "login")
    user_obj = st.session_state.get("user", {})
    if isinstance(user_obj, dict) and "id" in user_obj:
        st.session_state["user_id"] = user_obj["id"]
    if page == "signup":
        signup.show()
    else:
        login.show()
else:
    render_sidebar()
    current = st.session_state.get("current_page", "📊 Executive Dashboard")

    if current == "📊 Executive Dashboard":
        dashboard.show()
    elif current == "📋 Lead Pipeline":
        leads.show()
    elif current == "🏢 Company Intelligence":
        company.show()
    elif current == "✍️ AI Outreach Generator":
        outreach.show()
    elif current == "🎯 Lead Scoring & Qualification":
        scoring.show()
    elif current == "🎙️ Conversation Intelligence":
        conversation.show()