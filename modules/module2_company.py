import os

import streamlit as st
import requests
from components.theme import load_theme

load_theme()

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")





def show():

    st.markdown("""
<div class="page-header">
    <div class="page-tag">AI LEAD SCORING</div>
    <div class="page-title">Lead Score Prediction</div>
    <div class="page-subtitle">
        Evaluate lead quality using AI-powered scoring.
    </div>
</div>
""", unsafe_allow_html=True)
    

    st.info(
    "🎯 Enter lead details to predict conversion probability and sales priority."
)

    # ---------- Form ----------
    with st.container( key="analyze_form"):

        company = st.text_input("Company Name", placeholder="e.g. Microsoft")
        website = st.text_input("Website", placeholder="https://www.microsoft.com")
        industry = st.selectbox(
            "Industry",
            ["Technology", "Healthcare", "Finance", "Education",
             "Retail", "Manufacturing", "Other"],
        )

        


        
        if st.button("🚀 Analyze Company", use_container_width=True):

            if company.strip() == "":
                st.warning("Please enter a company name.")
            else:
                try:
                    with st.spinner("🤖 AI is analyzing the company. Please wait..."):
                        response = requests.post(
                            f"{API_URL}/analyze-company",
                            json={
                              "company": company,
                              "website": website,
                              "industry": industry
                            },
                            timeout=60,
                        )

                    if response.status_code == 200:
                        result = response.json()
                        st.success("✅ Analysis Completed Successfully")
                        st.divider()

                        # ---------- Top Metrics ----------
                        col1, col2 = st.columns(2)

                        with col1:
                            st.metric("🏢 Company", result.get("company", company))
                            st.metric("🏭 Industry", result.get("industry", "N/A"))

                        with col2:
                            st.metric("🎯 Lead Score", f"{result.get('lead_score', 0)}%")
                            st.progress(result.get("lead_score", 0) / 100)
                            st.metric("⭐ Grade", result.get("grade", "N/A"))

                        st.divider()

                        # ---------- Summary ----------
                        st.markdown("### 📝 Company Summary")
                        st.write(result.get("company_summary", "Not Available"))

                        st.markdown("### 💼 Sales Opportunity")
                        st.success(result.get(
                            "sales_opportunity",
                            "No sales opportunity available."
                        ))

                        st.markdown("### 🚀 Recommended Sales Approach")
                        st.info(result.get(
                            "recommended_sales_approach",
                            "No recommendation available."
                        ))
                    else:
                        st.error("Failed to analyze company. Please try again.")
                except requests.exceptions.ConnectionError:
                    # Demo fallback when no backend is running yet
                    st.success("Analysis Completed Successfully ✅")
                    st.caption(f"⚠️ Showing demo data — couldn't reach the API at `{API_URL}`.")
                    st.divider()

                    col1, col2, col3 = st.columns(3)
                    c1.metric("Lead Score","91%")
                    c2.metric("Grade","A")
                    c3.metric("Priority","High")

                    st.subheader("Company Overview")
                    st.info(
                        "This company operates in the Technology industry and has a strong global market presence with continuous growth."
                    )

                    st.subheader("🤖 AI Insights")
                    
                except requests.exceptions.Timeout:
                    st.error("The request timed out — the server took too long to respond.")
                except Exception as e:
                    st.error(f"Something went wrong: {e}")


if __name__ == "__main__":
    st.set_page_config(page_title="Analyze Company", page_icon="🔎", layout="wide")
    show()