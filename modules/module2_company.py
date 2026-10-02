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

        .saas-kpi-card {
            background: rgba(15, 23, 42, 0.75);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 18px;
            padding: 22px 20px;
            backdrop-filter: blur(16px);
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.4);
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        .saas-kpi-card:hover {
            transform: translateY(-3px);
            border-color: rgba(99, 102, 241, 0.4);
            box-shadow: 0 15px 35px -8px rgba(99, 102, 241, 0.25);
        }
        .saas-kpi-title {
            font-size: 0.78rem;
            font-weight: 700;
            color: #94A3B8;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            margin-bottom: 8px;
        }
        .saas-kpi-val {
            font-size: 2.1rem;
            font-weight: 800;
            color: #FFFFFF;
            letter-spacing: -0.03em;
            line-height: 1.1;
        }
        .saas-badge-green {
            background: rgba(16, 185, 129, 0.15);
            color: #10B981;
            border: 1px solid rgba(16, 185, 129, 0.3);
            padding: 2px 8px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 700;
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
                🏢 GEMINI DEEP RESEARCH
            </div>
            <h1 style="font-size: 2.1rem; font-weight: 800; margin: 0; letter-spacing: -0.03em;">Company Intelligence & Account Research</h1>
            <p style="color: #94A3B8; font-size: 0.92rem; margin-top: 4px;">Run automated ICP evaluation, identify pain points, and synthesize account dossiers.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    user_id = get_current_user_id()

    with st.container():
        st.markdown('<div class="panel-box">', unsafe_allow_html=True)
        st.markdown("<h4 style='margin: 0 0 14px 0; font-weight: 700;'>🔍 Target Account Parameters</h4>", unsafe_allow_html=True)

        with st.form("company_research_form"):
            col1, col2 = st.columns(2)
            with col1:
                company_name = st.text_input("Company Name *", placeholder="e.g. Snowflake, Datadog, Stripe")
                website = st.text_input("Website (Optional)", placeholder="https://company.com")
            with col2:
                industry = st.selectbox(
                    "Industry Sector",
                    ["Technology & SaaS", "Financial Services", "Healthcare & Biotech", "E-commerce & Retail", "Manufacturing", "Other"]
                )

            submit = st.form_submit_button("⚡ Run Gemini Account Research", type="primary", use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    if submit:
        if not company_name:
            st.error("Please provide a valid Company Name.")
        else:
            with st.spinner(f"Analyzing {company_name} across B2B market signals..."):
                try:
                    payload = {"company": company_name, "website": website, "industry": industry}
                    res = requests.post(f"{API_URL}/analyze-company", params={"user_id": user_id}, json=payload, timeout=25)

                    if res.status_code == 200:
                        data = res.json()
                        st.toast("Intelligence profile generated!", icon="🎉")

                        m1, m2, m3 = st.columns(3)
                        with m1:
                            st.markdown(f"""
                            <div class="saas-kpi-card">
                                <div class="saas-kpi-title">ICP FIT SCORE</div>
                                <div class="saas-kpi-val" style="color: #6366F1;">{data.get('lead_score', 80)} <span style="font-size: 0.85rem; color: #94A3B8;">/ 100</span></div>
                                <div style="margin-top: 8px;"><span class="saas-badge-green">High Intent Fit</span></div>
                            </div>
                            """, unsafe_allow_html=True)
                        with m2:
                            st.markdown(f"""
                            <div class="saas-kpi-card">
                                <div class="saas-kpi-title">OPPORTUNITY GRADE</div>
                                <div class="saas-kpi-val" style="color: #10B981;">Grade {data.get('grade', 'A')}</div>
                                <div style="margin-top: 8px;"><span class="saas-badge-green">Fast Track</span></div>
                            </div>
                            """, unsafe_allow_html=True)
                        with m3:
                            st.markdown(f"""
                            <div class="saas-kpi-card">
                                <div class="saas-kpi-title">TARGET VERTICAL</div>
                                <div class="saas-kpi-val" style="font-size: 1.4rem; color: #A855F7; margin-top: 6px;">{data.get('industry', industry)}</div>
                            </div>
                            """, unsafe_allow_html=True)

                        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

                        with st.expander("🏢 Executive Overview & Profile", expanded=True):
                            st.write(data.get("company_summary", "Summary not available."))

                        with st.expander("🎯 Identified Sales Opportunities & Pain Points", expanded=True):
                            st.write(data.get("sales_opportunity", "No specific opportunities identified."))

                        with st.expander("🚀 Recommended Outreach Angle", expanded=True):
                            st.info(data.get("recommended_sales_approach", "Reach out with tailored ROI value."))

                    else:
                        st.error(f"Server error: {res.text}")
                except Exception as ex:
                    st.error(f"Backend connection error: {ex}")


if __name__ == "__main__":
    show()