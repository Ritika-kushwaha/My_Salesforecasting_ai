import os
import requests
import streamlit as st
from components.theme import load_theme

load_theme()

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")


def show():
    # 1. Header Section
    st.markdown("""
        <div style="margin-bottom: 25px;">
            <div style="color: #6366f1; font-size: 12px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase;">
                AI Lead Scoring
            </div>
            <h1 style="font-size: 28px; font-weight: 800; color: #ffffff; margin-top: 4px;">
                🎯 Lead Scoring & Recommendation Engine
            </h1>
            <p style="color: #94a3b8; font-size: 14px;">
                Predict conversion probability, calculate lead scores, and generate AI next steps.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # 2. Check User Session
    user_id = st.session_state.get("user", {}).get("id")
    if not user_id:
        st.warning("⚠️ User session not found. Please log in again.")
        st.stop()

    st.info("🎯 Enter lead details below to run Gemini AI score prediction and priority ranking.")

    # 3. Form Layout
    with st.form("lead_score_form"):
        company = st.text_input("Company Name *", placeholder="e.g. Google")

        col1, col2 = st.columns(2)
        with col1:
            industry = st.selectbox(
                "Industry",
                ["Technology", "Finance", "Healthcare", "Education", "Retail", "Manufacturing", "Other"],
            )
            company_size = st.selectbox("Company Size", ["1-50", "50-200", "200-1000", "1000+"])

        with col2:
            revenue = st.selectbox("Annual Revenue", ["< $1M", "$1M - $10M", "$10M - $100M", "$100M+"])
            budget = st.selectbox("Estimated Budget", ["Low", "Medium", "High"])

        decision = st.radio("Decision Maker Identified?", ["Yes", "No"], horizontal=True)

        st.write("")
        submitted = st.form_submit_button("🚀 Predict Lead Score", type="primary", use_container_width=True)

    # 4. Form Action
    if submitted:
        if not company.strip():
            st.warning("⚠️ Please enter a Company Name.")
            return

        try:
            with st.spinner("🤖 AI is evaluating lead conversion probability..."):
                response = requests.post(
                    f"{API_URL}/lead-score",
                    params={"user_id": user_id},
                    json={
                        "company": company.strip(),
                        "industry": industry,
                        "company_size": company_size,
                        "revenue": revenue,
                        "budget": budget,
                        "decision_maker": decision,
                    },
                    timeout=25,
                )

            if response.status_code != 200:
                st.error(f"Unable to generate lead score (Error {response.status_code}).")
                return

            result = response.json()

            st.success("✅ Lead Evaluation Completed")
            st.balloons()

            # KPI Cards
            score = result.get("lead_score", 0)
            
            st.markdown("<br>", unsafe_allow_html=True)
            k1, k2, k3, k4 = st.columns(4)
            with k1:
                st.metric("🎯 Lead Score", f"{score}%")
            with k2:
                st.metric("⭐ Grade", result.get("grade", "N/A"))
            with k3:
                st.metric("🔥 Priority", result.get("priority", "N/A"))
            with k4:
                st.metric("📈 Conversion Prob.", result.get("conversion_probability", "0%"))

            st.write("")
            st.progress(score / 100.0 if score <= 100 else 1.0)
            st.divider()

            # Analysis Sections
            c_left, c_right = st.columns([1, 1])

            with c_left:
                st.markdown("### 🏢 Company Summary")
                st.info(result.get("company_summary", "No summary available."))

                st.markdown("### 💼 Sales Opportunity")
                st.success(result.get("sales_opportunity", "No details available."))

            with c_right:
                st.markdown("### 🤖 AI Evaluation Reasons")
                reasons = result.get("reasons", [])
                if reasons:
                    for reason in reasons:
                        st.markdown(f"✅ {reason}")
                else:
                    st.caption("No specific reasons returned.")

                st.markdown("### 🚀 Recommended Next Action")
                st.markdown(
                    f"""
                    <div style="background: #181a26; border: 1px solid #26293b; padding: 16px; border-radius: 10px; color: #10b981; font-weight: 600;">
                        👉 {result.get('next_action', 'Contact decision maker.')}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        except requests.exceptions.ConnectionError:
            st.error(f"Cannot connect to backend API at `{API_URL}`.")
        except requests.exceptions.Timeout:
            st.error("Request timed out waiting for AI model response.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    st.set_page_config(page_title="Lead Scoring", page_icon="🎯", layout="wide")
    show()