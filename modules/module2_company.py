import os
import requests
import streamlit as st

# Backend API Endpoint URL
API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")


def show():
    st.markdown("## 🏢 Company Intelligence & Prospect Analysis")
    st.caption("Perform AI-driven research and deep analysis on targeted company profiles.")

    # Retrieve current logged-in user ID (defaults to 1)
    user_id = st.session_state.get("user", {}).get("id", 1)

    # Two-Column Layout: Form on Left, Output on Right
    col_form, col_result = st.columns([1, 1.2], gap="large")

    # -------------------------------------------------------------------
    # LEFT COLUMN: COMPANY INPUT FORM
    # -------------------------------------------------------------------
    with col_form:
        st.markdown("### 🔍 Analyze Company Profile")

        with st.form("company_analysis_form", clear_on_submit=False):
            company_name = st.text_input(
                "Company Name *",
                placeholder="e.g. Acme Corp or Stripe",
                help="Required. The target company name for AI research.",
            ).strip()

            website = st.text_input(
                "Website URL (Optional)",
                placeholder="e.g. https://acme.com",
            ).strip()

            industry = st.text_input(
                "Industry (Optional)",
                placeholder="e.g. Financial Services / Fintech",
            ).strip()

            submit_btn = st.form_submit_button(
                "🤖 Analyze & Generate Insights",
                type="primary",
                use_container_width=True,
            )

        # Form Processing Logic
        if submit_btn:
            # 1. Frontend Input Validation
            if not company_name:
                st.warning("⚠️ Please enter a valid Company Name.")
            elif len(company_name) < 2:
                st.warning("⚠️ Company Name must be at least 2 characters long.")
            else:
                with st.spinner("Analyzing company background & market data with Gemini AI..."):
                    payload = {
                        "company": company_name,
                        "website": website if website else "Not Provided",
                        "industry": industry if industry else "General Business",
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
                            st.success(" Analysis completed successfully!")
                        else:
                            error_detail = res.json().get("detail", res.text)
                            st.error(f"Analysis failed ({res.status_code}): {error_detail}")

                    except requests.exceptions.ConnectionError:
                        st.error(
                            f"Cannot connect to backend server at `{API_URL}`. "
                            "Please ensure FastAPI (Uvicorn) is running."
                        )
                    except Exception as e:
                        st.error(f"An error occurred: {e}")

    # -------------------------------------------------------------------
    # RIGHT COLUMN: AI INTELLIGENCE DISPLAY
    # -------------------------------------------------------------------
    with col_result:
        st.markdown("### 📊 AI Intelligence Output")

        result = st.session_state.get("company_result")

        if result:
            # Metric Card Overview
            score = result.get("lead_score", 0)
            grade = result.get("grade", "N/A")
            target_company = result.get("company", company_name)
            target_industry = result.get("industry", "N/A")

            st.subheader(f"🏢 {target_company}")
            st.caption(f"Industry: {target_industry}")

            # Top KPI Cards
            m1, m2 = st.columns(2)
            with m1:
                st.metric(label="Propensity Score", value=f"{score} / 100")
            with m2:
                st.metric(label="Opportunity Grade", value=f"Grade {grade}")

            st.divider()

            # Structured Insights
            st.markdown("#### 📝 Executive Summary")
            st.info(result.get("company_summary", "No summary available."))

            st.markdown("#### 🎯 Identified Sales Opportunity & Pain Points")
            st.write(result.get("sales_opportunity", "No specific opportunities identified."))

            st.markdown("#### 🚀 Recommended Sales Approach")
            st.success(result.get("recommended_sales_approach", "Standard introductory call."))

        else:
            st.info("👈 Fill out the company form on the left and click **Analyze** to generate detailed AI sales insights.")


if __name__ == "__main__":
    show()