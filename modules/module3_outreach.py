import os
import streamlit as st
import requests
from components.theme import load_theme

load_theme()

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")


def show():

    st.markdown("""
<div class="page-header">
    <div class="page-tag">AI OUTREACH</div>
    <div class="page-title">Generate Sales Email</div>
    <div class="page-subtitle">
        Generate personalized outreach emails using AI.
    </div>
</div>
""", unsafe_allow_html=True)

    st.info(
        "✉️ Enter lead information and SalesGenie AI will generate a personalized outreach email."
    )

    company = st.text_input(
        "Company Name",
        placeholder="Microsoft"
    )

    contact = st.text_input(
        "Contact Person",
        placeholder="Satya Nadella"
    )

    industry = st.selectbox(
        "Industry",
        [
            "Technology",
            "Healthcare",
            "Finance",
            "Education",
            "Retail",
            "Manufacturing",
            "Other"
        ]
    )

    product = st.text_input(
        "Your Product / Service",
        placeholder="SalesGenie AI"
    )

    if st.button("✉️ Generate Email", use_container_width=True):

        if company == "" or contact == "":
            st.warning("Please fill all required fields.")

        else:

            try:

                with st.spinner("Generating AI Email..."):

                    response = requests.post(
                        f"{API_URL}/generate-email",
                        json={
                            "company": company,
                            "name": contact,
                            "industry": industry,
                            "product": product
                        },
                        timeout=60
                    )

                if response.status_code == 200:

                    result = response.json()

                    st.success("Email Generated Successfully")

                    st.subheader("Generated Email")

                    st.text_area(
                        "",
                        value=result["email"],
                        height=300
                    )

                    st.download_button(
                        "📄 Download Email",
                        result["email"],
                        file_name="sales_email.txt"
                    )

                else:
                    st.error("Failed to generate email.")

            except Exception as e:
                st.error(e)


if __name__ == "__main__":
    st.set_page_config(
        page_title="AI Outreach",
        page_icon="✉️",
        layout="wide"
    )
    show()