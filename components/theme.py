import streamlit as st

# ---------- COLORS ----------

BG = "#F8FAFC"

CARD = "rgba(255,255,255,0.78)"

CARD_LIGHT = "rgba(255,255,255,0.55)"

BORDER = "#E5E7EB"

TEXT = "#111827"

TEXT_LIGHT = "#748098"

PRIMARY = "#4C8DFF"

SUCCESS = "#22C55E"

WARNING = "#F59E0B"

ERROR = "#EF4444"

PURPLE = "#8B5CF6"

CYAN = "#06B6D4"


def load_theme():
    st.markdown("""
    <style>
    /* Dark Theme Core */
    .stApp {
        background-color: #0b0f19;
        color: #f3f4f6;
    }

    /* Sidebar - Fixed display issue */
    [data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 1px solid #1f2937;
    }

    /* Input Fields */
    .stTextInput input, .stSelectbox select, .stTextArea textarea {
        background-color: #111827 !important;
        color: #f3f4f6 !important;
        border: 1px solid #374151 !important;
        border-radius: 8px !important;
    }

    /* Buttons */
    .stButton>button {
        border-radius: 8px !important;
        font-weight: 500 !important;
    }

    /* Cards/Containers */
    div[data-testid="stVerticalBlock"] > div {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)