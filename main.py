import streamlit as st

# 1. Page Configuration MUST be the first Streamlit command
st.set_page_config(
    page_title="SalesGenie AI Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Safely import auth views
import login
import signup

# Safely import business modules
from modules import module1_leads as leads
from modules import module2_company as company
from modules import module3_outreach as outreach
from modules import module4_scoring as scoring
from modules import module5_conversation as crm
from modules import module6_dashboard as dashboard

# Safely attempt to import theme/navbar components if they exist
try:
    from components.theme import load_theme
    from components.navbar import render_sidebar
    HAS_CUSTOM_COMPONENTS = True
except Exception:
    HAS_CUSTOM_COMPONENTS = False


def main():
    # 2. Inject CSS Theme safely
    if HAS_CUSTOM_COMPONENTS:
        try:
            load_theme()
        except Exception:
            pass

    # 3. Initialize Session State Keys
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if "active_tab" not in st.session_state:
        st.session_state["active_tab"] = "Dashboard"

    if "page" not in st.session_state:
        st.session_state["page"] = "login"

    # Evaluate if user is logged in
    is_user_authenticated = (
        st.session_state.get("logged_in", False) or 
        st.session_state.get("authenticated", False)
    )

    # ---------------------------------------------------------------------
    # 4. AUTHENTICATION GATE (Renders Login or Signup View)
    # ---------------------------------------------------------------------
    if not is_user_authenticated:
        target_page = st.session_state.get("page", "login")

        if target_page == "signup":
            if hasattr(signup, "show"):
                signup.show()
            elif hasattr(signup, "signup"):
                signup.signup()
        else:
            if hasattr(login, "show"):
                login.show()
            elif hasattr(login, "render_login_page"):
                login.render_login_page()
            elif hasattr(login, "login"):
                login.login()

        return  # Stop execution here until logged in

    # ---------------------------------------------------------------------
    # 5. MAIN APPLICATION DASHBOARD (Renders Navigation & Modules)
    # ---------------------------------------------------------------------
    # Navigation Sidebar
    st.sidebar.title("⚡ SalesGenie AI")
    
    user_info = st.session_state.get("user") or {}
    user_name = user_info.get("name", "Sales Rep") if isinstance(user_info, dict) else "Sales Rep"
    st.sidebar.caption(f"👤 Active User: **{user_name}**")

    st.sidebar.markdown("---")
    
    # Module Selector
    selected_module = st.sidebar.radio(
        "Select Feature Module:",
        [
            "📊 Executive Dashboard",
            "👥 Lead Management",
            "🏢 Company Intelligence",
            "✉️ AI Outreach & Campaign",
            "🎯 Lead Scoring Engine",
            "💬 Conversation Intelligence",
        ]
    )

    if st.sidebar.button("🚪 Log Out", use_container_width=True):
        st.session_state["logged_in"] = False
        st.session_state["authenticated"] = False
        st.session_state["user"] = None
        st.rerun()

    st.markdown("---")

    # 6. Route to selected active module view
    if "Dashboard" in selected_module:
        dashboard.show()
    elif "Lead Management" in selected_module:
        leads.show()
    elif "Company Intelligence" in selected_module:
        company.show()
    elif "AI Outreach" in selected_module:
        outreach.show()
    elif "Lead Scoring" in selected_module:
        scoring.show()
    elif "Conversation Intelligence" in selected_module:
        crm.show()


if __name__ == "__main__":
    main()