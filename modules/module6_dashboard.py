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

    # Refresh leads state
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

    # -------------------------------------------------------------
    # 1. ADD / BULK IMPORT LEADS SECTION
    # -------------------------------------------------------------
    tab1, tab2 = st.tabs(["➕ Add Single Lead", "📁 Bulk Import (CSV)"])

    with tab1:
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

    with tab2:
        st.caption("Upload a CSV file with columns: `name`, `company`, `email`, `phone`, `industry`, `revenue`, `priority`, `status`")
        uploaded_file = st.file_uploader("Choose CSV File", type=["csv"])
        if uploaded_file is not None:
            try:
                csv_df = pd.read_csv(uploaded_file)
                st.write("Preview of leads to import:")
                st.dataframe(csv_df.head(), use_container_width=True)

                if st.button("🚀 Upload & Import All Leads", type="primary"):
                    bulk_payload = csv_df.to_dict(orient="records")
                    res = requests.post(
                        f"{API_URL}/leads/bulk",
                        params={"user_id": user_id},
                        json=bulk_payload,
                        timeout=10,
                    )
                    if res.status_code == 200:
                        st.success(res.json().get("message", "Bulk leads imported successfully!"))
                        st.session_state["force_refresh_leads"] = True
                        st.rerun()
                    else:
                        st.error(f"Failed to import leads: {res.text}")
            except Exception as e:
                st.error(f"Error processing CSV file: {e}")

    st.markdown("---")

    # -------------------------------------------------------------
    # 2. DISPLAY LEADS TABLE
    # -------------------------------------------------------------
    st.subheader("Your Leads")
    if not st.session_state.get("leads"):
        st.info("No leads found. Add your first lead above!")
    else:
        df = pd.DataFrame(st.session_state["leads"])

        # Format revenue
        if "revenue" in df.columns:
            df["revenue"] = df["revenue"].apply(
                lambda x: f"${float(x):,.2f}" if str(x).replace(".", "", 1).isdigit() else str(x)
            )

        # Add sequential UI counter
        df["#"] = range(1, len(df) + 1)
        cols = ["#"] + [c for c in df.columns if c not in ["#", "id", "user_id"]]

        st.dataframe(df[cols], use_container_width=True, hide_index=True)

        # -------------------------------------------------------------
        # 3. EDIT & DELETE LEAD SECTION
        # -------------------------------------------------------------
        st.markdown("---")
        st.subheader("⚡ Manage Selected Lead")

        lead_options = {
            f"#{idx + 1} - {l.get('name', 'N/A')} ({l.get('company', 'N/A')})": l
            for idx, l in enumerate(st.session_state["leads"])
        }
        selected_label = st.selectbox("Select Lead to Manage", list(lead_options.keys()))

        if selected_label:
            selected_lead = lead_options[selected_label]
            lead_db_id = selected_lead.get("id")

            action_col1, action_col2 = st.columns([2, 1])

            with action_col1:
                with st.expander("✏️ Edit Lead Details", expanded=False):
                    with st.form("edit_lead_form"):
                        e_name = st.text_input("Name", value=selected_lead.get("name", ""))
                        e_company = st.text_input("Company", value=selected_lead.get("company", ""))
                        e_email = st.text_input("Email", value=selected_lead.get("email", ""))
                        e_phone = st.text_input("Phone", value=selected_lead.get("phone", ""))
                        e_industry = st.text_input("Industry", value=selected_lead.get("industry", "General"))
                        
                        priorities = ["Low", "Medium", "High"]
                        cur_priority = selected_lead.get("priority", "Medium")
                        p_idx = priorities.index(cur_priority) if cur_priority in priorities else 1
                        e_priority = st.selectbox("Priority", priorities, index=p_idx)

                        statuses = ["New", "Contacted", "Qualified", "Proposal Sent", "Closed Won", "Closed Lost"]
                        cur_status = selected_lead.get("status", "New")
                        s_idx = statuses.index(cur_status) if cur_status in statuses else 0
                        e_status = st.selectbox("Status", statuses, index=s_idx)

                        save_changes = st.form_submit_button("💾 Save Changes", type="primary")

                        if save_changes:
                            update_payload = {
                                "name": e_name,
                                "company": e_company,
                                "email": e_email,
                                "phone": e_phone,
                                "industry": e_industry,
                                "priority": e_priority,
                                "status": e_status,
                            }
                            try:
                                res = requests.put(f"{API_URL}/leads/{lead_db_id}", json=update_payload, timeout=5)
                                if res.status_code == 200:
                                    st.success("Lead updated successfully!")
                                    st.session_state["force_refresh_leads"] = True
                                    st.rerun()
                                else:
                                    st.error(f"Update failed: {res.text}")
                            except Exception as ex:
                                st.error(f"Error connecting to backend: {ex}")

            with action_col2:
                st.write("")
                st.write("")
                if st.button("🗑️ Delete Lead", type="secondary", use_container_width=True):
                    try:
                        res = requests.delete(f"{API_URL}/leads/{lead_db_id}", timeout=5)
                        if res.status_code == 200:
                            st.success("Lead deleted successfully!")
                            st.session_state["force_refresh_leads"] = True
                            st.rerun()
                        else:
                            st.error(f"Delete failed: {res.text}")
                    except Exception as ex:
                        st.error(f"Error connecting to backend: {ex}")

            # -------------------------------------------------------------
            # 4. EXPORT BRIEF (PDF)
            # -------------------------------------------------------------
            st.markdown("---")
            st.subheader("📄 Export Brief")
            pdf_bytes = generate_pdf(selected_lead)
            st.download_button(
                label="📥 Download PDF Brief",
                data=pdf_bytes,
                file_name=f"Lead_Brief_{selected_lead.get('name', 'Lead')}.pdf",
                mime="application/pdf",
            )


if __name__ == "__main__":
    show()