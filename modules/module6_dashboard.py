import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from typing import Any
import textwrap
import numpy as np

# =========================================================
# DESIGN TOKENS  ·  "Pipeline Console" theme
# =========================================================
BG          = "#F8FAFC"
PANEL       = "rgba(255,255,255,0.75)"
PANEL_ALT   = "rgba(255,255,255,0.55)"
BORDER      = "rgba(255,255,255,0.35)"
TEXT        = "#111827"
TEXT_DIM    = "#4B5563"
BLUE        = "#4C8DFF"
GREEN       = "#34D399"
AMBER       = "#FBBF24"
RED         = "#F87171"
CYAN        = "#22D3EE"
VIOLET      = "#A78BFA"

STATUS_COLOR = {
    "Qualified":  GREEN,
    "Follow-up":  AMBER,
    "Email Sent": BLUE,
    "Pending":    RED,
}

PLOTLY_LAYOUT: dict[str, Any] = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color=TEXT, size=12),
    xaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER, linecolor=BORDER,
               tickfont=dict(color=TEXT), title=dict(font=dict(color=TEXT))),
    yaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER, linecolor=BORDER,
               tickfont=dict(color=TEXT), title=dict(font=dict(color=TEXT))),
    legend=dict(font=dict(color=TEXT)),
    margin=dict(t=30, b=20, l=10, r=10),
)


def load_custom_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    .stApp{{
        background: linear-gradient(
            135deg,
            #E0F2FE 0%,
            #BFDBFE 30%,
            #93C5FD 55%,
            #A5B4FC 75%,
            #DDD6FE 100%
        );
        background-attachment: fixed;
    }}

    /* Scoped to .main only — NOT .stApp — so this never touches
       Streamlit's own chrome (toolbar, "Rerun"/"Deploy" buttons,
       hamburger menu, running-status widget). Those live in the
       app header, outside .main, and are left at their defaults. */
    .main, .main p, .main span, .main li, .main label,
    .main .stMarkdown, .main .stCaption {{
        color: {TEXT};
    }}

    /* Sidebar always stays white text, independent of the dashboard's
       dark-text styling above. Universal selector = lowest possible
       specificity, so any more specific rule (multiselect chips,
       buttons, etc.) still wins and keeps its own correct contrast. */
    section[data-testid="stSidebar"] * {{
        color: #FFFFFF !important;
    }}

    #MainMenu, footer{{ visibility: hidden; }}
    .block-container {{ padding-top: 2rem; max-width: 1300px; padding-left: 3rem; padding-right: 3rem; }}

    /* ---------------- Header ---------------- */
    .console-eyebrow {{
        display:flex; align-items:center; gap:8px; flex-wrap:wrap;
        font-family:'JetBrains Mono', monospace;
        font-size:clamp(10px, 2.6vw, 12px); letter-spacing:2px; font-weight:600;
        color:{BLUE}; text-transform:uppercase; margin-bottom:10px;margin-top:25px;
    }}
    .pulse-dot {{
        width:8px; height:8px; border-radius:50%; flex-shrink:0;
        background:{BLUE}; box-shadow:0 0 0 0 rgba(52,211,153,0.7);
        animation: pulse 1.8s infinite;
    }}
    @keyframes pulse {{
        0%   {{ box-shadow: 0 0 0 0 rgba(52,211,153,0.55); }}
        70%  {{ box-shadow: 0 0 0 8px rgba(52,211,153,0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(52,211,153,0); }}
    }}
    .console-title {{
        font-size:clamp(28px, 6vw, 40px); font-weight:700; color:black;
        margin:0 0 6px 0; letter-spacing:-0.5px; word-break:break-word;
    }}
    .console-sub {{
        font-size:clamp(13px, 3vw, 15px); color:{TEXT_DIM}; margin:0 0 8px 0;
    }}
    .hairline {{
        height:1px; background:{BORDER}; border:none; margin:22px 0;
    }}

    /* ---------------- KPI Cards ---------------- */
    .kpi-card {{
        background:{PANEL}; border:1px solid {BORDER}; border-radius:10px;
        padding:16px 18px 14px 18px; position:relative; overflow:hidden;
        min-height:120px; height:100%; display:flex; flex-direction:column; justify-content:space-between;
        transition:transform .15s ease, box-shadow .15s ease;
    }}
    .kpi-card:hover {{
        transform:translateY(-2px);
        box-shadow:0 8px 20px rgba(15,23,42,0.12);
    }}
    .kpi-card::before {{
        content:''; position:absolute; top:0; left:0; right:0; height:3px;
        background:var(--accent);
    }}
    .kpi-label {{
        font-family:'JetBrains Mono', monospace; font-size:11px; font-weight:600;
        letter-spacing:1.5px; text-transform:uppercase; color:{TEXT_DIM};
        overflow-wrap:anywhere;
    }}
    .kpi-value {{
        font-family:'JetBrains Mono', monospace; font-size:clamp(24px, 5vw, 32px); font-weight:700;
        color:black; line-height:1.1; margin:4px 0; overflow-wrap:anywhere;
    }}
    .kpi-delta {{
        font-family:'JetBrains Mono', monospace; font-size:12px; font-weight:600;
    }}
    .kpi-spark {{ letter-spacing:1px; font-size:13px; opacity:.85; }}

    /* ---------------- Sidebar ---------------- */
    .sidebar-tag {{
        font-family:'JetBrains Mono', monospace; font-size:11px; font-weight:700;
        letter-spacing:2px; text-transform:uppercase; color:{TEXT_DIM};
    }}

    /* ---------------- Tabs ---------------- */
    .stTabs [data-baseweb="tab-list"] {{
        gap:4px; border-bottom:1px solid {BORDER};
    }}
    .stTabs [data-baseweb="tab"] {{
        font-family:'JetBrains Mono', monospace; font-size:12px; font-weight:600;
        letter-spacing:1px; text-transform:uppercase; color:{TEXT_DIM};
        background:transparent; padding:10px 4px;
    }}
    .stTabs [aria-selected="true"] {{
        color:{TEXT} !important; border-bottom:2px solid {BLUE} !important;
    }}
    /* ---------- Tabs ---------- */

    button[data-baseweb="tab"]{{
        color:#111827 !important;
        font-size:18px !important;
        font-weight:700 !important;
        margin-right:25px !important;   /* Space between tabs */
        padding:12px 18px !important;
    }}

    button[data-baseweb="tab"]:hover{{
        color:#2563EB !important;
    }}

    button[data-baseweb="tab"][aria-selected="true"]{{
        color:#111827 !important;
        font-weight:800 !important;
    }}

    /* ---------------- Inputs ---------------- */
    .stTextInput input, .stMultiSelect div[data-baseweb="select"] > div,
    .stSelectbox div[data-baseweb="select"] > div {{
        background:{PANEL_ALT} !important; border:1px solid {BORDER} !important;
        color:white !important; border-radius:8px !important;
    }}
    .stButton>button{{
        border-radius:8px !important;
    }}
    .stButton>button:hover{{
        border-color:{BLUE}; color:{BLUE} !important;
    }}
    .stProgress > div > div > div {{ background:{GREEN} !important; }}
    .stProgress > div > div {{ background:{PANEL_ALT} !important; }}

    /* ---------------- Panels ---------------- */
    .panel {{
        background:{PANEL}; border:1px solid {BORDER}; border-radius:10px;
        padding:16px 18px;
    }}
    .panel-title {{
        font-family:'JetBrains Mono', monospace; font-size:11px; font-weight:700;
        letter-spacing:2px; text-transform:uppercase; margin-bottom:12px;
        display:flex; align-items:center; justify-content:space-between; gap:8px;
    }}
    h3 {{ color:white !important; font-weight:600 !important; }}

    /* ---------------- Empty state ---------------- */
    .empty-state {{
        display:flex; flex-direction:column; align-items:center; justify-content:center;
        gap:6px; padding:48px 12px; text-align:center;
    }}
    .empty-state .emoji {{ font-size:26px; opacity:.7; }}
    .empty-state .title {{ font-weight:600; color:{TEXT}; font-size:14px; }}
    .empty-state .sub {{ color:{TEXT_DIM}; font-size:12.5px; }}

    /* ---------------- Leads grid ---------------- */
    .lead-row {{
        display:grid;
        grid-template-columns: 34px 1.6fr 1fr 1.3fr 0.9fr 1fr;
        align-items:center; gap:14px;
        padding:12px 10px; border-bottom:1px solid {BORDER};
        border-left:3px solid var(--rowcolor);
        background:{PANEL}; transition:background .12s ease;
    }}
    .lead-row > div {{ min-width:0; }}
    .lead-row:hover {{ background:{PANEL_ALT}; }}
    .lead-row.head {{
        border-left:3px solid transparent; border-bottom:1px solid {BORDER};
        font-family:'JetBrains Mono', monospace; font-size:10px; letter-spacing:1.5px;
        text-transform:uppercase; color:{TEXT_DIM}; padding-bottom:10px;
    }}
    .avatar {{
        width:28px; height:28px; border-radius:6px; background:{PANEL_ALT};
        border:1px solid {BORDER}; display:flex; align-items:center; justify-content:center;
        font-family:'JetBrains Mono', monospace; font-size:11px; font-weight:700; color:{TEXT};
        flex-shrink:0;
    }}
    .company-name {{
        font-weight:600; color:{TEXT}; font-size:14px;
        white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
        display:flex; align-items:center; gap:6px;
    }}
    .top-badge {{
        font-family:'JetBrains Mono', monospace; font-size:8.5px; font-weight:700;
        color:#111827; background:{AMBER}; border-radius:4px; padding:1px 5px;
        letter-spacing:0.5px; flex-shrink:0;
    }}
    .industry-tag {{
        color:{TEXT_DIM}; font-size:13px;
        white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
    }}
    .score-wrap {{ display:flex; align-items:center; gap:8px; min-width:0; }}
    .score-bar-bg {{ flex:1; min-width:20px; height:5px; background:{PANEL_ALT}; border-radius:3px; overflow:hidden; }}
    .score-bar-fill {{ height:100%; border-radius:3px; }}
    .score-num {{ font-family:'JetBrains Mono', monospace; font-size:12px; color:{TEXT}; width:26px; flex-shrink:0; }}
    .status-chip {{
        font-family:'JetBrains Mono', monospace; font-size:10px; font-weight:700;
        letter-spacing:1px; text-transform:uppercase; color:var(--rowcolor);
        white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
    }}
    .mono-dim {{
        font-family:'JetBrains Mono', monospace; font-size:12px; color:{TEXT_DIM};
        white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
    }}

    /* ---------------- Responsive breakpoints ---------------- */
    @media (max-width: 1000px) {{
        .block-container {{ padding-left: 1.5rem; padding-right: 1.5rem; }}
    }}

    @media (max-width: 900px) {{
        .lead-row.head {{ display:none; }}
        .lead-row {{
            grid-template-columns: 30px 1.3fr 0.8fr 1fr;
            row-gap:6px; column-gap:10px;
        }}
        .industry-tag {{ display:none; }}
        .mono-dim {{ grid-column: 1 / -1; padding-left:42px; font-size:11px; }}
    }}

    @media (max-width: 600px) {{
        .block-container {{ padding-top:1.2rem; padding-left:1rem; padding-right:1rem; }}
        .panel {{ padding:12px 12px; }}
        .lead-row {{
            grid-template-columns: 26px 1fr 0.9fr;
            padding:10px 8px; gap:8px;
        }}
        .avatar {{ width:24px; height:24px; font-size:10px; }}
        .company-name {{ font-size:13px; }}
        .score-bar-bg {{ display:none; }}
        .status-chip {{ font-size:9px; }}
        .mono-dim {{ padding-left:32px; }}
        .kpi-card {{ padding:14px 16px 12px 16px; }}
        .stTabs [data-baseweb="tab"] {{ font-size:10px; padding:8px 3px; letter-spacing:0.5px; }}
    }}
    .mono {{ font-family:'JetBrains Mono', monospace; font-size:13px; color:{TEXT}; }}

    /* ---------------- Insight log ---------------- */
    .log-row {{
        display:flex; gap:12px; align-items:flex-start;
        padding:10px 12px; border-left:3px solid var(--pcolor);
        background:{PANEL_ALT}; border-radius:6px; margin-bottom:8px;
    }}
    .log-tag {{
        font-family:'JetBrains Mono', monospace; font-size:10px; font-weight:700;
        color:var(--pcolor); min-width:52px;
    }}
    .log-text {{ font-size:13.5px; color:{TEXT}; }}
    /* Export CSV Button */

    div[data-testid="stDownloadButton"] button {{
        background:#111827 !important;
        color:white !important;
        border:none !important;
        border-radius:8px !important;
        font-family:'JetBrains Mono', monospace !important;
        font-size:12px !important;
        font-weight:600 !important;
    }}

    div[data-testid="stDownloadButton"] button:hover {{
        background:transparent !important;
        border:1px solid {BLUE} !important;
        color:white !important;
    }}

    div[data-testid="stDownloadButton"] button p,
    div[data-testid="stDownloadButton"] button span {{
        color:white !important;
    }}
    </style>
    """, unsafe_allow_html=True)


# =========================================================
# DATA
# =========================================================
@st.cache_data
def get_leads_data():
    return pd.DataFrame({
        "Company": ["Microsoft", "Google", "Amazon", "Adobe", "Infosys",
                    "IBM", "Oracle", "Salesforce", "SAP", "Meta"],
        "Industry": ["Technology", "Technology", "E-Commerce", "Software", "IT Services",
                     "Technology", "Software", "SaaS", "Software", "Technology"],
        "Lead Score": [95, 91, 88, 84, 79, 76, 73, 89, 68, 92],
        "Status": ["Qualified", "Qualified", "Follow-up", "Email Sent", "Pending",
                   "Follow-up", "Pending", "Qualified", "Pending", "Email Sent"],
        "Last Contact": pd.date_range(end=datetime.today(), periods=10).strftime("%b %d"),
        "Deal Value ($)": [120000, 95000, 60000, 40000, 25000,
                            30000, 22000, 88000, 18000, 105000],
    })


@st.cache_data
def get_trend_data():
    days = pd.date_range(end=datetime.today(), periods=30)
    rng = np.random.default_rng(42)
    leads = np.cumsum(rng.integers(1, 8, size=30)) + 20
    qualified = (leads * rng.uniform(0.55, 0.7, size=30)).astype(int)
    emails = np.cumsum(rng.integers(2, 10, size=30)) + 15
    return pd.DataFrame({
        "Date": days,
        "Total Leads": leads,
        "Qualified Leads": qualified,
        "Emails Sent": emails,
    })


def sparkline(values, color):
    blocks = "▁▂▃▄▅▆▇█"
    lo, hi = min(values), max(values)
    rng = (hi - lo) or 1
    chars = "".join(blocks[int((v - lo) / rng * (len(blocks) - 1))] for v in values)
    return f'<span class="kpi-spark" style="color:{color}">{chars}</span>'


def kpi_card(label, value, delta_val, delta_suffix, accent, spark_values, is_pct=False):
    arrow = "▲" if delta_val >= 0 else "▼"
    delta_color = GREEN if delta_val >= 0 else RED
    sign = "+" if delta_val >= 0 else ""
    unit = "%" if is_pct else ""
    delta_label = f"{sign}{delta_val}{unit} {delta_suffix}"
    # Use a non-breaking space instead of "" when there's no sparkline.
    # An interpolated blank line here would be a whitespace-only line,
    # which markdown's raw-HTML parser treats as a blank line — that
    # terminates the HTML block early and causes the trailing </div>
    # tags to be rendered as literal escaped text instead of parsed HTML.
    spark_html = sparkline(spark_values, accent) if spark_values else "&nbsp;"
    html = textwrap.dedent(f"""
    <div class="kpi-card" style="--accent:{accent}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span class="kpi-delta" style="color:{delta_color}">{arrow} {delta_label}</span>
            {spark_html}
        </div>
    </div>
    """).strip()
    # Extra safety net: strip any accidental whitespace-only lines so this
    # can never regress into the same blank-line-breaks-the-html-block issue.
    return "\n".join(line for line in html.splitlines() if line.strip() != "")


def week_over_week_delta(series: pd.Series, as_pct: bool = False):
    """Compare the sum/level of the last 7 points vs the prior 7 points."""
    if len(series) < 14:
        return 0
    last7 = series.tail(7).mean()
    prev7 = series.tail(14).head(7).mean()
    if as_pct:
        if prev7 == 0:
            return 0
        return round((last7 - prev7) / prev7 * 100, 1)
    return round(last7 - prev7, 0)


def score_color(score):
    if score >= 85:
        return GREEN
    if score >= 70:
        return AMBER
    return RED


def lead_row_html(row, top_company=None):
    color = STATUS_COLOR.get(row["Status"], TEXT_DIM)
    sc = score_color(row["Lead Score"])
    initials = "".join([w[0] for w in row["Company"].split()])[:2].upper()
    badge = '<span class="top-badge">TOP</span>' if row["Company"] == top_company else ""
    return textwrap.dedent(f"""
    <div class="lead-row" style="--rowcolor:{color}">
        <div class="avatar">{initials}</div>
        <div class="company-name">{row['Company']}{badge}</div>
        <div class="industry-tag">{row['Industry']}</div>
        <div class="score-wrap">
            <div class="score-bar-bg"><div class="score-bar-fill" style="width:{row['Lead Score']}%; background:{sc}"></div></div>
            <div class="score-num">{row['Lead Score']}</div>
        </div>
        <div class="status-chip">{row['Status']}</div>
        <div class="mono-dim">{row['Last Contact']} · ${row['Deal Value ($)']:,.0f}</div>
    </div>
    """).strip()


def empty_state(title, sub, emoji="🔍"):
    return textwrap.dedent(f"""
    <div class="empty-state">
        <div class="emoji">{emoji}</div>
        <div class="title">{title}</div>
        <div class="sub">{sub}</div>
    </div>
    """).strip()


def show():
    load_custom_css()

    # ---------------- Header ----------------
    st.markdown(f"""
    <div class="console-eyebrow"><div class="pulse-dot"></div>SALES OPS &middot; LIVE MONITOR</div>
    <div class="console-title">Dashboard</div>
    <div class="console-sub">Monitor leads, AI insights and sales performance in real time.</div>
    """, unsafe_allow_html=True)

    df = get_leads_data()
    trend_df = get_trend_data()

    # ---------------- Sidebar Filters ----------------
    with st.sidebar:
        st.markdown('<div class="sidebar-tag">Filters</div>', unsafe_allow_html=True)
        st.write("")
        industries = st.multiselect(
            "Industry", options=sorted(df["Industry"].unique()),
            default=sorted(df["Industry"].unique())
        )
        statuses = st.multiselect(
            "Status", options=sorted(df["Status"].unique()),
            default=sorted(df["Status"].unique())
        )
        score_range = st.slider("Lead Score Range", 0, 100, (0, 100))

        col_reset, col_refresh = st.columns(2)
        with col_reset:
            if st.button("⟲ Reset", use_container_width=True):
                st.session_state.pop("company_search", None)
                st.rerun()
        with col_refresh:
            if st.button("↻ Refresh", use_container_width=True):
                st.cache_data.clear()
                st.toast("Data refreshed", icon="✅")
                st.rerun()

        st.markdown('<hr class="hairline" style="margin:16px 0;">', unsafe_allow_html=True)
        st.caption("Last refreshed " + datetime.now().strftime("%b %d, %Y · %I:%M %p"))

    filtered = df[
        df["Industry"].isin(industries)
        & df["Status"].isin(statuses)
        & df["Lead Score"].between(score_range[0], score_range[1])
    ]

    st.markdown('<hr class="hairline">', unsafe_allow_html=True)

    # ---------------- KPI Cards (computed from live trend data) ----------------
    total_delta = week_over_week_delta(trend_df["Total Leads"])
    qualified_delta = week_over_week_delta(trend_df["Qualified Leads"])
    emails_delta = week_over_week_delta(trend_df["Emails Sent"])
    score_delta_pct = week_over_week_delta(
        pd.Series(np.linspace(df["Lead Score"].mean() - 6, df["Lead Score"].mean(), 30)), as_pct=True
    )
    win_rate = (df["Status"] == "Qualified").sum() / len(df) * 100 if len(df) else 0

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.markdown(kpi_card("Total Leads", str(len(df)), int(total_delta), "this wk", BLUE,
                          list(trend_df["Total Leads"].tail(8))), unsafe_allow_html=True)
    c2.markdown(kpi_card("Qualified", str((df["Status"] == "Qualified").sum()), int(qualified_delta), "this wk", GREEN,
                          list(trend_df["Qualified Leads"].tail(8))), unsafe_allow_html=True)
    c3.markdown(kpi_card("Emails Sent", str(int(trend_df["Emails Sent"].iloc[-1])), int(emails_delta), "this wk", CYAN,
                          list(trend_df["Emails Sent"].tail(8))), unsafe_allow_html=True)
    c4.markdown(kpi_card("Avg Lead Score", f"{df['Lead Score'].mean():.0f}", score_delta_pct, "this wk", AMBER,
                          list(np.round(np.linspace(df["Lead Score"].mean() - 6, df["Lead Score"].mean(), 8))), is_pct=True), unsafe_allow_html=True)
    c5.markdown(kpi_card("Pipeline Value", f"${df['Deal Value ($)'].sum()/1000:,.0f}K", 12, "this wk", VIOLET,
                          [420, 440, 470, 500, 540, 560, 580, 603]), unsafe_allow_html=True)
    c6.markdown(kpi_card("Win Rate", f"{win_rate:.0f}%", 0, "vs last wk", GREEN,
                          None), unsafe_allow_html=True)

    st.markdown('<hr class="hairline">', unsafe_allow_html=True)

    # ---------------- Tabs ----------------
    tab1, tab2, tab3 = st.tabs(["LEADS", "TRENDS", "AI INSIGHTS"])

    # ----- Leads Tab -----
    with tab1:
        col_search, col_sort, col_dl = st.columns([2.2, 1.6, 1])
        with col_search:
            search = st.text_input(
                "Search company", placeholder="Search company or industry…",
                label_visibility="collapsed", key="company_search"
            )
        with col_sort:
            sort_choice = st.selectbox(
                "Sort by",
                ["Score (High→Low)", "Score (Low→High)", "Deal Value (High→Low)",
                 "Company (A→Z)", "Most Recent Contact"],
                label_visibility="collapsed",
            )

        view = filtered.copy()
        if search:
            mask = (
                view["Company"].str.contains(search, case=False, regex=False)
                | view["Industry"].str.contains(search, case=False, regex=False)
            )
            view = view[mask]

        sort_map = {
            "Score (High→Low)": ("Lead Score", False),
            "Score (Low→High)": ("Lead Score", True),
            "Deal Value (High→Low)": ("Deal Value ($)", False),
            "Company (A→Z)": ("Company", True),
            "Most Recent Contact": ("Last Contact", False),
        }
        sort_col, sort_asc = sort_map[sort_choice]
        view = view.sort_values(sort_col, ascending=sort_asc)

        with col_dl:
            st.download_button("⬇ Export CSV", data=view.to_csv(index=False).encode("utf-8"),
                                file_name="leads.csv", mime="text/csv", use_container_width=True)

        cL, cR = st.columns([2.1, 1])
        with cL:
            st.markdown('<div class="panel-title" style="color:%s"><span>RECENT LEADS &middot; %d</span></div>' % (TEXT_DIM, len(view)),
                        unsafe_allow_html=True)
            if view.empty:
                panel_html = f'<div class="panel">{empty_state("No leads match your filters", "Try widening the score range or clearing the search box.")}</div>'
            else:
                top_company = df.loc[df["Lead Score"].idxmax(), "Company"]
                rows_html = "".join(lead_row_html(r, top_company) for _, r in view.iterrows())
                header_html = textwrap.dedent("""
                <div class="lead-row head">
                    <div></div><div>Company</div><div>Industry</div><div>Score</div><div>Status</div><div>Last Contact</div>
                </div>
                """).strip()
                panel_html = f'<div class="panel" style="padding:8px 14px;">{header_html}{rows_html}</div>'
            st.markdown(panel_html, unsafe_allow_html=True)
        with cR:
            st.markdown('<div class="panel-title" style="color:%s">STATUS BREAKDOWN</div>' % TEXT_DIM, unsafe_allow_html=True)
            if filtered.empty:
                st.markdown(f'<div class="panel">{empty_state("Nothing to chart", "Adjust filters to see status breakdown.", "📊")}</div>', unsafe_allow_html=True)
            else:
                status_counts = filtered["Status"].value_counts().reset_index()
                status_counts.columns = ["Status", "Count"]
                fig = px.pie(status_counts, names="Status", values="Count", hole=0.6,
                            color="Status", color_discrete_map=STATUS_COLOR)
                fig.update_traces(textfont=dict(color=TEXT), marker=dict(line=dict(color=BG, width=2)))
                pie_layout = dict(PLOTLY_LAYOUT)
                pie_layout["legend"] = dict(orientation="h", yanchor="bottom", y=-0.60, font=dict(color=TEXT, size=10))
                fig.update_layout(**pie_layout, height=260, showlegend=True)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ----- Trends Tab -----
    with tab2:
        st.markdown('<div class="panel-title" style="color:%s">LEAD GROWTH &middot; LAST 30 DAYS</div>' % TEXT_DIM, unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=trend_df["Date"], y=trend_df["Total Leads"],
                                   name="Total Leads", mode="lines",
                                   line=dict(color=BLUE, width=2.5),
                                   fill="tozeroy", fillcolor="rgba(76,141,255,0.08)"))
        fig2.add_trace(go.Scatter(x=trend_df["Date"], y=trend_df["Qualified Leads"],
                                   name="Qualified Leads", mode="lines",
                                   line=dict(color=GREEN, width=2.5),
                                   fill="tozeroy", fillcolor="rgba(52,211,153,0.08)"))
        trend_layout = dict(PLOTLY_LAYOUT)
        trend_layout["legend"] = dict(orientation="h", yanchor="bottom", y=1.02, font=dict(color=TEXT))
        fig2.update_layout(**trend_layout, height=340)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="panel-title" style="color:%s">SCORE BY INDUSTRY</div>' % TEXT_DIM, unsafe_allow_html=True)
            if filtered.empty:
                st.markdown(f'<div class="panel">{empty_state("No data to plot", "Adjust filters to see scores by industry.", "📈")}</div>', unsafe_allow_html=True)
            else:
                avg_score = filtered.groupby("Industry")["Lead Score"].mean().reset_index()
                fig3 = px.bar(avg_score, x="Industry", y="Lead Score")
                fig3.update_traces(marker_color=CYAN, marker_line_width=0)
                fig3.update_layout(**PLOTLY_LAYOUT, height=300)
                st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
        with c2:
            st.markdown('<div class="panel-title" style="color:%s">DEAL VALUE BY COMPANY</div>' % TEXT_DIM, unsafe_allow_html=True)
            if filtered.empty:
                st.markdown(f'<div class="panel">{empty_state("No data to plot", "Adjust filters to see deal values.", "📈")}</div>', unsafe_allow_html=True)
            else:
                dv = filtered.sort_values("Deal Value ($)", ascending=True)
                fig4 = px.bar(dv, x="Deal Value ($)", y="Company", orientation="h")
                fig4.update_traces(marker_color=VIOLET, marker_line_width=0)
                fig4.update_layout(**PLOTLY_LAYOUT, height=300)
                st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})

        st.markdown('<hr class="hairline">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title" style="color:%s">SALES PROGRESS</div>' % TEXT_DIM, unsafe_allow_html=True)
        progress = 74
        st.progress(progress / 100)
        st.markdown(f'<span class="mono">{progress}% OF QUARTERLY TARGET</span>', unsafe_allow_html=True)

    # ----- AI Insights Tab (now computed from live data) -----
    with tab3:
        st.markdown('<div class="panel-title" style="color:%s">AI INSIGHT LOG</div>' % TEXT_DIM, unsafe_allow_html=True)

        insights = []
        top2 = df.nlargest(2, "Lead Score")
        for _, r in top2.iterrows():
            insights.append(("HIGH", GREEN, f"{r['Company']} has a strong lead score of {r['Lead Score']} — high conversion probability."))
        for _, r in df[df["Status"] == "Follow-up"].iterrows():
            insights.append(("URGENT", RED, f"{r['Company']} is marked Follow-up and needs outreach within 48 hours."))
        for _, r in df[df["Status"] == "Pending"].nsmallest(2, "Lead Score").iterrows():
            insights.append(("LOW", TEXT_DIM, f"{r['Company']} is a lower-priority lead pending contact."))

        log_html = "".join(
            f'<div class="log-row" style="--pcolor:{c}"><div class="log-tag">{t}</div><div class="log-text">{txt}</div></div>'
            for t, c, txt in insights
        )
        st.markdown(log_html, unsafe_allow_html=True)

        st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            top_industry_row = df.groupby("Industry")["Lead Score"].mean().idxmax()
            top_industry_score = df.groupby("Industry")["Lead Score"].mean().max()
            st.markdown(textwrap.dedent(f"""
            <div class="panel" style="border-left:3px solid {BLUE}">
                <div class="panel-title" style="color:{BLUE}">TOP INDUSTRY</div>
                <div style="font-size:22px; font-weight:700; color:{TEXT}">{top_industry_row}</div>
                <div class="mono-dim" style="margin-top:6px;">Highest average lead score: <span class="mono" style="color:{TEXT}">{top_industry_score:.0f}</span></div>
            </div>
            """).strip(), unsafe_allow_html=True)
        with c2:
            follow_ups = df[df["Status"].isin(["Follow-up", "Pending"])].sort_values("Lead Score", ascending=False)["Company"].tolist()
            follow_up_html = "<br>".join(f"&middot; {c}" for c in follow_ups) if follow_ups else "No follow-ups due"
            st.markdown(textwrap.dedent(f"""
            <div class="panel" style="border-left:3px solid {AMBER}">
                <div class="panel-title" style="color:{AMBER}">FOLLOW-UPS DUE</div>
                <div class="mono" style="line-height:2;">
                    {follow_up_html}
                </div>
            </div>
            """).strip(), unsafe_allow_html=True)


if __name__ == "__main__":
    st.set_page_config(page_title="Sales Dashboard", page_icon="📊", layout="wide")
    show()