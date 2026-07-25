import os
import pandas as pd
import requests
import streamlit as st

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")


def show():
    st.markdown("## 👥 Lead Management")
    st.caption("Manage, view, delete, and bulk import B2B leads into your sales pipeline.")

    user_id = st.session_state.get("user", {}).get("id", 1)

    tab1, tab2, tab3 = st.tabs(
        ["📋 View & Manage Leads", "➕ Add Single Lead", "📁 Bulk CSV Upload"]
    )

    # -------------------------------------------------------------------
    # TAB 1: VIEW ALL LEADS
    # -------------------------------------------------------------------
    with tab1:
        st.markdown("### All Registered Leads")
        
        try:
            res = requests.get(f"{API_URL}/leads", timeout=10)
            if res.status_code == 200:
                leads_data = res.json()
                if leads_data:
                    df = pd.DataFrame(leads_data)

                    display_columns = {
                        "id": "Lead ID",
                        "name": "Contact Name",
                        "company": "Company Name",
                        "email": "Email Address",
                        "phone": "Phone Number",
                        "industry": "Industry",
                        "priority": "Priority",
                        "status": "Status",
                    }

                    available_cols = [c for c in display_columns.keys() if c in df.columns]
                    df_display = df[available_cols].rename(columns=display_columns)

                    st.dataframe(df_display, use_container_width=True, hide_index=True)

                    st.divider()

                    # DELETE LEAD SECTION
                    st.markdown("### 🗑️ Delete a Lead")
                    col_del1, col_del2 = st.columns([3, 1])

                    with col_del1:
                        lead_options = {
                            f"ID {l['id']}: {l.get('name', 'N/A')} ({l.get('company', 'N/A')})": l['id']
                            for l in leads_data
                        }
                        selected_lead_str = st.selectbox(
                            "Select Lead to Delete",
                            options=list(lead_options.keys()),
                            key="delete_lead_select"
                        )

                    with col_del2:
                        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                        if st.button("❌ Delete Lead", type="primary", use_container_width=True):
                            lead_id_to_delete = lead_options[selected_lead_str]
                            try:
                                del_res = requests.delete(f"{API_URL}/leads/{lead_id_to_delete}")
                                if del_res.status_code == 200:
                                    st.success("✅ Lead deleted successfully!")
                                    st.rerun()
                                else:
                                    st.error(f"Failed to delete lead: {del_res.text}")
                            except Exception as e:
                                st.error(f"Error connecting to server: {e}")

                else:
                    st.info("No leads found in database.")
            else:
                st.error("Failed to load leads from backend.")
        except Exception as e:
            st.error(f"Connection error: {e}")

    # -------------------------------------------------------------------
    # TAB 2 & 3: ADD SINGLE LEAD & CSV UPLOAD
    # -------------------------------------------------------------------
    with tab2:
        st.markdown("### ➕ Add New Lead Manually")
        with st.form("add_lead_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Contact Name *")
                company = st.text_input("Company Name *")
                email = st.text_input("Email Address *")
                phone = st.text_input("Phone Number")
            with col2:
                industry = st.selectbox("Industry", ["Technology", "Healthcare", "Finance", "Retail", "Other"])
                priority = st.selectbox("Priority", ["High", "Medium", "Low"])
                company_size = st.selectbox("Company Size", ["1-10", "11-50", "51-200", "201-500", "500+"])
                revenue = st.selectbox("Revenue", ["<$1M", "$1M-$10M", "$10M-$50M", "$50M+"])

            if st.form_submit_button("🚀 Save Lead", type="primary", use_container_width=True):
                if not name or not company or not email:
                    st.warning("⚠️ Contact Name, Company Name, and Email are required.")
                else:
                    payload = {
                        "name": name, "company": company, "email": email, "phone": phone,
                        "industry": industry, "priority": priority, "company_size": company_size,
                        "revenue": revenue, "status": "New"
                    }
                    requests.post(f"{API_URL}/leads", params={"user_id": user_id}, json=payload)
                    st.success(f"Lead '{name}' added!")
                    st.rerun()

    with tab3:
        st.markdown("### 📁 Bulk CSV Upload")
        uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
        if uploaded_file:
            csv_df = pd.read_csv(uploaded_file).fillna("")
            st.dataframe(csv_df.head(5), use_container_width=True)
            if st.button("📤 Import All Leads", type="primary"):
                requests.post(f"{API_URL}/leads/bulk", params={"user_id": user_id}, json=csv_df.to_dict(orient="records"))
                st.success("Leads imported!")
                st.rerun()


if __name__ == "__main__":
    show()