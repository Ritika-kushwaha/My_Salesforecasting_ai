import os
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")


@st.cache_data(ttl=5)
def fetch_dashboard_metrics(user_id: int):
    try:
        res = requests.get(f"{API_URL}/dashboard", params={"user_id": user_id}, timeout=10)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return {}


@st.cache_data(ttl=5)
def fetch_leads_data(user_id: int):
    try:
        res = requests.get(f"{API_URL}/leads", params={"user_id": user_id}, timeout=10)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return []


def show():
    st.markdown("## 📊 Executive Sales Intelligence Dashboard")
    st.caption("Real-time pipeline analytics, lead score metrics, and database activity.")

    # ✅ SAFE CODE (Handles None values, empty dicts, or missing keys)
    user_data = st.session_state.get("user") or {}
    user_id = user_data.get("id", 1) if isinstance(user_data, dict) else st.session_state.get("user_id", 1)

    col_header, col_ref = st.columns([4, 1])
    with col_ref:
        if st.button("🔄 Sync Database", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    metrics = fetch_dashboard_metrics(user_id)
    leads = fetch_leads_data(user_id)

    total_leads = metrics.get("total_leads", len(leads))
    qualified_leads = metrics.get("qualified_leads", sum(1 for l in leads if l.get("status") == "Qualified"))
    high_priority = metrics.get("high_priority_leads", sum(1 for l in leads if l.get("priority") == "High"))
    conv_rate = metrics.get("conversion_rate", 0.0)

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Active Leads", total_leads)
    kpi2.metric("High Priority Leads", high_priority)
    kpi3.metric("Qualified Leads", qualified_leads)
    kpi4.metric("Conversion Rate", f"{conv_rate}%")

    st.markdown("---")

    df_leads = pd.DataFrame(leads) if leads else pd.DataFrame()

    chart_left, chart_right = st.columns(2)

    with chart_left:
        st.subheader("🎯 Lead Stage Conversion Funnel")
        if not df_leads.empty and "status" in df_leads.columns:
            stage_counts = df_leads["status"].value_counts().reset_index()
            stage_counts.columns = ["Stage", "Count"]
            fig_funnel = px.funnel(stage_counts, x="Count", y="Stage", color="Stage")
            fig_funnel.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_funnel, use_container_width=True)
        else:
            st.info("No lead data available to render conversion funnel.")

    with chart_right:
        st.subheader("🔥 Lead Priority Breakdown")
        if not df_leads.empty and "priority" in df_leads.columns:
            prio_counts = df_leads["priority"].value_counts().reset_index()
            prio_counts.columns = ["Priority", "Count"]
            fig_prio = px.bar(
                prio_counts, x="Priority", y="Count", color="Priority",
                color_discrete_map={"High": "#2ecc71", "Medium": "#f39c12", "Low": "#e74c3c"}
            )
            fig_prio.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_prio, use_container_width=True)
        else:
            st.info("No priority metrics available in database.")

    st.markdown("---")

    st.subheader("📋 Active Lead Pipeline Records")
    if not df_leads.empty:
        display_cols = [c for c in ["id", "name", "company", "email", "industry", "priority", "status"] if c in df_leads.columns]
        st.dataframe(df_leads[display_cols], use_container_width=True, hide_index=True)
    else:
        st.write("No lead records registered in your account database.")


if __name__ == "__main__":
    show()