import re
import os
import streamlit as st
import requests
from components.theme import load_theme

load_theme()

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate(company: str, industry: str, name: str, email: str):
    """Validate required input fields before sending requests to backend."""
    errors = []
    if not st.session_state.get("logged_in"):
        st.warning("Please log in first.")
        st.stop()

    if not company.strip():
        errors.append("Company Name is required.")

    if not name.strip():
        errors.append("Contact Name is required.")

    if not email.strip():
        errors.append("Email is required.")
    elif not EMAIL_RE.match(email.strip()):
        errors.append("Email format is invalid — e.g. name@company.com")

    return errors


def show():
    # Page Header
    st.markdown("""
        <div style="margin-bottom: 25px;">
            <div style="color: #6366f1; font-size: 12px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase;">
                Lead Management
            </div>
            <h1 style="font-size: 28px; font-weight: 800; color: #ffffff; margin-top: 4px;">
                ➕ Add New Lead
            </h1>
            <p style="color: #94a3b8; font-size: 14px;">
                Create and store a new lead into your isolated account database.
            </p>
        </div>
    """, unsafe_allow_html=True)

    with st.form("lead_form", clear_on_submit=True):
        company = st.text_input("Company Name *", placeholder="e.g. Acme Corp")

        c1, c2 = st.columns(2)
        with c1:
            industry = st.selectbox(
                "Industry *",
                [
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
            name = st.text_input("Contact Name *", placeholder="e.g. Jane Doe")

        c3, c4 = st.columns(2)
        with c3:
            email = st.text_input("Email *", placeholder="name@company.com")
        with c4:
            phone = st.text_input("Phone Number", placeholder="+1 (555) 123-4567")

        c5, c6 = st.columns(2)
        with c5:
            company_size = st.selectbox("Company Size", ["1-10", "11-50", "51-200", "201-500", "500+"])
        with c6:
            revenue = st.number_input("Annual Revenue ($)", min_value=0.0, step=10000.0, value=100000.0)

        st.write("")
        submitted = st.form_submit_button("➕ Add Lead to CRM", type="primary", use_container_width=True)

    if submitted:
        errors = validate(company, industry, name, email)

        if errors:
            for err in errors:
                st.warning(f"⚠️ {err}")
        else:
            # Get logged-in user id from session
            user_id = st.session_state.get("user", {}).get("id")

            if not user_id:
                st.error("User session missing! Please log out and log back in.")
                return

            # Payload matches Pydantic schema (LeadCreate)
            payload = {
                "name": name.strip(),
                "email": email.strip(),
                "phone": phone.strip() if phone else "",
                "company": company.strip(),
                "industry": industry,
                "company_size": company_size,
                "revenue": float(revenue),
            }

            try:
                with st.spinner("💾 Analyzing with AI and saving lead..."):
                    response = requests.post(
                        f"{API_URL}/add-lead",
                        params={"user_id": user_id},
                        json=payload,
                        timeout=25,
                    )

                if response.status_code in [200, 201]:
                    result = response.json()
                    st.success("✅ Lead Added Successfully!")
                    
                    st.markdown(f"""
                        <div style="background: #181a26; border: 1px solid #26293b; padding: 18px; border-radius: 12px; margin-top: 10px;">
                            <div style="color: #10b981; font-weight: 700; margin-bottom: 8px;">📊 AI Lead Evaluation Results</div>
                            <div style="color: #e2e8f0;"><b>Company:</b> {company}</div>
                            <div style="color: #e2e8f0;"><b>Contact:</b> {name} ({email})</div>
                            <div style="color: #e2e8f0;"><b>AI Lead Score:</b> <span style="color: #6366f1; font-weight: 700;">{result.get('lead_score', 'N/A')}</span></div>
                            <div style="color: #e2e8f0;"><b>Priority:</b> {result.get('priority', 'Medium')}</div>
                            <div style="color: #e2e8f0;"><b>Status:</b> {result.get('status', 'New')}</div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error(f"Failed to add lead (Error {response.status_code}):\n{response.text}")

            except requests.exceptions.ConnectionError:
                st.error(f"Cannot connect to backend server at `{API_URL}`. Ensure FastAPI is running.")
            except requests.exceptions.Timeout:
                st.error("Request timed out waiting for backend.")
            except Exception as e:
                st.error(f"An error occurred: {e}")


if __name__ == "__main__":
    st.set_page_config(page_title="Add Lead - SalesGenie", page_icon="➕", layout="wide")
    show()