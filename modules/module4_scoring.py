import os
import pandas as pd
import requests
import streamlit as st

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")


def compute_dynamic_factors(lead):
    """Calculates factor scores dynamically using the actual attributes of the lead record."""
    # 1. Company Growth / Revenue Factor (Max 35)
    size = str(lead.get("company_size", "")).strip()
    rev = str(lead.get("revenue", "")).strip()
    growth_score = 15
    if size in ["201-500", "500+"] or "$50M" in rev or "$10M" in rev:
        growth_score = 35
    elif size in ["51-200", "11-50"]:
        growth_score = 25

    # 2. Industry Match Factor (Max 35)
    ind = str(lead.get("industry", "")).strip().lower()
    industry_score = 20
    if ind in ["technology", "finance", "healthcare", "fintech", "software"]:
        industry_score = 35
    elif ind in ["retail", "manufacturing"]:
        industry_score = 25

    # 3. Engagement & Priority Factor (Max 30)
    prio = str(lead.get("priority", "")).strip().lower()
    status = str(lead.get("status", "")).strip().lower()
    engagement_score = 10
    if prio == "high" or status == "qualified":
        engagement_score = 30
    elif prio == "medium":
        engagement_score = 20

    total_score = min(growth_score + industry_score + engagement_score, 100)
    conversion_prob = min(int(total_score * 0.88), 98)

    return {
        "growth": growth_score,
        "industry": industry_score,
        "engagement": engagement_score,
        "total": total_score,
        "conversion_prob": conversion_prob,
    }


def show():
    st.markdown("## 🎯 Lead Scoring & Recommendation Engine")
    st.caption("AI-powered conversion likelihood calculated from your custom database records.")

    # 1. FETCH ALL USER-UPLOADED LEADS FROM BACKEND
    try:
        res = requests.get(f"{API_URL}/leads", timeout=10)
        leads_data = res.json() if res.status_code == 200 else []
    except Exception:
        leads_data = []

    if not leads_data:
        st.info("💡 No leads found in your database. Please add or import CSV leads in **Lead Management**.")
        return

    # Process all leads dynamically
    scored_prospects = []
    for lead in leads_data:
        metrics = compute_dynamic_factors(lead)
        tier = (
            "🔥 Highly Qualified"
            if metrics["total"] >= 80
            else ("⚡ Warm Lead" if metrics["total"] >= 60 else "❄️ Cold Lead")
        )

        scored_prospects.append({
            "id": lead.get("id"),
            "name": lead.get("name") or lead.get("contact_name", "Unknown Contact"),
            "company": lead.get("company") or lead.get("company_name", "Unknown Company"),
            "industry": lead.get("industry", "General"),
            "priority": lead.get("priority", "Medium"),
            "status": lead.get("status", "New"),
            "score": metrics["total"],
            "conversion_prob": metrics["conversion_prob"],
            "tier": tier,
            "factors": metrics,
            "raw": lead,
        })

    df = pd.DataFrame(scored_prospects).sort_values(by="score", ascending=False)

    # Overview KPIs
    m1, m2, m3 = st.columns(3)
    m1.metric("Your Uploaded Prospects", len(df))
    m2.metric("Highly Qualified (Score ≥ 80)", len(df[df["score"] >= 80]))
    m3.metric("Avg Conversion Likelihood", f"{int(df['conversion_prob'].mean())}%")

    st.divider()

    # Lead Inspector Selector
    st.markdown("### 🔍 Inspect Prospect Factors")
    prospect_map = {
        f"[{row['tier']}] {row['name']} - {row['company']} (Score: {row['score']})": row
        for _, row in df.iterrows()
    }
    selected_label = st.selectbox("Select Lead to Analyze", options=list(prospect_map.keys()))
    target = prospect_map[selected_label]
    factors = target["factors"]
    raw_lead = target["raw"]

    # Score breakdown layout
    col_score, col_strategy = st.columns([1, 1.2], gap="large")

    with col_score:
        st.markdown(f"#### 🏆 Score Breakdown: {target['name']}")
        st.caption(f"Company: **{target['company']}** | Industry: **{target['industry']}**")

        c1, c2 = st.columns(2)
        c1.metric("Lead Score", f"{target['score']} / 100")
        c2.metric("Conversion Probability", f"{target['conversion_prob']}%")

        st.progress(target["conversion_prob"] / 100)

        st.markdown("##### Factor Contributions:")
        st.write(f"📈 **Company Growth & Scale**: `{factors['growth']} / 35 pts`")
        st.progress(factors["growth"] / 35)

        st.write(f"🏢 **Industry Match**: `{factors['industry']} / 35 pts`")
        st.progress(factors["industry"] / 35)

        st.write(f"⚡ **Engagement & Priority ({target['priority']})**: `{factors['engagement']} / 30 pts`")
        st.progress(factors["engagement"] / 30)

    with col_strategy:
        st.markdown("#### 🚀 Dynamic Outreach Strategy")

        if target["score"] >= 80:
            st.success("🔥 **High Priority Direct Conversion Strategy**")
            st.markdown(f"""
            * **Follow-up Timing:** High conversion signal! Reach out to **{target['name']}** within **2 hours**.
            * **Channel Mix:** Send personalized email to `{raw_lead.get('email', 'contact')}` + LinkedIn DM.
            * **Tailored Focus:** Highlight ROI and efficiency for the **{target['industry']}** industry.
            """)
        elif target["score"] >= 60:
            st.warning("⚡ **Warm Nurture Campaign Strategy**")
            st.markdown(f"""
            * **Follow-up Timing:** Schedule contact within **24–48 hours**.
            * **Channel Mix:** Email outreach referencing **{target['company']}**'s growth stage.
            * **Tailored Focus:** Share relevant case studies and industry benchmarks.
            """)
        else:
            st.info("❄️ **Long-Term Educational Strategy**")
            st.markdown(f"""
            * **Follow-up Timing:** Add contact to your monthly automated newsletter drip.
            * **Tailored Focus:** Provide general product updates and educational content.
            """)

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