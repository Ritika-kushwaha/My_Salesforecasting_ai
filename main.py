import streamlit as st

# 1. Page Config MUST be the very first Streamlit command
st.set_page_config(
    page_title="SalesGenie AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Authentication views
import login
import signup

# UI Components
from components.theme import load_theme
from components.navbar import render_sidebar

# Application Modules
from modules import module1_leads as leads
from modules import module2_company as company
from modules import module3_outreach as outreach
from modules import module4_scoring as scoring
from modules import module5_conversation as crm
from modules import module6_dashboard as dashboard


def main():
    # 2. Inject global dark CSS theme
    load_theme()

    # 3. Initialize state variables
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "Dashboard"

    # 4. Auth Gate
    if not st.session_state.logged_in:
        page = st.session_state.get("page", "login")
        if page == "signup":
            signup.signup()
        else:
            if hasattr(login, "render_login_page"):
                login.render_login_page()
            elif hasattr(login, "show"):
                login.show()
            elif hasattr(login, "login"):
                login.login()
        return  # Halt UI rendering until logged in

    # 5. Render Sidebar Navigation for authenticated users
    render_sidebar()

    # 6. Route to selected active tab module
    current_tab = st.session_state.get("active_tab", "Dashboard")

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
    elif current_tab == "CRM Conversations":
        crm.show()


if __name__ == "__main__":
    main()