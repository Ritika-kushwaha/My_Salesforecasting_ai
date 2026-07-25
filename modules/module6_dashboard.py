import os
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="SalesGenie Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

def inject_custom_css():
    st.markdown(
        """
        <style>
        /* Modern Dark Theme Base */
        .stApp {
            background-color: #0d0e15;
            color: #e2e8f0;
        }
        
        .main .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 1600px;
        }
        
        /* Metric Cards */
        .metric-card {
            background: #181a26;
            border: 1px solid #26293b;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }
        
        .metric-title {
            color: #8e95a5;
            font-size: 0.88rem;
            font-weight: 500;
        }
        
        .metric-value {
            color: #ffffff;
            font-size: 2rem;
            font-weight: 700;
            margin-top: 6px;
        }

        .metric-delta {
            font-size: 0.8rem;
            color: #10b981;
            margin-top: 4px;
        }
        
        /* Section Containers */
        .dashboard-card {
            background: #181a26;
            border: 1px solid #26293b;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }

        /* Streamlit Dataframe Dark Override */
        [data-testid="stDataFrame"] {
            background: #181a26;
            border-radius: 10px;
            border: 1px solid #26293b;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )

@st.cache_data(ttl=5)
def fetch_dashboard_metrics(user_id: int):
    try:
        r = requests.get(f"{API_URL}/dashboard", params={"user_id": user_id})
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {"total_leads": 0, "qualified_leads": 0, "companies": 0, "average_score": 0.0}

@st.cache_data(ttl=5)
def fetch_leads_data(user_id: int):
    try:
        r = requests.get(f"{API_URL}/leads", params={"user_id": user_id})
        if r.status_code == 200:
            return pd.DataFrame(r.json())
    except Exception as e:
        st.error(f"Error fetching leads: {e}")
    return pd.DataFrame()

def render_metrics_row(metrics):
    col1, col2, col3, col4 = st.columns(4)
    
    cards_data = [
        ("Total Leads", metrics.get("total_leads", 0), "+12% vs last month"),
        ("Qualified Leads", metrics.get("qualified_leads", 0), "+8% conversion"),
        ("Companies", metrics.get("companies", 0), "Active accounts"),
        ("Average Lead Score", f"{metrics.get('average_score', 0):.1f}", "Target > 70"),
    ]
    
    cols = [col1, col2, col3, col4]
    for col, (title, val, delta) in zip(cols, cards_data):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">{title}</div>
                    <div class="metric-value">{val}</div>
                    <div class="metric-delta">↑ {delta}</div>
                </div>
            """,
                unsafe_allow_html=True,
            )

def render_dashboard():
    inject_custom_css()
    
    # Extract user information from session state
    user_info = st.session_state.get("user", {})
    user_id = user_info.get("id")
    user_name = user_info.get("name", "User")
    today_str = datetime.now().strftime("%b %d, %Y")
    
    # Handle missing session state
    if not user_id:
        st.warning("⚠️ User session not found. Please log out and log in again.")
        st.stop()

    # Top Bar Header
    c_title, c_actions = st.columns([3, 1])
    with c_title:
        st.markdown(f"## Good morning, {user_name}! 👋")
        st.caption("Here is what's happening with your sales pipeline today.")
    with c_actions:
        st.markdown(f"**Date:** `{today_str}`")
        if st.button("🔄 Sync Database", use_container_width=True):
            fetch_dashboard_metrics.clear()
            fetch_leads_data.clear()
            st.rerun()

    st.markdown("---")

    # Fetch User Specific Metrics & Leads
    metrics = fetch_dashboard_metrics(user_id)
    df_leads = fetch_leads_data(user_id)

    # Metrics Overview
    render_metrics_row(metrics)
    st.write("")

    # Visualizations Row 1: Lead Distribution & Quality
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown("### 📊 Leads by Status")
        if not df_leads.empty and "status" in df_leads.columns:
            status_df = df_leads["status"].value_counts().reset_index()
            status_df.columns = ["status", "count"]
            
            fig_pie = px.pie(
                status_df,
                names="status",
                values="count",
                hole=0.6,
                color_discrete_sequence=["#6366f1", "#10b981", "#f59e0b", "#ef4444"],
            )
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e2e8f0"),
                margin=dict(l=20, r=20, t=20, b=20),
                height=300,
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No lead status data available.")

    with col_right:
        st.markdown("### ⭐ Top Scoring Accounts")
        if not df_leads.empty and "lead_score" in df_leads.columns:
            top_leads = df_leads.sort_values("lead_score", ascending=False).head(5)
            fig_bar = px.bar(
                top_leads,
                x="lead_score",
                y="company",
                orientation="h",
                color="lead_score",
                color_continuous_scale="Purples",
                text="lead_score",
            )
            fig_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e2e8f0"),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False, categoryorder="total ascending"),
                coloraxis_showscale=False,
                margin=dict(l=20, r=20, t=20, b=20),
                height=300,
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No score data available.")

    # Section 2: Recent Leads Table
    st.markdown("### 📋 Recent Leads")
    
    search_query = st.text_input("🔍 Search Leads", placeholder="Type company name or contact...")
    
    filtered_df = df_leads
    if search_query and not df_leads.empty:
        filtered_df = df_leads[
            df_leads["company"].str.contains(search_query, case=False, na=False)
            | df_leads["name"].str.contains(search_query, case=False, na=False)
        ]

    if not filtered_df.empty:
        display_cols = ["name", "company", "industry", "status", "priority", "lead_score"]
        existing_cols = [c for c in display_cols if c in filtered_df.columns]
        st.dataframe(
            filtered_df[existing_cols],
            use_container_width=True,
            hide_index=True,
            height=300,
        )
    else:
        st.warning("No records matched your search.")

def show():
    render_dashboard()

if __name__ == "__main__":
    show()