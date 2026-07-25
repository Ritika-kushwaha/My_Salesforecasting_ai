import os
import pandas as pd
import requests
import streamlit as st
from components.theme import load_theme

load_theme()

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")


def show():
    # Page Header
    st.markdown("""
        <div style="margin-bottom: 25px;">
            <div style="color: #6366f1; font-size: 12px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase;">
                Conversation Intelligence & CRM
            </div>
            <h1 style="font-size: 28px; font-weight: 800; color: #ffffff; margin-top: 4px;">
                🗣️ Meeting Summarization & CRM Sync
            </h1>
            <p style="color: #94a3b8; font-size: 14px;">
                Extract key discussion points, action items, and sync interactions automatically to PostgreSQL.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Validate User Session
    user_id = st.session_state.get("user", {}).get("id")
    if not user_id:
        st.warning("⚠️ User session not found. Please log in again.")
        st.stop()

    # Load Leads for Selection
    try:
        res = requests.get(f"{API_URL}/leads", params={"user_id": user_id}, timeout=10)
        leads = res.json() if res.status_code == 200 else []
    except Exception:
        leads = []

    if not leads:
        st.info("💡 No leads found in your account database. Add a lead in 'Lead Management' first.")
        st.stop()

    # Layout Setup
    col_left, col_right = st.columns([1.6, 1])

    with col_left:
        st.markdown("### 📝 Input Meeting Notes / Transcript")
        
        lead_map = {}
        for l in leads:
          contact = l.get("contact_name") or l.get("name") or "Contact"
          company = l.get("company_name") or l.get("company") or "Company"
          label = f"{contact} ({company})"
          lead_map[label] = l

        selected_label = st.selectbox("Select Prospect", options=list(lead_map.keys()))
        selected_lead = lead_map[selected_label]

        interaction_type = st.selectbox(
            "Interaction Type",
            ["Discovery Call (45 min)", "Demo Call (30 min)", "Follow-up Email Thread", "Negotiation Call"],
        )

        transcript_input = st.text_area(
            "Meeting Transcript or Notes",
            height=200,
            placeholder="Paste raw transcript or notes here... e.g. Customer mentioned data processing bottlenecks. Budget is approved for Q3 infrastructure upgrade. Needs technical architecture doc.",
        )

        st.write("")
        analyze_btn = st.button("🤖 Analyze & Extract Intelligence", type="primary", use_container_width=True)

        if analyze_btn:
            if not transcript_input.strip():
                st.warning("⚠️ Please paste meeting notes or transcript to analyze.")
            else:
                try:
                    with st.spinner("⚡ AI is extracting key points, action items, and updating CRM..."):
                        response = requests.post(
                            f"{API_URL}/analyze-conversation",
                            params={"user_id": user_id},
                            json={
                                "lead_id": selected_lead["id"],
                                "transcript": transcript_input.strip(),
                                "interaction_type": interaction_type,
                            },
                            timeout=25,
                        )

                    if response.status_code == 200:
                        result = response.json()
                        st.session_state["latest_analysis"] = result
                        st.success("✅ Conversation Analyzed & Synced to CRM!")
                    else:
                        st.error(f"Analysis failed (Error {response.status_code}): {response.text}")

                except Exception as e:
                    st.error(f"Backend connection error: {e}")

        # Display AI Analysis Card if available
        if "latest_analysis" in st.session_state:
            data = st.session_state["latest_analysis"]
            st.divider()
            
            st.markdown(f"#### 📊 Meeting Summary: {data.get('company_name')}")
            st.info(data.get("summary"))

            st.markdown("#### 🎯 Key Discussion Points")
            for point in data.get("key_discussion_points", []):
                st.markdown(f"• {point}")

            st.markdown("#### ⚡ Extracted Action Items")
            for item in data.get("action_items", []):
                st.markdown(f"""
                    <div style="background: #181a26; border-left: 4px solid #6366f1; padding: 10px 14px; border-radius: 6px; margin-bottom: 8px;">
                        <span style="color: #ffffff; font-weight: 600;">{item.get('task')}</span><br>
                        <span style="color: #94a3b8; font-size: 12px;">Assigned to: {item.get('assigned_to')} | Due: {item.get('due_in')}</span>
                    </div>
                """, unsafe_allow_html=True)

    with col_right:
        st.markdown("### 🔄 CRM Sync & Activity Feed")
        
        # CRM Sync Status Widget
        st.markdown(f"""
            <div style="background: #181a26; border: 1px solid #26293b; border-radius: 12px; padding: 18px; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <span style="font-weight: 700; color: #ffffff;">CRM Sync Status</span>
                    <span style="color: #10b981; font-weight: 700; font-size: 12px;">● Synced</span>
                </div>
                <div style="font-size: 13px; color: #cbd5e1; margin-bottom: 6px;"><b>Contact:</b> {selected_lead['contact_name']}</div>
                <div style="font-size: 13px; color: #cbd5e1; margin-bottom: 6px;"><b>Company:</b> {selected_lead['company_name']}</div>
                <div style="font-size: 13px; color: #cbd5e1;"><b>Current Stage:</b> <span style="color: #6366f1;">{selected_lead.get('lead_status', 'Qualified')}</span></div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 📜 Recent Activity Feed")
        try:
            feed_res = requests.get(
                f"{API_URL}/interactions",
                params={"lead_id": selected_lead["id"], "user_id": user_id},
                timeout=10,
            )
            if feed_res.status_code == 200:
                history = feed_res.json()
                if history:
                    for entry in history:
                        st.markdown(f"""
                            <div style="background: #13151f; border-left: 3px solid #10b981; padding: 10px 12px; border-radius: 6px; margin-bottom: 10px;">
                                <div style="font-size: 12px; color: #e2e8f0;">{entry['message']}</div>
                                <div style="font-size: 10px; color: #64748b; margin-top: 4px;">{entry['timestamp']}</div>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.caption("No past activity recorded for this prospect.")
            else:
                st.caption("Activity feed currently empty.")
        except Exception:
            st.caption("Could not connect to activity log.")


if __name__ == "__main__":
    st.set_page_config(page_title="CRM Conversations", page_icon="🗣️", layout="wide")
    show()