import login
import streamlit as st
from modules import module1_leads
from modules import module2_company
from modules import module3_outreach
from modules import module4_scoring
from modules import module5_conversation
from modules import module6_dashboard

st.set_page_config(
    page_title="SalesGenie AI",
    page_icon="🤖",
    layout="wide"
)

# --------- Login Check -----------
if "logged_in" not in st.session_state:
    if st.sidebar.button("Logout", use_container_width=True):
         st.session_state.clear()
         st.rerun()

if "user" not in st.session_state:
    st.session_state["user"] = None
if "logged_in" not in st.session_state:
    if st.sidebar.button("Logout", use_container_width=True):
         st.session_state.clear()
         st.rerun()

if not st.session_state.logged_in:
    login.login()
    st.stop()
option = st.sidebar.radio(
    "Choose Module",
    [
        "Dashboard",
        "Add Lead",
        "Analyze Company",
        "Lead Enrichment",
        "Generate Email",
        "Lead Score",
    ],
)
# ---------- Global CSS ----------
st.markdown("""
<style>

.stApp{
    background: linear-gradient(
        135deg,
        #E0F2FE 0%,
        #BFDBFE 30%,
        #93C5FD 55%,
        #A5B4FC 75%,
        #DDD6FE 100%
    );
    background-attachment: fixed;
}

</style>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------
st.sidebar.markdown("""
    <h1 style="
        font-size:34px;
        font-weight:600;
        margin:0;
    ">
        🤖 SalesGenie AI
    </h1>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
<h3>
Choose Module
</h3>
""", unsafe_allow_html=True)

option = st.sidebar.selectbox(
    "",
    [
        "Add Lead",
        "Analyze Company",
        "Lead Enrichment",
        "Generate Email",
        "Lead Score",
        "Dashboard"
    ],
    label_visibility="collapsed"
)

# ----------- Logout ------------

# Push logout down 
st.sidebar.markdown("---")
st.sidebar.write("")
st.sidebar.write("")

# Single divider
st.sidebar.divider() 

if st.sidebar.button("Logout"):
    st.session_state["logged_in"] = False
    st.session_state["user"] = None
    st.rerun()

# ---------- Navigation ----------
if "user" in st.session_state:
    st.sidebar.success(f"Welcome, {st.session_state.user}")
pages = {
    "Add Lead": module1_leads.show,
    "Analyze Company": module2_company.show,
    #"Lead Enrichment": module3_outreach.show,
    #"Generate Email": module4_scoring.show,
    #"Lead Score": module5_conversation.show,
    "Dashboard": module6_dashboard.show,
}

pages[option]()