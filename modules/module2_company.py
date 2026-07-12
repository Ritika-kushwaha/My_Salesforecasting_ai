import os
import textwrap
import streamlit as st
import requests

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")

# =========================================================
# DESIGN TOKENS  ·  same transparent / black-border theme as Add Lead
# =========================================================
PANEL       = "transparent"
BORDER      = "#000000"
TEXT        = "#111827"
TEXT_DIM    = "#4B5563"
BLUE        = "#4291B6"


def load_custom_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {{ font-family:'Inter', sans-serif; }}

    /* Scoped to .main only — leaves the sidebar and Streamlit's own
       toolbar (Rerun/Deploy/menu) untouched. */
    .main, .main p, .main span, .main li, .main label {{
        color: {TEXT};
    }}

    .block-container {{ padding-top: 4rem !important; }}

    .console-eyebrow {{
        display:flex; align-items:center; gap:8px;
        font-family:'JetBrains Mono', monospace;
        font-size:12px; letter-spacing:2px; font-weight:600;
        color:{BLUE}; text-transform:uppercase; margin-bottom:10px;
    }}
    .console-title {{
        font-size:clamp(28px, 6vw, 40px); font-weight:700; color:{TEXT};
        margin:0 0 6px 0; letter-spacing:-0.5px;
    }}
    .console-sub {{
        font-size:14px; color:{TEXT_DIM}; margin:0 0 20px 0;
    }}

    /* ---------------- Form container ---------------- */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background:{PANEL} !important;
        border:1.5px solid {BORDER} !important;
        border-radius:12px !important;
    }}

    /* Field labels */
    label {{
        color:{TEXT} !important;
        font-weight:600 !important;
    }}
    .stTextInput label, .stSelectbox label {{
        font-family:'JetBrains Mono', monospace !important;
        font-size:11px !important; font-weight:700 !important;
        letter-spacing:1.5px !important; text-transform:uppercase !important;
        color:{TEXT_DIM} !important;
    }}

    .stTextInput input,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
        background:{PANEL} !important;
        border:1.5px solid {BORDER} !important;
        border-radius:8px !important;
        color:white !important;
    }}
    .stTextInput input:focus {{
        color:white !important;
        border-color:{BORDER} !important;
        box-shadow:0 0 0 2px rgba(0,0,0,0.12) !important;
    }}
    .stTextInput input::placeholder {{ color:#6B7280 !important; }}
    div[data-testid="stSelectbox"] svg {{ fill:#ffffff !important; }}

    /* Info box */
    div[data-testid="stAlertContainer"] {{
        background:transparent blue !important;
        border:1.5px solid light blue !important;
        border-radius:10px !important;
    }}
    div[data-testid="stAlertContainer"] p {{ color:{TEXT} !important; }}

    /* Metrics */
    [data-testid="stMetricValue"] {{ color:{TEXT} !important; }}
    [data-testid="stMetricLabel"] {{ color:{TEXT_DIM} !important; }}

    /* Buttons — kept solid; a fully transparent button has no
       visible click target, so this is a deliberate exception
       to the "everything transparent" rule. */
    .stButton > button {{
        background:#111827 !important; color:#FFFFFF !important;
        border:1.5px solid {BORDER} !important;
        border-radius:10px; height:45px; padding:0 20px;
        font-size:16px; font-weight:600;
    }}
    .stButton > button:hover {{
        background:{PANEL} !important; color:{TEXT} !important;
        border:1.5px solid {BORDER} !important;
    }}
    </style>
    """, unsafe_allow_html=True)


def show():
    load_custom_css()

    st.markdown(textwrap.dedent(f"""
    <div class="console-eyebrow">COMPANY INTELLIGENCE &middot; AI ANALYSIS</div>
    <div class="console-title">Analyze Company</div>
    <div class="console-sub">Get AI-powered insights about a company.</div>
    """).strip(), unsafe_allow_html=True)

    st.info(
        "🤖 AI will analyze the company's industry, market presence, business size, and provide intelligent sales insights."
    )

    # ---------- Form ----------
    with st.container(border=True, key="analyze_form"):

        company = st.text_input("Company Name", placeholder="e.g. Microsoft")
        website = st.text_input("Website", placeholder="https://www.microsoft.com")
        industry = st.selectbox(
            "Industry",
            ["Technology", "Healthcare", "Finance", "Education",
             "Retail", "Manufacturing", "Other"],
        )

        st.markdown("""
        <style>
        div.st-key-analyze_form {
            border: 1.5px solid #000000 !important;
            border-radius: 12px !important;
        }
        </style>
        """, unsafe_allow_html=True)


        st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

        if st.button("Analyze Company", use_container_width=True):

            if company.strip() == "":
                st.warning("Please enter a company name.")
            else:
                try:
                    with st.spinner("Analyzing company…"):
                        response = requests.post(
                            f"{API_URL}/analyze-company",
                            json={"company": company, "website": website, "industry": industry},
                            timeout=8,
                        )

                    if response.status_code == 200:
                        data = response.json()

                        st.success("Analysis Completed Successfully ✅")
                        st.divider()

                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Company Size", data.get("company_size", "Unknown"))
                            st.metric("Revenue", data.get("revenue", "Unknown"))
                        with col2:
                            st.metric("👥 Employees", data.get("employees", "Unknown"))
                            st.metric("📍 Headquarters", data.get("headquarters", "Unknown"))

                        st.subheader("🤖 AI Summary")
                        st.info(data.get("summary", "No summary available."))

                    else:
                        st.error(f"Server returned an error ({response.status_code}): {response.text}")

                except requests.exceptions.ConnectionError:
                    # Demo fallback when no backend is running yet
                    st.success("Analysis Completed Successfully ✅")
                    st.caption(f"⚠️ Showing demo data — couldn't reach the API at `{API_URL}`.")
                    st.divider()

                    col1, col2, col3 = st.columns(3)
                    col1.metric("Employees", "12,500")
                    col2.metric("Revenue", "$5.4B")
                    col3.metric("Growth", "18%")

                    st.subheader("Company Overview")
                    st.info(
                        "This company operates in the Technology industry and has a strong global market presence with continuous growth."
                    )

                    st.subheader("🤖 AI Insights")
                    st.markdown("""
- Strong digital presence.
- Active on LinkedIn and major business platforms.
- High B2B sales potential.
- Excellent candidate for enterprise sales.
- Recommended for personalized AI email outreach.
                    """)

                except requests.exceptions.Timeout:
                    st.error("The request timed out — the server took too long to respond.")
                except Exception as e:
                    st.error(f"Something went wrong: {e}")


if __name__ == "__main__":
    st.set_page_config(page_title="Analyze Company", page_icon="🔎", layout="wide")
    show()