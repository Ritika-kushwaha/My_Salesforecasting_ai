import streamlit as st
import requests
import os
from datetime import datetime

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")

def show():
    st.title("💬 Module 5: Conversation Intelligence & CRM")
    st.caption("Analyze sales calls, extract action items, and sync interactions with PostgreSQL.")

    # ✅ SAFE CODE (Handles None values, empty dicts, or missing keys)
    user_data = st.session_state.get("user") or {}
    user_id = user_data.get("id", 1) if isinstance(user_data, dict) else st.session_state.get("user_id", 1)

    # 2. Fetch Leads from Backend API
    leads_list = []
    try:
        res = requests.get(f"{API_URL}/leads", params={"user_id": user_id}, timeout=10)
        if res.status_code == 200:
            leads_list = res.json()
    except Exception as e:
        st.warning(f"Unable to reach backend database at {API_URL}. Ensure Uvicorn is running.")

    if not leads_list:
        st.info("💡 No leads found in your account database. Please add leads in 'Lead Management' first.")
        return

    # Formulate Lead Selector Map
    lead_options = {}
    for lead in leads_list:
        l_id = lead.get("id") or lead.get("lead_id")
        l_name = lead.get("name") or lead.get("contact_name", "Unknown Contact")
        l_comp = lead.get("company") or lead.get("company_name", "Unknown Company")
        lead_options[f"{l_name} ({l_comp})"] = l_id

    # UI Layout: Column Selection
    col_select, col_info = st.columns([2, 1])
    with col_select:
        selected_lead_label = st.selectbox("🎯 Select Lead / Prospect for Meeting Analysis:", list(lead_options.keys()))
        selected_lead_id = lead_options[selected_lead_label]

    # Find full selected lead dict
    selected_lead = next((l for l in leads_list if (l.get("id") == selected_lead_id or l.get("lead_id") == selected_lead_id)), {})

    with col_info:
        st.markdown(f"**Industry:** `{selected_lead.get('industry', 'N/A')}`")
        st.markdown(f"**Current Status:** `{selected_lead.get('status', 'New')}`")
        st.markdown(f"**Priority:** `{selected_lead.get('priority', 'Medium')}`")

    st.markdown("---")

    # Tabs for Input & Recent History
    tab_analyze, tab_history = st.tabs(["🤖 AI Transcript Summarizer", "📜 Interaction History"])

    with tab_analyze:
        st.subheader("🎙️ Input Call Transcript or Meeting Notes")
        transcript_text = st.text_area(
            "Paste Meeting Notes, Email Threads, or Call Transcripts:",
            height=180,
            placeholder="e.g., Met with VP of Technology. They expressed strong interest in our AI automation features but requested custom enterprise SLAs. Target closing Q3..."
        )

        call_type = st.selectbox("Interaction Type:", ["Discovery Call", "Demo Meeting", "Follow-up Email", "Closing Pitch"])

        if st.button("🚀 Analyze & Extract Intelligence", type="primary"):
            if not transcript_text.strip():
                st.error("Please enter transcript text before analyzing.")
            else:
                with st.spinner("Processing transcript with Gemini AI..."):
                    payload = {
                        "lead_id": selected_lead_id,
                        "transcript": transcript_text,
                        "interaction_type": call_type
                    }
                    try:
                        # API call to process conversation and save to database
                        response = requests.post(
                            f"{API_URL}/analyze-conversation",
                            json=payload,
                            params={"user_id": user_id},
                            timeout=25
                        )
                        if response.status_code == 200:
                            data = response.json().get("data", {})
                            st.success("✅ Interaction analyzed and saved to PostgreSQL successfully!")

                            # Display Results Cards
                            res_col1, res_col2 = st.columns(2)
                            with res_col1:
                                st.markdown("### 📋 Executive Summary")
                                st.info(data.get("summary", "Summary compiled from call notes."))

                                st.markdown("### 🎯 Key Discussion Points")
                                points = data.get("key_points", ["Customer requirements discussed.", "Timeline evaluated."])
                                for pt in points:
                                    st.write(f"• {pt}")

                            with res_col2:
                                st.markdown("### ⚡ Next Action Items")
                                actions = data.get("action_items", ["Follow up by end of week."])
                                for act in actions:
                                    st.write(f"✅ {act}")

                                st.markdown("### 📈 Stage Recommendation")
                                st.success(f"Recommended Lead Status: **{data.get('recommended_stage', 'Qualified')}**")
                        else:
                            st.error(f"Backend returned error {response.status_code}: {response.text}")
                    except Exception as ex:
                        st.error(f"Error connecting to server: {ex}")

    with tab_history:
        st.subheader(f"📜 Logged Interactions for {selected_lead_label}")
        try:
            hist_res = requests.get(
                f"{API_URL}/conversations",
                params={"lead_id": selected_lead_id, "user_id": user_id},
                timeout=10
            )
            if hist_res.status_code == 200:
                history_data = hist_res.json()
                if history_data:
                    for item in history_data:
                        with st.expander(f"🗓️ {item.get('created_at', 'Recent')} - {item.get('interaction_type', 'Call')}"):
                            st.write(f"**Notes/Transcript:** {item.get('transcript', '')}")
                            if item.get('summary'):
                                st.info(f"**AI Summary:** {item.get('summary')}")
                else:
                    st.write("No recorded interactions found for this lead in PostgreSQL.")
            else:
                st.write("Unable to fetch interaction history.")
        except Exception as e:
            st.write(f"Error loading history: {e}")

if __name__ == "__main__":
    show()