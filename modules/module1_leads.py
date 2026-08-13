import io
import os
import re
import pandas as pd
import requests
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")


def generate_pdf(lead):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, f"Lead Brief: {lead.get('name', 'N/A')}")
    c.setFont("Helvetica", 12)
    c.drawString(100, 720, f"Company: {lead.get('company', 'N/A')}")
    c.drawString(100, 700, f"Email: {lead.get('email', 'N/A')}")
    c.drawString(100, 680, f"Phone: {lead.get('phone', 'N/A')}")
    c.drawString(100, 660, f"Industry: {lead.get('industry', 'N/A')}")
    c.drawString(100, 640, f"Company Size: {lead.get('company_size', 'N/A')}")
    c.drawString(100, 620, f"Revenue: ${lead.get('revenue', 'N/A')}")
    c.drawString(100, 600, f"Priority: {lead.get('priority', 'N/A')}")
    c.drawString(100, 580, f"Status: {lead.get('status', 'N/A')}")
    c.save()
    buffer.seek(0)
    return buffer


def show():
    st.header("📋 Module 1: Lead Management & Export")

    user_id = st.session_state.get("user_id", 1)

    # Load leads into session state if not present
    if "leads" not in st.session_state or st.session_state.get("force_refresh_leads"):
        try:
            res = requests.get(f"{API_URL}/leads", params={"user_id": user_id}, timeout=5)
            if res.status_code == 200:
                st.session_state["leads"] = res.json()
            else:
                st.error("Failed to fetch leads from server.")
                st.session_state["leads"] = []
        except Exception as e:
            st.error(f"Could not connect to backend server: {e}")
            st.session_state["leads"] = []
        st.session_state["force_refresh_leads"] = False

    # Lead Creation Section
    with st.expander("➕ Add New Lead", expanded=False):
        with st.form("add_lead_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Contact Name *")
                company = st.text_input("Company Name *")
                email = st.text_input("Email *")
                phone = st.text_input("Phone Number")
            with col2:
                industry = st.selectbox(
                    "Industry", ["Technology", "Healthcare", "Finance", "Retail", "Manufacturing", "General"]
                )
                company_size = st.selectbox("Company Size", ["1-10", "11-50", "51-200", "201-500", "500+"])
                revenue = st.number_input("Annual Revenue ($)", min_value=0.0, step=10000.0)
                priority = st.selectbox("Priority", ["Low", "Medium", "High"])

            submit = st.form_submit_button("Save Lead", type="primary")

            if submit:
                if not name or not company or not email:
                    st.error("Name, Company, and Email are required!")
                else:
                    payload = {
                        "name": name,
                        "company": company,
                        "email": email,
                        "phone": phone,
                        "industry": industry,
                        "company_size": company_size,
                        "revenue": str(revenue),
                        "priority": priority,
                        "status": "New",
                    }
                    try:
                        res = requests.post(f"{API_URL}/leads", params={"user_id": user_id}, json=payload, timeout=5)
                        if res.status_code == 200:
                            st.success("Lead added successfully!")
                            st.session_state["force_refresh_leads"] = True
                            st.rerun()
                        else:
                            st.error(f"Error adding lead: {res.text}")
                    except Exception as ex:
                        st.error(f"Connection error: {ex}")

    # Display Leads Table
    st.subheader("Your Leads")
    if not st.session_state.get("leads"):
        st.info("No leads found. Click 'Add New Lead' above to get started!")
    else:
        df = pd.DataFrame(st.session_state["leads"])

        # Format revenue column for better display
        if "revenue" in df.columns:
            df["revenue"] = df["revenue"].apply(
                lambda x: f"${float(x):,.2f}" if str(x).replace(".", "", 1).isdigit() else str(x)
            )

        # -------------------------------------------------------------
        # 1. ADD ROW COUNTER FOR CLEAN DISPLAY (#1, #2, #3...)
        # -------------------------------------------------------------
        df["#"] = range(1, len(df) + 1)

        # Filter out backend primary key IDs and place '#' at the front
        cols = ["#"] + [c for c in df.columns if c not in ["#", "id", "user_id"]]

        # -------------------------------------------------------------
        # 2. RENDER DATAFRAME WITH HIDDEN STREAMLIT INDEX
        # -------------------------------------------------------------
        st.dataframe(df[cols], use_container_width=True, hide_index=True)

        # Export Brief Section
        st.subheader("📄 Export Lead Brief (PDF)")
        lead_options = {f"{l.get('name', 'N/A')} ({l.get('company', 'N/A')})": l for l in st.session_state["leads"]}
        selected_lead_label = st.selectbox("Select a Lead to Export", list(lead_options.keys()))

        if selected_lead_label:
            selected_lead = lead_options[selected_lead_label]
            pdf_bytes = generate_pdf(selected_lead)
            st.download_button(
                label="📥 Download PDF Brief",
                data=pdf_bytes,
                file_name=f"Lead_Brief_{selected_lead.get('name', 'Lead')}.pdf",
                mime="application/pdf",
            )


if __name__ == "__main__":
    show()