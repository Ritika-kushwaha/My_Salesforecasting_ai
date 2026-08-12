import os
import io
import pandas as pd
import requests
import streamlit as st

# Import PDF generator helper
try:
    from utils.pdf_generator import generate_lead_pdf_brief
except ImportError:
    # Fallback if utils folder is not used
    from pdf_generator import generate_lead_pdf_brief

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")


def show():
    st.markdown("## 👥 Lead Management")
    st.caption("View, edit, delete, search, manually create, export PDF briefs, and bulk import B2B leads.")

    # Retrieve current logged-in user ID
    user_data = st.session_state.get("user") or {}
    user_id = user_data.get("id", 1) if isinstance(user_data, dict) else 1

    tab1, tab2, tab3 = st.tabs(
        ["📋 View & Manage Leads", "➕ Add Single Lead", "📁 Bulk CSV Upload"]
    )

    # -------------------------------------------------------------------
    # TAB 1: VIEW, SEARCH, EDIT, DELETE & EXPORT PDF LEADS
    # -------------------------------------------------------------------
    with tab1:
        st.markdown("### All Registered Leads")

        try:
            res = requests.get(f"{API_URL}/leads", params={"user_id": user_id}, timeout=10)
            if res.status_code == 200:
                leads_data = res.json()
                if leads_data:
                    df = pd.DataFrame(leads_data)

                    # 🔍 SEARCH & FILTER BAR
                    st.markdown("#### 🔍 Search & Filter Prospects")
                    s_col1, s_col2, s_col3 = st.columns([2, 1, 1])
                    with s_col1:
                        search_term = st.text_input(
                            "Search by Name, Company, or Email:",
                            placeholder="Type keyword...",
                        ).lower()
                    with s_col2:
                        industry_filter = st.selectbox(
                            "Industry:",
                            options=["All"] + sorted(list(df["industry"].dropna().unique())),
                        )
                    with s_col3:
                        priority_filter = st.selectbox(
                            "Priority:",
                            options=["All", "High", "Medium", "Low"],
                        )

                    # Apply Filters
                    filtered_df = df.copy()
                    if search_term:
                        filtered_df = filtered_df[
                            filtered_df["name"].str.lower().str.contains(search_term, na=False)
                            | filtered_df["company"].str.lower().str.contains(search_term, na=False)
                            | filtered_df["email"].str.lower().str.contains(search_term, na=False)
                        ]
                    if industry_filter != "All":
                        filtered_df = filtered_df[filtered_df["industry"] == industry_filter]
                    if priority_filter != "All":
                        filtered_df = filtered_df[filtered_df["priority"] == priority_filter]

                    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

                    # ⚙️ EDIT / DELETE / EXPORT PDF SECTION
                    st.markdown("---")
                    st.markdown("#### ⚙️ Lead Actions & Executive PDF Brief")
                    
                    lead_options = {
                        f"ID #{l['id']} - {l['name']} ({l['company']})": l for l in leads_data
                    }
                    selected_label = st.selectbox("Select Lead to Manage / Export:", list(lead_options.keys()))
                    selected_lead = lead_options[selected_label]

                    e_col1, e_col2 = st.columns(2)
                    
                    # Edit Lead Details
                    with e_col1:
                        with st.form("edit_lead_form"):
                            st.write("##### ✏️ Update Details")
                            edit_name = st.text_input("Name", value=selected_lead.get("name", ""))
                            edit_company = st.text_input("Company", value=selected_lead.get("company", ""))
                            edit_email = st.text_input("Email", value=selected_lead.get("email", ""))
                            edit_phone = st.text_input("Phone", value=selected_lead.get("phone", ""))
                            edit_priority = st.selectbox("Priority", ["High", "Medium", "Low"], index=["High", "Medium", "Low"].index(selected_lead.get("priority", "Medium")))
                            edit_status = st.selectbox("Status", ["New", "Contacted", "Qualified", "Proposal Sent", "Closed Won", "Closed Lost"], index=0)

                            if st.form_submit_button("💾 Save Updates"):
                                update_payload = {
                                    "name": edit_name,
                                    "company": edit_company,
                                    "email": edit_email,
                                    "phone": edit_phone,
                                    "priority": edit_priority,
                                    "status": edit_status,
                                }
                                requests.put(f"{API_URL}/leads/{selected_lead['id']}", json=update_payload)
                                st.success("Lead updated successfully!")
                                st.rerun()

                    # PDF Export & Delete Action
                    with e_col2:
                        st.write("##### 📄 Export Brief")
                        st.caption("Generate a single-page Executive PDF Brief for client meetings.")
                        
                        try:
                            pdf_bytes = generate_lead_pdf_brief(selected_lead)
                            file_name_clean = f"Brief_{selected_lead.get('company', 'Lead')}.pdf".replace(" ", "_")
                            
                            st.download_button(
                                label="📥 Download Executive PDF Brief",
                                data=pdf_bytes,
                                file_name=file_name_clean,
                                mime="application/pdf",
                                use_container_width=True
                            )
                        except Exception as pdf_err:
                            st.error(f"Error generating PDF: {pdf_err}")

                        st.markdown("---")
                        st.write("##### 🗑️ Delete Record")
                        if st.button("Delete Lead Record", type="primary", use_container_width=True):
                            requests.delete(f"{API_URL}/leads/{selected_lead['id']}")
                            st.success("Lead deleted successfully!")
                            st.rerun()

                else:
                    st.info("No leads registered yet. Add single leads or upload a CSV file.")
            else:
                st.error("Failed to load leads from backend server.")
        except Exception as e:
            st.error(f"Error connecting to backend API: {e}")

    # -------------------------------------------------------------------
    # TAB 2: ADD SINGLE LEAD
    # -------------------------------------------------------------------
    with tab2:
        st.markdown("### ➕ Register New Single Lead")
        with st.form("add_single_lead_form"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Full Name *", placeholder="e.g. John Doe")
                company = st.text_input("Company Name *", placeholder="e.g. Acme Corp")
                email = st.text_input("Email Address *", placeholder="e.g. john@acme.com")
                phone = st.text_input("Phone Number", placeholder="e.g. +1 555-0192")
            with c2:
                industry = st.text_input("Industry", placeholder="e.g. Technology")
                priority = st.selectbox("Priority Level", ["High", "Medium", "Low"], index=1)
                company_size = st.selectbox("Company Size", ["1-10", "11-50", "51-200", "201-500", "500+"])
                revenue = st.text_input("Estimated Revenue", placeholder="e.g. $1M-$5M")

            if st.form_submit_button("🚀 Save Lead"):
                if not name or not company or not email:
                    st.error("Name, Company, and Email are required.")
                else:
                    payload = {
                        "name": name,
                        "company": company,
                        "email": email,
                        "phone": phone,
                        "industry": industry,
                        "priority": priority,
                        "company_size": company_size,
                        "revenue": revenue,
                        "status": "New",
                    }
                    requests.post(f"{API_URL}/leads", params={"user_id": user_id}, json=payload)
                    st.success(f"Lead '{name}' added successfully!")
                    st.rerun()

    # -------------------------------------------------------------------
    # TAB 3: BULK CSV UPLOAD
    # -------------------------------------------------------------------
    with tab3:
        st.markdown("### 📁 Bulk CSV Upload")
        uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])
        if uploaded_file:
            csv_df = pd.read_csv(uploaded_file).fillna("")
            st.dataframe(csv_df.head(5), use_container_width=True)
            if st.button("📤 Import All Leads", type="primary"):
                requests.post(
                    f"{API_URL}/leads/bulk",
                    params={"user_id": user_id},
                    json=csv_df.to_dict(orient="records"),
                )
                st.success("Leads imported successfully!")
                st.rerun()


if __name__ == "__main__":
    show()