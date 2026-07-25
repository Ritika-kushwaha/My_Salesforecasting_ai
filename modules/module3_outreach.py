import os
import pandas as pd
import requests
import streamlit as st
from components.theme import load_theme

load_theme()

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")


def show():
    # Header Section
    st.markdown("""
        <div style="margin-bottom: 25px;">
            <div style="color: #6366f1; font-size: 12px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase;">
                AI Outreach
            </div>
            <h1 style="font-size: 28px; font-weight: 800; color: #ffffff; margin-top: 4px;">
                ✉️ AI Outreach & Campaigns
            </h1>
            <p style="color: #94a3b8; font-size: 14px;">
                Generate personalized cold outreach emails and manage stored campaign history.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Check User Session
    user_id = st.session_state.get("user", {}).get("id")
    if not user_id:
        st.warning("⚠️ User session not found. Please log in again.")
        st.stop()

    tab1, tab2 = st.tabs(["✉️ Generate Email", "📜 Saved Campaigns History"])

    # ---------------- TAB 1: GENERATE EMAIL ----------------
    with tab1:
        st.info("✉️ Enter prospect details to generate a tailored outreach email.")

        with st.form("email_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                company = st.text_input("Company Name *", placeholder="e.g. Microsoft")
                industry = st.selectbox(
                    "Industry",
                    [
                        "Technology",
                        "Healthcare",
                        "Finance",
                        "Education",
                        "Retail",
                        "Manufacturing",
                        "Other",
                    ],
                )
            with c2:
                contact = st.text_input("Contact Person *", placeholder="e.g. Satya Nadella")
                product = st.text_input("Your Product / Service", placeholder="e.g. SalesGenie AI")

            st.write("")
            submit_btn = st.form_submit_button("✉️ Generate AI Email", type="primary", use_container_width=True)

        if submit_btn:
            if not company.strip() or not contact.strip():
                st.warning("⚠️ Please fill in all required fields (Company Name & Contact Person).")
            else:
                payload = {
                    "company": company.strip(),
                    "name": contact.strip(),
                    "industry": industry,
                    "product": product.strip() if product else "Our Solutions",
                }

                try:
                    with st.spinner("🤖 Crafting email and saving to database..."):
                        response = requests.post(
                            f"{API_URL}/generate-email",
                            params={"user_id": user_id},
                            json=payload,
                            timeout=25,
                        )

                    if response.status_code == 200:
                        result = response.json()
                        email_body = result.get("email", "")

                        st.success("✅ Email Generated & Saved to History!")
                        st.text_area("Generated Email Content", value=email_body, height=280)

                        st.download_button(
                            "📄 Download Email (.txt)",
                            data=email_body,
                            file_name=f"email_{company.lower().replace(' ', '_')}.txt",
                            mime="text/plain",
                        )
                    else:
                        st.error(f"Failed to generate email (Error {response.status_code}): {response.text}")

                except requests.exceptions.ConnectionError:
                    st.error(f"Cannot connect to backend server at `{API_URL}`.")
                except requests.exceptions.Timeout:
                    st.error("Request timed out waiting for AI model.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")

    # ---------------- TAB 2: SAVED CAMPAIGNS HISTORY ----------------
    with tab2:
        st.markdown("### 📜 Your Database Campaign History")

        try:
            res = requests.get(f"{API_URL}/campaigns", params={"user_id": user_id}, timeout=10)

            if res.status_code == 200:
                campaigns = res.json()
                if campaigns:
                    # Overview Table
                    df = pd.DataFrame(campaigns)
                    st.dataframe(
                        df[["id", "title", "target_industry", "status", "created_at"]],
                        use_container_width=True,
                        hide_index=True,
                    )

                    st.divider()
                    st.markdown("#### 🔍 View & Manage Saved Email")

                    col_select, col_del = st.columns([3, 1])

                    with col_select:
                        options = {f"#{c['id']} - {c['title']}": c for c in campaigns}
                        selected_key = st.selectbox("Select a campaign record:", options=list(options.keys()))
                        selected_campaign = options.get(selected_key)

                    with col_del:
                        st.write("<br>", unsafe_allow_html=True)
                        if selected_campaign:
                            if st.button("🗑️ Delete Campaign", type="secondary", use_container_width=True):
                                del_res = requests.delete(
                                    f"{API_URL}/campaigns/{selected_campaign['id']}",
                                    params={"user_id": user_id},
                                    timeout=10,
                                )
                                if del_res.status_code == 200:
                                    st.success("Deleted successfully!")
                                    st.rerun()
                                else:
                                    st.error("Could not delete record.")

                    if selected_campaign:
                        st.text_area(
                            f"Email Body ({selected_campaign.get('title')})",
                            value=selected_campaign.get("body", ""),
                            height=220,
                        )
                else:
                    st.info("No saved campaigns found in your account database yet. Generate an email above to create your first record.")
            else:
                st.error(f"Failed to load campaign records (Error {res.status_code}).")

        except Exception as e:
            st.error(f"Backend connection error: {e}")


if __name__ == "__main__":
    st.set_page_config(page_title="AI Outreach", page_icon="✉️", layout="wide")
    show()