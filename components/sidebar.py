import streamlit as st

def render_sidebar():
    # 1. Sidebar Styling
    st.markdown("""
        <style>
        /* Hide default Streamlit sidebar nav */
        [data-testid="stSidebarNav"] {display: none;}
        
        /* Sidebar Container */
        section[data-testid="stSidebar"] {
            background-color: #11121d !important;
            padding: 10px 0px;
        }

        /* Nav Item Styling */
        .nav-item {
            display: flex;
            align-items: center;
            padding: 12px 20px;
            margin: 4px 15px;
            border-radius: 10px;
            color: #8e95a5;
            text-decoration: none;
            transition: all 0.3s;
            cursor: pointer;
            font-weight: 500;
        }

        .nav-item:hover {
            background-color: #1e2030;
            color: #ffffff;
        }

        .nav-item.active {
            background-color: #4f46e5;
            color: #ffffff;
            box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3);
        }

        .nav-icon {
            margin-right: 15px;
            font-size: 18px;
        }

        /* Logo Area */
        .sidebar-logo {
            padding: 20px 30px;
            margin-bottom: 20px;
            font-size: 24px;
            font-weight: 800;
            color: #ffffff;
            display: flex;
            align-items: center;
        }
        
        .logo-dot {
            color: #6366f1;
            margin-left: 2px;
        }
        </style>
    """, unsafe_allow_html=True)

    # 2. Logo Header
    st.sidebar.markdown('<div class="sidebar-logo">SalesGenie<span class="logo-dot">.</span></div>', unsafe_allow_html=True)

    # 3. Navigation Items
    menu_items = [
        {"label": "Dashboard", "icon": "📊", "id": "dashboard"},
        {"label": "Leads", "icon": "👥", "id": "leads"},
        {"label": "Outreach", "icon": "✉️", "id": "outreach"},
        {"label": "Conversations", "icon": "💬", "id": "conversations"},
        {"label": "Companies", "icon": "🏢", "id": "companies"},
        {"label": "Reports", "icon": "📈", "id": "reports"},
        {"label": "Settings", "icon": "⚙️", "id": "settings"},
    ]

    # Initialize session state for page if not exists
    if "page" not in st.session_state:
        st.session_state.page = "dashboard"

    for item in menu_items:
        is_active = "active" if st.session_state.page == item["id"] else ""
        
        # We use a button hidden inside the styled div to trigger page changes
        if st.sidebar.button(f"{item['icon']} {item['label']}", key=f"btn_{item['id']}", use_container_width=True):
            st.session_state.page = item["id"]
            st.rerun()

    # 4. Bottom Logout Area
    st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
    if st.sidebar.button("🚪 Logout", use_container_width=True, type="secondary"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()