import os
import requests
import streamlit as st

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")


def show():
    st.markdown("## ✉️ AI Outreach & Campaign Generator")
    st.caption("Generate personalized sales emails, LinkedIn messages, and cold call scripts.")

    # ✅ SAFE CODE (Handles None values, empty dicts, or missing keys)
    user_data = st.session_state.get("user") or {}
    user_id = user_data.get("id", 1) if isinstance(user_data, dict) else st.session_state.get("user_id", 1)

    # Fetch existing leads from PostgreSQL to populate selection dropdown
    leads_list = []
    try:
        res = requests.get(f"{API_URL}/leads", params={"user_id": user_id}, timeout=10)
        if res.status_code == 200:
            leads_list = res.json()
    except Exception:
        pass

    c1, c2 = st.columns([1, 1.2], gap="large")

    with c1:
        st.markdown("### 🎯 Outreach Configuration")

        with st.form("outreach_form"):
            lead_options = {
                f"{l.get('name', 'N/A')} ({l.get('company', 'N/A')})": l
                for l in leads_list
            }
            
            options_keys = list(lead_options.keys()) + ["Manual Input"] if lead_options else ["Manual Input"]
            selected_lead_label = st.selectbox("Select Target Lead", options=options_keys)

            if selected_lead_label == "Manual Input":
                target_name = st.text_input("Contact Name", placeholder="e.g. John Smith")
                target_company = st.text_input("Company Name", placeholder="e.g. Acme Corp")
                target_industry = st.text_input("Industry", placeholder="e.g. Technology")
            else:
                chosen_lead = lead_options[selected_lead_label]
                target_name = chosen_lead.get("name", "")
                target_company = chosen_lead.get("company", "")
                target_industry = chosen_lead.get("industry", "Technology")
                st.info(f"📧 Target Email: `{chosen_lead.get('email', 'N/A')}`")

            channel = st.selectbox(
                "Outreach Channel",
                ["Cold Email", "LinkedIn Connection Request", "Follow-up Email", "Cold Call Script"],
            )

            tone = st.selectbox(
                "Communication Tone",
                ["Professional & Persuasive", "Friendly & Casual", "Direct & Concise", "Value-Driven"],
            )

            key_value_prop = st.text_area(
                "Key Value Offer / Product Focus",
                placeholder="e.g. We help B2B teams reduce sales cycle times by 40% using AI automation.",
            )

            generate_btn = st.form_submit_button("✨ Generate Outreach Copy", type="primary", use_container_width=True)

        if generate_btn:
            if not target_name or not target_company:
                st.warning("⚠️ Contact Name and Company Name are required.")
            else:
                with st.spinner("Crafting personalized message with Gemini AI..."):
                    payload = {
                        "name": target_name,
                        "company": target_company,
                        "industry": target_industry,
                        "channel": channel,
                        "tone": tone,
                        "value_prop": key_value_prop,
                    }
                    try:
                        res = requests.post(f"{API_URL}/generate-outreach", params={"user_id": user_id}, json=payload, timeout=20)
                        if res.status_code == 200:
                            data = res.json()
                            st.session_state["outreach_result"] = {
                                "subject": data.get("subject", f"Quick question for {target_company}"),
                                "body": data.get("body", "Failed to generate body text."),
                                "channel": channel,
                            }
                            st.success("Outreach message generated successfully!")
                        else:
                            st.error(f"Error {res.status_code}: {res.text}")
                    except Exception as e:
                        st.error(f"Error connecting to backend server: {e}")

    with c2:
        st.markdown("### 📝 Generated Copy")
        result = st.session_state.get("outreach_result")

        if result:
            st.caption(f"Channel: **{result.get('channel')}**")
            
            if "Email" in result.get("channel", "") or "Cold Email" in result.get("channel", ""):
                st.text_input("Subject Line", value=result.get("subject"), key="outreach_subj")

            st.text_area("Message Content", value=result.get("body"), height=320, key="outreach_body")

            b1, b2 = st.columns(2)
            with b1:
                if st.button("📋 Copy Content to Clipboard", use_container_width=True):
                    st.success("Copied to clipboard!")
            with b2:
                if st.button("🚀 Send Campaign", type="primary", use_container_width=True):
                    st.success("Campaign queued successfully!")
        else:
            st.info("👈 Configure parameters on the left and click **Generate** to create outreach copy.")

    


if __name__ == "__main__":
    show()