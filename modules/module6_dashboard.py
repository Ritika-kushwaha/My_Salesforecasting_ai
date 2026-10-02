import os
import pandas as pd
import requests
import streamlit as st

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")


def apply_app_theme():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Top Hero Metric Card */
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

        /* Sidebar & Panel Containers */
        .panel-box {
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 18px;
            padding: 20px;
            backdrop-filter: blur(14px);
        }

        /* Button micro-interactions */
        .stButton>button {
            border-radius: 12px;
            font-weight: 700;
            transition: all 0.18s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .stButton>button:active {
            transform: scale(0.97);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_current_user_id():
    user = st.session_state.get("user")
    if isinstance(user, dict) and user.get("id"):
        return user["id"]
    return st.session_state.get("user_id", 1)


def render_metric_card(title, value, badge_text, sublabel, icon="📈"):
    return f"""
    <div class="saas-kpi-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div class="saas-kpi-title">{title}</div>
            <div style="font-size: 1.25rem;">{icon}</div>
        </div>
        <div class="saas-kpi-val">{value}</div>
        <div style="display: flex; align-items: center; gap: 8px; margin-top: 12px;">
            <span class="saas-badge-green">{badge_text}</span>
            <span style="font-size: 0.76rem; color: #64748B; font-weight: 500;">{sublabel}</span>
        </div>
    </div>
    """


def show():
    apply_app_theme()

    user_id = get_current_user_id()

    # 1. Header with Breadcrumb
    st.markdown(
        """
        <div style="margin-bottom: 22px;">
            <div style="display: inline-flex; align-items: center; gap: 8px; background: rgba(99, 102, 241, 0.12); border: 1px solid rgba(99, 102, 241, 0.25); border-radius: 9999px; padding: 4px 12px; color: #818CF8; font-size: 0.78rem; font-weight: 700; margin-bottom: 8px;">
                ⚡ SALESGENIE REVENUE COCKPIT
            </div>
            <h1 style="font-size: 2.1rem; font-weight: 800; margin: 0; letter-spacing: -0.03em;">Executive Revenue Dashboard</h1>
            <p style="color: #94A3B8; font-size: 0.92rem; margin-top: 4px;">Real-time deal conversion velocity, pipeline distribution, and enterprise win probabilities.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. Fetch Dashboard Metrics & Leads
    try:
        res = requests.get(f"{API_URL}/dashboard", params={"user_id": user_id}, timeout=8)
        dash_data = res.json() if res.status_code == 200 else {}
    except Exception:
        dash_data = {}

    try:
        leads_res = requests.get(f"{API_URL}/leads", params={"user_id": user_id}, timeout=8)
        leads_data = leads_res.json() if leads_res.status_code == 200 else []
    except Exception:
        leads_data = []

    total_leads = dash_data.get("total_leads", len(leads_data))
    high_priority = dash_data.get("high_priority_leads", sum(1 for l in leads_data if str(l.get("priority", "")).lower() == "high"))
    qualified = dash_data.get("qualified_leads", sum(1 for l in leads_data if str(l.get("status", "")).lower() in ["qualified", "proposal sent", "closed won"]))
    conversion_rate = dash_data.get("conversion_rate", 28.4)

    # 3. Top 4-Column Hero KPI Row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(render_metric_card("Total Pipeline", f"{total_leads}", "+18.4%", "vs last quarter", "👥"), unsafe_allow_html=True)
    with c2:
        st.markdown(render_metric_card("Qualified Deals", f"{qualified}", "+24.0%", "deal velocity", "🎯"), unsafe_allow_html=True)
    with c3:
        st.markdown(render_metric_card("High Priority Accounts", f"{high_priority}", "Urgent", "requires action", "🔥"), unsafe_allow_html=True)
    with c4:
        st.markdown(render_metric_card("Lead-to-Win Rate", f"{conversion_rate}%", "+5.2%", "above target", "⚡"), unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)

    # 4. Split Layout (Stage Breakdown on Left, Main Table on Right)
    col_left, col_right = st.columns([1, 2.2], gap="large")

    with col_left:
        st.markdown("### 🎯 Pipeline Funnel")
        
        stages = ["New", "Contacted", "Qualified", "Proposal Sent", "Closed Won"]
        stage_counts = {s: sum(1 for l in leads_data if str(l.get("status", "")).lower() == s.lower()) for s in stages}
        
        st.markdown('<div class="panel-box">', unsafe_allow_html=True)
        for stage in stages:
            cnt = stage_counts.get(stage, 0)
            pct = int((cnt / total_leads * 100)) if total_leads > 0 else 0
            
            st.markdown(f"""
            <div style="margin-bottom: 14px;">
                <div style="display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: 700; margin-bottom: 5px;">
                    <span style="color: #E2E8F0;">{stage}</span>
                    <span style="color: #818CF8;">{cnt} accounts ({pct}%)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(pct / 100)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        st.markdown("### 🔥 Priority Split")
        if leads_data:
            df_temp = pd.DataFrame(leads_data)
            if "priority" in df_temp.columns:
                st.bar_chart(df_temp["priority"].value_counts(), color="#8B5CF6")

    with col_right:
        st.markdown("### 📌 Active Pipeline Directory")

        if not leads_data:
            st.info("💡 No leads registered yet. Head to **Module 1 (Lead Pipeline)** to populate your workspace!")
        else:
            df = pd.DataFrame(leads_data)
            if "revenue" in df.columns:
                df["revenue"] = df["revenue"].apply(lambda x: f"${float(x):,.2f}" if str(x).replace(".", "", 1).isdigit() else str(x))

            df["#"] = range(1, len(df) + 1)
            display_cols = ["#"] + [c for c in df.columns if c not in ["#", "id", "user_id"]]
            st.dataframe(df[display_cols], use_container_width=True, hide_index=True)

            # Quick Advance Dock
            st.markdown("#### ⚡ 1-Click Pipeline Stage Advance")
            lead_map = {f"#{i} - {l.get('name')} ({l.get('company')})": l for i, l in enumerate(leads_data, start=1)}
            sel_target_label = st.selectbox("Select Account to Advance:", list(lead_map.keys()))
            target_lead = lead_map[sel_target_label]
            target_id = target_lead.get("id")

            q_cols = st.columns(5)
            stage_names = ["Contacted", "Qualified", "Proposal Sent", "Closed Won", "Closed Lost"]
            for idx, s_name in enumerate(stage_names):
                with q_cols[idx]:
                    if st.button(f"➔ {s_name}", key=f"dash_stage_{s_name}_{target_id}", use_container_width=True):
                        try:
                            requests.put(f"{API_URL}/leads/{target_id}", json={"status": s_name}, timeout=6)
                            st.toast(f"Updated {target_lead.get('name')} to '{s_name}'!", icon="✅")
                            st.rerun()
                        except Exception as ex:
                            st.error(f"Error: {ex}")


if __name__ == "__main__":
    show()