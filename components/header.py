import streamlit as st
from datetime import datetime

def render_header(title="Dashboard", subtitle="Overview of your sales pipeline and performance metrics"):
    """Renders a top header bar with breadcrumbs, user info, and quick actions."""
    
    st.markdown("""
        <style>
        .header-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0px 20px 0px;
            border-bottom: 1px solid #1e2030;
            margin-bottom: 25px;
        }
        
        .header-title-section h2 {
            font-size: 24px !important;
            font-weight: 700 !important;
            color: #ffffff !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        .header-title-section p {
            color: #8e95a5 !important;
            font-size: 13px !important;
            margin-top: 4px !important;
        }

        .header-actions {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .status-badge {
            background-color: rgba(16, 185, 129, 0.1);
            color: #10b981;
            border: 1px solid rgba(16, 185, 129, 0.2);
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background-color: #10b981;
            border-radius: 50%;
        }

        .user-profile-avatar {
            width: 36px;
            height: 36px;
            background: linear-gradient(135deg, #6366f1, #4f46e5);
            color: #ffffff;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 14px;
        }
        </style>
    """, unsafe_allow_html=True)

    user_name = st.session_state.get("user", {}).get("name", "Ritika")
    user_initial = user_name[0].upper() if user_name else "U"
    current_date = datetime.now().strftime("%B %d, %Y")

    c_info, c_controls = st.columns([3, 1])

    with c_info:
        st.markdown(f"""
            <div class="header-title-section">
                <h2>{title}</h2>
                <p>{subtitle}</p>
            </div>
        """, unsafe_allow_html=True)

    with c_controls:
        st.markdown(f"""
            <div class="header-actions" style="justify-content: flex-end;">
                <div class="status-badge">
                    <div class="status-dot"></div> API Connected
                </div>
                <div class="user-profile-avatar" title="{user_name}">
                    {user_initial}
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.write("")