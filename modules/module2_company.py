import os
import requests
import streamlit as st
from components.theme import load_theme

load_theme()

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")


def show():
    # 1. Page Header Section
    st.markdown("""
        <div style="margin-bottom: 25px;">
            <div style="color: #6366f1; font-size: 12px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase;">
                Company Intelligence
            </div>
            <h1 style="font-size: 28px; font-weight: 800; color: #ffffff; margin-top: 4px;">
                🔎 Analyze Company
            </h1>
            <p style="color: #94a3b8; font-size: 14px;">
                Analyze target accounts with AI to identify sales opportunities and recommend tailored outreach strategies.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # 2. Check User Session
    user_id = st.session_state.get("user", {}).get("id")
    if not user_id:
        st.warning("⚠️ User session missing. Please log in again.")
        st.stop()

    # 3. Input Form
    with st.container():
        company = st.text_input("Company Name *", placeholder="e.g. Microsoft")
        
        c1, c2 = st.columns(2)
        with c1:
            website = st.text_input("Website", placeholder="https://www.microsoft.com")
        with c2:
            industry = st.selectbox(
                "Industry",
                ["Technology", "Healthcare", "Finance", "Education", "Retail", "Manufacturing", "Other"],
            )

        st.write("")
        analyze_btn = st.button("🚀 Analyze Company with AI", type="primary", use_container_width=True)

    # 4. Form Action
    if analyze_btn:
        if not company.strip():
            st.warning("⚠️ Please enter a Company Name to analyze.")
        else:
            payload = {
                "company": company.strip(),
                "website": website.strip() if website else "",
                "industry": industry,
            }

            try:
                with st.spinner("🤖 AI is analyzing account profile and sales opportunity..."):
                    response = requests.post(
                        f"{API_URL}/analyze-company",
                        params={"user_id": user_id},
                        json=payload,
                        timeout=25,
                    )

                if response.status_code == 200:
                    result = response.json()
                    st.success("✅ Analysis Completed Successfully")
                    st.divider()

                    # Metrics Overview
                    col_m1, col_m2, col_m3 = st.columns(3)
                    with col_m1:
                        st.metric("🏢 Company", result.get("company", company))
                        st.metric("🏭 Industry", result.get("industry", industry))
                    with col_m2:
                        score = result.get("lead_score", 0)
                        st.metric("🎯 Lead Score", f"{score}%")
                        st.progress(score / 100.0 if score <= 100 else 1.0)
                    with col_m3:
                        st.metric("⭐ Grade", result.get("grade", "N/A"))

                    st.divider()

                    # Detailed Insights Cards
                    st.markdown("### 📝 Account Summary")
                    st.info(result.get("company_summary", "Summary not available."))

                    st.markdown("### 💼 Sales Opportunity")
                    st.success(result.get("sales_opportunity", "Opportunity details not available."))

                    st.markdown("### 🚀 Recommended Approach")
                    st.markdown(
                        f"""
                        <div style="background: #181a26; border: 1px solid #26293b; padding: 18px; border-radius: 12px; color: #cbd5e1;">
                            {result.get('recommended_sales_approach', 'No specific approach generated.')}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                else:
                    st.error(f"Error {response.status_code}: {response.text}")

            except requests.exceptions.ConnectionError:
                st.error(f"Cannot connect to API at `{API_URL}`. Please verify the FastAPI server is running.")
            except requests.exceptions.Timeout:
                st.error("Request timed out. The AI model took longer than expected to process.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    st.set_page_config(page_title="Analyze Company", page_icon="🔎", layout="wide")
    show()