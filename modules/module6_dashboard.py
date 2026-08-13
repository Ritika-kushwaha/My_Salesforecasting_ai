import os
import pandas as pd
import requests
import streamlit as st

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")


def show():
    st.title("📊 SalesGenie Executive Dashboard")

    user_id = st.session_state.get("user_id", 1)

    # -------------------------------------------------------------
    # 1. FETCH EXECUTIVE KPI METRICS
    # -------------------------------------------------------------
    try:
        res = requests.get(f"{API_URL}/dashboard", params={"user_id": user_id}, timeout=5)
        if res.status_code == 200:
            dash_data = res.json()
        else:
            dash_data = {}
    except Exception:
        dash_data = {}

    total_leads = dash_data.get("total_leads", 0)
    high_priority = dash_data.get("high_priority_leads", 0)
    qualified = dash_data.get("qualified_leads", 0)
    conversion_rate = dash_data.get("conversion_rate", 0.0)
    total_companies = dash_data.get("total_companies", 0)

    # KPI Summary Metric Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Leads", total_leads)
    with col2:
        st.metric("High Priority", high_priority)
    with col3:
        st.metric("Qualified Leads", qualified)
    with col4:
        st.metric("Conversion Rate", f"{conversion_rate}%")
    with col5:
        st.metric("Researched Cos.", total_companies)

    st.markdown("---")

    # -------------------------------------------------------------
    # 2. FETCH LEADS DATA FOR CHARTS AND OVERVIEW TABLE
    # -------------------------------------------------------------
    try:
        leads_res = requests.get(f"{API_URL}/leads", params={"user_id": user_id}, timeout=5)
        leads_data = leads_res.json() if leads_res.status_code == 200 else []
    except Exception:
        leads_data = []

    if leads_data:
        df_leads = pd.DataFrame(leads_data)

        # -------------------------------------------------------------
        # CHARTS SECTION
        # -------------------------------------------------------------
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("🎯 Leads by Status")
            if "status" in df_leads.columns:
                status_counts = df_leads["status"].value_counts()
                st.bar_chart(status_counts)
            else:
                st.info("No status data available.")

        with col_right:
            st.subheader("🔥 Leads by Priority")
            if "priority" in df_leads.columns:
                priority_counts = df_leads["priority"].value_counts()
                st.bar_chart(priority_counts)
            else:
                st.info("No priority data available.")

        st.markdown("---")

        # -------------------------------------------------------------
        # RECENT LEADS OVERVIEW TABLE
        # -------------------------------------------------------------
        st.subheader("📌 Recent Leads Overview")

        # Format revenue column for display
        if "revenue" in df_leads.columns:
            df_leads["revenue"] = df_leads["revenue"].apply(
                lambda x: f"${float(x):,.2f}" if str(x).replace(".", "", 1).isdigit() else str(x)
            )

        # Create clean display counter (#1, #2, #3...)
        df_leads["#"] = range(1, len(df_leads) + 1)

        # Position '#' at the front and exclude internal DB IDs
        cols = ["#"] + [c for c in df_leads.columns if c not in ["#", "id", "user_id"]]

        # Display table with hidden Streamlit index
        st.dataframe(df_leads[cols], use_container_width=True, hide_index=True)

    else:
        st.info("No leads available yet. Head over to Module 1 to add your first lead!")


if __name__ == "__main__":
    show()