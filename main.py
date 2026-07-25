import streamlit as st
<<<<<<< Updated upstream
import login
import signup
from modules import module6_dashboard as dashboard
from modules import module1_leads as leads
from modules import module2_company as company
from modules import module3_outreach as outreach
from modules import module4_scoring as scoring
from modules import module5_conversation as crm
from components.theme import load_theme
=======

st.set_page_config(
    page_title="SalesGenie AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

import login
import signup
from components.theme import load_theme
from components.navbar import render_sidebar

def main():
    load_theme()

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "Dashboard"

    if not st.session_state.logged_in:
        if hasattr(login, "show"):
            login.show()
        elif hasattr(login, "render_login_page"):
            login.render_login_page()
        elif hasattr(login, "login"):
            login.login()
        return

    # Render sidebar ONCE when logged in
    render_sidebar()

    current_tab = st.session_state.get("active_tab", "Dashboard")
>>>>>>> Stashed changes

    if current_tab == "Dashboard":
        from modules import module6_dashboard as dashboard
        dashboard.show()
    elif current_tab == "Lead Management":
        from modules import module1_leads as leads
        leads.show()
    elif current_tab == "Company Intelligence":
        from modules import module2_company as company
        company.show()
    elif current_tab == "AI Outreach":
        from modules import module3_outreach as outreach
        outreach.show()
    elif current_tab == "Lead Scoring":
        from modules import module4_scoring as scoring
        scoring.show()
    elif current_tab == "CRM Conversations":
        from modules import module5_conversation as crm
        crm.show()

if __name__ == "__main__":
    st.set_page_config(
        page_title="Sales Genie AI",
        page_icon="🤖",
        layout="wide"
        )
    
load_theme()
if "page" not in st.session_state:
    st.session_state.page = "login"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
#----------------- Login Check -------------------

if "page" not in st.session_state:
    st.session_state.page = "login"


if st.session_state.logged_in:

    with st.sidebar:
        st.success(f"Welcome, {st.session_state.user['name']} 👋")
        page = st.radio(
            
            "Navigation",
            [
                "Lead Management",
                "Company Intelligence",
                "AI Outreach",
                "Lead Scoring",
                "CRM",
                "Dashboard"
            ]
        )
        st.divider()
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.page = "login"
            st.session_state.pop("user", None)
            st.rerun()

    if page == "Lead Management":
        leads.show()

    elif page == "Company Intelligence":
        company.show()

    elif page == "AI Outreach":
        outreach.show()

    elif page == "Lead Scoring":
        scoring.show()

    elif page == "CRM":
        crm.show()

    elif page == "Dashboard":
        dashboard.show()

elif st.session_state.page == "login":
    login.login()

elif st.session_state.page == "signup":
    signup.signup()