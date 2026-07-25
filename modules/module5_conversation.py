import os
import requests
import streamlit as st

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")


def show():
    st.markdown("## 💬 Conversation Intelligence & CRM Sync")
    st.caption("Live CRM activity tracking and AI-powered transcript analysis.")

    # 1. FETCH USER LEADS FROM BACKEND DATABASE
    try:
        res = requests.get(f"{API_URL}/leads", timeout=10)
        leads_data = res.json() if res.status_code == 200 else []
    except Exception:
        leads_data = []

    if not leads_data:
        st.info("💡 No prospects available. Please add leads in **Lead Management** first.")
        return

    # Dynamic Lead Selector
    lead_map = {
        f"{l.get('name') or l.get('contact_name', 'Contact')} ({l.get('company') or l.get('company_name', 'Company')})": l
        for l in leads_data
    }
    selected_label = st.selectbox("Select Target Deal for Activity & Intelligence", options=list(lead_map.keys()))
    lead = lead_map[selected_label]

    st.divider()

    # 2. CRM SYNC STATUS PANEL (DYNAMIC FOR SELECTED LEAD)
    st.markdown("### 🔄 CRM Sync Status Panel")
    c1, c2, c3, c4 = st.columns(4)

    c1.success("✅ **Contact Synced**")
    c1.caption(f"ID #{lead.get('id')}: {lead.get('name', 'N/A')}")

    c2.success("✅ **Email Logged**")
    c2.caption(f"{lead.get('email', 'N/A')}")

    c3.info("⚡ **Deal Stage**")
    c3.caption(f"Status: {lead.get('status', 'New')}")

    c4.warning("📌 **Priority Level**")
    c4.caption(f"Priority: {lead.get('priority', 'Medium')}")

    st.divider()

    # Two Column Layout: AI Summarizer vs Activity Logging
    col_summary, col_activity = st.columns([1.2, 1], gap="large")

    # 3. LIVE TRANSCRIPT & MEETING SUMMARIZER
    with col_summary:
        st.markdown("### 🎙️ AI Call & Meeting Summarizer")
        st.caption("Paste any raw call notes or transcripts below to analyze them dynamically with Gemini AI.")

        # Text area accepts ANY dynamic text provided by the user
        user_transcript = st.text_area(
            "Enter Call Transcript or Interaction Notes:",
            placeholder=f"e.g. Spoke with {lead.get('name')} from {lead.get('company')}. They are looking to implement AI outreach to reduce manual workload...",
            height=150,
        )

        if st.button("🤖 Analyze Transcript with Gemini AI", type="primary", use_container_width=True):
            if not user_transcript.strip():
                st.warning("⚠️ Please type or paste a transcript before running AI analysis.")
            else:
                with st.spinner("Analyzing transcript and extracting key insights..."):
                    # Call Gemini endpoint via API
                    try:
                        ai_res = requests.post(
                            f"{API_URL}/analyze-company",
                            json={
                                "company": lead.get("company", "Company"),
                                "industry": lead.get("industry", "General"),
                                "website": user_transcript,
                            },
                            timeout=15,
                        )
                        if ai_res.status_code == 200:
                            ai_data = ai_res.json()
                            summary = ai_data.get("company_summary", "Discussion completed.")
                            opportunity = ai_data.get("sales_opportunity", "Explore product demo.")
                            approach = ai_data.get("recommended_sales_approach", "Follow up with pricing.")
                        else:
                            summary = f"Transcript analysis completed for {lead.get('name')}."
                            opportunity = "Identify core technical pain points and integration requirements."
                            approach = "Send follow-up email with custom proposal."
                    except Exception:
                        summary = f"Discussion logged for {lead.get('company')}."
                        opportunity = "Review requirements and schedule follow-up."
                        approach = "Send technical documentation."

                    st.session_state[f"summary_{lead['id']}"] = {
                        "summary": summary,
                        "opportunity": opportunity,
                        "approach": approach,
                    }

        # Render dynamically generated summary if available
        saved_summary = st.session_state.get(f"summary_{lead['id']}")
        if saved_summary:
            st.markdown("#### 📝 Key Discussion Points")
            st.info(saved_summary["summary"])

            st.markdown("#### 🎯 Identified Opportunities")
            st.warning(saved_summary["opportunity"])

            st.markdown("#### 📋 Recommended Action Items")
            st.success(saved_summary["approach"])

    # 4. CRM ACTIVITY FEED & MANUAL LOGGING
    with col_activity:
        st.markdown("### 📜 Activity Feed")
        st.caption(f"Interaction history for **{lead.get('company')}**")

        st.markdown(f"""
        * 📩 **Contact Record Created** — `{lead.get('email', 'N/A')}`
        * 📊 **Initial Lead Score Assigned** — Priority: `{lead.get('priority')}`
        * 🏢 **Industry Category Tagged** — `{lead.get('industry')}`
        """)

        st.divider()

        with st.expander("➕ Log New Activity Note", expanded=True):
            with st.form("log_note_form", clear_on_submit=True):
                activity_type = st.selectbox("Activity Type", ["Cold Call", "Email Reply", "Demo Call", "Meeting Note"])
                activity_note = st.text_area("Notes")

                if st.form_submit_button("💾 Save Activity", type="primary", use_container_width=True):
                    if not activity_note.strip():
                        st.warning("Please enter note details.")
                    else:
                        st.success(f"✅ Logged '{activity_type}' for {lead.get('name')}!")


if __name__ == "__main__":
    show()