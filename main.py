import streamlit as st
import login
import signup

st.set_page_config(
    page_title="Sales Genie AI",
    page_icon="🤖",
    layout="wide"
)

#----------------- Login Check -------------------

if "page" not in st.session_state:
    st.session_state.page = "login"

#----------------- Page Navigation -------------------
st.markdown("""
<style>
.main {
    background-color: #f8fafc;
}

.stButton>button{
    width:100%;
    border-radius:8px;
    height:45px;
    background:#2563eb;
    color:white;
    font-weight:bold;
}

.stTextInput input{
    border-radius:8px;
}

section[data-testid="stSidebar"]{
    background:#f1f5f9;
}
</style>
""", unsafe_allow_html=True)

# ---------------- Page Navigation ----------------
if st.session_state.page == "login":
    login.login()

elif st.session_state.page == "signup":
    signup.signup()