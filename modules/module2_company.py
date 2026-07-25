<<<<<<< Updated upstream
import os

import streamlit as st
import requests
from components.theme import load_theme

load_theme()
=======
import streamlit as st
import requests
import os
>>>>>>> Stashed changes

load_theme()

<<<<<<< Updated upstream



    st.html("""
    <div style="margin-top:10px; margin-bottom:35px;">

        <div style="
            display:inline-block;
            padding:6px 14px;
            background:rgba(37,99,235,.12);
            color:#2563EB;
            border-radius:30px;
            font-size:13px;
            font-weight:700;
            letter-spacing:1px;
            text-transform:uppercase;
            margin-bottom:14px;
            margin-top:-100rem !important;
        ">
            COMPANY ANALYSIS
        </div>

        <h1 style="
            font-size:42px;
            font-weight:800;
            color:#111827;
            margin:14px 0 12px 0;
            line-height:1.1;
        ">
            Analyze Company
        </h1>

        <p style="
            font-size:17px;
            color:#4B5563;
            line-height:1.6;
            max-width:760px;
            margin:0;
        ">
            Analyze a company's profile using AI to generate business insights,
            identify sales opportunities, and recommend the best sales approach.
        </p>

    </div>
    """)

    st.markdown("""
    <div style="
    background:rgba(255,255,255,.45);
    border-left:6px solid #3B82F6;
    padding:22px 28px;
    border-radius:18px;
    margin-bottom:30px;
    margin-top:-30px;
    ">

    <div style="
    font-size:18px;
    font-weight:700;
    color:#374151;
    margin-bottom:8px;
    ">
    Quick Tip
    </div>

    <div style="
    font-size:16px;
    line-height:1.8;
    color:#4B5563;
    ">
    Enter the <b>Company Name</b>, <b>Website</b>, and <b>Industry</b>, then click
    <b>Analyze Company</b>. AI will evaluate the company profile, estimate lead quality,
    identify business opportunities, and recommend the most suitable sales strategy.
    </div>

    </div>
    """, unsafe_allow_html=True)

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

    </style>
    """, unsafe_allow_html=True)

    
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
=======
def show():
    st.markdown("## 🏢 Company Intelligence & Prospect Analysis")
    st.caption("Perform AI-driven research on targeted company profiles.")

    user_id = st.session_state.get("user", {}).get("id", 1)

    c1, c2 = st.columns([1, 1.2])

    with c1:
        st.markdown("### 🔍 Analyze Company Profile")
        
        with st.form("company_analysis_form"):
            company_name = st.text_input("Company Name *", placeholder="e.g. Acme Corp").strip()
            website = st.text_input("Website URL", placeholder="e.g. https://acme.com").strip()
            industry = st.text_input("Industry", placeholder="e.g. Enterprise Software").strip()
            
            submit_btn = st.form_submit_button("🤖 Analyze & Generate Insights", type="primary", use_container_width=True)

        if submit_btn:
            # Frontend Input Checks
            if not company_name:
                st.warning("⚠️ Company Name is required.")
            elif len(company_name) < 2:
                st.warning("⚠️ Please enter a valid Company Name.")
            else:
                with st.spinner("Analyzing company profile with Gemini AI..."):
                    try:
                        res = requests.post(
                            f"{API_URL}/analyze-company",
                            params={"user_id": user_id},
                            json={
                                "company": company_name,
                                "website": website,
                                "industry": industry,
                            },
                            timeout=20,
                        )
                        if res.status_code == 200:
                            st.session_state["company_result"] = res.json()
                            st.success("Analysis complete!")
                        else:
                            st.error(f"Error ({res.status_code}): {res.json().get('detail', res.text)}")
                    except Exception as e:
                        st.error(f"Connection failed: {e}")

    with c2:
        st.markdown("### 📊 AI Intelligence Output")
        result = st.session_state.get("company_result")
        
        if result:
            st.metric("Lead Score", f"{result.get('lead_score', 0)} / 100", f"Grade {result.get('grade', 'N/A')}")
            
            st.markdown("#### 📝 Business Overview")
            st.info(result.get("company_summary", "No summary available."))
            
            st.markdown("#### 🎯 Sales Opportunity")
            st.write(result.get("sales_opportunity", "N/A"))
            
            st.markdown("#### 🚀 Recommended Sales Approach")
            st.success(result.get("recommended_sales_approach", "N/A"))
        else:
            st.info("👈 Fill out the company form and click analyze to view generated insights.")
>>>>>>> Stashed changes
