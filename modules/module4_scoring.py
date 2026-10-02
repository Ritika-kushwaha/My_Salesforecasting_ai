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
    def get_current_user_id():
        user = st.session_state.get("user")
        if isinstance(user, dict) and user.get("id"):
            return user["id"]
        return st.session_state.get("user_id", 1)

    user_id = get_current_user_id()
    st.markdown("<h1 style='font-weight: 800; letter-spacing: -0.02em;'>🎯Lead Scoring & Qualification Engine</h1>", unsafe_allow_html=True)
    st.caption("AI-assisted multi-factor scoring model prioritizing high-intent accounts and conversion velocity.")

    # Retrieve user ID safely
    user_data = st.session_state.get("user") or {}
    user_id = user_data.get("id", 1) if isinstance(user_data, dict) else st.session_state.get("user_id", 1)

    # 1. Fetch leads
    leads_data = []
    try:
        res = requests.get(f"{API_URL}/leads", params={"user_id": user_id}, timeout=10)
        if res.status_code == 200:
            leads_data = res.json()
    except Exception:
        pass

    if not leads_data:
        st.info("💡 No lead records available to score. Please register or import leads in **(Lead Pipeline)** first.")
        return

    # 2. Process Scoring & Tiers
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

    # 3. Top Metrics Row
    avg_score = int(df["score"].mean()) if not df.empty else 0
    tier_1_count = sum(1 for r in processed_leads if r["score"] >= 80)
    tier_2_count = sum(1 for r in processed_leads if 60 <= r["score"] < 80)
    tier_3_count = sum(1 for r in processed_leads if r["score"] < 60)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Average ICP Score</div>
            <div class="kpi-value">{avg_score} <span style="font-size: 1rem; color: #94A3B8;">/ 100</span></div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Tier 1 • High Intent</div>
            <div class="kpi-value" style="color: #10B981;">{tier_1_count} <span style="font-size: 1rem; color: #94A3B8;">leads</span></div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Tier 2 • Warm Prospects</div>
            <div class="kpi-value" style="color: #F59E0B;">{tier_2_count} <span style="font-size: 1rem; color: #94A3B8;">leads</span></div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Tier 3 • Nurture Drip</div>
            <div class="kpi-value" style="color: #64748B;">{tier_3_count} <span style="font-size: 1rem; color: #94A3B8;">leads</span></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

    # 4. Lead Drill-Down & Strategy Section
    col_selector, col_details = st.columns([1.1, 1.2], gap="large")

    with col_selector:
        st.markdown("### 🔍 Prospect Factor Drilldown")
        lead_options = {
            f"#{idx} - {r.get('name', 'N/A')} ({r.get('company', 'N/A')}) • Score: {r['score']}": r 
            for idx, r in enumerate(processed_leads, start=1)
        }
        selected_label = st.selectbox("Select Target Lead to Inspect", list(lead_options.keys()))
        target = lead_options[selected_label]

        # Score Visual Card
        score_color = "#10B981" if target["score"] >= 80 else ("#F59E0B" if target["score"] >= 60 else "#64748B")
        
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 14px; padding: 18px; margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3 style="margin: 0; font-weight: 800;">{target.get('name', 'N/A')}</h3>
                    <p style="margin: 0; font-size: 0.85rem; color: #94A3B8;">{target.get('company', 'N/A')} • {target.get('industry', 'General')}</p>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 1.8rem; font-weight: 800; color: {score_color};">{target['score']}</span>
                    <span style="font-size: 0.85rem; color: #94A3B8;">/100</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.progress(target["score"] / 100, text=f"Overall Propensity: {target['score']}%")

        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        st.markdown(f"• **Company Growth & Size Fit:** `{target['growth_factor']} / 35`")
        st.markdown(f"• **Industry & Market Vertical:** `{target['industry_factor']} / 35`")
        st.markdown(f"• **Engagement & Account Priority:** `{target['engagement_factor']} / 30`")
        st.markdown(f"• **Estimated Conversion Probability:** `{target['conversion_prob']}%`")

    with col_details:
        st.markdown("### 💡 Recommended Conversion Strategy")

        if target["score"] >= 80:
            st.markdown(f"""
            <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 14px; padding: 20px;">
                <h4 style="color: #10B981; margin: 0 0 10px 0;">🔥 Tier 1: Fast-Track Direct Close Strategy</h4>
                <p style="font-size: 0.9rem; margin-bottom: 8px;"><b>Account Fit:</b> Exceptional profile fit with immediate budget availability signals.</p>
                <ul style="font-size: 0.88rem; line-height: 1.6; margin: 0; padding-left: 20px;">
                    <li>Initiate multi-channel touchpoint (InMail + Email) within <b>24 hours</b>.</li>
                    <li>Tailor initial pitch around <b>immediate ROI and time saved</b> for {target.get('company', 'their team')}.</li>
                    <li>Offer an exclusive 15-minute executive demo with technical integration walkthrough.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        elif target["score"] >= 60:
            st.markdown(f"""
            <div style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.25); border-radius: 14px; padding: 20px;">
                <h4 style="color: #F59E0B; margin: 0 0 10px 0;">⚡ Tier 2: Warm Solution Nurturing Strategy</h4>
                <p style="font-size: 0.9rem; margin-bottom: 8px;"><b>Account Fit:</b> Moderate-to-high viability, requires targeted education.</p>
                <ul style="font-size: 0.88rem; line-height: 1.6; margin: 0; padding-left: 20px;">
                    <li>Send relevant industry case study comparing automation benefits.</li>
                    <li>Schedule follow-up touchpoint within <b>48-72 hours</b>.</li>
                    <li>Identify secondary decision-makers on LinkedIn.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: rgba(100, 116, 139, 0.08); border: 1px solid rgba(100, 116, 139, 0.25); border-radius: 14px; padding: 20px;">
                <h4 style="color: #94A3B8; margin: 0 0 10px 0;">❄️ Tier 3: Long-Term Automated Drip Strategy</h4>
                <p style="font-size: 0.9rem; margin-bottom: 8px;"><b>Account Fit:</b> Low current buying signals or nascent company stage.</p>
                <ul style="font-size: 0.88rem; line-height: 1.6; margin: 0; padding-left: 20px;">
                    <li>Enroll in monthly product release updates and best practice newsletter.</li>
                    <li>Set automated reminder to reassess company headcount and revenue in 90 days.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # 5. Leaderboard Table
    st.markdown("### 🏆 Prospect Conversion Leaderboard")
    
    # Format leaderboard dataframe
    leaderboard_df = df[["name", "company", "industry", "priority", "score", "conversion_prob", "tier"]].copy()
    leaderboard_df.insert(0, "#", range(1, len(leaderboard_df) + 1))
    leaderboard_df.rename(
        columns={
            "name": "Contact Name",
            "company": "Company",
            "industry": "Industry",
            "priority": "Priority",
            "score": "ICP Score",
            "conversion_prob": "Win Prob %",
            "tier": "Intent Tier",
        },
        inplace=True
    )

    st.dataframe(leaderboard_df, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    show()