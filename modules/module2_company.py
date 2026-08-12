import os
import requests
import streamlit as st

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")


def show():
    st.markdown("## 🏢 Company Intelligence & Prospect Analysis")
    st.caption("Perform AI-driven research and deep analysis on targeted company profiles.")

    # ✅ SAFE CODE (Handles None values, empty dicts, or missing keys)
    user_data = st.session_state.get("user") or {}
    user_id = user_data.get("id", 1) if isinstance(user_data, dict) else st.session_state.get("user_id", 1)

    col_form, col_result = st.columns([1, 1.2], gap="large")

    with col_form:
        st.markdown("### 🔍 Analyze Company Profile")

        with st.form("company_analysis_form", clear_on_submit=False):
            company_name = st.text_input(
                "Company Name *",
                placeholder="e.g. Acme Corp or Stripe",
            ).strip()

            website = st.text_input(
                "Website URL (Optional)",
                placeholder="e.g. https://stripe.com",
            ).strip()

            industry = st.text_input(
                "Industry Focus",
                placeholder="e.g. Fintech, Healthcare",
            ).strip()

            submit_btn = st.form_submit_button("🤖 Analyze Company with AI", type="primary")

        if submit_btn:
            if not company_name:
                st.error("Please enter a Company Name.")
            else:
                with st.spinner(f"Analyzing research profile for '{company_name}'..."):
                    payload = {
                        "company": company_name,
                        "website": website,
                        "industry": industry,
                    }
                    try:
                        res = requests.post(
                            f"{API_URL}/analyze-company",
                            params={"user_id": user_id},
                            json=payload,
                            timeout=25,
                        )
                        if res.status_code == 200:
                            st.session_state["company_result"] = res.json()
                            st.success("Analysis generated & saved!")
                        else:
                            st.error(f"API Error {res.status_code}: {res.text}")
                    except Exception as e:
                        st.error(f"Error connecting to API server: {e}")

    with col_result:
        st.markdown("### 📊 AI Intelligence Output")

        result = st.session_state.get("company_result")

        if result:
            score = result.get("lead_score", 0)
            grade = result.get("grade", "N/A")
            target_company = result.get("company", company_name)
            target_industry = result.get("industry", "N/A")

            st.subheader(f"🏢 {target_company}")
            st.caption(f"Industry: {target_industry}")

            m1, m2 = st.columns(2)
            with m1:
                st.metric(label="Propensity Score", value=f"{score} / 100")
            with m2:
                st.metric(label="Opportunity Grade", value=f"Grade {grade}")

            st.divider()

            st.markdown("#### 📝 Executive Summary")
            st.info(result.get("company_summary", "No summary available."))

            st.markdown("#### 🎯 Identified Sales Opportunity & Pain Points")
            st.write(result.get("sales_opportunity", "No specific opportunities identified."))

            st.markdown("#### 🚀 Recommended Sales Approach")
            st.success(result.get("recommended_sales_approach", "Standard introductory outreach."))

        else:
            st.info("👈 Fill out the form on the left and click **Analyze** to generate company insights.")


if __name__ == "__main__":
    show()