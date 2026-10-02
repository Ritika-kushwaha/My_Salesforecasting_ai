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
                ✉️ COPYWRITER AGENT
            </div>
            <h1 style="font-size: 2.1rem; font-weight: 800; margin: 0; letter-spacing: -0.03em;">AI Outreach & Cold Copy Generator</h1>
            <p style="color: #94A3B8; font-size: 0.92rem; margin-top: 4px;">Generate personalized cold emails, InMails, and phone scripts, then log outreach in 1 click.</p>
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

    lead_options = {"✍️ Custom / Manual Prospect": None}
    for idx, lead in enumerate(leads_list, start=1):
        lead_options[f"#{idx} - {lead.get('name')} ({lead.get('company')})"] = lead

    c1, c2 = st.columns([1.1, 1.2], gap="large")

    with c1:
        st.markdown("### 🎯 Outreach Persona & Context")
        selected_label = st.selectbox("📌 Select Lead from Pipeline:", list(lead_options.keys()))
        selected_lead = lead_options[selected_label]

        default_name = selected_lead.get("name", "") if selected_lead else ""
        default_comp = selected_lead.get("company", "") if selected_lead else ""
        default_ind = selected_lead.get("industry", "") if selected_lead else ""

        with st.form("outreach_form"):
            ca, cb = st.columns(2)
            with ca:
                name = st.text_input("Prospect Name *", value=default_name, placeholder="e.g. Alex Morgan")
            with cb:
                company = st.text_input("Company Name *", value=default_comp, placeholder="e.g. Snowflake")

            industry = st.text_input("Industry", value=default_ind, placeholder="e.g. Cloud Security")
            channel = st.selectbox("Format", ["Cold Email", "LinkedIn InMail", "Follow-up Email", "Cold Call Script"])
            tone = st.selectbox("Tone", ["Professional & Persuasive", "Casual & Friendly", "Urgent & Direct", "Value & ROI-Driven"])
            value_prop = st.text_area("Your Core Value Prop / Offer", placeholder="e.g. We automate B2B qualification and save reps 8 hours/week.", height=85)

            gen_btn = st.form_submit_button("✨ Generate AI Copy", type="primary", use_container_width=True)

    with c2:
        st.markdown("### 📝 Generated Copy Workbench")

        if gen_btn:
            if not name or not company:
                st.error("Contact Name and Company Name are required.")
            else:
                with st.spinner(f"Drafting tailored {channel.lower()}..."):
                    try:
                        payload = {
                            "name": name, "company": company, "industry": industry or "General",
                            "channel": channel, "tone": tone, "value_prop": value_prop
                        }
                        res = requests.post(f"{API_URL}/generate-outreach", params={"user_id": user_id}, json=payload, timeout=20)
                        if res.status_code == 200:
                            data = res.json()
                            st.session_state["outreach_result"] = {
                                "subject": data.get("subject", ""),
                                "body": data.get("body", ""),
                                "channel": channel,
                                "name": name,
                                "company": company,
                                "lead_id": selected_lead.get("id") if selected_lead else None
                            }
                            st.toast("Copy generated successfully!", icon="🎉")
                    except Exception as ex:
                        st.error(f"Error: {ex}")

        result = st.session_state.get("outreach_result")
        if result:
            st.caption(f"Channel Format: **{result.get('channel')}**")
            subj_val = st.text_input("Subject Line", value=result.get("subject", ""), key="out_subj")
            body_val = st.text_area("Message Body", value=result.get("body", ""), height=260, key="out_body")

            b1, b2 = st.columns(2)
            with b1:
                st.download_button(
                    "📥 Download Copy (.txt)",
                    data=f"Subject: {subj_val}\n\n{body_val}",
                    file_name=f"Outreach_{result.get('name')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            with b2:
                lead_id = result.get("lead_id")
                if lead_id:
                    if st.button("🚀 Mark Lead as 'Contacted'", type="secondary", use_container_width=True):
                        requests.put(f"{API_URL}/leads/{lead_id}", json={"status": "Contacted"}, timeout=6)
                        st.toast(f"{result.get('name')} marked as Contacted!", icon="✅")
                else:
                    st.button("📋 Ready to Send", use_container_width=True, disabled=True)
        else:
            st.markdown("""
            <div style="background: rgba(255, 255, 255, 0.02); border: 1px dashed rgba(255, 255, 255, 0.15); border-radius: 16px; padding: 45px 20px; text-align: center; color: #94A3B8;">
                👈 Select a prospect and generate copy to edit, download, and advance pipeline stage.
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    show()