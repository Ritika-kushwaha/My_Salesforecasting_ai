import io
import os
import pandas as pd
import requests
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")


def apply_app_theme():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        .saas-kpi-card {
            background: rgba(15, 23, 42, 0.75);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 18px;
            padding: 22px 20px;
            backdrop-filter: blur(16px);
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.4);
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        .saas-kpi-card:hover {
            transform: translateY(-3px);
            border-color: rgba(99, 102, 241, 0.4);
            box-shadow: 0 15px 35px -8px rgba(99, 102, 241, 0.25);
        }
        .saas-kpi-title {
            font-size: 0.78rem;
            font-weight: 700;
            color: #94A3B8;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            margin-bottom: 8px;
        }
        .saas-kpi-val {
            font-size: 2.1rem;
            font-weight: 800;
            color: #FFFFFF;
            letter-spacing: -0.03em;
            line-height: 1.1;
        }
        .saas-badge-green {
            background: rgba(16, 185, 129, 0.15);
            color: #10B981;
            border: 1px solid rgba(16, 185, 129, 0.3);
            padding: 2px 8px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 700;
        }
        .saas-badge-purple {
            background: rgba(168, 85, 247, 0.15);
            color: #C084FC;
            border: 1px solid rgba(168, 85, 247, 0.3);
            padding: 2px 8px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 700;
        }

        .panel-box {
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 18px;
            padding: 22px;
            backdrop-filter: blur(14px);
        }

        .chip {
            display: inline-flex;
            align-items: center;
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 0.76rem;
            font-weight: 700;
        }
        .chip-qualified { background: rgba(16, 185, 129, 0.15); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.3); }
        .chip-proposal { background: rgba(168, 85, 247, 0.15); color: #C084FC; border: 1px solid rgba(168, 85, 247, 0.3); }
        .chip-contacted { background: rgba(59, 130, 246, 0.15); color: #60A5FA; border: 1px solid rgba(59, 130, 246, 0.3); }
        .chip-new { background: rgba(99, 102, 241, 0.15); color: #818CF8; border: 1px solid rgba(99, 102, 241, 0.3); }
        .chip-lost { background: rgba(239, 68, 68, 0.15); color: #EF4444; border: 1px solid rgba(239, 68, 68, 0.3); }

        .stButton>button {
            border-radius: 12px;
            font-weight: 700;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def sanitize_status_str(val) -> str:
    if not val or str(val).strip() in ["", "1", "0", "None", "null"]:
        return "New"
    val_clean = str(val).strip()
    mapping = {
        "new": "New",
        "contacted": "Contacted",
        "qualified": "Qualified",
        "proposal sent": "Proposal Sent",
        "proposal": "Proposal Sent",
        "closed won": "Closed Won",
        "won": "Closed Won",
        "closed lost": "Closed Lost",
        "lost": "Closed Lost",
    }
    return mapping.get(val_clean.lower(), val_clean[:50])


def get_current_user_id():
    user = st.session_state.get("user")
    if isinstance(user, dict) and user.get("id"):
        return user["id"]
    return st.session_state.get("user_id", 1)


def generate_pdf(lead):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(60, 750, "SalesGenie Lead Executive Brief")
    c.setStrokeColorRGB(0.39, 0.40, 0.95)
    c.setLineWidth(2)
    c.line(60, 740, 550, 740)

    rev_val = lead.get("revenue", "0")
    try:
        rev_str = f"${float(rev_val):,.2f}"
    except Exception:
        rev_str = f"${rev_val}"

    fields = [
        ("Contact Name:", lead.get("name", "N/A")),
        ("Company Name:", lead.get("company", "N/A")),
        ("Email Address:", lead.get("email", "N/A")),
        ("Phone Number:", lead.get("phone", "N/A")),
        ("Industry Focus:", lead.get("industry", "N/A")),
        ("Company Size:", lead.get("company_size", "N/A")),
        ("Est. Revenue:", rev_str),
        ("Priority Level:", lead.get("priority", "Medium")),
        ("Pipeline Status:", sanitize_status_str(lead.get("status", "New"))),
    ]

    y = 700
    for label, val in fields:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(60, y, label)
        c.setFont("Helvetica", 12)
        c.drawString(180, y, str(val))
        y -= 25

    c.setFont("Helvetica-Oblique", 9)
    c.drawString(60, 440, "Generated automatically via SalesGenie AI Platform.")
    c.save()
    buffer.seek(0)
    return buffer


def show():
    apply_app_theme()

    user_id = get_current_user_id()

    st.markdown(
        """
        <div style="margin-bottom: 22px;">
            <div style="display: inline-flex; align-items: center; gap: 8px; background: rgba(99, 102, 241, 0.12); border: 1px solid rgba(99, 102, 241, 0.25); border-radius: 9999px; padding: 4px 12px; color: #818CF8; font-size: 0.78rem; font-weight: 700; margin-bottom: 8px;">
                👥 PIPELINE MANAGER
            </div>
            <h1 style="font-size: 2.1rem; font-weight: 800; margin: 0; letter-spacing: -0.03em;">Lead Pipeline & Account Directory</h1>
            <p style="color: #94A3B8; font-size: 0.92rem; margin-top: 4px;">Advance stages, edit every parameter, bulk import prospects, and export executive briefs.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. Fetch leads (loaded chronologically: newest at the bottom)
    leads_data = []
    try:
        res = requests.get(f"{API_URL}/leads", params={"user_id": user_id}, timeout=8)
        if res.status_code == 200:
            raw_leads = res.json()
            for item in raw_leads:
                item["status"] = sanitize_status_str(item.get("status"))
            leads_data = raw_leads
            st.session_state["leads"] = leads_data
    except Exception:
        leads_data = st.session_state.get("leads", [])

    # 2. Metric KPI Cards Row
    t_count = len(leads_data)
    h_count = sum(1 for l in leads_data if str(l.get("priority", "")).lower() == "high")
    q_count = sum(1 for l in leads_data if str(l.get("status", "")).lower() in ["qualified", "proposal sent", "closed won"])
    n_count = sum(1 for l in leads_data if str(l.get("status", "")).lower() == "new")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="saas-kpi-card"><div class="saas-kpi-title">TOTAL PIPELINE</div><div class="saas-kpi-val">{t_count}</div><div style="margin-top: 8px;"><span class="saas-badge-purple">Active Accounts</span></div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="saas-kpi-card"><div class="saas-kpi-title">HIGH PRIORITY</div><div class="saas-kpi-val" style="color: #EF4444;">{h_count}</div><div style="margin-top: 8px;"><span class="saas-badge-green">Urgent Action</span></div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="saas-kpi-card"><div class="saas-kpi-title">QUALIFIED DEALS</div><div class="saas-kpi-val" style="color: #10B981;">{q_count}</div><div style="margin-top: 8px;"><span class="saas-badge-green">Proposal Ready</span></div></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="saas-kpi-card"><div class="saas-kpi-title">NEW UNCONTACTED</div><div class="saas-kpi-val" style="color: #F59E0B;">{n_count}</div><div style="margin-top: 8px;"><span class="saas-badge-purple">Needs Outreach</span></div></div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)

    # 3. Main Workspace Tabs
    tab_pipeline, tab_add, tab_bulk = st.tabs([
        "📋 Pipeline Table & Actions",
        "➕ Add Single Lead",
        "📁 Bulk CSV Import"
    ])

    with tab_pipeline:
        if not leads_data:
            st.info("💡 No leads registered yet. Use the tabs above to add your first lead!")
        else:
            fc1, fc2, fc3 = st.columns([2, 1, 1])
            with fc1:
                search_q = st.text_input("🔍 Live Search Pipeline", placeholder="Filter by name, company, email...").strip().lower()
            with fc2:
                filter_prio = st.selectbox("Priority Filter", ["All Priorities", "High", "Medium", "Low"])
            with fc3:
                filter_stat = st.selectbox("Stage Filter", ["All Stages", "New", "Contacted", "Qualified", "Proposal Sent", "Closed Won", "Closed Lost"])

            filtered = leads_data
            if search_q:
                filtered = [
                    l for l in filtered
                    if search_q in l.get("name", "").lower()
                    or search_q in l.get("company", "").lower()
                    or search_q in l.get("email", "").lower()
                ]
            if filter_prio != "All Priorities":
                filtered = [l for l in filtered if l.get("priority") == filter_prio]
            if filter_stat != "All Stages":
                filtered = [l for l in filtered if l.get("status") == filter_stat]

            if filtered:
                df = pd.DataFrame(filtered)
                if "revenue" in df.columns:
                    df["revenue"] = df["revenue"].apply(
                        lambda x: f"${float(x):,.2f}" if str(x).replace(".", "", 1).isdigit() else str(x)
                    )

                df["#"] = range(1, len(df) + 1)
                display_cols = ["#"] + [c for c in df.columns if c not in ["#", "id", "user_id"]]
                st.dataframe(df[display_cols], use_container_width=True, hide_index=True)

            # -------------------------------------------------------------
            # ACTION DOCK & COMPREHENSIVE EDIT DRAWER
            # -------------------------------------------------------------
            st.markdown("### ⚡ Lead Action Dock & Parameter Editor")
            lead_map = {f"#{i} - {l.get('name')} ({l.get('company')})": l for i, l in enumerate(leads_data, start=1)}
            selected_key = st.selectbox("Select Target Account:", list(lead_map.keys()))
            target_lead = lead_map[selected_key]
            lead_db_id = target_lead.get("id")

            current_status = sanitize_status_str(target_lead.get("status"))

            chip_class = "chip-qualified" if current_status in ["Qualified", "Closed Won"] else (
                "chip-proposal" if current_status == "Proposal Sent" else (
                    "chip-contacted" if current_status == "Contacted" else "chip-new"
                )
            )

            st.markdown(f"""
            <div class="panel-box" style="margin: 12px 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h3 style="margin: 0; font-weight: 800; font-size: 1.15rem;">{target_lead.get('name')} • <span style="color: #94A3B8;">{target_lead.get('company')}</span></h3>
                        <p style="margin: 3px 0 0 0; font-size: 0.88rem; color: #94A3B8;">{target_lead.get('email')} • {target_lead.get('phone', 'N/A')} • {target_lead.get('industry', 'General')} • Scale: {target_lead.get('company_size', '1-10')} • Revenue: ${target_lead.get('revenue', '0')}</p>
                    </div>
                    <div>
                        <span class="chip {chip_class}">{current_status}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.write("**1-Click Pipeline Advance:**")
            q_cols = st.columns(6)
            stages = ["New", "Contacted", "Qualified", "Proposal Sent", "Closed Won", "Closed Lost"]
            for idx, s_name in enumerate(stages):
                with q_cols[idx]:
                    if st.button(f"➔ {s_name}", key=f"lead_dock_{s_name}_{lead_db_id}", use_container_width=True):
                        try:
                            requests.put(f"{API_URL}/leads/{lead_db_id}", json={"status": s_name}, timeout=6)
                            st.toast(f"Status updated to '{s_name}'!", icon="✅")
                            st.rerun()
                        except Exception as ex:
                            st.error(f"Error: {ex}")

            sub1, sub2 = st.columns([1.7, 1], gap="large")
            with sub1:
                with st.expander("✏️ Edit Complete Lead Details", expanded=True):
                    with st.form(f"edit_lead_{lead_db_id}"):
                        e1, e2 = st.columns(2)
                        with e1:
                            u_name = st.text_input("Contact Name *", value=target_lead.get("name", ""))
                            u_comp = st.text_input("Company Name *", value=target_lead.get("company", ""))
                            u_email = st.text_input("Work Email *", value=target_lead.get("email", ""))
                            u_phone = st.text_input("Phone Number", value=target_lead.get("phone", ""))
                        with e2:
                            # Industry Selector
                            ind_options = ["Technology", "Healthcare", "Finance", "Retail", "Manufacturing", "General", "Other"]
                            curr_ind = target_lead.get("industry", "Technology")
                            u_ind = st.selectbox(
                                "Industry Focus",
                                ind_options,
                                index=ind_options.index(curr_ind) if curr_ind in ind_options else 0,
                            )

                            # Company Size Selector
                            size_options = ["1-10", "11-50", "51-200", "201-500", "500+"]
                            curr_size = target_lead.get("company_size", "1-10")
                            u_size = st.selectbox(
                                "Company Size",
                                size_options,
                                index=size_options.index(curr_size) if curr_size in size_options else 0,
                            )

                            # Annual Revenue
                            try:
                                raw_rev_float = float(str(target_lead.get("revenue", "0")).replace("$", "").replace(",", "").strip() or 0.0)
                            except Exception:
                                raw_rev_float = 0.0
                            u_rev = st.number_input("Annual Revenue ($)", min_value=0.0, value=raw_rev_float, step=25000.0)

                            # Priority Level
                            p_opts = ["High", "Medium", "Low"]
                            curr_p = target_lead.get("priority", "Medium")
                            u_prio = st.selectbox("Priority Level", p_opts, index=p_opts.index(curr_p) if curr_p in p_opts else 1)

                        # Pipeline Stage
                        stage_options = ["New", "Contacted", "Qualified", "Proposal Sent", "Closed Won", "Closed Lost"]
                        curr_st = sanitize_status_str(target_lead.get("status", "New"))
                        u_status = st.selectbox(
                            "Pipeline Stage",
                            stage_options,
                            index=stage_options.index(curr_st) if curr_st in stage_options else 0,
                        )

                        if st.form_submit_button("💾 Save All Lead Updates", type="primary", use_container_width=True):
                            payload = {
                                "name": u_name,
                                "company": u_comp,
                                "email": u_email,
                                "phone": u_phone,
                                "industry": u_ind,
                                "company_size": u_size,
                                "revenue": str(u_rev),
                                "priority": u_prio,
                                "status": u_status,
                            }
                            try:
                                requests.put(f"{API_URL}/leads/{lead_db_id}", json=payload, timeout=6)
                                st.toast("All lead details updated successfully!", icon="🎉")
                                st.rerun()
                            except Exception as ex:
                                st.error(f"Failed to update lead: {ex}")

            with sub2:
                st.markdown("#### 📄 Export & Actions")
                st.download_button(
                    label="📥 Download Executive PDF Brief",
                    data=generate_pdf(target_lead),
                    file_name=f"Brief_{target_lead.get('name')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                if st.button("🗑️ Delete Lead Record", key=f"d_btn_{lead_db_id}", type="secondary", use_container_width=True):
                    try:
                        requests.delete(f"{API_URL}/leads/{lead_db_id}", timeout=6)
                        st.toast("Lead deleted.", icon="🗑️")
                        st.rerun()
                    except Exception as ex:
                        st.error(f"Error: {ex}")

    with tab_add:
        st.markdown("### ➕ Create New Lead Record")
        with st.form("add_lead_form", clear_on_submit=True):
            a1, a2 = st.columns(2)
            with a1:
                n_name = st.text_input("Full Contact Name *", placeholder="e.g. Sarah Connor")
                n_company = st.text_input("Company Name *", placeholder="e.g. Cyberdyne Systems")
                n_email = st.text_input("Work Email *", placeholder="sarah@cyberdyne.com")
                n_phone = st.text_input("Phone Number", placeholder="+1 (555) 234-5678")
            with a2:
                n_ind = st.selectbox("Industry Focus", ["Technology", "Healthcare", "Finance", "Retail", "Manufacturing", "General"])
                n_size = st.selectbox("Company Size", ["1-10", "11-50", "51-200", "201-500", "500+"])
                n_rev = st.number_input("Annual Revenue ($)", min_value=0.0, step=25000.0)
                n_prio = st.selectbox("Priority Level", ["High", "Medium", "Low"], index=1)

            if st.form_submit_button("✨ Save Lead to Pipeline", type="primary", use_container_width=True):
                if not n_name or not n_company or not n_email:
                    st.error("Name, Company, and Email are required.")
                else:
                    payload = {
                        "name": n_name,
                        "company": n_company,
                        "email": n_email,
                        "phone": n_phone,
                        "industry": n_ind,
                        "company_size": n_size,
                        "revenue": str(n_rev),
                        "priority": n_prio,
                        "status": "New"
                    }
                    requests.post(f"{API_URL}/leads", params={"user_id": user_id}, json=payload, timeout=6)
                    st.toast(f"Lead '{n_name}' added at the end of pipeline!", icon="🚀")
                    st.rerun()

    with tab_bulk:
        st.markdown("### 📁 Import Prospects via CSV")
        sample_csv = "name,company,email,phone,industry,company_size,revenue,priority,status\nJane Doe,Acme Cloud,jane@acme.com,+1555123456,Technology,51-200,5000000,High,New\nJohn Smith,Nexus Health,john@nexus.com,+1555987654,Healthcare,11-50,1200000,Medium,New"
        st.download_button("📄 Download Sample CSV Template", data=sample_csv, file_name="sample_leads.csv", mime="text/csv")
        st.markdown("---")

        up_file = st.file_uploader("Upload CSV Spreadsheet", type=["csv"])
        if up_file is not None:
            try:
                import_df = pd.read_csv(up_file).fillna("")
                if "status" in import_df.columns:
                    import_df["status"] = import_df["status"].apply(sanitize_status_str)
                else:
                    import_df["status"] = "New"

                st.write("📋 **Preview of data to import:**")
                st.dataframe(import_df.head(5), use_container_width=True)

                if st.button("🚀 Confirm & Import All Records", type="primary", use_container_width=True):
                    res = requests.post(
                        f"{API_URL}/leads/bulk",
                        params={"user_id": user_id},
                        json=import_df.to_dict(orient="records"),
                        timeout=15
                    )
                    if res.status_code == 200:
                        st.toast("Bulk import completed!", icon="🎉")
                        st.rerun()
            except Exception as e:
                st.error(f"Error reading file: {e}")


if __name__ == "__main__":
    show()