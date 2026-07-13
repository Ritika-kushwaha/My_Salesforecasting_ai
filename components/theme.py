import streamlit as st

# ---------- COLORS ----------

BG = "#F8FAFC"

CARD = "rgba(255,255,255,0.78)"

CARD_LIGHT = "rgba(255,255,255,0.55)"

BORDER = "#E5E7EB"

TEXT = "#111827"

TEXT_LIGHT = "#748098"

PRIMARY = "#4C8DFF"

SUCCESS = "#22C55E"

WARNING = "#F59E0B"

ERROR = "#EF4444"

PURPLE = "#8B5CF6"

CYAN = "#06B6D4"


def load_theme():
    st.markdown(
    f"""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html,
body,
[class*="css"] {{
    font-family: Inter;
}}

.stApp {{
    background: linear-gradient(
        135deg,
        #EEF5FF,
        #DCEBFF,
        #CCE0FF
    );
}}

.block-container {{
    padding-top:2rem;
    padding-left:2rem;
    padding-right:2rem;
}}

</style>
""",
unsafe_allow_html=True
)