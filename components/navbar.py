import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.markdown("## ⚡ SalesGenie AI")
        st.caption("AI-Powered B2B Sales Engine")
        st.divider()

        nav_options = [
            ("📊 Dashboard", "Dashboard"),
            ("👥 Lead Management", "Lead Management"),
            ("🏢 Company Intelligence", "Company Intelligence"),
            ("✉️ AI Outreach", "AI Outreach"),
            ("🎯 Lead Scoring", "Lead Scoring"),
            ("💬 CRM Conversations", "CRM Conversations"),
        ]

        active_tab = st.session_state.get("active_tab", "Dashboard")

        for idx, (label, tab_name) in enumerate(nav_options):
            btn_type = "primary" if active_tab == tab_name else "secondary"
            if st.button(
                label,
                key=f"sidebar_btn_{idx}_{tab_name}",
                type=btn_type,
                use_container_width=True,
            ):
                st.session_state["active_tab"] = tab_name
                st.rerun()

        st.divider()

        if st.button("🚪 Log Out", key="sidebar_logout_btn", use_container_width=True):
            st.session_state["logged_in"] = False
            st.session_state["user"] = None
            st.session_state["active_tab"] = "Dashboard"
            st.rerun()