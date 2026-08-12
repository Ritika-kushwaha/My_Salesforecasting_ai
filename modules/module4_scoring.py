import os
import pandas as pd
import requests
import streamlit as st

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")


def compute_dynamic_factors(lead):
    """Calculates factor scores dynamically using the actual attributes of the lead record."""
    size = str(lead.get("company_size", "")).strip()
    rev = str(lead.get("revenue", "")).strip()
    growth_score = 15
    if size in ["201-500", "500+"] or "$50M" in rev or "$10M" in rev:
        growth_score = 35
    elif size in ["51-200", "11-50"]:
        growth_score = 25

    ind = str(lead.get("industry", "")).strip().lower()
    industry_score = 20
    if ind in ["technology", "finance", "healthcare", "fintech", "software"]:
        industry_score = 35
    elif ind in ["retail", "manufacturing"]:
        industry_score = 25

    prio = str(lead.get("priority", "")).strip().lower()
    status = str(lead.get("status", "")).strip().lower()
    engagement_score = 15
    if prio == "high" or status in ["qualified", "proposal sent"]:
        engagement_score = 30
    elif prio == "medium":
        engagement_score = 20

    total_score = min(100, growth_score + industry_score + engagement_score)
    return growth_score, industry_score, engagement_score, total_score


def show():
    st.markdown("## 🎯 Lead Scoring & Conversion Engine")
    st.caption("AI-assisted scoring model prioritizing high-intent accounts.")

    # ✅ SAFE CODE (Handles None values, empty dicts, or missing keys)
    user_data = st.session_state.get("user") or {}
    user_id = user_data.get("id", 1) if isinstance(user_data, dict) else st.session_state.get("user_id", 1)

    leads_data = []
    try:
        res = requests.get(f"{API_URL}/leads", params={"user_id": user_id}, timeout=10)
        if res.status_code == 200:
            leads_data = res.json()
    except Exception:
        pass

    if not leads_data:
        st.info("No lead records available to score. Please register leads in Module 1.")
        return

    processed_leads = []
    for l in leads_data:
        g, i, e, tot = compute_dynamic_factors(l)
        l_copy = dict(l)
        l_copy["score"] = tot
        l_copy["growth_factor"] = g
        l_copy["industry_factor"] = i
        l_copy["engagement_factor"] = e
        l_copy["conversion_prob"] = min(98, max(15, int(tot * 0.92)))
        l_copy["tier"] = "Tier 1 (High Intent)" if tot >= 80 else ("Tier 2 (Warm)" if tot >= 60 else "Tier 3 (Nurture)")
        processed_leads.append(l_copy)

    df = pd.DataFrame(processed_leads).sort_values("score", ascending=False)

    col_selector, col_details = st.columns([1, 1.2], gap="large")

    with col_selector:
        st.markdown("### 🔍 Select Lead to Analyze")
        lead_options = {f"{r['name']} ({r['company']}) - Score: {r['score']}": r for r in processed_leads}
        selected_label = st.selectbox("Registered Prospects:", list(lead_options.keys()))
        target = lead_options[selected_label]

        st.markdown("#### 📊 Score Factor Breakdown")
        st.progress(target["score"] / 100, text=f"Overall Lead Score: {target['score']} / 100")
        st.write(f"• **Company Growth Factor:** {target['growth_factor']} / 35")
        st.write(f"• **Industry Match Factor:** {target['industry_factor']} / 35")
        st.write(f"• **Engagement & Priority Factor:** {target['engagement_factor']} / 30")

    with col_details:
        st.markdown("### 💡 Strategic Action Recommendations")
        
        if target["score"] >= 80:
            st.success("🔥 **High Priority Direct Conversion Strategy**")
            st.markdown(f"• Schedule direct outreach within **24 hours**.")
            st.markdown(f"• Highlight technical ROI tailored for **{target['company']}**.")
        elif target["score"] >= 60:
            st.warning("⚡ **Warm Nurture Strategy**")
            st.markdown(f"• Schedule follow-up within **48 hours** with relevant case studies.")
        else:
            st.info("❄️ **Long-Term Educational Drip Strategy**")
            st.markdown("• Add to monthly automated product updates.")

    st.divider()
    st.markdown("### 🏆 Prospect Leaderboard")
    st.dataframe(
        df[["name", "company", "industry", "priority", "score", "conversion_prob", "tier"]].rename(
            columns={
                "name": "Contact Name",
                "company": "Company",
                "industry": "Industry",
                "priority": "Priority",
                "score": "Score",
                "conversion_prob": "Conversion %",
                "tier": "Tier",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )


if __name__ == "__main__":
    show()