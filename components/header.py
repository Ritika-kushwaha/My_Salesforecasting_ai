import streamlit as st

def page_header(title, subtitle, icon):
    st.markdown(
        f"""
<div style="
margin-bottom:30px;
">

<h1 style="
margin-bottom:0;
font-size:38px;
">
{icon} {title}
</h1>

<p style="
color:#6B7280;
font-size:18px;
margin-top:5px;
">
{subtitle}
</p>

</div>
""",
unsafe_allow_html=True
    )