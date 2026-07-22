import os

import streamlit as st
import requests
from components.theme import load_theme

load_theme()

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")

def show():

    st.markdown("""
    <style>

    .page-tag{
        display:inline-block;
        padding:10px 18px;
        background:rgba(59,130,246,.12);
        border-radius:999px;
        color:#3B82F6 !important;
        font-size:14px;
        font-weight:700;
        letter-spacing:2px;
        text-transform:uppercase;
        margin-bottom:18px;
    }

    .page-title{
        color:#111827 !important;
        font-size:58px;
        font-weight:800;
        margin-bottom:12px;
    }

    .page-subtitle{
        color:#4B5563 !important;
        font-size:20px;
        line-height:1.8;
        max-width:900px;
        margin-bottom:30px;
    }
    /* ---------- Form Container ---------- */
    /* Target Streamlit's actual form wrapper instead of a custom div */
    div[data-testid="stForm"]{
        border:2px solid black !important;
        border-radius:15px !important;
        padding:25px !important;
        margin-top:10px !important;
        background:transparent !important;
    }

    /* Labels */
    .stTextInput label,
    .stSelectbox label{
        font-family:'JetBrains Mono', monospace !important;
        font-size:11px !important;
        font-weight:700 !important;
        letter-spacing:2px !important;
        text-transform:uppercase !important;
        color:#4C535D !important;
    }

    /* Input Boxes */
    .stTextInput input,
    .stSelectbox div[data-baseweb="select"] > div{
        border:1.5px solid #000 !important;
        border-radius:10px !important;
        background:transparent !important;
        color:#111827 !important;
    }

    /* Placeholder */
    .stTextInput input::placeholder{
        color:#6B7280 !important;
    }

    /* Button */
    .stFormSubmitButton>button{
        width:220px !important;
        height:52px !important;
        background:#111827 !important;
        color:white !important;
        border-radius:10px !important;
        border:none !important;
    }

    .stFormSubmitButton>button:hover{
        background:transparent !important; color:#111827 !important;
        border:1px solid #111827 !important;
    }

    </style>
    """, unsafe_allow_html=True)

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

    st.markdown("""
    <style>           

    /* TextInput labels */
    .stTextInput label p{
        color:#111827 !important;
        font-weight:600 !important;
    }

    /* Selectbox labels */
    .stSelectbox label p{
        color:#111827 !important;
        font-weight:600 !important;
    }

    /* TextArea labels */
    .stTextArea label p{
        color:#111827 !important;
        font-weight:600 !important;
    }

    </style>
    """, unsafe_allow_html=True)

    
    # ---------- Form ----------
    
    with st.form( key="analyze_form"):

        company = st.text_input("Company Name", placeholder="e.g. Microsoft")
        website = st.text_input("Website", placeholder="https://www.microsoft.com")
        industry = st.selectbox(
            "Industry",
            ["Technology", "Healthcare", "Finance", "Education",
             "Retail", "Manufacturing", "Other"],
        )

        
        submitted = st.form_submit_button("Analyze Company")


        if submitted:

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
                            st.metric("Company", result.get("company", company))
                            st.metric("Industry", result.get("industry", "N/A"))

                        with col2:
                            st.metric("Lead Score", f"{result.get('lead_score', 0)}%")
                            st.progress(result.get("lead_score", 0) / 100)
                            st.metric("Grade", result.get("grade", "N/A"))

                        st.divider()

                        # ---------- Summary ----------
                        st.markdown("### Company Summary")
                        st.write(result.get("company_summary", "Not Available"))

                        st.markdown("### Sales Opportunity")
                        st.success(result.get(
                            "sales_opportunity",
                            "No sales opportunity available."
                        ))

                        st.markdown("### Recommended Sales Approach")
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
                    col1.metric("Lead Score","91%")
                    col2.metric("Grade","A")
                    col3.metric("Priority","High")

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