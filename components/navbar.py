import streamlit as st

def render_sidebar():
    """Renders a custom vertical dark-themed navigation sidebar matching the SalesGenie UI design."""
    
    # 1. Custom CSS styling to customize the default Streamlit sidebar look
    st.markdown("""
        <style>
        /* Hide standard Streamlit auto-generated navigation */
        [data-testid="stSidebarNav"] { 
            display: none !important; 
        }
        
        /* Dark Sidebar Main Container */
        section[data-testid="stSidebar"] {
            background-color: #0e1017 !important;
            border-right: 1px solid #1e2030 !important;
            padding-top: 1rem;
        }

        /* App Branding Header */
        .sidebar-brand {
            font-size: 22px;
            font-weight: 800;
            color: #ffffff;
            padding: 10px 12px 15px 12px;
            display: flex;
            align-items: center;
            gap: 10px;
            letter-spacing: -0.5px;
        }
        
        .brand-accent {
            color: #6366f1;
        }

        /* User Info Box */
        .user-card {
            background: #181a26;
            border: 1px solid #26293b;
            border-radius: 12px;
            padding: 12px 15px;
            margin: 5px 0px 20px 0px;
        }
        
        .user-label {
            color: #64748b;
            font-size: 11px;
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 0.5px;
        }

        .user-name {
            color: #f8fafc;
            font-weight: 600;
            font-size: 14px;
            margin-top: 2px;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        /* Sidebar Inactive Navigation Buttons */
        div[data-testid="stSidebar"] button[kind="secondary"] {
            background-color: transparent !important;
            color: #94a3b8 !important;
            border: 1px solid transparent !important;
            text-align: left !important;
            justify-content: flex-start !important;
            padding: 10px 16px !important;
            font-weight: 500 !important;
            font-size: 14px !important;
            border-radius: 10px !important;
            margin-bottom: 4px !important;
            transition: all 0.2s ease-in-out !important;
        }

        div[data-testid="stSidebar"] button[kind="secondary"]:hover {
            background-color: #1e2030 !important;
            color: #ffffff !important;
            border-color: #26293b !important;
        }

        /* Active Navigation Button Style */
        div[data-testid="stSidebar"] button[kind="primary"] {
            background-color: #4f46e5 !important;
            color: #ffffff !important;
            border: none !important;
            justify-content: flex-start !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            border-radius: 10px !important;
            margin-bottom: 4px !important;
            box-shadow: 0 4px 14px rgba(79, 70, 229, 0.4) !important;
        }

        /* Divider styling */
        .sidebar-divider {
            border-top: 1px solid #26293b;
            margin: 15px 0px;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        # App Logo / Title
        st.markdown(
            '<div class="sidebar-brand">⚡ SalesGenie<span class="brand-accent">.ai</span></div>', 
            unsafe_allow_html=True
        )

        # Active User Indicator
        user_name = st.session_state.get("user", {}).get("name", "Ritika")
        st.markdown(
            f"""
            <div class="user-card">
                <div class="user-label">Logged In As</div>
                <div class="user-name">👤 {user_name}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Navigation Options matching your project modules & design specs
        navigation_items = [
            {"id": "Dashboard", "label": "Dashboard", "icon": "📊"},
            {"id": "Lead Management", "label": "Leads", "icon": "👥"},
            {"id": "Company Intelligence", "label": "Companies", "icon": "🏢"},
            {"id": "AI Outreach", "label": "Outreach", "icon": "✉️"},
            {"id": "Lead Scoring", "label": "Lead Scoring", "icon": "🎯"},
            {"id": "CRM", "label": "Conversations", "icon": "💬"},
        ]

        # State initialization for active page selection
        if "active_tab" not in st.session_state:
            st.session_state.active_tab = "Dashboard"

        # Render menu buttons dynamically
        for item in navigation_items:
            is_active = (st.session_state.active_tab == item["id"])
            btn_kind = "primary" if is_active else "secondary"
            
            # Click action updates state and reruns session
            if st.button(f"{item['icon']}  {item['label']}", key=f"nav_btn_{item['id']}", type=btn_kind, use_container_width=True):
                st.session_state.active_tab = item["id"]
                st.rerun()

        # Bottom section divider
        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

        # Logout Action Trigger
        if st.button("🚪  Logout", key="btn_logout", type="secondary", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.page = "login"
            st.session_state.pop("user", None)
            st.rerun()