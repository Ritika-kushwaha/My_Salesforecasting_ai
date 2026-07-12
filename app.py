import login
import streamlit as st

from modules import module1_leads
from modules import module2_company
from modules import module3_enrichment
from modules import module4_email
from modules import module5_scoring
from modules import module6_dashboard

st.set_page_config(
    page_title="SalesGenie AI",
    page_icon="🤖",
    layout="wide"
)

# --------- Login Check -----------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login.login()
    st.stop()

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
st.sidebar.markdown("<br>" * 11, 
unsafe_allow_html=True) 

st.sidebar.divider() 

if st.sidebar.button("Logout", 
use_container_width=True): 
        st.session_state.logged_in = False 
        st.rerun()

# ---------- Navigation ----------
if option == "Add Lead":
    module1_leads.show()

elif option == "Analyze Company":
    module2_company.show()

elif option == "Lead Enrichment":
    module3_enrichment.show()

elif option == "Generate Email":
    module4_email.show()

elif option == "Lead Score":
    module5_scoring.show()

elif option == "Dashboard":
    module6_dashboard.show()