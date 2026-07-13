import streamlit as st
import login
import signup
from modules import module6_dashboard as dashboard
from modules import module1_leads as leads
from modules import module2_company as company
from modules import module3_outreach as outreach
from modules import module4_scoring as scoring
from modules import module5_conversation as crm
from components.theme import load_theme


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