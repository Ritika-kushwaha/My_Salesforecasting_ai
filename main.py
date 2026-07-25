import streamlit as st

# Imports for authentication views
import login
import signup

# Imports for functional modules
from modules import module6_dashboard as dashboard
from modules import module1_leads as leads
from modules import module2_company as company
from modules import module3_outreach as outreach
from modules import module4_scoring as scoring
from modules import module5_conversation as crm

# Custom UI Theme and Navbar Components
from components.theme import load_theme
from components.navbar import render_sidebar
from components.header import render_header
import login  # or from modules/pages import login

# Check login status
if not st.session_state.get("logged_in", False):
    # Call the login view
    if hasattr(login, "login"):
        login.login()
    elif hasattr(login, "show"):
        login.show()
    st.stop()

def main():
    # 1. Page Configuration
    render_header(
        title="Dashboard Overview", 
        subtitle="Real-time sales performance and AI pipeline stats"
    )
    st.set_page_config(
        page_title="SalesGenie AI",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # 2. Load Global Dark Theme Styling
    load_theme()

    # 3. Session State Initialization
    if "page" not in st.session_state:
        st.session_state.page = "login"

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "Dashboard"

    # 4. App Routing Logic
    if st.session_state.logged_in:
        # Render the custom dark enterprise vertical navbar
        render_sidebar()

        # Retrieve current selected tab
        current_tab = st.session_state.get("active_tab", "Dashboard")

        # Route to respective module view
        if current_tab == "Dashboard":
            dashboard.show()

        elif current_tab == "Lead Management":
            leads.show()

        elif current_tab == "Company Intelligence":
            company.show()

        elif current_tab == "AI Outreach":
            outreach.show()

        elif current_tab == "Lead Scoring":
            scoring.show()

        elif current_tab == "CRM":
            crm.show()

    # Unauthenticated Views
    elif st.session_state.page == "login":
        login.login()

    elif st.session_state.page == "signup":
        signup.signup()


if __name__ == "__main__":
    main()