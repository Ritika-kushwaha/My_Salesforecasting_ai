import re
import os
import textwrap
from unittest import result
import streamlit as st
import requests
from components.theme import load_theme

load_theme()

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")

# =========================================================
# DESIGN TOKENS  ·  matches the "Pipeline Console" dashboard theme
# =========================================================
PANEL       = "transparent"
PANEL_ALT   = "transparent"
BORDER      = "#000000"
TEXT        = "#FBF5F5"   # dark, for readability against the gradient background
TEXT_DIM    = "#4C535D"
GREEN       = "#348BD3"
RED         = "#F87171"

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def load_custom_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {{ font-family:'Inter', sans-serif; }}

    /* Scoped to .main only, so the sidebar and Streamlit's own
       toolbar (Rerun/Deploy/menu) are left completely untouched. */
    .main, .main p, .main span, .main li, .main label {{
        color: {TEXT};
    }}

    .console-eyebrow {{
        display:flex; align-items:center; gap:8px;
        font-family:'JetBrains Mono', monospace;
        font-size:12px; letter-spacing:2px; font-weight:600;
        color:{GREEN}; text-transform:uppercase; margin-bottom:10px;
    }}
    .console-title {{
        font-size:clamp(28px, 6vw, 40px); font-weight:700; color:{TEXT};
        margin:0 0 6px 0; letter-spacing:-0.5px;
    }}
    .console-sub {{
        font-size:14px; color:{TEXT_DIM}; margin:0 0 24px 0;
    }}
    .hairline {{ height:1px; background:{BORDER}; border:none; margin:20px 0; }}

    /* ---------------- Form panel ---------------- */
    div[data-testid="stForm"] {{
        background:{PANEL}; border:1.5px solid {BORDER}; border-radius:12px;
        padding:28px 28px 20px 28px;
    }}

    /* Field labels */
    .stTextInput label, .stSelectbox label {{
        font-family:'JetBrains Mono', monospace !important;
        font-size:11px !important; font-weight:700 !important;
        letter-spacing:1.5px !important; text-transform:uppercase !important;
        color:{TEXT_DIM} !important;
    }}

    /* Input boxes: light translucent background + dark text.
       (Fixes the original bug: text color was forced black but the
       background stayed Streamlit's default dark box, so typed text
       was effectively invisible.) */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {{
        background:{PANEL_ALT} !important;
        border:1.5px solid {BORDER} !important;
        border-radius:8px !important;
        color:{TEXT} !important;
        font-size:14.5px !important;
    }}
    .stTextInput input:focus {{
        border-color:{BORDER} !important;
        box-shadow:0 0 0 2px rgba(0,0,0,0.12) !important;
    }}
    .stTextInput input::placeholder {{ color:#6B7280 !important; }}

    /* Buttons */
    .stFormSubmitButton>button {{
        background:#111827 !important; color:#FFFFFF !important;
        border:none !important; border-radius:8px !important;
        font-family:'JetBrains Mono', monospace !important;
        font-weight:600 !important; letter-spacing:0.5px !important;
        padding:10px 22px !important;
    }}
    .stFormSubmitButton>button:hover {{
        background:transparent !important; color:#111827 !important;
        border:1px solid #111827 !important;
    }}
    .stButton>button {{ border-radius:8px !important; }}

    .field-hint {{
        font-family:'JetBrains Mono', monospace; font-size:11px;
        color:{TEXT_DIM}; margin-top:-6px; margin-bottom:14px;
    }}
    </style>
    """, unsafe_allow_html=True)


def validate(company: str, industry: str, name: str, email: str, phone: str):

    errors = []

    if not company.strip():
        errors.append("Company Name is required.")

    if not name.strip():
        errors.append("Contact Name is required.")

    if not email.strip():
        errors.append("Email is required.")

    elif not EMAIL_RE.match(email.strip()):
        errors.append("Email doesn't look valid — check the format.")

    return errors


def show():
    load_custom_css()

    st.markdown("""
    <style>             
    .page-header{
        margin-top:-40px;
        margin-bottom:25px;
    }

    .page-tag{
        display:inline-block;
        background:rgba(37,99,235,.12);
        color:#2563EB;
        padding:6px 14px;
        border-radius:30px;
        font-size:13px;
        font-weight:700;
        letter-spacing:1px;
        text-transform:uppercase;
        margin-bottom:14px;
    }

    .page-title{
        font-size:42px;
        font-weight:800;
        color:#111827;
        margin-bottom:8px;
    }

    .page-subtitle{
        font-size:17px;
        color:#4B5563;
        line-height:1.6;
        max-width:760px;
    }

    .info-box{
        margin-top:22px;
        margin-bottom:20px;
        padding:18px 22px;
        background:rgba(255,255,255,.45);
        border-left:5px solid #2563EB;
        border-radius:12px;
        font-size:15px;
        color:#374151;
    }
    </style>

    <div class="page-header">

    <div class="page-tag">
    Lead Management
    </div>

    <div class="page-title">
    Add New Lead
    </div>

    <div class="page-subtitle">
    Capture new prospects and instantly add them to the SalesGenie CRM pipeline for tracking, analysis, and AI-powered insights.
    </div>

    </div>

    <div class="info-box">
    <b>Quick Tip</b><br>
    Complete all required fields and click <b>Add Lead</b>. Once saved, the lead will automatically become available across the Dashboard, Lead Scoring, CRM, and AI modules.
    </div>

    """, unsafe_allow_html=True)

    with st.form("lead_form", clear_on_submit=True):

        company = st.text_input("Company Name", placeholder="e.g. Acme Corp")

        c1, c2 = st.columns(2)

        with c1:
            industry = st.selectbox(
                "Industry",
                [
                    "",
                    "Technology",
                    "Software",
                    "SaaS",
                    "E-Commerce",
                    "IT Services",
                    "Finance",
                    "Healthcare",
                    "Manufacturing",
                    "Other",
                ],
            )

        with c2:
            name = st.text_input(
                "Contact Name",
                placeholder="e.g. Jane Doe"
            )
        c3, c4 = st.columns(2)

        with c3:
            email = st.text_input(
                "Email",
                placeholder="name@company.com"
            )

        with c4:
            phone = st.text_input(
                "Phone",
                placeholder="+1 (555) 123-4567"
            )

        submitted = st.form_submit_button("Add Lead")

    if submitted:

        errors = validate(company, industry, name, email, phone)

        if errors:
            for e in errors:
                st.warning(e)

        else:

            data = {
                "name": name.strip(),
                "email": email.strip(),
                "phone": phone.strip(),
                "company": company.strip(),
                "industry": industry,
            }

            try:
                with st.spinner("💾 Saving lead to database..."):
                    response = requests.post(
                        f"{API_URL}/add-lead",
                        json=data,
                        timeout=8,
                    )

                if response.status_code in [200, 201]:
                    result = response.json()

                    st.success("✅ Lead Added Successfully!")
                    st.info(f"""
                            Company : {company}
                            Contact : {name}
                            Industry : {industry}
                            Lead ID : {result.get('lead_id')}
""")
                    st.divider()

                else:
                    st.error(
                        f"Error {response.status_code}\n\n{response.text}"
                    )

            except requests.exceptions.ConnectionError:

                st.error(
                    f"Cannot connect to FastAPI backend.\n\n"
                    f"Make sure the backend is running at:\n{API_URL}"
                )

            except requests.exceptions.Timeout:

                st.error("Request Timed Out.")

            except Exception as e:

                st.error(f"Unexpected Error:\n{e}")
   


if __name__ == "__main__":
    st.set_page_config(page_title="Add Lead", page_icon="➕", layout="wide")
    show()