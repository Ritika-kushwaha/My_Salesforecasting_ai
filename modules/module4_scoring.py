import os
import requests
import streamlit as st
from components.theme import load_theme

load_theme()

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")


def show():

    st.markdown("""
    <div class="page-header">
        <div class="page-tag">AI LEAD SCORING</div>
        <div class="page-title">Lead Scoring & Recommendation Engine</div>
        <div class="page-subtitle">
            Predict conversion probability and prioritize leads using AI.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.caption("SalesGenie AI • Lead Scoring Engine • Milestone 2")

    st.info(
        "🎯 Enter lead information below. Gemini AI will evaluate the lead quality and recommend the next sales action."
    )

    with st.form("lead_score_form"):

        company = st.text_input(
            "Company Name",
            placeholder="Google"
        )

        col1, col2 = st.columns(2)

        with col1:

            industry = st.selectbox(
                "Industry",
                [
                    "Technology",
                    "Finance",
                    "Healthcare",
                    "Education",
                    "Retail",
                    "Manufacturing",
                    "Other"
                ]
            )

            company_size = st.selectbox(
                "Company Size",
                [
                    "1-50",
                    "50-200",
                    "200-1000",
                    "1000+"
                ]
            )

        with col2:

            revenue = st.selectbox(
                "Annual Revenue",
                [
                    "< $1M",
                    "$1M - $10M",
                    "$10M - $100M",
                    "$100M+"
                ]
            )

            budget = st.selectbox(
                "Estimated Budget",
                [
                    "Low",
                    "Medium",
                    "High"
                ]
            )

        decision = st.radio(
            "Decision Maker Identified?",
            ["Yes", "No"],
            horizontal=True
        )

        submitted = st.form_submit_button(
            "🚀 Predict Lead Score",
            use_container_width=True
        )

    if submitted:

        if company.strip() == "":
            st.warning("Please enter a company name.")
            return

        try:

            with st.spinner("🤖 AI is evaluating this lead..."):

                response = requests.post(
                    f"{API_URL}/lead-score",
                    json={
                        "company": company,
                        "industry": industry,
                        "company_size": company_size,
                        "revenue": revenue,
                        "budget": budget,
                        "decision_maker": decision
                    },
                    timeout=60
                )

            if response.status_code != 200:
                st.error("Unable to generate lead score.")
                return

            result = response.json()
            

            st.success("✅ Lead Evaluation Completed")
            st.balloons()
            st.info(
    f"""
### 🤖 AI Decision

**{company}** has been classified as a **{result.get('qualification','Lead')}**
with a **{result.get('lead_score',0)}%** lead score.

Recommended Priority:
**{result.get('priority','Medium')}**
"""
)

            st.divider()
            # ---------------- KPI Cards ----------------

            col1, col2 = st.columns(2)
            with col1:
                 st.metric("🎯 Lead Score", f"{result.get('lead_score',0)}%")
            with col2:
                 st.metric("⭐ Grade", result.get("grade","N/A"))
            col3, col4 = st.columns(2)
            with col3:
                 st.metric("🔥 Priority", result.get("priority","N/A"))
            with col4:
                st.metric(
                    "📈 Conversion",
                    result.get("conversion_probability","0%")
    )

            
            st.divider()
            st.subheader("🏢 Company Summary")
            st.write(
                result.get(
                    "company_summary",
                    "No summary available."
                )
            )

            st.divider()
            st.subheader("💼 Sales Opportunity")
            st.success(
                result.get(
                    "sales_opportunity",
                    "No opportunity available."
                )
            )

            st.divider()
            st.subheader("🤖 AI Recommendation")
            st.info(
                result.get(
                    "recommended_sales_approach",
                    "No recommendation."
    )
)

            score = result.get("lead_score",0)
            if score >= 85:
                 st.success(f"🔥 Excellent Lead ({score}%)")
            elif score >= 70:
                 st.warning(f"⭐ Good Lead ({score}%)")
            else:
                 st.error(f"⚠ Low Quality Lead ({score}%)")
            st.progress(score / 100)
            st.subheader("🏆 Lead Qualification")
            st.success(
                result.get(
                    "qualification",
                    "Not Available"
                    )
                )
            st.subheader("🤖 Why did AI give this score?")

            reasons = result.get("reasons", [])

            if len(reasons):

                for reason in reasons:

                    st.markdown(f"✅ {reason}")

            else:

                st.info("No explanation available.")
            st.divider()
            st.subheader("🚀 Recommended Next Action")
            st.info(
                result.get(
                    "next_action",
                    "Follow up with the lead."
                    )
                    )

            

            st.divider()

        except requests.exceptions.ConnectionError:

            st.error("Cannot connect to FastAPI backend.")

        except requests.exceptions.Timeout:

            st.error("Request timed out.")

        except Exception as e:

            st.error(str(e))


if __name__ == "__main__":
    st.set_page_config(
        page_title="Lead Scoring",
        page_icon="🎯",
        layout="wide"
    )

    show()