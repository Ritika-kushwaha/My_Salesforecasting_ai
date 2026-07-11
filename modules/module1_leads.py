import re
import os
import textwrap
import streamlit as st
import requests

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")

# =========================================================
# DESIGN TOKENS  ·  matches the "Pipeline Console" dashboard theme
# =========================================================
PANEL       = "transparent"
PANEL_ALT   = "transparent"
BORDER      = "#000000"
TEXT        = "#111827"   # dark, for readability against the gradient background
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


def validate(company: str, industry: str, contact: str, email: str, phone: str):
    """Returns a list of human-readable validation errors, empty if the form is OK."""
    errors = []
    if not company.strip():
        errors.append("Company Name is required.")
    if not contact.strip():
        errors.append("Contact Name is required.")
    if not email.strip():
        errors.append("Email is required.")
    elif not EMAIL_RE.match(email.strip()):
        errors.append("Email doesn't look valid — check the format (name@company.com).")
    return errors


def show():
    load_custom_css()

    st.markdown(textwrap.dedent(f"""
    <div class="console-eyebrow">LEAD CAPTURE &middot; NEW ENTRY</div>
    <div class="console-title">Add New Lead</div>
    <div class="console-sub">Log a new prospect straight into the pipeline.</div>
    """).strip(), unsafe_allow_html=True)

    with st.form("lead_form", clear_on_submit=False):
        company = st.text_input("Company Name", placeholder="e.g. Acme Corp")

        c1, c2 = st.columns(2)
        with c1:
            industry = st.selectbox(
                "Industry",
                ["", "Technology", "Software", "SaaS", "E-Commerce", "IT Services",
                 "Finance", "Healthcare", "Manufacturing", "Other"],
            )
        with c2:
            contact = st.text_input("Contact Name", placeholder="e.g. Jane Doe")

        c3, c4 = st.columns(2)
        with c3:
            email = st.text_input("Email", placeholder="name@company.com")
        with c4:
            phone = st.text_input("Phone", placeholder="+1 (555) 123-4567")

        st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
        submitted = st.form_submit_button("Add Lead", use_container_width=False)

        if submitted:
            errors = validate(company, industry, contact, email, phone)
            if errors:
                for e in errors:
                    st.warning(e)
            else:
                data = {
                    "company": company.strip(),
                    "industry": industry,
                    "contact": contact.strip(),
                    "email": email.strip(),
                    "phone": phone.strip(),
                }
                try:
                    with st.spinner("Adding lead…"):
                        response = requests.post(f"{API_URL}/add-lead", json=data, timeout=8)
                    if response.status_code == 200:
                        st.success(f"**{company}** was added to the pipeline ✅")
                    else:
                        st.error(f"Server returned an error ({response.status_code}): {response.text}")
                except requests.exceptions.ConnectionError:
                    st.error(f"Can't reach the API server at `{API_URL}`. Is it running?")
                except requests.exceptions.Timeout:
                    st.error("The request timed out — the server took too long to respond.")
                except Exception as e:
                    st.error(f"Something went wrong: {e}")


if __name__ == "__main__":
    st.set_page_config(page_title="Add Lead", page_icon="➕", layout="wide")
    show()