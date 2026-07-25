import streamlit as st

def load_theme():
    """Injects global dark theme CSS to override default Streamlit styling."""
    st.markdown("""
        <style>
        /* Import Google Font (Inter) */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        /* Global Typography & Background */
        html, body, [class*="css"], .stApp {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            background-color: #0d0e15 !important;
            color: #e2e8f0 !important;
        }

        /* Adjust Main Container Padding */
        .main .block-container {
            padding-top: 1.8rem !important;
            padding-bottom: 2.5rem !important;
            padding-left: 2.5rem !important;
            padding-right: 2.5rem !important;
            max-width: 1600px !important;
        }

        /* Headers and Headings */
        h1, h2, h3, h4, h5, h6 {
            color: #ffffff !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em !important;
        }

        p, label, span {
            color: #94a3b8 !important;
        }

        /* Input Fields (Text Inputs, Text Areas, Select Boxes) */
        .stTextInput input, .stTextArea textarea, div[data-baseweb="select"] > div {
            background-color: #181a26 !important;
            color: #ffffff !important;
            border: 1px solid #26293b !important;
            border-radius: 8px !important;
            padding: 10px 14px !important;
        }

        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: #6366f1 !important;
            box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
        }

        /* Primary Action Buttons */
        div.stButton > button[kind="primary"] {
            background-color: #4f46e5 !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            padding: 8px 18px !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3) !important;
        }

        div.stButton > button[kind="primary"]:hover {
            background-color: #4338ca !important;
            transform: translateY(-1px) !important;
        }

        /* Secondary Action Buttons */
        div.stButton > button[kind="secondary"] {
            background-color: #181a26 !important;
            color: #cbd5e1 !important;
            border: 1px solid #26293b !important;
            border-radius: 8px !important;
            font-weight: 500 !important;
            padding: 8px 18px !important;
            transition: all 0.2s ease !important;
        }

        div.stButton > button[kind="secondary"]:hover {
            background-color: #212435 !important;
            color: #ffffff !important;
            border-color: #3b82f6 !important;
        }

        /* Dataframes & Data Tables */
        [data-testid="stDataFrame"] {
            background-color: #181a26 !important;
            border: 1px solid #26293b !important;
            border-radius: 12px !important;
            padding: 8px !important;
        }

        /* Metric Cards Override */
        [data-testid="stMetricValue"] {
            color: #ffffff !important;
            font-weight: 700 !important;
        }
        
        [data-testid="stMetricLabel"] {
            color: #64748b !important;
        }

        /* Scrollbars Styling */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #0d0e15;
        }
        ::-webkit-scrollbar-thumb {
            background: #26293b;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #374151;
        }

        /* Hide Streamlit Header Menu & Footer Branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)