import os
import pandas as pd
import requests
import streamlit as st

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")


def show():
    st.markdown("## 👥 Lead Management")
    st.caption("View, edit, delete, search, manually create, and bulk import B2B leads.")

    user_id = st.session_state.get("user", {}).get("id", 1)

    tab1, tab2, tab3 = st.tabs(
        ["📋 View & Manage Leads", "➕ Add Single Lead", "📁 Bulk CSV Upload"]
    )

    # -------------------------------------------------------------------
    # TAB 1: VIEW, SEARCH, EDIT & DELETE LEADS
    # -------------------------------------------------------------------
    with tab1:
        st.markdown("### All Registered Leads")

        try:
            res = requests.get(f"{API_URL}/leads", timeout=10)
            if res.status_code == 200:
                leads_data = res.json()
                if leads_data:
                    df = pd.DataFrame(leads_data)

                    # ---------------------------------------------------
                    # 🔍 SEARCH & FILTER BAR
                    # ---------------------------------------------------
                    st.markdown("#### 🔍 Search & Filter Prospects")
                    s_col1, s_col2, s_col3 = st.columns([2, 1, 1])

                    with s_col1:
                        search_term = st.text_input(
                            "Search",
                            placeholder="🔎 Type name, company, or email...",
                            key="lead_search_input",
                        ).strip().lower()

                    with s_col2:
                        industry_filter = st.selectbox(
                            "Filter by Industry",
                            options=["All"] + sorted(list(df["industry"].unique())) if "industry" in df.columns else ["All"],
                            key="lead_industry_filter",
                        )

                    with s_col3:
                        priority_filter = st.selectbox(
                            "Filter by Priority",
                            options=["All", "High", "Medium", "Low"],
                            key="lead_priority_filter",
                        )

                    # Apply Filters dynamically
                    df_filtered = df.copy()

                    if search_term:
                        df_filtered = df_filtered[
                            df_filtered["name"].str.lower().str.contains(search_term, na=False)
                            | df_filtered["company"].str.lower().str.contains(search_term, na=False)
                            | df_filtered["email"].str.lower().str.contains(search_term, na=False)
                        ]

                    if industry_filter != "All":
                        df_filtered = df_filtered[df_filtered["industry"] == industry_filter]

                    if priority_filter != "All":
                        df_filtered = df_filtered[df_filtered["priority"] == priority_filter]

                    # Column mapping for presentation
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

                    available_cols = [c for c in display_columns.keys() if c in df_filtered.columns]
                    df_display = df_filtered[available_cols].rename(columns=display_columns)

                    st.markdown(f"**Showing {len(df_display)} of {len(df)} total leads:**")
                    st.dataframe(df_display, use_container_width=True, hide_index=True)

                    st.divider()

                    # Mapping options cleanly for Edit and Delete dropdowns
                    lead_options = {
                        f"ID #{l['id']}: {l.get('name', 'N/A')} ({l.get('company', 'N/A')})": l
                        for l in leads_data
                    }

                    col_edit_sec, col_del_sec = st.columns(2, gap="large")

                    # ---------------------------------------------------
                    # ✏️ EDIT LEAD SECTION
                    # ---------------------------------------------------
                    with col_edit_sec:
                        st.markdown("### ✏️ Edit Lead Information")
                        selected_edit_str = st.selectbox(
                            "Select Lead to Edit",
                            options=list(lead_options.keys()),
                            key="edit_lead_select",
                        )
                        target_lead = lead_options[selected_edit_str]
                        lead_id_to_edit = int(target_lead["id"])

                        with st.form("edit_lead_form", clear_on_submit=False):
                            edit_name = st.text_input("Contact Name", value=target_lead.get("name", ""))
                            edit_company = st.text_input("Company Name", value=target_lead.get("company", ""))
                            edit_email = st.text_input("Email Address", value=target_lead.get("email", ""))
                            edit_phone = st.text_input("Phone Number", value=target_lead.get("phone", ""))

                            ind_list = ["Technology", "Healthcare", "Finance", "Retail", "Manufacturing", "General"]
                            current_ind = target_lead.get("industry", "General")
                            ind_idx = ind_list.index(current_ind) if current_ind in ind_list else 0
                            edit_industry = st.selectbox("Industry", ind_list, index=ind_idx)

                            prio_list = ["High", "Medium", "Low"]
                            current_prio = target_lead.get("priority", "Medium")
                            prio_idx = prio_list.index(current_prio) if current_prio in prio_list else 1
                            edit_priority = st.selectbox("Priority", prio_list, index=prio_idx)

                            status_list = ["New", "Contacted", "Qualified", "Proposal Sent", "Closed Won", "Closed Lost"]
                            current_status = target_lead.get("status", "New")
                            status_idx = status_list.index(current_status) if current_status in status_list else 0
                            edit_status = st.selectbox("Status", status_list, index=status_idx)

                            submit_edit = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)

                            if submit_edit:
                                update_payload = {
                                    "name": edit_name,
                                    "company": edit_company,
                                    "email": edit_email,
                                    "phone": edit_phone,
                                    "industry": edit_industry,
                                    "priority": edit_priority,
                                    "status": edit_status,
                                }
                                try:
                                    put_res = requests.put(
                                        f"{API_URL}/leads/{lead_id_to_edit}",
                                        json=update_payload,
                                    )
                                    if put_res.status_code == 200:
                                        st.success("✅ Lead updated successfully!")
                                        st.rerun()
                                    else:
                                        err = put_res.json().get("detail", put_res.text)
                                        st.error(f"Failed to update lead: {err}")
                                except Exception as e:
                                    st.error(f"Error connecting to backend: {e}")

                    # ---------------------------------------------------
                    # 🗑️ DELETE LEAD SECTION
                    # ---------------------------------------------------
                    with col_del_sec:
                        st.markdown("### 🗑️ Delete Lead")
                        selected_del_str = st.selectbox(
                            "Select Lead to Remove",
                            options=list(lead_options.keys()),
                            key="delete_lead_select",
                        )
                        del_target_id = int(lead_options[selected_del_str]["id"])

                        st.warning(f"⚠️ Confirm deletion of **Lead ID #{del_target_id}**.")
                        if st.button("❌ Confirm & Delete Lead", type="primary", use_container_width=True):
                            try:
                                del_res = requests.delete(f"{API_URL}/leads/{del_target_id}")
                                if del_res.status_code == 200:
                                    st.success(f"✅ Lead #{del_target_id} deleted successfully!")
                                    st.rerun()
                                else:
                                    err = del_res.json().get("detail", del_res.text)
                                    st.error(f"Failed to delete lead: {err}")
                            except Exception as e:
                                st.error(f"Error connecting to server: {e}")

                else:
                    st.info("No leads found in database. Add new leads below or via CSV.")
            else:
                st.error("Failed to load leads from backend.")
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
                name = st.text_input("Contact Name *")
                company = st.text_input("Company Name *")
                email = st.text_input("Email Address *")
                phone = st.text_input("Phone Number")
            with col2:
                industry = st.selectbox("Industry", ["Technology", "Healthcare", "Finance", "Retail", "Manufacturing", "Other"])
                priority = st.selectbox("Priority", ["High", "Medium", "Low"])
                company_size = st.selectbox("Company Size", ["1-10", "11-50", "51-200", "201-500", "500+"])
                revenue = st.selectbox("Revenue", ["<$1M", "$1M-$10M", "$10M-$50M", "$50M+"])

            if st.form_submit_button("🚀 Save Lead", type="primary", use_container_width=True):
                if not name or not company or not email:
                    st.warning("⚠️ Contact Name, Company Name, and Email are required.")
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
        uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
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