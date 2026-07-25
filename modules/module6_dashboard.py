import os
import pandas as pd
import requests
import streamlit as st

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")


def show():
    st.markdown("## 📊 Executive Dashboard")
    st.caption("Real-time pipeline analytics, lead conversion tracking, and visual breakdown.")

    # Fetch global metrics & leads (No user filtering)
    metrics = {"total_leads": 0, "high_priority_leads": 0, "qualified_leads": 0, "conversion_rate": 0.0}
    leads_list = []

    try:
        dash_res = requests.get(f"{API_URL}/dashboard", timeout=10)
        if dash_res.status_code == 200:
            metrics = dash_res.json()

        leads_res = requests.get(f"{API_URL}/leads", timeout=10)
        if leads_res.status_code == 200:
            leads_list = leads_res.json()
    except Exception as e:
        st.error(f"Error fetching metrics: {e}")

    # Top KPI Summary Cards
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Leads", metrics.get("total_leads", 0))
    m2.metric("High Priority", metrics.get("high_priority_leads", 0))
    m3.metric("Qualified Leads", metrics.get("qualified_leads", 0))
    m4.metric("Conversion Rate", f"{metrics.get('conversion_rate', 0.0)}%")

    st.divider()

    # Visual Charts
    c1, c2 = st.columns(2, gap="large")

    if leads_list:
        df_leads = pd.DataFrame(leads_list)

        with c1:
            st.markdown("### 🎯 Priority Breakdown")
            if "priority" in df_leads.columns:
                st.bar_chart(df_leads["priority"].value_counts(), color="#6366f1")

        with c2:
            st.markdown("### 🏢 Industry Breakdown")
            if "industry" in df_leads.columns:
                st.bar_chart(df_leads["industry"].value_counts().head(5), color="#3b82f6")
    else:
        st.info("No leads found in database.")


if __name__ == "__main__":
    show()