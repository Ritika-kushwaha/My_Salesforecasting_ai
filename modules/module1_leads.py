<<<<<<< Updated upstream
import re
import os
import textwrap
from unittest import result
=======
>>>>>>> Stashed changes
import streamlit as st
import requests
import pandas as pd
import os

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")

<<<<<<< Updated upstream
# =========================================================
# DESIGN TOKENS  ·  matches the "Pipeline Console" dashboard theme
# =========================================================
PANEL       = "transparent"
PANEL_ALT   = "transparent"
BORDER      = "#000000"
TEXT        = "#ADB6CB"   # dark, for readability against the gradient background
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
    if not st.session_state.get("logged_in"):
        st.warning("Please login first.")
        st.stop()

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
<div class="page-header">
    <div class="page-tag">LEAD MANAGEMENT</div>
    <div class="page-title">Add New Lead</div>
    <div class="page-subtitle">
        Create and store a new lead in the SalesGenie CRM.
    </div>
</div>
""", unsafe_allow_html=True)
    st.caption(
        "SalesGenie AI • Lead Management & Intelligence Engine • 2026"
    )
    st.info(
        "➕ Fill in the lead details below. Once submitted, the lead will be saved to the database and appear on the dashboard."
    )

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

        submitted = st.form_submit_button("➕ Add Lead")

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
   
=======
def show():
    st.markdown("## 👥 Lead Management")
    st.caption("Manage, view, and bulk import B2B leads into your pipeline.")

    user_id = st.session_state.get("user", {}).get("id", 1)

    # Tabs for different Lead Actions
    tab1, tab2, tab3 = st.tabs(["📋 View All Leads", "➕ Add Single Lead", "📁 Bulk CSV Upload"])

    # -------------------------------------------------------------------
    # TAB 1: VIEW LEADS (Fixes column header display issue)
    # -------------------------------------------------------------------
    with tab1:
        st.markdown("### Existing Leads")
        if st.button("🔄 Refresh Data", type="secondary"):
            st.rerun()

        try:
            res = requests.get(f"{API_URL}/leads", params={"user_id": user_id}, timeout=10)
            if res.status_code == 200:
                leads_data = res.json()
                if leads_data:
                    df = pd.DataFrame(leads_data)

                    # Ensure proper column names and ordering
                    display_columns = {
                        "name": "Contact Name",
                        "company": "Company Name",
                        "email": "Email Address",
                        "phone": "Phone Number",
                        "industry": "Industry",
                        "lead_score": "Lead Score",
                        "priority": "Priority",
                        "status": "Status"
                    }

                    # Clean up fallback keys if API returned alternate names
                    if "contact_name" in df.columns and "name" not in df.columns:
                        df["name"] = df["contact_name"]
                    if "company_name" in df.columns and "company" not in df.columns:
                        df["company"] = df["company_name"]

                    # Filter and rename for display
                    available_cols = [col for col in display_columns.keys() if col in df.columns]
                    df_display = df[available_cols].rename(columns=display_columns)

                    st.dataframe(df_display, use_container_width=True, hide_index=True)
                else:
                    st.info("No leads found in database. Add a lead manually or upload a CSV.")
            else:
                st.error("Failed to load leads from backend server.")
        except Exception as e:
            st.error(f"Connection error: {e}")

    # -------------------------------------------------------------------
    # TAB 2: ADD SINGLE LEAD
    # -------------------------------------------------------------------
    with tab2:
        st.markdown("### ➕ Add New Lead Manually")
        with st.form("add_lead_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Contact Name *", placeholder="e.g. John Doe")
                company = st.text_input("Company Name *", placeholder="e.g. Acme Corp")
                email = st.text_input("Email Address *", placeholder="e.g. john@acme.com")
                phone = st.text_input("Phone Number", placeholder="e.g. +1 555-0192")
>>>>>>> Stashed changes

            with col2:
                industry = st.selectbox("Industry", ["Technology", "Healthcare", "Finance", "Retail", "Manufacturing", "Other"])
                company_size = st.selectbox("Company Size", ["1-10", "11-50", "51-200", "201-500", "500+"])
                revenue = st.selectbox("Annual Revenue", ["<$1M", "$1M-$10M", "$10M-$50M", "$50M+"])
                priority = st.selectbox("Priority", ["High", "Medium", "Low"])

<<<<<<< Updated upstream
if __name__ == "__main__":
    st.set_page_config(page_title="Add Lead", page_icon="➕", layout="wide")
    show()
=======
            submitted = st.form_submit_button("🚀 Save Lead", type="primary", use_container_width=True)

            if submitted:
                if not name or not company or not email:
                    st.warning("⚠️ Contact Name, Company Name, and Email are required.")
                else:
                    payload = {
                        "name": name,
                        "company": company,
                        "email": email,
                        "phone": phone,
                        "industry": industry,
                        "company_size": company_size,
                        "revenue": revenue,
                        "priority": priority,
                        "status": "New"
                    }
                    try:
                        res = requests.post(f"{API_URL}/leads", params={"user_id": user_id}, json=payload)
                        if res.status_code in [200, 201]:
                            st.success(f"✅ Lead '{name}' created successfully!")
                        else:
                            st.error(f"Failed to add lead: {res.text}")
                    except Exception as e:
                        st.error(f"Error connecting to backend: {e}")

    # -------------------------------------------------------------------
    # TAB 3: BULK CSV UPLOAD
    # -------------------------------------------------------------------
    with tab3:
        st.markdown("### 📁 Import Leads from CSV File")
        st.caption("Upload a `.csv` file containing lead records.")

        uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

        # In Tab 3 (Bulk CSV Upload) of module1_leads.py:
    if uploaded_file is not None:
      try:
        csv_df = pd.read_csv(uploaded_file)
        
        # CRITICAL: Replace NaN values with empty strings so JSON conversion doesn't send floats
        csv_df = csv_df.fillna("")

        st.markdown("#### 📄 Preview Uploaded Data:")
        st.dataframe(csv_df.head(5), use_container_width=True)

        if st.button("📤 Upload & Save All Leads to Database", type="primary"):
            records = csv_df.to_dict(orient="records")
            
            with st.spinner("Importing leads into PostgreSQL..."):
                res = requests.post(f"{API_URL}/leads/bulk", params={"user_id": user_id}, json=records)
                
                if res.status_code == 200:
                    st.success(f"🎉 {res.json().get('message', 'Leads imported successfully!')}")
                else:
                    st.error(f"Failed to bulk upload leads: {res.text}")
      except Exception as e:
        st.error(f"Could not parse CSV file: {e}")
>>>>>>> Stashed changes
