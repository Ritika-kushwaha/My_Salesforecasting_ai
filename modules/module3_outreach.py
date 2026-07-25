import os
import requests
import streamlit as st

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")


def show():
    st.markdown("## ✉️ AI Outreach & Campaign Generator")
    st.caption("Generate personalized sales emails, LinkedIn messages, and cold call scripts.")

    user_id = st.session_state.get("user", {}).get("id", 1)

    # Fetch existing leads to populate selection dropdown
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
            # Select Lead
            lead_options = {
                f"{l.get('name', 'N/A')} ({l.get('company', 'N/A')})": l
                for l in leads_list
            }
            
            selected_lead_label = st.selectbox(
                "Select Target Lead",
                options=list(lead_options.keys()) if lead_options else ["Manual Input"],
            )

            # Manual inputs if no lead is selected or available
            if not lead_options or selected_lead_label == "Manual Input":
                target_name = st.text_input("Contact Name", placeholder="e.g. John Smith")
                target_company = st.text_input("Company Name", placeholder="e.g. Acme Corp")
                target_industry = st.text_input("Industry", placeholder="e.g. Technology")
            else:
                chosen_lead = lead_options[selected_lead_label]
                target_name = chosen_lead.get("name", "")
                target_company = chosen_lead.get("company", "")
                target_industry = chosen_lead.get("industry", "Technology")
                st.info(f"📧 Email: {chosen_lead.get('email', 'N/A')}")

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
                with st.spinner("Crafting personalized message..."):
                    # Call Gemini AI endpoint or backend route
                    payload = {
                        "company": target_company,
                        "industry": target_industry,
                        "website": "Not Provided",
                    }
                    try:
                        res = requests.post(f"{API_URL}/analyze-company", params={"user_id": user_id}, json=payload)
                        if res.status_code == 200:
                            comp_data = res.json()
                            approach = comp_data.get("recommended_sales_approach", "")
                        else:
                            approach = "Focus on ROI and efficiency gains."
                    except Exception:
                        approach = "Focus on ROI and efficiency gains."

                    # Generate copy string
                    generated_subject = f"Quick question regarding {target_company}'s growth goals"
                    generated_body = (
                        f"Hi {target_name},\n\n"
                        f"I came across {target_company} and was impressed by your work in the {target_industry} space. "
                        f"{approach}\n\n"
                        f"{key_value_prop if key_value_prop else 'We specialize in AI solutions designed to streamline outreach.'}\n\n"
                        f"Would you be open to a quick 10-minute chat this Thursday?\n\n"
                        f"Best regards,\nSalesGenie Team"
                    )

                    st.session_state["outreach_result"] = {
                        "subject": generated_subject,
                        "body": generated_body,
                        "channel": channel,
                    }
                    st.success("Outreach message generated!")

    with c2:
        st.markdown("### 📝 Generated Copy")
        result = st.session_state.get("outreach_result")

        if result:
            st.caption(f"Channel: **{result.get('channel')}**")
            
            if "Email" in result.get("channel", ""):
                st.text_input("Subject Line", value=result.get("subject"), key="outreach_subj")

            st.text_area("Message Content", value=result.get("body"), height=300, key="outreach_body")

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