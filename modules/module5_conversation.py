import os
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

        .panel-box {
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 18px;
            padding: 22px;
            backdrop-filter: blur(14px);
        }
        .stButton>button {
            border-radius: 12px;
            font-weight: 700;
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


def show():
    apply_app_theme()

    st.markdown(
        """
        <div style="margin-bottom: 22px;">
            <div style="display: inline-flex; align-items: center; gap: 8px; background: rgba(99, 102, 241, 0.12); border: 1px solid rgba(99, 102, 241, 0.25); border-radius: 9999px; padding: 4px 12px; color: #818CF8; font-size: 0.78rem; font-weight: 700; margin-bottom: 8px;">
                🎙️ MEETING INTELLIGENCE
            </div>
            <h1 style="font-size: 2.1rem; font-weight: 800; margin: 0; letter-spacing: -0.03em;">Conversation Intelligence & Interaction Feed</h1>
            <p style="color: #94A3B8; font-size: 0.92rem; margin-top: 4px;">Analyze sales call transcripts, extract key action items, and sync CRM pipeline stages automatically.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    user_id = get_current_user_id()

    leads_list = []
    try:
        res = requests.get(f"{API_URL}/leads", params={"user_id": user_id}, timeout=8)
        if res.status_code == 200:
            leads_list = res.json()
    except Exception:
        pass

    if not leads_list:
        st.info("💡 No leads registered. Add prospects in **Module 1 (Lead Pipeline)** to analyze conversations!")
        return

    lead_options = {}
    for idx, lead in enumerate(leads_list, start=1):
        lead_options[f"#{idx} - {lead.get('name')} ({lead.get('company')})"] = lead.get("id")

    c_select, c_card = st.columns([1.2, 1], gap="large")
    with c_select:
        selected_label = st.selectbox("🎯 Target Prospect for Conversation Analysis:", list(lead_options.keys()))
        selected_lead_id = lead_options[selected_label]

    selected_lead = next((l for l in leads_list if l.get("id") == selected_lead_id), {})

    with c_card:
        prio_color = "#EF4444" if selected_lead.get("priority") == "High" else "#F59E0B"
        st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 14px; padding: 14px 18px;">
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem;">
                <span><b>Industry:</b> {selected_lead.get('industry', 'General')}</span>
                <span><b>Stage:</b> <code style="color: #6366F1;">{selected_lead.get('status', 'New')}</code></span>
                <span><b>Priority:</b> <span style="color: {prio_color}; font-weight: 700;">{selected_lead.get('priority', 'Medium')}</span></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

    tab_analyze, tab_history = st.tabs(["🤖 AI Transcript Analyzer", "📜 Chronological Notes Timeline"])

    with tab_analyze:
        col_type, _ = st.columns([1, 2])
        with col_type:
            call_type = st.selectbox("Call Type", ["Discovery Call", "Demo Meeting", "Technical Evaluation", "Negotiation & Closing", "Follow-up Call"])

        transcript_text = st.text_area(
            "Paste Call Transcript or Meeting Notes:",
            height=180,
            placeholder="e.g. Sales Rep: Thanks for meeting today. Prospect: We need automated lead scoring and CRM sync..."
        )

        if st.button("⚡ Run AI Analysis & Advance Pipeline", type="primary", use_container_width=True):
            if not transcript_text.strip():
                st.error("Please enter a meeting transcript.")
            else:
                with st.spinner("Analyzing conversation and updating CRM..."):
                    payload = {"lead_id": selected_lead_id, "transcript": transcript_text, "interaction_type": call_type}
                    try:
                        res = requests.post(f"{API_URL}/analyze-conversation", json=payload, params={"user_id": user_id}, timeout=30)
                        if res.status_code == 200:
                            ai_res = res.json().get("data", {})
                            st.toast("Meeting analyzed and stage synced!", icon="🎉")

                            st.markdown(f"""
                            <div style="background: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.25); border-radius: 16px; padding: 20px; margin: 15px 0;">
                                <h4 style="margin: 0 0 8px 0; color: #6366F1;">📋 Executive Meeting Summary</h4>
                                <p style="margin: 0; font-size: 0.92rem; line-height: 1.6;">{ai_res.get('summary', 'Logged.')}</p>
                            </div>
                            """, unsafe_allow_html=True)

                            r1, r2 = st.columns(2, gap="medium")
                            with r1:
                                st.markdown("#### 🎯 Key Discussion Points")
                                for pt in ai_res.get("key_points", ["Discussed technical requirements.", "Evaluated budget and timeline."]):
                                    st.markdown(f"• {pt}")
                            with r2:
                                st.markdown("#### ⚡ Recommended Next Actions")
                                for act in ai_res.get("action_items", ["Send customized proposal.", "Schedule follow-up demo."]):
                                    st.markdown(f"✅ **{act}**")
                        else:
                            st.error(f"Error {res.status_code}: {res.text}")
                    except Exception as ex:
                        st.error(f"Error: {ex}")

    with tab_history:
        st.markdown(f"### 📜 Interaction Timeline for {selected_label}")
        with st.expander("➕ Log a Quick Meeting Note", expanded=False):
            with st.form("quick_note_feed", clear_on_submit=True):
                n_type = st.selectbox("Type", ["Quick Note", "Phone Call", "Follow-up Email", "Demo Meeting"])
                n_content = st.text_area("Note Content", placeholder="e.g. Followed up on proposal. Prospect requested 5% discount for annual contract.")
                if st.form_submit_button("📌 Save to Timeline", type="primary"):
                    if n_content.strip():
                        requests.post(f"{API_URL}/analyze-conversation", json={"lead_id": selected_lead_id, "transcript": n_content, "interaction_type": n_type}, params={"user_id": user_id}, timeout=15)
                        st.toast("Note saved!", icon="✅")
                        st.rerun()

        try:
            hist_res = requests.get(f"{API_URL}/conversations", params={"lead_id": selected_lead_id, "user_id": user_id}, timeout=8)
            if hist_res.status_code == 200:
                history_data = hist_res.json()
                if history_data:
                    for item in reversed(history_data):
                        created = item.get('created_at', 'Recent')
                        itype = item.get('interaction_type', 'Call')
                        transcript_full = item.get('transcript', '')
                        summary_full = item.get('summary')

                        st.markdown(f"""
                        <div style="background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 14px; padding: 18px; margin-bottom: 12px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <span style="font-weight: 700; color: #6366F1;">🗓️ {itype}</span>
                                <span style="font-size: 0.8rem; color: #94A3B8;">{created[:19] if len(created) > 19 else created}</span>
                            </div>
                            <p style="font-size: 0.9rem; margin-bottom: 8px;">{transcript_full}</p>
                            {f'<div style="font-size: 0.85rem; color: #10B981; background: rgba(16, 185, 129, 0.06); padding: 8px 12px; border-radius: 8px;"><b>AI Summary:</b> {summary_full}</div>' if summary_full else ''}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No recorded interactions found for this prospect yet.")
        except Exception:
            pass


if __name__ == "__main__":
    show()