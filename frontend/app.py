"""
VP CX Agent OS — Streamlit Frontend v2
Run: streamlit run frontend/app.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Auto-seed the database on first run (e.g. Hugging Face Spaces where the DB
# is not committed to the repo).
_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "cx_agent_os.db")
if not os.path.exists(_DB_PATH):
    import subprocess
    _seed = os.path.join(os.path.dirname(_DB_PATH), "generate_synthetic_data.py")
    subprocess.run([sys.executable, _seed], check=True)

import streamlit as st
import pandas as pd
from datetime import datetime

# set_page_config must be the FIRST Streamlit command in the script (before any
# other st.* call, including st.secrets access below).
st.set_page_config(
    page_title="VP CX Agent OS",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Resolve the real Anthropic key ONCE per *process* and cache it. The Mock/Live
# toggle mutates os.environ (popping the key in mock mode), and os.environ is
# shared across every session in the process — so reading it on each rerun would
# lose the key globally as soon as any session sits in mock mode. st.cache_resource
# captures the key on first call (env still intact) and returns it thereafter for
# all sessions, without re-touching st.secrets (avoids the "No secrets found"
# error box on hosts like Hugging Face that inject the key as an env var).
@st.cache_resource
def _resolve_real_api_key():
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        # Only touch st.secrets when a secrets file exists — accessing it
        # otherwise renders a red "No secrets found" banner in the app.
        _candidates = [
            os.path.join(os.path.expanduser("~"), ".streamlit", "secrets.toml"),
            os.path.join(os.getcwd(), ".streamlit", "secrets.toml"),
        ]
        if any(os.path.exists(p) for p in _candidates):
            try:
                key = st.secrets["ANTHROPIC_API_KEY"]
            except Exception:
                key = ""
    return key

_REAL_API_KEY = _resolve_real_api_key()

from backend.crud import (
    get_all_customers, get_customer_360, get_portfolio_summary,
    save_agent_run, save_briefing, get_agent_runs, get_briefings, get_cost_summary,
    get_action_status, set_action_status, get_action_summary, get_implementation_overview
)
from backend.context_builder import build_customer_context, build_portfolio_context
from agents.agents import AGENT_REGISTRY, AGENT_DESCRIPTIONS, AGENT_MODEL_TIER
from agents.model_router import route as _route
from backend.database import fetchall

AGENT_DISPLAY = {
    "CustomerHealthAgent":       "Health Assessment",
    "ImplementationAgent":       "Implementation Report",
    "BriefingAgent":             "Executive Briefing",
    "EscalationCommanderAgent":  "Escalation Command",
    "SkeptikQAAgent":            "Skeptik QA Review",
    "VPChiefOfStaffAgent":       "VP Weekly Review",
    "ExpansionOpportunityAgent": "Expansion Opportunity",
    "QBRPreparationAgent":       "QBR Preparation",
    "SuccessPlanAgent":          "Success Plan",
}

def agent_display_name(name: str) -> str:
    return AGENT_DISPLAY.get(name, name.replace("Agent", "").strip() or name)

# ── Global styles — Onyx brand (light, pink-lavender, dark navy) ───────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

* { font-family: 'Inter', sans-serif !important; }

/* Page background — gradient lives on the NON-scrolling app container.
   Putting it on stMain (a scroll container) with background-attachment:fixed
   broke painting during reruns/scrolls, flashing the page white. The app
   container spans the viewport and never scrolls, so the gradient is stable
   no matter how long the page gets or what reruns. */
html, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"],
[data-testid="stMainBlockContainer"] {
    background: transparent !important;
}
/* Solid brand fallback — even if the gradient layer ever fails, the page is
   never stark white. */
body { background: #FBF3F8 !important; }
/* Gradient painted on a fixed full-viewport layer BEHIND all content.
   position:fixed + z-index:-1 is immune to scroll containers, reruns, and
   content height changes. */
body::before {
    content: "";
    position: fixed;
    inset: 0;
    z-index: -1;
    background: linear-gradient(160deg, #FFFFFF 0%, #FDF4F8 30%, #FAEFF6 58%, #F4EAF6 100%);
}

/* Tighter main content padding */
[data-testid="stMainBlockContainer"] { padding: 1.4rem 1.8rem 2.5rem !important; max-width: 1500px; }
[data-testid="stVerticalBlockBorderWrapper"] > div { gap: 0.35rem !important; }

/* Sidebar — compact */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E8E4DC !important;
    box-shadow: 2px 0 12px rgba(27,16,64,0.06) !important;
}
[data-testid="stSidebar"] > div { padding: 0.25rem 0.8rem 1rem !important; }
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span { color: #3D3458 !important; }
[data-testid="stSidebar"] .stRadio label { color: #1B1040 !important; font-weight: 500 !important; font-size: 0.82rem !important; }

/* Hide decorations + the Deploy/menu toolbar (overlaps page content) */
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { display: none !important; }
#MainMenu { visibility: hidden !important; }

/* Typography — exec-readable scale */
h1 { color: #1B1040 !important; font-weight: 800 !important; font-size: 1.75rem !important; letter-spacing: -0.03em !important; margin-bottom: 0 !important; }
h2 { color: #1B1040 !important; font-weight: 700 !important; font-size: 1.15rem !important; letter-spacing: -0.02em !important; margin: 0 !important; }
h3 { color: #1B1040 !important; font-weight: 600 !important; font-size: 1.0rem !important; margin: 0 !important; }
p, li { color: #3D3458; font-size: 0.88rem; margin: 0; }
.stMarkdown p { color: #3D3458; font-size: 0.88rem; }

/* Cards */
.card {
    background: #FFFFFF;
    border: 1px solid #E8E4DC;
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 8px;
    box-shadow: 0 1px 4px rgba(27,16,64,0.05);
}
.card-red    { border-left: 3px solid #9B2335; }
.card-yellow { border-left: 3px solid #7A5C1E; }
.card-green  { border-left: 3px solid #2D5A3D; }

/* KPI cards */
.kpi-card {
    background: #FFFFFF;
    border: 1px solid #E8E4DC;
    border-radius: 12px;
    padding: 16px 18px;
    box-shadow: 0 1px 4px rgba(27,16,64,0.05);
    min-height: 102px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.kpi-label {
    font-size: 0.66rem; color: #6B6280; text-transform: uppercase;
    letter-spacing: 0.10em; margin-bottom: 3px; font-weight: 700;
}
.kpi-value { font-size: 1.7rem; font-weight: 800; color: #1B1040; line-height: 1.1; }
.kpi-sub   { font-size: 0.72rem; color: #6B6280; margin-top: 2px; }

/* Badges */
.badge {
    display: inline-block; padding: 2px 8px; border-radius: 20px;
    font-size: 0.67rem; font-weight: 700; margin-right: 4px; vertical-align: middle;
}
.badge-haiku  { background: #E8EDF5; color: #2D4A7A; border: 1px solid #A8BAD4; }
.badge-sonnet { background: #EDEAF4; color: #3D3458; border: 1px solid #C0BAD4; }
.badge-opus   { background: #EAE6E0; color: #1B1040; border: 1px solid #B8B0A0; }
.badge-mock   { background: #F5F0E8; color: #5C4A1E; border: 1px solid #C8B88A; }
.badge-risk-high   { background: #F5ECEC; color: #9B2335; border: 1px solid #D4AAAA; }
.badge-risk-medium { background: #F5F0E8; color: #7A5C1E; border: 1px solid #C8B88A; }
.badge-risk-low    { background: #EBF2EE; color: #2D5A3D; border: 1px solid #96BAA4; }

/* Buttons — slim Onyx pill */
.stButton > button, .stDownloadButton > button {
    border-radius: 50px !important;
    font-weight: 600 !important;
    font-size: 0.78rem !important;
    padding: 0.34rem 0.8rem !important;
    height: auto !important;
    min-height: 0 !important;
    line-height: 1.4 !important;
    transition: all 0.15s ease !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}
/* Primary — dark navy, always white text (cover kind + stBaseButton testid) */
.stButton > button[kind="primary"],
.stButton > button[kind="primaryFormSubmit"],
button[data-testid="stBaseButton-primary"] {
    background: #1B1040 !important;
    border: 1.5px solid #1B1040 !important;
    box-shadow: 0 1px 6px rgba(27,16,64,0.20) !important;
}
.stButton > button[kind="primary"]:hover,
button[data-testid="stBaseButton-primary"]:hover {
    background: #2D1A5E !important;
    border-color: #2D1A5E !important;
    box-shadow: 0 3px 10px rgba(27,16,64,0.30) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="primary"],
.stButton > button[kind="primary"] *,
button[data-testid="stBaseButton-primary"],
button[data-testid="stBaseButton-primary"] * { color: #FFFFFF !important; fill: #FFFFFF !important; }

/* Secondary + download — white, always dark navy text */
.stButton > button[kind="secondary"],
button[data-testid="stBaseButton-secondary"],
.stDownloadButton > button,
button[data-testid="stBaseButton-secondaryFormSubmit"],
button[data-testid="stDownloadButton"] {
    background: #FFFFFF !important;
    border: 1.5px solid #D0CADE !important;
    box-shadow: none !important;
}
.stButton > button[kind="secondary"]:hover,
button[data-testid="stBaseButton-secondary"]:hover,
.stDownloadButton > button:hover {
    background: #F0ECE8 !important;
    border-color: #6B6280 !important;
}
.stButton > button[kind="secondary"],
.stButton > button[kind="secondary"] *,
button[data-testid="stBaseButton-secondary"],
button[data-testid="stBaseButton-secondary"] *,
.stDownloadButton > button,
.stDownloadButton > button * { color: #1B1040 !important; fill: #1B1040 !important; }

/* Metrics — very compact */
[data-testid="stMetricLabel"] { color: #6B6280 !important; font-size: 0.62rem !important; font-weight: 700 !important; text-transform: uppercase !important; letter-spacing: 0.08em !important; }
[data-testid="stMetricValue"] { color: #1B1040 !important; font-weight: 800 !important; font-size: 1.3rem !important; }
[data-testid="stMetricDelta"] { font-size: 0.72rem !important; }
[data-testid="metric-container"] {
    background: #FFFFFF;
    border: 1px solid #E8E4DC;
    border-radius: 8px;
    padding: 10px 12px !important;
    box-shadow: 0 1px 4px rgba(27,16,64,0.04);
}

/* Tabs — slim pill */
.stTabs [data-baseweb="tab-list"] {
    background: #E8E4DC !important;
    border-radius: 50px !important;
    padding: 3px !important;
    gap: 1px !important;
    border: none !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 50px !important;
    color: #6B6280 !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    padding: 6px 16px !important;
    background: transparent !important;
    white-space: nowrap !important;
}
.stTabs [aria-selected="true"] {
    background: #1B1040 !important;
    box-shadow: 0 1px 4px rgba(27,16,64,0.22) !important;
}
.stTabs [aria-selected="true"],
.stTabs [aria-selected="true"] * {
    color: #FFFFFF !important;
    fill: #FFFFFF !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background: transparent !important;
    padding-top: 10px !important;
}
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* Selectbox trigger */
[data-baseweb="select"] > div {
    background: #FFFFFF !important;
    border: 1.5px solid #D8D3C8 !important;
    border-radius: 8px !important;
    color: #1B1040 !important;
    min-height: 36px !important;
    font-size: 0.82rem !important;
}
[data-baseweb="select"] > div:focus-within {
    border-color: #1B1040 !important;
    box-shadow: 0 0 0 2px rgba(27,16,64,0.10) !important;
}
[data-baseweb="select"] span { color: #1B1040 !important; font-size: 0.82rem !important; }

/* Dropdown list popup */
[data-baseweb="popover"] { z-index: 9999 !important; }
[data-baseweb="menu"] {
    background: #FFFFFF !important;
    border: 1px solid #E8E4DC !important;
    border-radius: 10px !important;
    box-shadow: 0 8px 24px rgba(27,16,64,0.12) !important;
    padding: 4px !important;
    overflow: hidden !important;
}
[data-baseweb="menu"] ul { padding: 0 !important; }
[role="option"] {
    background: transparent !important;
    color: #1B1040 !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 7px 10px !important;
    border-radius: 6px !important;
    margin: 1px 2px !important;
}
[role="option"]:hover, [role="option"][aria-selected="true"] {
    background: #EDE9E4 !important;
    color: #1B1040 !important;
}
[role="option"] span, [role="option"] div { color: #1B1040 !important; font-size: 0.82rem !important; }

/* Dataframe */
[data-testid="stDataFrame"] { border-radius: 10px !important; overflow: hidden !important; border: 1px solid #E8E4DC !important; }

/* Expanders — compact */
details {
    background: #FFFFFF !important;
    border: 1px solid #E8E4DC !important;
    border-radius: 8px !important;
    margin-bottom: 5px !important;
}
details > summary { padding: 8px 12px !important; font-size: 0.82rem !important; }
summary { color: #1B1040 !important; font-weight: 600 !important; }

/* Alerts */
[data-testid="stAlert"] { border-radius: 8px !important; border: none !important; padding: 8px 12px !important; font-size: 0.82rem !important; }

/* Divider */
hr { border-color: #E0DBD3 !important; margin: 8px 0 !important; }

/* Sidebar radio nav — hide radio circles, style as clean nav links */
[data-testid="stSidebar"] .stRadio > div { gap: 3px !important; }
[data-testid="stSidebar"] .stRadio > div > label {
    border-radius: 8px !important;
    padding: 8px 12px !important;
    margin-bottom: 0 !important;
    transition: background 0.12s ease !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    color: #3D3458 !important;
    display: flex !important;
    flex-wrap: wrap !important;
    align-items: center !important;
    cursor: pointer !important;
}
[data-testid="stSidebar"] .stRadio > div > label:hover { background: #EDE9E4 !important; color: #1B1040 !important; }
/* Hide the actual radio circle */
[data-testid="stSidebar"] .stRadio > div > label > div:first-child { display: none !important; }
/* Highlight selected item — left accent bar + tint */
[data-testid="stSidebar"] .stRadio > div > label[data-baseweb="radio"]:has(input:checked),
[data-testid="stSidebar"] .stRadio > div > label:has(input[type="radio"]:checked) {
    background: #F4EAF6 !important;
    box-shadow: inset 3px 0 0 #1B1040 !important;
    color: #1B1040 !important;
    font-weight: 700 !important;
}
/* Workflow section labels above nav groups (pages 1, 5, 7) */
[data-testid="stSidebar"] .stRadio > div > label:nth-child(1)::before { content: "Monitor"; }
[data-testid="stSidebar"] .stRadio > div > label:nth-child(5)::before { content: "Deliver"; margin-top: 10px; }
[data-testid="stSidebar"] .stRadio > div > label:nth-child(7)::before { content: "Govern"; margin-top: 10px; }
[data-testid="stSidebar"] .stRadio > div > label:nth-child(1)::before,
[data-testid="stSidebar"] .stRadio > div > label:nth-child(5)::before,
[data-testid="stSidebar"] .stRadio > div > label:nth-child(7)::before {
    display: block;
    width: 100%;
    font-size: 0.60rem;
    font-weight: 700;
    color: #9B93A8;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 4px;
}

/* Skeptik boxes */
.skeptik-before {
    border-left: 3px solid #3D3458;
    background: #FAF8F4; border-radius: 0 6px 6px 0; padding: 10px 12px;
    font-size: 0.82rem;
}
.skeptik-after {
    border-left: 3px solid #2D5A3D;
    background: #F4F7F4; border-radius: 0 6px 6px 0; padding: 10px 12px;
    font-size: 0.82rem;
}

/* Agent report card — executive document treatment.
   :has(.agent-report-marker) alone matches EVERY ancestor wrapper of the
   report (nested cards/watermarks); the :not(:has(...)) clause restricts the
   styling to the innermost container that directly holds the marker. */
[data-testid="stVerticalBlockBorderWrapper"]:has(.agent-report-marker):not(:has([data-testid="stVerticalBlockBorderWrapper"] .agent-report-marker)) {
    background: linear-gradient(180deg, #FDFBF7 0%, #FFFFFF 120px) !important;
    border: 1px solid #E0D8E8 !important;
    border-top: 4px solid #1B1040 !important;
    border-radius: 14px !important;
    box-shadow: 0 10px 30px rgba(27,16,64,0.10), 0 2px 6px rgba(27,16,64,0.05) !important;
    padding: 14px 30px 22px !important;
    position: relative !important;
}
/* Neutralize ancestor wrappers that merely contain a report deeper down */
[data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stVerticalBlockBorderWrapper"] .agent-report-marker) {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}
/* Watermark-style brand mark in the report's top-right corner */
[data-testid="stVerticalBlockBorderWrapper"]:has(.agent-report-marker):not(:has([data-testid="stVerticalBlockBorderWrapper"] .agent-report-marker))::after {
    content: "ONYX";
    position: absolute;
    top: 14px;
    right: 20px;
    font-size: 0.62rem;
    font-weight: 900;
    letter-spacing: 0.18em;
    color: #D8CFE4;
}
[data-testid="stVerticalBlockBorderWrapper"]:has(.agent-report-marker) [data-testid="stMarkdownContainer"] h1 {
    font-size: 1.2rem !important; margin: 8px 0 4px !important; letter-spacing: -0.02em !important;
    padding-bottom: 8px !important; border-bottom: 2px solid #1B1040 !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:has(.agent-report-marker) [data-testid="stMarkdownContainer"] h2 {
    font-size: 0.80rem !important; font-weight: 800 !important; color: #1B1040 !important;
    text-transform: uppercase !important; letter-spacing: 0.10em !important;
    margin: 20px 0 8px !important; padding: 5px 10px !important;
    background: #F4EAF6 !important; border-radius: 6px !important;
    border-bottom: none !important; display: inline-block !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:has(.agent-report-marker) [data-testid="stMarkdownContainer"] h3 {
    font-size: 0.9rem !important; margin: 12px 0 4px !important; color: #1B1040 !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:has(.agent-report-marker) [data-testid="stMarkdownContainer"] p {
    font-size: 0.88rem !important; line-height: 1.55 !important; color: #3D3458 !important; margin: 4px 0 !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:has(.agent-report-marker) [data-testid="stMarkdownContainer"] li {
    font-size: 0.88rem !important; line-height: 1.5 !important; color: #3D3458 !important; margin: 3px 0 !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:has(.agent-report-marker) [data-testid="stMarkdownContainer"] strong { color: #1B1040 !important; }
[data-testid="stVerticalBlockBorderWrapper"]:has(.agent-report-marker) [data-testid="stMarkdownContainer"] em { color: #6B6280 !important; }
[data-testid="stVerticalBlockBorderWrapper"]:has(.agent-report-marker) [data-testid="stMarkdownContainer"] hr {
    margin: 14px 0 !important; border-color: #EFEBE4 !important;
}

/* Spinner */
[data-testid="stSpinner"] > div { border-top-color: #1B1040 !important; }

/* Caption */
.stCaption { color: #6B6280 !important; font-size: 0.70rem !important; }

/* Progress bar */
.stProgress > div > div > div > div { background: #1B1040 !important; border-radius: 4px !important; }
.stProgress > div > div > div { background: #E8E4DC !important; border-radius: 4px !important; }
.stProgress { margin: 4px 0 !important; }

/* Line chart — white card, chart clipped inside the rounded border */
[data-testid="stVegaLiteChart"], [data-testid="stArrowVegaLiteChart"] {
    background: #FFFFFF !important;
    border-radius: 10px !important;
    border: 1px solid #E8E4DC !important;
    padding: 10px 12px 4px !important;
    overflow: hidden !important;
    width: 100% !important;
}
[data-testid="stVegaLiteChart"] canvas, [data-testid="stArrowVegaLiteChart"] canvas {
    background: #FFFFFF !important;
    max-width: 100% !important;
}

/* Vertical gaps between streamlit elements */
.element-container { margin-bottom: 0.55rem !important; }
.stVerticalBlock { gap: 0.55rem !important; }
div[data-testid="column"] > div { gap: 0.55rem !important; }

/* Tooltips — compact dark pill instead of full-width white slab */
[data-testid="stTooltipContent"] {
    background: #1B1040 !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
    padding: 8px 12px !important;
    font-size: 0.74rem !important;
    line-height: 1.4 !important;
    max-width: 260px !important;
    box-shadow: 0 4px 16px rgba(27,16,64,0.25) !important;
    border: none !important;
}
[data-testid="stTooltipContent"] p,
[data-testid="stTooltipContent"] * { color: #FFFFFF !important; font-size: 0.74rem !important; }

/* ── Final guaranteed overrides: white text on dark surfaces ── */
.stTabs [data-baseweb="tab-list"] button[aria-selected="true"],
.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] *,
.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] p {
    color: #FFFFFF !important; fill: #FFFFFF !important;
}
.stButton > button[kind="primary"] p,
.stButton > button[kind="primaryFormSubmit"] p,
button[data-testid="stBaseButton-primary"] p,
button[data-testid="stBaseButton-primaryFormSubmit"] p {
    color: #FFFFFF !important;
}
/* Bulletproof primary-button text — covers Streamlit 1.39 (baseButton-*) and
   1.40+ (stBaseButton-*) testids, and forces -webkit-text-fill-color which
   otherwise visually overrides `color` regardless of !important. */
button[kind="primary"], button[kind="primary"] *,
button[kind="primaryFormSubmit"], button[kind="primaryFormSubmit"] *,
[data-testid="baseButton-primary"], [data-testid="baseButton-primary"] *,
[data-testid="baseButton-primaryFormSubmit"], [data-testid="baseButton-primaryFormSubmit"] *,
[data-testid="stBaseButton-primary"], [data-testid="stBaseButton-primary"] *,
[data-testid="stBaseButton-primaryFormSubmit"], [data-testid="stBaseButton-primaryFormSubmit"] * {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}
</style>
""", unsafe_allow_html=True)


# ── Direct backend helpers (no HTTP) ─────────────────────────────────────────

@st.cache_data(ttl=20)
def fetch_customers():
    try:
        return get_all_customers()
    except Exception:
        return []

@st.cache_data(ttl=20)
def fetch_summary():
    try:
        return get_portfolio_summary()
    except Exception:
        return {}

def fetch_360(cid):
    try:
        return get_customer_360(cid)
    except Exception:
        return {}

def call_agent(agent_name, customer_id=None):
    try:
        agent = AGENT_REGISTRY[agent_name]()

        if agent_name == "VPChiefOfStaffAgent":
            context = build_portfolio_context()
            cid = None
        elif agent_name == "SkeptikQAAgent":
            runs = get_agent_runs(20)
            prior = next(
                (r for r in runs if r.get("customer_id") == customer_id
                 and r["agent_name"] != "SkeptikQAAgent"), None
            )
            if not prior:
                return {"error": "No prior agent output found. Run another agent first."}
            context = build_customer_context(customer_id)
            context["prior_agent"]      = prior["agent_name"]
            context["prior_output"]     = prior["output_text"]
            context["prior_confidence"] = prior.get("confidence_score", 0.75)
            cid = customer_id
        else:
            context = build_customer_context(customer_id)
            cid = customer_id

        result = agent.run(context, customer_id=cid)
        run_id = save_agent_run(result)

        if agent_name in ("BriefingAgent", "VPChiefOfStaffAgent"):
            briefing_type = "CEO" if agent_name == "BriefingAgent" else "VP_CX"
            save_briefing(briefing_type, cid, result.output_text, run_id)

        routing = _route(agent_name)
        return {
            "run_id":             run_id,
            "agent_name":         result.agent_name,
            "agent_description":  AGENT_DESCRIPTIONS.get(agent_name, ""),
            "customer_id":        result.customer_id,
            "model_used":         result.model_used,
            "model_display":      result.model_display,
            "model_tier":         AGENT_MODEL_TIER.get(agent_name, "sonnet"),
            "model_rationale":    result.model_rationale,
            "input_tokens":       result.input_tokens,
            "output_tokens":      result.output_tokens,
            "estimated_cost_usd": result.estimated_cost_usd,
            "confidence_score":   result.confidence_score,
            "output_text":        result.output_text,
            "structured":         result.to_dict().get("structured"),
            "created_at":         result.created_at,
            "is_mock":            result.is_mock,
        }
    except Exception as e:
        return {"error": str(e)}

def call_portfolio_health():
    try:
        customers = get_all_customers()
        agent     = AGENT_REGISTRY["CustomerHealthAgent"]()
        results   = []
        for c in customers:
            context = build_customer_context(c["id"])
            result  = agent.run(context, customer_id=c["id"])
            run_id  = save_agent_run(result)
            results.append({
                "customer_id":        c["id"],
                "customer_name":      c["name"],
                "arr":                c["arr"],
                "health_score":       result.structured.health_score if result.structured else c["health_score"],
                "risk_level":         result.structured.risk_level if result.structured else c.get("risk_level","?"),
                "confidence_score":   result.confidence_score,
                "top_risk_drivers":   result.structured.top_risk_drivers[:2] if result.structured else [],
                "recommended_actions":result.structured.recommended_actions[:2] if result.structured else [],
                "run_id":             run_id,
                "model_used":         result.model_used,
                "estimated_cost_usd": result.estimated_cost_usd,
            })
        results.sort(key=lambda r: r["health_score"])
        return {
            "scan_completed_at": result.created_at,
            "customers_scanned": len(results),
            "total_cost_usd":    round(sum(r["estimated_cost_usd"] for r in results), 6),
            "results":           results,
        }
    except Exception as e:
        return {"error": str(e)}

def call_impl_digest():
    try:
        impls  = fetchall("SELECT DISTINCT customer_id FROM implementations")
        agent  = AGENT_REGISTRY["ImplementationAgent"]()
        results = []
        for row in impls:
            cid     = row["customer_id"]
            context = build_customer_context(cid)
            result  = agent.run(context, customer_id=cid)
            run_id  = save_agent_run(result)
            results.append({
                "customer_id":         cid,
                "customer_name":       context["customer_name"],
                "overall_status":      result.structured.overall_status if result.structured else "?",
                "pct_complete":        result.structured.pct_complete if result.structured else 0,
                "launch_confidence":   result.structured.launch_confidence if result.structured else "Unknown",
                "active_blockers":     result.structured.active_blockers[:2] if result.structured else [],
                "recommended_intervention": result.structured.recommended_intervention if result.structured else "",
                "run_id":              run_id,
                "estimated_cost_usd":  result.estimated_cost_usd,
            })
        results.sort(key=lambda r: {"Very Low":0,"Low":1,"Medium":2,"High":3}.get(r["launch_confidence"],2))
        return {
            "projects_reviewed": len(results),
            "total_cost_usd":    round(sum(r["estimated_cost_usd"] for r in results), 6),
            "results":           results,
        }
    except Exception as e:
        return {"error": str(e)}

def fetch_audit(limit=50, agent_name=None, customer_id=None):
    try:
        runs = get_agent_runs(limit)
        if agent_name:  runs = [r for r in runs if r["agent_name"] == agent_name]
        if customer_id: runs = [r for r in runs if r.get("customer_id") == customer_id]
        return runs
    except Exception:
        return []

def fetch_briefings(btype=None, cid=None):
    try:
        return get_briefings(btype, cid)
    except Exception:
        return []

def fetch_costs():
    try:
        return get_cost_summary()
    except Exception:
        return {}


# ── UI utilities ──────────────────────────────────────────────────────────────

def risk_icon(level):
    return {"High": "High risk", "Medium": "Medium risk", "Low": "Healthy",
            "Critical": "Critical", "At Risk": "At risk", "Healthy": "Healthy"}.get(level, "")

def health_color(score):
    if score < 40: return "#9B2335"
    if score < 60: return "#7A5C1E"
    return "#2D5A3D"

def model_tier_from_id(model_id):
    if "haiku" in model_id.lower(): return "haiku"
    if "opus"  in model_id.lower(): return "opus"
    return "sonnet"

def tier_color(tier):
    return {"haiku": "#2D4A7A", "sonnet": "#3D3458", "opus": "#1B1040"}.get(tier, "#1B1040")

def render_meta_pills(result):
    """Compact, subtle pill strip: model tier · confidence · cost · tokens."""
    tier  = result.get("model_tier") or model_tier_from_id(result.get("model_used",""))
    color = tier_color(tier)
    conf  = result.get("confidence_score", 0)
    conf_color = "#2D5A3D" if conf >= 0.75 else "#7A5C1E" if conf >= 0.55 else "#9B2335"
    disp  = result.get("model_display") or result.get("model_used","?")
    mock_pill = ("<span style='background:#F5F0E8;color:#7A5C1E;border:1px solid #D8C89A;"
                 "border-radius:20px;padding:2px 10px;font-size:0.68rem;font-weight:700'>MOCK</span>") if result.get("is_mock") else ""

    sep = "<span style='color:#C8C2B8'>·</span>"
    pills = (
        "<div style=\"display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin:2px 0 10px\">"
        f"<span style=\"background:#FFFFFF;border:1px solid {color};color:{color};border-radius:20px;padding:2px 11px;font-size:0.70rem;font-weight:700\">{disp}</span>"
        f"{sep}"
        f"<span style=\"color:#6B6280;font-size:0.72rem\">Confidence <b style=\"color:{conf_color}\">{conf:.0%}</b></span>"
        f"{sep}"
        f"<span style=\"color:#6B6280;font-size:0.72rem\">Est. cost <b style=\"color:#3D3458\">${result.get('estimated_cost_usd',0):.4f}</b></span>"
        f"{sep}"
        f"<span style=\"color:#6B6280;font-size:0.72rem\">{result.get('input_tokens',0):,} in · {result.get('output_tokens',0):,} out</span>"
        f"{mock_pill}"
        "</div>"
    )
    st.markdown(pills, unsafe_allow_html=True)


def render_model_meta(result, expanded=False, nested=False):
    """Backwards-compatible meta renderer used by some pages."""
    render_meta_pills(result)
    rationale = result.get("model_rationale", "")
    if rationale and not nested:
        with st.expander("Model routing rationale", expanded=expanded):
            st.markdown(f"<div style='color:#6B6280;font-size:0.82rem;font-style:italic'>{rationale}</div>", unsafe_allow_html=True)


def render_agent_output(result, show_structured=True, nested=False):
    """Full agent result renderer: compact meta + styled report card.

    Set nested=True when rendered inside an st.expander to avoid nesting
    expanders (which Streamlit disallows).
    """
    if "error" in result:
        st.error(f"Agent error: {result['error']}")
        return

    render_meta_pills(result)

    # Output rendered inside a bordered container styled as an executive report
    report = st.container(border=True)
    with report:
        st.markdown("<span class='agent-report-marker'></span>", unsafe_allow_html=True)
        st.markdown(result.get("output_text", ""), unsafe_allow_html=False)

    ts = result.get("created_at", "")[:16].replace("T", " ")
    st.caption(f"Generated {ts} UTC · Run #{result.get('run_id','?')} · {agent_display_name(result.get('agent_name',''))}")

    # Details tucked away — routing rationale + parsed structured output
    rationale = result.get("model_rationale", "")
    has_struct = show_structured and result.get("structured")
    if (rationale or has_struct) and not nested:
        with st.expander("Run details · model routing & structured data", expanded=False):
            if rationale:
                st.markdown(f"<div style='font-size:0.72rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:4px'>Why this model</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='color:#6B6280;font-size:0.82rem;font-style:italic;margin-bottom:10px'>{rationale}</div>", unsafe_allow_html=True)
            if has_struct:
                st.markdown(f"<div style='font-size:0.72rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:4px'>Structured output</div>", unsafe_allow_html=True)
                st.json(result["structured"], expanded=False)
    elif has_struct and nested:
        st.json(result["structured"], expanded=False)


def page_header(title, subtitle=""):
    today = datetime.now().strftime("%A, %B %d, %Y")
    sub = f"<div style='color:#6B6280;font-size:0.84rem;margin-top:2px'>{subtitle}</div>" if subtitle else ""
    st.markdown(f"""
<div style="display:flex;align-items:flex-end;justify-content:space-between;gap:16px;
     border-bottom:1px solid #E8E4DC;padding-bottom:12px;margin-bottom:16px">
  <div><h1 style="margin:0">{title}</h1>{sub}</div>
  <div style="text-align:right;flex-shrink:0">
    <div style="font-size:0.70rem;color:#9B93A8">{today}</div>
    <div style="font-size:0.66rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.10em;margin-top:2px">Onyx · Secure AI Control Plane</div>
  </div>
</div>""", unsafe_allow_html=True)


_export_counter = [0]
def export_button(content: str, filename: str, label: str = "Export"):
    _export_counter[0] += 1
    st.download_button(label=label, data=content, file_name=filename,
                       mime="text/markdown", key=f"dl_{_export_counter[0]}_{filename[:20]}")


# ── Executive dashboard helpers ───────────────────────────────────────────────

import random as _rnd

def mom_delta(metric_key, magnitude=1.0):
    """Deterministic month-over-month delta for a metric (stable across reruns).
    Returns (text, direction) where direction is 'up' | 'down' | 'flat'."""
    r = _rnd.Random(hash(metric_key) & 0xffffffff)
    val = round(r.uniform(-magnitude, magnitude), 1)
    if abs(val) < magnitude * 0.15:
        return ("flat", "flat")
    return (f"{'+' if val > 0 else ''}{val}", "up" if val > 0 else "down")

def kpi_card(label, value, sub="", delta=None, delta_dir="flat", good_when="up"):
    """Render an executive KPI card with optional MoM delta + risk coloration."""
    if delta is not None and delta_dir != "flat":
        is_good = (delta_dir == good_when)
        dcolor  = "#2D5A3D" if is_good else "#9B2335"
        arrow   = "▲" if delta_dir == "up" else "▼"
        delta_html = f"<span style='color:{dcolor};font-size:0.66rem;font-weight:700'>{arrow} {delta}</span>"
    elif delta is not None:
        delta_html = "<span style='color:#9B93A8;font-size:0.66rem;font-weight:600'>— flat</span>"
    else:
        delta_html = ""
    sub_html = f"<span style='color:#9B93A8;font-size:0.62rem'>{sub}</span>" if sub else ""
    sep = " &nbsp;·&nbsp; " if (delta_html and sub_html) else ""
    return (
        f"<div class='kpi-card'>"
        f"<div class='kpi-label'>{label}</div>"
        f"<div class='kpi-value'>{value}</div>"
        f"<div style='margin-top:2px'>{delta_html}{sep}{sub_html}</div>"
        f"</div>"
    )

def build_exec_summary(summary, customers):
    """Generate a VP-style weekly narrative dynamically from portfolio data."""
    nrr   = summary.get("nrr_pct", 0)
    grr   = summary.get("grr_pct", 0)
    hi    = summary.get("critical_count", 0)
    arr_risk = summary.get("arr_at_risk", 0)
    exp   = summary.get("expansion_pipeline_arr", 0)
    esc   = summary.get("open_escalations", 0)
    fc    = summary.get("renewal_forecast_pct", 0)

    # Top 2 at-risk strategic/enterprise accounts by ARR
    at_risk = sorted([c for c in customers if c["risk_level"] == "High"],
                     key=lambda c: -c["arr"])[:2]
    risk_names = " and ".join(c["name"] for c in at_risk) if at_risk else "no major accounts"

    # Leading industry in expansion
    exp_by_ind = {}
    for c in customers:
        if c.get("expansion_pipeline_arr"):
            exp_by_ind[c["industry"]] = exp_by_ind.get(c["industry"], 0) + c["expansion_pipeline_arr"]
    lead_ind = max(exp_by_ind, key=exp_by_ind.get) if exp_by_ind else "financial services"

    health_word = "stable" if nrr >= 105 else "under pressure" if nrr < 100 else "holding"
    b = lambda t: f"<strong style='color:#FFFFFF;font-weight:700'>{t}</strong>"
    sentences = [
        f"Net revenue retention is {nrr}% with gross retention at {grr}%, leaving portfolio health {b(health_word)}.",
        f"{hi} account{'s' if hi != 1 else ''} {'are' if hi != 1 else 'is'} in high-risk status representing {b(f'${arr_risk/1e6:.1f}M')} of ARR — most notably {risk_names}, driven by adoption decline and unresolved escalations.",
        f"The 90-day renewal forecast stands at {b(f'{fc}%')}, with {esc} active escalation{'s' if esc != 1 else ''} requiring attention.",
        f"Expansion pipeline totals {b(f'${exp/1e6:.1f}M')}, led by strong growth in {lead_ind} accounts.",
    ]
    return " ".join(sentences)


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("<div style='padding:10px 0 6px'><span style='font-size:1.3rem;font-weight:900;color:#1B1040;letter-spacing:-0.04em'>ONYX</span><span style='font-size:0.65rem;font-weight:700;color:#6B6280;letter-spacing:0.12em;margin-left:8px;vertical-align:middle'>CX AGENT OS</span></div>", unsafe_allow_html=True)

    # Ordered to follow the exec workflow: monitor → inspect → deliver → report → govern
    _pages = ["Executive Dashboard", "Customer 360", "Implementation Digest", "CSM Performance",
              "Briefings", "Agent Console", "Audit Trail & Costs"]
    # Single source of truth: the radio's own key holds the current page.
    # Programmatic navigation from other pages stages "_pending_nav" and reruns;
    # we apply it here (before the widget is instantiated) to avoid Streamlit's
    # "cannot modify a widget key after instantiation" error.
    if "_pending_nav" in st.session_state:
        st.session_state["nav_page"] = st.session_state.pop("_pending_nav")
    if st.session_state.get("nav_page") not in _pages:
        st.session_state["nav_page"] = "Executive Dashboard"
    page = st.radio(
        "",
        _pages,
        label_visibility="collapsed",
        key="nav_page",
    )

    st.markdown("---")
    summary = fetch_summary()
    if summary:
        arr_risk = summary.get('arr_at_risk', 0)
        total    = summary.get('total_arr', 1)
        pct      = arr_risk / total * 100
        hi  = summary.get('critical_count', 0)
        med = summary.get('at_risk_count', 0)
        ok  = summary.get('healthy_count', 0)
        st.markdown(f"""
<div style="background:#FFFFFF;border:1px solid #E8E4DC;border-radius:10px;padding:10px 12px;margin-bottom:2px">
  <div style="font-size:0.62rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.10em;margin-bottom:8px">Portfolio</div>
  <div style="display:flex;gap:6px;margin-bottom:10px">
    <div style="flex:1;background:#FDF1F2;border-radius:7px;padding:6px 8px;text-align:center">
      <div style="font-size:1.1rem;font-weight:800;color:#9B2335;line-height:1">{hi}</div>
      <div style="font-size:0.60rem;color:#9B2335;font-weight:600;margin-top:1px">High</div>
    </div>
    <div style="flex:1;background:#FDF8EE;border-radius:7px;padding:6px 8px;text-align:center">
      <div style="font-size:1.1rem;font-weight:800;color:#7A5C1E;line-height:1">{med}</div>
      <div style="font-size:0.60rem;color:#7A5C1E;font-weight:600;margin-top:1px">Med</div>
    </div>
    <div style="flex:1;background:#EFF6F1;border-radius:7px;padding:6px 8px;text-align:center">
      <div style="font-size:1.1rem;font-weight:800;color:#2D5A3D;line-height:1">{ok}</div>
      <div style="font-size:0.60rem;color:#2D5A3D;font-weight:600;margin-top:1px">OK</div>
    </div>
  </div>
  <div style="border-top:1px solid #E8E4DC;padding-top:8px;display:flex;align-items:baseline;justify-content:space-between">
    <div>
      <div style="font-size:1.15rem;font-weight:800;color:#9B2335;line-height:1">${arr_risk/1e6:.1f}M</div>
      <div style="font-size:0.62rem;color:#6B6280;margin-top:1px">ARR at risk</div>
    </div>
    <div style="text-align:right">
      <div style="font-size:1.15rem;font-weight:800;color:#1B1040;line-height:1">{pct:.0f}%</div>
      <div style="font-size:0.62rem;color:#6B6280;margin-top:1px">of portfolio</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("---")

    # Quick agent run shortcuts
    customers = fetch_customers()
    if customers:
        st.markdown("<div style='font-size:0.68rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.10em;margin:4px 0 6px'>Quick Run</div>", unsafe_allow_html=True)
        qcust = st.selectbox("Customer", [c["id"] for c in customers],
                             format_func=lambda x: next((c["name"] for c in customers if c["id"]==x), str(x)),
                             key="sidebar_cust", label_visibility="collapsed")
        if st.button("Health Check", use_container_width=True, key="sb_health", type="secondary"):
            st.session_state["quick_run"] = ("CustomerHealthAgent", qcust)
            st.rerun()

    st.markdown("---")

    # ── Footer controls: data mode + agent guide ──────────────────────────────
    if _REAL_API_KEY:
        live = st.toggle("Live Anthropic API", value=st.session_state.get("live_api", False))
        st.session_state["live_api"] = live
        if live:
            os.environ["ANTHROPIC_API_KEY"] = _REAL_API_KEY
            st.markdown("<div style='font-size:0.66rem;color:#2D5A3D;font-weight:700;margin:-4px 0 6px'>LIVE — calling Claude</div>", unsafe_allow_html=True)
        else:
            os.environ.pop("ANTHROPIC_API_KEY", None)
            st.markdown("<div style='font-size:0.66rem;color:#7A5C1E;font-weight:700;margin:-4px 0 6px'>MOCK — no API calls</div>", unsafe_allow_html=True)
    else:
        os.environ.pop("ANTHROPIC_API_KEY", None)
        st.session_state["live_api"] = False
        st.markdown("<div style='font-size:0.66rem;color:#7A5C1E;font-weight:700;margin:0 0 6px'>MOCK — set ANTHROPIC_API_KEY to enable live</div>", unsafe_allow_html=True)

    if st.button("About the Agents", use_container_width=True, key="sb_about", type="secondary"):
        st.session_state["show_agent_guide"] = True



@st.dialog("Agent Guide", width="large")
def show_agent_guide():
    AGENTS = [
        {
            "name": "Customer Health Agent",
            "icon": "🩺",
            "model": "Haiku",
            "model_color": "#2D4A7A",
            "model_bg": "#E8EDF5",
            "when": "Run first — gives you the overall risk picture for any customer.",
            "what": "Scores customer health 0–100, identifies the top risk drivers pulling the score down, surfaces early warning signals (champion disengagement, declining DAU, overdue milestones), and lists concrete recommended actions.",
            "outputs": ["Health score & risk level", "Top risk drivers (ranked)", "Early warning signals", "Positive signals", "Recommended actions", "Confidence score + rationale"],
        },
        {
            "name": "Implementation Agent",
            "icon": "🔧",
            "model": "Sonnet",
            "model_color": "#3D3458",
            "model_bg": "#EDEAF4",
            "when": "Use when a customer is in onboarding or has active implementation milestones.",
            "what": "Reviews all milestones, calculates % complete, identifies blockers and delayed items, rates launch confidence (Very Low → High), and drafts an owner action plan with intervention recommendations.",
            "outputs": ["Overall status & % complete", "Launch confidence rating", "Delayed milestones & blockers", "Owner action plan", "Executive summary", "Recommended intervention"],
        },
        {
            "name": "Briefing Agent",
            "icon": "📋",
            "model": "Sonnet",
            "model_color": "#3D3458",
            "model_bg": "#EDEAF4",
            "when": "Before a QBR, exec meeting, or renewal conversation with a customer.",
            "what": "Generates a CEO-ready executive briefing covering the business situation, risk narrative, key asks, and a 30/60/90-day action plan. Written for a non-technical exec audience with zero fluff.",
            "outputs": ["Situation summary", "Business risk & financial impact", "Key asks from the customer", "30 / 60 / 90-day plan", "Recommended executive action", "Risk narrative"],
        },
        {
            "name": "Escalation Commander",
            "icon": "🚨",
            "model": "Opus",
            "model_color": "#1B1040",
            "model_bg": "#EAE6E0",
            "when": "When a customer has an active escalation or is at risk of churning imminently.",
            "what": "Performs a full crisis analysis: determines likely root cause, quantifies customer impact, maps internal owners, builds a 48-hour recovery plan and 2-week stabilization plan, and drafts executive communications.",
            "outputs": ["Severity assessment", "Root cause analysis", "Customer impact statement", "Internal owner map", "48-hour recovery plan", "2-week stabilization plan", "Executive comms draft"],
        },
        {
            "name": "Skeptik QA Agent",
            "icon": "🔍",
            "model": "Opus",
            "model_color": "#1B1040",
            "model_bg": "#EAE6E0",
            "when": "After running any other agent — especially before sharing a briefing or escalation plan with executives.",
            "what": "Adversarially reviews the most recent agent output for that customer. Challenges unsupported claims, flags missing evidence, identifies overconfident conclusions, and suggests alternative explanations. Revises the confidence score.",
            "outputs": ["Unsupported claims", "Missing evidence", "Overconfident conclusions", "Alternative explanations", "Recommended edits", "Revised confidence score", "Verdict (Approved / Needs Revision / Reject)"],
        },
        {
            "name": "VP Chief of Staff",
            "icon": "📊",
            "model": "Opus",
            "model_color": "#1B1040",
            "model_bg": "#EAE6E0",
            "when": "Weekly — generates the VP CX operating review across the full portfolio.",
            "what": "Synthesizes the entire portfolio into a board-ready weekly review: top 5 risks, ARR at risk, renewal watchlist, implementation bottlenecks, product feedback themes, support burden, cross-functional asks, and a CEO-ready paragraph summary.",
            "outputs": ["Portfolio health summary", "Top 5 risks + actions", "ARR at risk breakdown", "Renewals watchlist", "Impl bottlenecks", "Product feedback themes", "Cross-functional asks", "CEO-ready paragraph"],
        },
        {
            "name": "Expansion Opportunity Agent",
            "icon": "", "model": "Sonnet", "model_color": "#3D3458", "model_bg": "#EDEAF4",
            "when": "When an account is healthy and you want to quantify and land upsell.",
            "what": "Builds an evidence-backed expansion thesis, recommends modules to cross-sell, projects ARR uplift, and lays out a concrete play timed to the renewal — grounded in adoption, ROI, and relationship signals.",
            "outputs": ["Expansion thesis", "Recommended modules", "Projected ARR uplift", "Confidence", "Proof points", "Recommended play", "Best timing"],
        },
        {
            "name": "QBR Preparation Agent",
            "icon": "", "model": "Sonnet", "model_color": "#3D3458", "model_bg": "#EDEAF4",
            "when": "Ahead of a Quarterly Business Review with any customer.",
            "what": "Assembles an executive-ready QBR briefing: value delivered, adoption summary, open items, a proposed agenda, expansion talking points, and success metrics to review with the customer.",
            "outputs": ["Executive headline", "Value delivered", "Adoption summary", "Open items", "Proposed agenda", "Expansion talking points", "Success metrics"],
        },
        {
            "name": "Success Plan Agent",
            "icon": "", "model": "Sonnet", "model_color": "#3D3458", "model_bg": "#EDEAF4",
            "when": "For at-risk or onboarding accounts that need a structured path to value.",
            "what": "Creates a time-phased 30/60/90 success plan: objective, current vs. target state, owned workstreams, dated milestones, success metrics, and risks with mitigations.",
            "outputs": ["Objective", "Current & target state", "Workstreams", "30/60/90 milestones", "Success metrics", "Risks & mitigations"],
        },
    ]

    # model routing legend
    st.markdown("""
<div style="display:flex;gap:8px;margin-bottom:18px;flex-wrap:wrap">
  <div style="font-size:0.68rem;color:#6B6280;align-self:center;margin-right:4px;font-weight:600;text-transform:uppercase;letter-spacing:0.08em">Model routing</div>
  <span style="background:#E8EDF5;color:#2D4A7A;font-size:0.68rem;font-weight:700;padding:3px 10px;border-radius:20px">Haiku — fast scanning</span>
  <span style="background:#EDEAF4;color:#3D3458;font-size:0.68rem;font-weight:700;padding:3px 10px;border-radius:20px">Sonnet — synthesis</span>
  <span style="background:#EAE6E0;color:#1B1040;font-size:0.68rem;font-weight:700;padding:3px 10px;border-radius:20px">Opus — judgment & adversarial</span>
</div>
""", unsafe_allow_html=True)

    for i, a in enumerate(AGENTS):
        outputs_html = "".join(
            f'<span style="background:#F5F2EE;color:#3D3458;font-size:0.67rem;font-weight:600;'
            f'padding:2px 9px;border-radius:20px;border:1px solid #E8E4DC">{o}</span>'
            for o in a["outputs"]
        )
        border_top = "border-top:1px solid #E8E4DC;" if i > 0 else ""
        st.markdown(f"""
<div style="padding:16px 4px;{border_top}">
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:7px">
    <div style="font-size:1.0rem;font-weight:800;color:#1B1040;letter-spacing:-0.01em">{a['name']}</div>
    <span style="background:{a['model_bg']};color:{a['model_color']};font-size:0.65rem;font-weight:700;
          padding:3px 10px;border-radius:20px;flex-shrink:0">{a['model']}</span>
  </div>
  <div style="font-size:0.78rem;color:#3D3458;line-height:1.55;margin-bottom:8px">{a['what']}</div>
  <div style="font-size:0.70rem;color:#6B6280;margin-bottom:10px;padding:5px 10px;
       background:#F5F2EE;border-radius:6px;border-left:2px solid #D8D3C8">
    When: {a['when']}
  </div>
  <div style="display:flex;flex-wrap:wrap;gap:4px">{outputs_html}</div>
</div>
""", unsafe_allow_html=True)


# Show agent guide dialog
if st.session_state.pop("show_agent_guide", False):
    show_agent_guide()


# Handle quick run from sidebar
if "quick_run" in st.session_state:
    agent_name, cid = st.session_state.pop("quick_run")
    with st.spinner(f"Running {agent_name}..."):
        result = call_agent(agent_name, cid)
    st.session_state["console_result"] = result
    st.session_state["_pending_nav"] = "Agent Console"
    st.rerun()


# ── Data sources banner (shown on every page) ─────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;background:#FFFFFF;border:1px solid #E8E4DC;border-radius:10px;padding:7px 14px;margin-bottom:14px">
  <span style="font-size:0.65rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.10em;margin-right:4px;white-space:nowrap">Data Sources</span>
  <span style="display:inline-flex;align-items:center;gap:5px;background:#fff;border:1px solid #E8E4DC;border-radius:50px;padding:3px 10px 3px 4px"><span style="background:#00A1E0;color:#fff;font-size:0.58rem;font-weight:800;width:17px;height:17px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center">SF</span><span style="font-size:0.72rem;font-weight:600;color:#3D3458">Salesforce</span></span>
  <span style="display:inline-flex;align-items:center;gap:5px;background:#fff;border:1px solid #E8E4DC;border-radius:50px;padding:3px 10px 3px 4px"><span style="background:#03363D;color:#fff;font-size:0.58rem;font-weight:800;width:17px;height:17px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center">ZD</span><span style="font-size:0.72rem;font-weight:600;color:#3D3458">Zendesk</span></span>
  <span style="display:inline-flex;align-items:center;gap:5px;background:#fff;border:1px solid #E8E4DC;border-radius:50px;padding:3px 10px 3px 4px"><span style="background:#F6821F;color:#fff;font-size:0.58rem;font-weight:800;width:17px;height:17px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center">GS</span><span style="font-size:0.72rem;font-weight:600;color:#3D3458">Gainsight</span></span>
  <span style="display:inline-flex;align-items:center;gap:5px;background:#fff;border:1px solid #E8E4DC;border-radius:50px;padding:3px 10px 3px 4px"><span style="background:#3D3458;color:#fff;font-size:0.58rem;font-weight:800;width:17px;height:17px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center">@</span><span style="font-size:0.72rem;font-weight:600;color:#3D3458">Email</span></span>
  <span style="margin-left:auto;font-size:0.65rem;color:#9B93A8;font-style:italic">Synthetic demo data</span>
</div>
""", unsafe_allow_html=True)
# PAGE: PORTFOLIO DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

if page == "Executive Dashboard":
    page_header("Executive Dashboard", "The state of the customer base at a glance")

    summary   = fetch_summary()
    customers = fetch_customers()

    if not summary or not customers:
        st.error("Failed to load data. Check that the database is initialized.")
        st.stop()

    total_arr = summary.get('total_arr', 0)
    arr_risk  = summary.get('arr_at_risk', 0)
    hi_c      = summary.get('critical_count', 0)
    med_c     = summary.get('at_risk_count', 0)
    ok_c      = summary.get('healthy_count', 0)
    total_c   = max(summary.get('total_customers', 1), 1)

    # ── Metric values ─────────────────────────────────────────────────────────
    nrr  = summary.get("nrr_pct", 0)
    grr  = summary.get("grr_pct", 0)
    fc   = summary.get("renewal_forecast_pct", 0)
    churn = summary.get("churn_risk_pct", 0)
    exp  = summary.get("expansion_pipeline_arr", 0)
    ttv  = summary.get("avg_time_to_value_days", 0)
    adopt = summary.get("avg_adoption", 0)
    esc_n = summary.get("open_escalations", 0)
    act   = get_action_summary()

    d_nrr   = mom_delta("nrr", 3.0)
    d_grr   = mom_delta("grr", 2.0)
    d_fc    = mom_delta("forecast", 4.0)
    d_exp   = mom_delta("expansion", 8.0)
    d_ttv   = mom_delta("ttv", 5.0)
    d_adopt = mom_delta("adoption", 4.0)
    d_esc   = mom_delta("escalations", 2.0)

    # ── AI Executive Summary (narrative first — the "so what") ─────────────────
    st.markdown(f"""
<div style="background:linear-gradient(135deg,#1B1040 0%,#2D2154 100%);border-radius:12px;
     padding:16px 20px;margin:2px 0 16px">
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
    <span style="font-size:0.62rem;font-weight:700;color:#B9AEE0;text-transform:uppercase;letter-spacing:0.12em">AI Executive Summary</span>
    <span style="font-size:0.58rem;color:#8579B0;background:#ffffff14;padding:2px 8px;border-radius:20px">Weekly · auto-generated</span>
  </div>
  <div style="color:#F0EDF7;font-size:0.92rem;line-height:1.65">{build_exec_summary(summary, customers)}</div>
</div>
""", unsafe_allow_html=True)

    # ── 5 hero KPIs ───────────────────────────────────────────────────────────
    hero = st.columns(5)
    hero_cards = [
        kpi_card("Net Revenue Retention", f"{nrr}%", "ARR-weighted", d_nrr[0], d_nrr[1], good_when="up"),
        kpi_card("ARR at Risk", f"${arr_risk/1e6:.1f}M", f"{hi_c} high · {med_c} medium", None, "down", good_when="down"),
        kpi_card("Renewal Forecast (90d)", f"{fc}%", f"${summary.get('upcoming_renewal_arr',0)/1e6:.1f}M up for renewal", d_fc[0], d_fc[1], good_when="up"),
        kpi_card("Expansion Pipeline", f"${exp/1e6:.1f}M", "open upsell ARR", d_exp[0], d_exp[1], good_when="up"),
        kpi_card("AI Actions Taken", f"{act['actions_actioned']}/{act['at_risk_accounts']}",
                 f"${act['arr_protected']/1e6:.1f}M ARR protected · {act['coverage_pct']:.0f}% of at-risk"),
    ]
    for col, card in zip(hero, hero_cards):
        col.markdown(card, unsafe_allow_html=True)

    st.markdown("<div style='margin:14px 0 2px'></div>", unsafe_allow_html=True)

    # ── Secondary metrics (drill-in) ──────────────────────────────────────────
    with st.expander("More portfolio metrics"):
        m = st.columns(5)
        more_cards = [
            kpi_card("Gross Revenue Retention", f"{grr}%", "ARR-weighted", d_grr[0], d_grr[1], good_when="up"),
            kpi_card("Avg Time to Value", f"{ttv}d", "to first value", d_ttv[0], d_ttv[1], good_when="down"),
            kpi_card("Product Adoption", f"{adopt:.0f}%", "portfolio average", d_adopt[0], d_adopt[1], good_when="up"),
            kpi_card("Open Escalations", str(esc_n), f"NPS {summary.get('avg_nps',0)} avg", d_esc[0], d_esc[1], good_when="down"),
            kpi_card("Churn Risk", f"{churn}%", f"{hi_c} accounts high-risk", None, "down", good_when="down"),
        ]
        for col, card in zip(m, more_cards):
            col.markdown(card, unsafe_allow_html=True)

    st.markdown("<div style='margin:6px 0 4px'></div>", unsafe_allow_html=True)

    # ── At-Risk Accounts + Expansion Opportunities ────────────────────────────
    col_risk, col_exp = st.columns(2)

    with col_risk:
        st.markdown("<div style='font-size:0.72rem;font-weight:700;color:#9B2335;text-transform:uppercase;letter-spacing:0.10em;margin-bottom:8px'>Accounts Requiring Attention</div>", unsafe_allow_html=True)
        at_risk = sorted([c for c in customers if c["risk_level"] == "High"], key=lambda c: -c["arr"])[:5]
        for c in at_risk:
            st.markdown(f"""
<div style="background:#FFFFFF;border:1px solid #E8E4DC;border-left:3px solid #9B2335;
     border-radius:8px;padding:10px 13px;margin-bottom:8px">
  <div style="display:flex;justify-content:space-between;align-items:baseline">
    <span style="font-weight:700;color:#1B1040;font-size:0.86rem">{c['name']}</span>
    <span style="font-size:0.7rem;color:#9B2335;font-weight:700">${c['arr']/1e3:.0f}K ARR</span>
  </div>
  <div style="font-size:0.7rem;color:#6B6280;margin-top:1px">{c['industry']} · {c['customer_tier']} · {c['region']}</div>
  <div style="font-size:0.74rem;color:#3D3458;margin-top:6px;line-height:1.4"><b style="color:#9B2335">Why:</b> {c['primary_risk_reason']}</div>
  <div style="font-size:0.74rem;color:#3D3458;margin-top:3px;line-height:1.4"><b style="color:#2D5A3D">Action:</b> {c['recommended_next_action']}</div>
</div>""", unsafe_allow_html=True)

    with col_exp:
        st.markdown("<div style='font-size:0.72rem;font-weight:700;color:#2D5A3D;text-transform:uppercase;letter-spacing:0.10em;margin-bottom:8px'>Expansion Opportunities</div>", unsafe_allow_html=True)
        exp_accts = sorted([c for c in customers if c.get("expansion_pipeline_arr")],
                           key=lambda c: -(c["expansion_pipeline_arr"] * c.get("upsell_likelihood", 0)))[:5]
        for c in exp_accts:
            ep = c["expansion_pipeline_arr"]
            ul = c.get("upsell_likelihood", 0)
            st.markdown(f"""
<div style="background:#FFFFFF;border:1px solid #E8E4DC;border-left:3px solid #2D5A3D;
     border-radius:8px;padding:10px 13px;margin-bottom:8px">
  <div style="display:flex;justify-content:space-between;align-items:baseline">
    <span style="font-weight:700;color:#1B1040;font-size:0.86rem">{c['name']}</span>
    <span style="font-size:0.7rem;color:#2D5A3D;font-weight:700">+${ep/1e3:.0f}K</span>
  </div>
  <div style="font-size:0.7rem;color:#6B6280;margin-top:1px">{c['industry']} · NRR {c.get('nrr_pct','?')}% · {int(ul*100)}% likely</div>
  <div style="font-size:0.74rem;color:#3D3458;margin-top:6px;line-height:1.4"><b style="color:#2D5A3D">Signal:</b> {c['roi_outcome']}; adoption {c.get('adoption_score','?')}%</div>
  <div style="font-size:0.74rem;color:#3D3458;margin-top:3px;line-height:1.4"><b style="color:#1B1040">Next:</b> {c['recommended_next_action']}</div>
</div>""", unsafe_allow_html=True)

    # ── Drill-in: health heatmap + full portfolio table ───────────────────────
    with st.expander("Drill in — health heatmap & full portfolio"):
        st.markdown("<div style='font-size:0.72rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.10em;margin:2px 0 8px'>Customer Health Heatmap</div>", unsafe_allow_html=True)
        tiles = []
        for c in sorted(customers, key=lambda c: c["health_score"]):
            hc = health_color(c["health_score"])
            initials = "".join(w[0] for w in c["name"].split()[:2]).upper()
            tiles.append(
                f"<div title=\"{c['name']} — health {c['health_score']}, {c['risk_level']} risk\" "
                f"style='flex:0 0 auto;width:60px;height:46px;background:{hc};border-radius:7px;"
                f"display:flex;flex-direction:column;align-items:center;justify-content:center;color:#fff'>"
                f"<div style='font-size:0.72rem;font-weight:800;line-height:1'>{c['health_score']}</div>"
                f"<div style='font-size:0.52rem;opacity:0.85;margin-top:1px'>{initials}</div></div>"
            )
        st.markdown(
            "<div style='display:flex;flex-wrap:wrap;gap:5px;margin-bottom:6px'>" + "".join(tiles) + "</div>"
            "<div style='display:flex;gap:16px;font-size:0.66rem;color:#6B6280'>"
            "<span><span style='display:inline-block;width:9px;height:9px;background:#9B2335;border-radius:2px;margin-right:4px'></span>Critical (&lt;40)</span>"
            "<span><span style='display:inline-block;width:9px;height:9px;background:#7A5C1E;border-radius:2px;margin-right:4px'></span>At Risk (40–59)</span>"
            "<span><span style='display:inline-block;width:9px;height:9px;background:#2D5A3D;border-radius:2px;margin-right:4px'></span>Healthy (60+)</span>"
            "</div>",
            unsafe_allow_html=True
        )

        st.markdown(
            "<div style='font-size:0.72rem;font-weight:700;color:#6B6280;text-transform:uppercase;"
            "letter-spacing:0.10em;margin:14px 0 8px'>Customer Portfolio"
            " <span style=\"font-weight:400;text-transform:none;letter-spacing:0\">— select a row to open the account</span></div>",
            unsafe_allow_html=True
        )

        df = pd.DataFrame(customers)
        df["Risk"]     = df["risk_level"].map({"High": "High", "Medium": "Medium", "Low": "Healthy"})
        df["ARR"]      = df["arr"].map(lambda x: f"${x:,.0f}")
        df["Health"]   = df["health_score"]
        df["NRR"]      = df["nrr_pct"].map(lambda x: f"{x}%")
        df["Adoption"] = df["adoption_score"].map(lambda x: f"{x}%")
        df["Tier"]     = df["customer_tier"]
        df["Renewal"]  = df["renewal_date"]
        disp = df[["name","industry","Tier","region","ARR","Health","NRR","Adoption","Renewal","Risk"]].rename(
            columns={"name": "Customer", "industry": "Industry", "region": "Region"}
        )
        disp = disp.sort_values("Health")

        sel = st.dataframe(disp, use_container_width=True, height=420,
                           on_select="rerun", selection_mode="single-row")
        if sel and sel.get("selection", {}).get("rows"):
            ridx   = sel["selection"]["rows"][0]
            chosen = customers[disp.index[ridx]]
            st.session_state["selected_cid"]   = chosen["id"]
            st.session_state["selected_cname"] = chosen["name"]
            st.session_state["_pending_nav"]   = "Customer 360"
            st.rerun()



# ══════════════════════════════════════════════════════════════════════════════
# PAGE: CUSTOMER 360
# ══════════════════════════════════════════════════════════════════════════════

elif page == "Customer 360":
    page_header("Customer 360")
    customers = fetch_customers()
    if not customers:
        st.error("No customers loaded.")
        st.stop()

    cmap = {c["id"]: c for c in customers}
    default_id = st.session_state.get("selected_cid", customers[0]["id"])

    cid = st.selectbox(
        "Select customer",
        options=[c["id"] for c in customers],
        format_func=lambda x: f"{cmap[x]['name']} — {cmap[x]['industry']} · ${cmap[x]['arr']:,} · {risk_icon(cmap[x].get('risk_level','?'))}",
        index=next((i for i, c in enumerate(customers) if c["id"] == default_id), 0),
    )
    st.session_state["selected_cid"] = cid

    data = fetch_360(cid)
    if not data or not data.get("customer"):
        st.error("Failed to load customer data.")
        st.stop()

    c         = data["customer"]
    tickets   = data.get("tickets", [])
    escs      = data.get("escalations", [])
    stk       = data.get("stakeholders", [])
    metrics   = data.get("metrics", [])
    milestones= data.get("milestones", [])
    notes     = data.get("meeting_notes", [])
    impl      = data.get("implementation") or {}
    renewal   = data.get("renewal") or {}
    history   = data.get("health_history", [])

    # ── Header ────────────────────────────────────────────────────────────────
    risk_color  = {"High":"#9B2335","Medium":"#C9952A","Low":"#2D5A3D"}.get(c.get("risk_level",""), "#1B1040")
    risk_bg     = {"High":"#FDF1F2","Medium":"#FDF8EE","Low":"#EFF6F1"}.get(c.get("risk_level",""), "#F5F2EE")
    renewal_days = renewal.get("days_to_renewal", "?")
    open_tickets = sum(1 for t in tickets if t["status"] != "Resolved")
    champ_status = c.get("champion_status", "?")
    champ_color  = {"Active":"#2D5A3D","Disengaged":"#7A5C1E","Left Company":"#9B2335"}.get(champ_status,"#6B6280")

    st.markdown(f"""
    <div style="background:#FFFFFF;border:1px solid #E8E4DC;border-radius:12px;
                border-left:4px solid {risk_color};padding:16px 20px;margin-bottom:14px">
      <div style="display:flex;align-items:flex-start;gap:20px">
        <div style="flex:1;min-width:0">
          <div style="font-size:1.25rem;font-weight:800;color:#1B1040;letter-spacing:-0.02em;line-height:1.2">
            {c['name']}</div>
          <div style="color:#6B6280;font-size:0.75rem;margin-top:3px">
            {c['industry']} &nbsp;·&nbsp; {c.get('customer_tier','?')} &nbsp;·&nbsp; {c.get('region','?')} &nbsp;·&nbsp;
            {c.get('employee_count','?'):,} employees &nbsp;·&nbsp;
            <span style="font-weight:700;color:#1B1040">${c['arr']:,} ARR</span>
          </div>
          <div style="margin-top:10px;padding:8px 12px;background:#F5F2EE;border-radius:8px;font-size:0.78rem;color:#3D3458;line-height:1.5">
            <span style="font-weight:700;color:#1B1040">Risk:</span> {c.get('primary_risk_reason','')}
            <br><span style="color:#6B6280">→</span> {c.get('recommended_next_action','')}
          </div>
        </div>
        <div style="text-align:center;background:{risk_bg};border:1px solid {risk_color}33;
                    border-radius:10px;padding:12px 16px;flex-shrink:0;min-width:80px">
          <div style="font-size:2.4rem;font-weight:900;color:{risk_color};line-height:1">{c['health_score']}</div>
          <div style="font-size:0.58rem;font-weight:700;color:#6B6280;letter-spacing:0.10em;margin-top:2px">HEALTH</div>
          <div style="font-size:0.72rem;font-weight:700;color:{risk_color};margin-top:4px">{c.get('risk_level','?')}</div>
          <div style="font-size:0.65rem;color:#6B6280">{c.get('health_trend','?')}</div>
        </div>
      </div>
      <div style="display:flex;gap:10px;margin-top:12px;flex-wrap:wrap">
        <div style="background:#F5F2EE;border-radius:8px;padding:7px 14px;text-align:center;min-width:80px">
          <div style="font-size:0.60rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.08em">Adoption</div>
          <div style="font-size:1.05rem;font-weight:800;color:#1B1040;line-height:1.3">{c.get('adoption_score',0)}<span style="font-size:0.65rem;font-weight:500;color:#6B6280">/100</span></div>
        </div>
        <div style="background:#F5F2EE;border-radius:8px;padding:7px 14px;text-align:center;min-width:80px">
          <div style="font-size:0.60rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.08em">Churn Risk</div>
          <div style="font-size:1.05rem;font-weight:800;color:{risk_color};line-height:1.3">{c.get('renewal_risk_score',0):.0%}</div>
        </div>
        <div style="background:#F5F2EE;border-radius:8px;padding:7px 14px;text-align:center;min-width:80px">
          <div style="font-size:0.60rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.08em">Renewal</div>
          <div style="font-size:1.05rem;font-weight:800;color:#1B1040;line-height:1.3">{renewal_days}d</div>
        </div>
        <div style="background:#F5F2EE;border-radius:8px;padding:7px 14px;text-align:center;min-width:90px">
          <div style="font-size:0.60rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.08em">Champion</div>
          <div style="font-size:0.82rem;font-weight:700;color:{champ_color};line-height:1.4">{champ_status}</div>
        </div>
        <div style="background:#F5F2EE;border-radius:8px;padding:7px 14px;text-align:center;min-width:70px">
          <div style="font-size:0.60rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.08em">NRR</div>
          <div style="font-size:1.05rem;font-weight:800;color:{'#2D5A3D' if c.get('nrr_pct',0)>=105 else '#7A5C1E' if c.get('nrr_pct',0)>=98 else '#9B2335'};line-height:1.3">{c.get('nrr_pct','?')}%</div>
        </div>
        <div style="background:#F5F2EE;border-radius:8px;padding:7px 14px;text-align:center;min-width:70px">
          <div style="font-size:0.60rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.08em">NPS</div>
          <div style="font-size:1.05rem;font-weight:800;color:{'#2D5A3D' if c.get('nps',0)>=8 else '#7A5C1E' if c.get('nps',0)>=5 else '#9B2335'};line-height:1.3">{c.get('nps','?')}</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabbed layout — everything below the hero lives in a tab ──────────────
    tab_over, tab_ai, tab_use, tab_impl, tab_support, tab_people, tab_renew = st.tabs(
        ["Overview", "AI Agents", "Usage & Health", "Implementation", "Support", "People", "Renewal"]
    )
    # Merged tabs: Support = tickets + escalations, People = stakeholders + notes.
    tab_tick = tab_escs = tab_support
    tab_stk = tab_notes = tab_people

    with tab_over:
        # ── Renewal prediction + ROI + recommended action plan ────────────────
        rr      = c.get("renewal_risk_score", 0)
        renew_conf = round((1 - rr) * 100)
        rconf_color = "#2D5A3D" if renew_conf >= 70 else "#7A5C1E" if renew_conf >= 45 else "#9B2335"
        rverdict = "Likely to Renew" if renew_conf >= 70 else "Renewal at Risk" if renew_conf < 45 else "Needs Attention"
        # Build a concrete action plan from the account's signals
        plan = []
        if c.get("champion_status") == "Left Company":
            plan.append("Identify and recruit a new executive champion")
        if escs:
            plan.append(f"Resolve {len(escs)} open escalation{'s' if len(escs)!=1 else ''} with daily exec updates")
        if open_tickets >= 3:
            plan.append(f"Clear support backlog ({open_tickets} open tickets)")
        if c.get("adoption_score", 100) < 50:
            plan.append("Run an adoption workshop to drive feature activation")
        if c.get("qbr_completion") == "Overdue":
            plan.append("Schedule the overdue QBR with the economic buyer")
        if c.get("expansion_pipeline_arr"):
            plan.append(f"Advance ${c['expansion_pipeline_arr']/1e3:.0f}K expansion opportunity")
        if not plan:
            plan = ["Maintain cadence; pursue reference and advocacy opportunities"]
        plan = plan[:4]
        plan_html = "".join(f"<div style='font-size:0.76rem;color:#3D3458;margin-top:5px;line-height:1.35'>{i+1}. {step}</div>" for i, step in enumerate(plan))

        rp1, rp2, rp3 = st.columns([1, 1, 1.4])
        with rp1:
            st.markdown(f"""
<div style="background:#FFFFFF;border:1px solid #E8E4DC;border-radius:10px;padding:12px 14px;height:100%">
  <div style="font-size:0.62rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.08em">Renewal Prediction</div>
  <div style="font-size:1.6rem;font-weight:900;color:{rconf_color};line-height:1.1;margin-top:4px">{renew_conf}%</div>
  <div style="font-size:0.74rem;font-weight:700;color:{rconf_color}">{rverdict}</div>
  <div style="font-size:0.68rem;color:#6B6280;margin-top:4px">{renewal_days}d to renewal · {c.get('forecast_category', renewal.get('forecast_category','—') if renewal else '—')}</div>
</div>""", unsafe_allow_html=True)
        with rp2:
            st.markdown(f"""
<div style="background:#FFFFFF;border:1px solid #E8E4DC;border-radius:10px;padding:12px 14px;height:100%">
  <div style="font-size:0.62rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.08em">Proven Business Outcome</div>
  <div style="font-size:0.92rem;font-weight:700;color:#2D5A3D;line-height:1.3;margin-top:6px">{c.get('roi_outcome','—')}</div>
  <div style="font-size:0.68rem;color:#6B6280;margin-top:6px">Utilization {c.get('utilization_pct','?')}% · Exec engagement {c.get('executive_engagement','?')}</div>
</div>""", unsafe_allow_html=True)
        with rp3:
            st.markdown(f"""
<div style="background:#FFFFFF;border:1px solid #E8E4DC;border-radius:10px;padding:12px 14px;height:100%">
  <div style="font-size:0.62rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.08em">Recommended Action Plan</div>
  {plan_html}
</div>""", unsafe_allow_html=True)

        st.markdown("<div style='margin:8px 0'></div>", unsafe_allow_html=True)
        # ── Outcome tracking: did we act on the AI's recommendation? ──────────
        action = get_action_status(cid)
        cur_status = action.get("status", "Open")
        status_meta = {
            "Open":        ("#7A5C1E", "#FDF8EE", "Not yet actioned"),
            "In Progress": ("#2D4A7A", "#EEF2FB", "In progress"),
            "Done":        ("#2D5A3D", "#EFF6F1", "Closed — action taken"),
            "Dismissed":   ("#6B6280", "#F0EEEA", "Dismissed"),
        }
        scolor, sbg, slabel = status_meta.get(cur_status, status_meta["Open"])
        when = (action.get("updated_at") or "")[:16].replace("T", " ")

        ac_l, ac_r = st.columns([1.5, 2.5])
        with ac_l:
            st.markdown(
                f"<div style='background:{sbg};border:1px solid {scolor}33;border-radius:10px;padding:10px 14px'>"
                f"<div style='font-size:0.62rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.08em'>Recommendation Status</div>"
                f"<div style='font-size:0.95rem;font-weight:800;color:{scolor};margin-top:3px'>{slabel}</div>"
                f"<div style='font-size:0.64rem;color:#9B93A8;margin-top:2px'>{('updated '+when) if when else 'no action logged yet'}</div>"
                f"</div>", unsafe_allow_html=True)
        with ac_r:
            st.markdown("<div style='font-size:0.62rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:4px'>Log Outcome</div>", unsafe_allow_html=True)
            b1, b2, b3, b4 = st.columns(4)
            if b1.button("Open", use_container_width=True, key="act_open",
                         type="primary" if cur_status == "Open" else "secondary"):
                set_action_status(cid, "Open"); st.rerun()
            if b2.button("In Progress", use_container_width=True, key="act_prog",
                         type="primary" if cur_status == "In Progress" else "secondary"):
                set_action_status(cid, "In Progress"); st.rerun()
            if b3.button("Done", use_container_width=True, key="act_done",
                         type="primary" if cur_status == "Done" else "secondary"):
                set_action_status(cid, "Done"); st.rerun()
            if b4.button("Dismiss", use_container_width=True, key="act_dismiss",
                         type="primary" if cur_status == "Dismissed" else "secondary"):
                set_action_status(cid, "Dismissed"); st.rerun()

    with tab_ai:
        # ── Agent action bar — grouped by workflow ────────────────────────────
        triggered = None
        agent_groups = [
            ("Assess", [
                ("CustomerHealthAgent", "Health Assessment",     "secondary"),
                ("ImplementationAgent", "Implementation Report", "secondary"),
            ]),
            ("Grow", [
                ("ExpansionOpportunityAgent", "Expansion Opportunity", "secondary"),
                ("QBRPreparationAgent",       "Prepare QBR",           "secondary"),
                ("SuccessPlanAgent",          "Build Success Plan",    "secondary"),
            ]),
            ("Communicate & Respond", [
                ("BriefingAgent",            "Generate CEO Briefing", "primary"),
                ("EscalationCommanderAgent", "Escalation Commander",  "primary"),
            ]),
            ("Verify", [
                ("SkeptikQAAgent", "Skeptik QA Review", "secondary"),
            ]),
        ]
        group_cols = st.columns(4)
        for col, (group_label, group_btns) in zip(group_cols, agent_groups):
            with col:
                st.markdown(f"<div style='font-size:0.60rem;font-weight:700;color:#9B93A8;text-transform:uppercase;letter-spacing:0.10em;margin-bottom:4px'>{group_label}</div>", unsafe_allow_html=True)
                for aname, label, btype in group_btns:
                    if st.button(label, use_container_width=True, type=btype, key=f"360_{aname}"):
                        triggered = aname

        if triggered:
            with st.spinner(f"Running {agent_display_name(triggered)}…"):
                result = call_agent(triggered, cid)
            st.session_state[f"360_result_{cid}_{triggered}"] = result
            # Track which agent was last run for this customer so the freshest
            # result always renders, even when an agent is re-run (which overwrites
            # its key in place rather than appending it to session_state).
            st.session_state[f"360_last_{cid}"] = triggered

        # Show the result for the most recently triggered agent on this customer
        last_agent = st.session_state.get(f"360_last_{cid}")
        recent_key = f"360_result_{cid}_{last_agent}" if last_agent else None
        if not (recent_key and recent_key in st.session_state):
            # Fallback: any stored result for this customer
            recent_key = next(
                (k for k in reversed(list(st.session_state.keys()))
                 if k.startswith(f"360_result_{cid}_")), None
            )
        if recent_key:
            result = st.session_state[recent_key]
            agent_label = recent_key.split(f"360_result_{cid}_")[-1]
            agent_nice  = agent_display_name(result.get("agent_name", agent_label))
            st.markdown(f"<div style='font-size:0.78rem;font-weight:800;color:#1B1040;letter-spacing:-0.01em;margin:12px 0 4px'>{agent_nice}</div>", unsafe_allow_html=True)

            # Skeptik shows before/after
            if "SkeptikQAAgent" in recent_key:
                prior_key = next(
                    (k for k in reversed(list(st.session_state.keys()))
                     if k.startswith(f"360_result_{cid}_") and "Skeptik" not in k), None
                )
                if prior_key:
                    bc, ac = st.columns(2)
                    with bc:
                        st.markdown("<div style='font-size:0.72rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.10em;margin-bottom:6px'>Original Output</div>", unsafe_allow_html=True)
                        with st.container(border=True):
                            st.markdown("<span class='agent-report-marker'></span>", unsafe_allow_html=True)
                            prior = st.session_state[prior_key]
                            st.markdown(prior.get("output_text", "")[:1200] + "...", unsafe_allow_html=False)
                    with ac:
                        st.markdown("<div style='font-size:0.72rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.10em;margin-bottom:6px'>Skeptik QA Review</div>", unsafe_allow_html=True)
                        render_agent_output(result)
                else:
                    render_agent_output(result)
            else:
                render_agent_output(result)

            # Export button for briefings
            if "Briefing" in recent_key or "Escalation" in recent_key:
                fn = f"{c['name'].replace(' ','_')}_{agent_label}_{datetime.now().strftime('%Y%m%d')}.md"
                export_button(result.get("output_text",""), fn)
        else:
            st.caption("Pick an agent above — results appear here and stay while you browse the other tabs.")

    with tab_use:
        mrow = metrics[0] if metrics else {}
        if mrow:
            dau_trend = mrow.get('dau_trend_30d', 0)
            trend_color = "#2D5A3D" if dau_trend >= 0 else "#9B2335"
            trend_sign  = "+" if dau_trend >= 0 else ""
            usage_items = [
                ("Daily Active Users", str(int(mrow.get("dau",0))),
                 f"<span style='color:{trend_color};font-size:0.68rem'>{trend_sign}{dau_trend:.0%} vs 30d</span>"),
                ("AI Asset Coverage", f"{int(mrow.get('asset_coverage_pct',0))}%", ""),
                ("Modules Active",    f"{int(mrow.get('features_enabled',0))}/18", ""),
                ("Guardian False-Positive Rate", f"{mrow.get('false_positive_rate',0):.0%}", ""),
                ("Prompts Inspected (30d)", f"{int(mrow.get('api_calls_last_30d',0)):,}", ""),
                ("Guardian Interventions (30d)", str(int(mrow.get("alerts_generated_last_30d",0))), ""),
                ("Logins (7d)",       str(int(mrow.get("unique_logins_last_7d",0))), ""),
                ("AI Agents Governed", str(int(mrow.get("agents_deployed",0))), ""),
            ]
            cols = st.columns(4)
            for i, (lbl, val, sub) in enumerate(usage_items):
                with cols[i % 4]:
                    st.markdown(
                        f"<div class='kpi-card'><div class='kpi-label'>{lbl}</div>"
                        f"<div class='kpi-value' style='font-size:1.3rem'>{val}</div>"
                        f"<div class='kpi-sub'>{sub}</div></div>",
                        unsafe_allow_html=True
                    )

        if history:
            st.markdown("<div style='margin-top:14px;font-size:0.72rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.10em;margin-bottom:6px'>30-Day Health Trend</div>", unsafe_allow_html=True)
            import altair as alt
            hdf = pd.DataFrame(history)[["date","health_score"]].copy()
            hdf["date"] = pd.to_datetime(hdf["date"])
            hdf = hdf.sort_values("date")
            chart = (
                alt.Chart(hdf)
                .mark_line(color="#1B1040", strokeWidth=2.2, point=alt.OverlayMarkDef(color="#1B1040", size=18))
                .encode(
                    x=alt.X("date:T", axis=alt.Axis(title=None, grid=False, labelColor="#6B6280", domainColor="#E8E4DC", tickColor="#E8E4DC", format="%b %d")),
                    y=alt.Y("health_score:Q", scale=alt.Scale(domain=[0, 100]),
                            axis=alt.Axis(title=None, labelColor="#6B6280", gridColor="#F0EDE7", domainOpacity=0, tickOpacity=0)),
                    tooltip=[alt.Tooltip("date:T", title="Date", format="%b %d"),
                             alt.Tooltip("health_score:Q", title="Health")],
                )
                .properties(height=160, background="#FFFFFF")
                .configure_view(strokeWidth=0)
            )
            st.altair_chart(chart, use_container_width=True, theme=None)

        sec = c.get('security_review_status','?')
        sec_color = {"Complete":"#2D5A3D","In Progress":"#7A5C1E","Blocked":"#9B2335","Not Started":"#6B6280"}.get(sec,"#6B6280")
        onb = c.get('onboarding_status','?')
        sent = c.get('sentiment','?')
        sent_color = {"Positive":"#2D5A3D","Negative":"#9B2335","Neutral":"#6B6280"}.get(sent,"#6B6280")
        st.markdown(f"""
<div style="display:flex;gap:8px;margin-top:10px;flex-wrap:wrap">
  <div style="background:#F5F2EE;border-radius:8px;padding:6px 14px;font-size:0.75rem">
    <span style="color:#6B6280;font-weight:600">Security Review</span>
    <span style="margin-left:8px;font-weight:700;color:{sec_color}">{sec}</span>
  </div>
  <div style="background:#F5F2EE;border-radius:8px;padding:6px 14px;font-size:0.75rem">
    <span style="color:#6B6280;font-weight:600">Onboarding</span>
    <span style="margin-left:8px;font-weight:700;color:#1B1040">{onb}</span>
  </div>
  <div style="background:#F5F2EE;border-radius:8px;padding:6px 14px;font-size:0.75rem">
    <span style="color:#6B6280;font-weight:600">Sentiment</span>
    <span style="margin-left:8px;font-weight:700;color:{sent_color}">{sent}</span>
  </div>
</div>""", unsafe_allow_html=True)

    with tab_impl:
        if impl:
            behind = impl.get("days_behind_schedule", 0)
            status = impl.get("overall_status", "?")
            pct    = impl.get("pct_complete", 0)
            sc     = "#9B2335" if status in ("Stalled","Behind Schedule") else "#C9952A" if status == "Slight Delay" else "#2D5A3D"
            sc_bg  = "#FDF1F2" if status in ("Stalled","Behind Schedule") else "#FDF8EE" if status == "Slight Delay" else "#EFF6F1"
            st.markdown(f"""
<div style="background:#FFFFFF;border:1px solid #E8E4DC;border-radius:10px;padding:12px 16px;margin-bottom:12px">
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
    <span style="background:{sc_bg};color:{sc};font-size:0.72rem;font-weight:700;
          padding:3px 10px;border-radius:20px;border:1px solid {sc}33">{status}</span>
    <span style="font-size:0.72rem;color:#6B6280">{pct}% complete</span>
  </div>
  <div style="background:#E8E4DC;border-radius:50px;height:6px;overflow:hidden">
    <div style="width:{pct}%;background:{sc};height:100%;border-radius:50px"></div>
  </div>
  <div style="display:flex;gap:16px;margin-top:8px;font-size:0.72rem;color:#6B6280">
    <span>Owner: <b style="color:#1B1040">{impl.get('implementation_owner','?')}</b></span>
    <span>Go-live: <b style="color:#1B1040">{impl.get('go_live_target','?')}</b></span>
    {f'<span style="color:#9B2335;font-weight:600">{behind}d behind schedule</span>' if behind > 0 else ''}
  </div>
</div>""", unsafe_allow_html=True)
        else:
            st.markdown("<div style='font-size:0.78rem;color:#6B6280;padding:8px 0'>No implementation record found.</div>", unsafe_allow_html=True)

        for m in milestones:
            status_m = m.get("status","")
            m_color  = {"Complete":"#2D5A3D","In Progress":"#7A5C1E","Not Started":"#6B6280"}.get(status_m,"#6B6280")
            m_bg     = {"Complete":"#EFF6F1","In Progress":"#FDF8EE","Not Started":"#F5F2EE"}.get(status_m,"#F5F2EE")
            mname    = m.get("milestone_name") or m.get("name","?")
            blocker  = m.get("blocker")
            st.markdown(f"""
<div style="display:flex;align-items:flex-start;gap:10px;padding:7px 0;border-bottom:1px solid #E8E4DC">
  <span style="background:{m_bg};color:{m_color};font-size:0.65rem;font-weight:700;padding:2px 8px;
        border-radius:20px;white-space:nowrap;margin-top:1px">{status_m}</span>
  <div>
    <div style="font-size:0.82rem;font-weight:600;color:#1B1040">{mname}</div>
    {f'<div style="font-size:0.72rem;color:#9B2335;margin-top:2px">{blocker}</div>' if blocker else ''}
  </div>
</div>""", unsafe_allow_html=True)

    with tab_tick:
        st.markdown("<div style='font-size:0.72rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.10em;margin-bottom:6px'>Support Tickets</div>", unsafe_allow_html=True)
        open_t    = [t for t in tickets if t["status"] != "Resolved"]
        closed_t  = [t for t in tickets if t["status"] == "Resolved"]
        st.markdown(f"<div style='font-size:0.78rem;font-weight:700;color:#1B1040;margin-bottom:6px'>{len(open_t)} Open <span style=\"color:#6B6280;font-weight:400\">· {len(closed_t)} Resolved</span></div>", unsafe_allow_html=True)
        for t in sorted(tickets, key=lambda x: ("P1P2P3P4".index(x["severity"]) if x["severity"] in "P1P2P3P4" else 9, x["status"] == "Resolved")):
            sc = {"P1":"#9B2335","P2":"#7A5C1E","P3":"#5C4A1E","P4":"#6B6280"}.get(t["severity"],"#6B6280")
            st_color = {"Open": "#9B2335", "In Progress": "#7A5C1E"}.get(t["status"], "#2D5A3D")
            st.markdown(f"""<div class="card">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <span style="background:{sc}18;color:{sc};font-weight:700;font-size:0.72rem;padding:2px 8px;border-radius:20px;border:1px solid {sc}44">{t['severity']}</span>
                    <span style="color:{st_color};font-size:0.72rem;font-weight:700">{t['status']}</span>
                </div>
                <div style="color:#1B1040;font-size:0.88rem;margin-top:6px;font-weight:500">{t['title']}</div>
                <div style="color:#6B6280;font-size:0.72rem;margin-top:3px">Opened {t['opened_at'][:10]} · Assignee: {t.get('assignee','?')}</div>
                {f'<div style="color:#7A5C1E;font-size:0.72rem;margin-top:2px">{t["escalation_reference"]}</div>' if t.get("escalation_reference") else ''}
            </div>""", unsafe_allow_html=True)

    with tab_escs:
        st.markdown("<div style='font-size:0.72rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.10em;margin:14px 0 6px'>Escalations</div>", unsafe_allow_html=True)
        if not escs:
            st.markdown("<div style='font-size:0.78rem;color:#2D5A3D;padding:8px 0'>No active escalations.</div>", unsafe_allow_html=True)
        for e in escs:
            is_crit = e["severity"] == "Critical"
            sc      = "#9B2335" if is_crit else "#7A5C1E"
            sc_bg   = "#FDF1F2" if is_crit else "#FDF8EE"
            exec_badge = "<span style='background:#EAE6E0;color:#3D3458;font-size:0.62rem;font-weight:700;padding:2px 7px;border-radius:20px;margin-left:6px'>Exec Aware</span>" if e.get("executive_aware") else ""
            st.markdown(f"""
<div style="background:#FFFFFF;border:1px solid #E8E4DC;border-left:3px solid {sc};
     border-radius:8px;padding:11px 14px;margin-bottom:8px">
  <div style="display:flex;align-items:center;justify-content:space-between">
    <div>
      <span style="background:{sc_bg};color:{sc};font-size:0.65rem;font-weight:700;
            padding:2px 9px;border-radius:20px;border:1px solid {sc}33">{e['severity']}</span>
      <span style="background:#F5F2EE;color:#6B6280;font-size:0.65rem;font-weight:600;
            padding:2px 9px;border-radius:20px;margin-left:5px">{e['status']}</span>
      {exec_badge}
    </div>
    <span style="font-size:0.68rem;color:#9B93A8">{e['opened_at'][:10]}</span>
  </div>
  <div style="font-size:0.85rem;font-weight:600;color:#1B1040;margin-top:7px">{e['title']}</div>
  <div style="font-size:0.72rem;color:#6B6280;margin-top:3px">Owner: {e['owner']}</div>
  {f'<div style="font-size:0.72rem;color:#6B6280;margin-top:4px;font-style:italic">{e["resolution_plan"]}</div>' if e.get("resolution_plan") else ''}
</div>""", unsafe_allow_html=True)

    with tab_stk:
        st.markdown("<div style='font-size:0.72rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.10em;margin-bottom:6px'>Stakeholders</div>", unsafe_allow_html=True)
        role_colors = {"Champion":"#1B1040","Technical Sponsor":"#3D3458","Business Sponsor":"#5C4A1E",
                       "Executive Sponsor":"#2D3A4A","Economic Buyer":"#9B2335"}
        role_bg = {"Champion":"#EAE6E0","Technical Sponsor":"#EDEAF4","Business Sponsor":"#F0EBE0",
                   "Executive Sponsor":"#E8EBF0","Economic Buyer":"#F5ECEC"}
        eng_colors = {"High":"#2D5A3D","Medium":"#7A5C1E","Low":"#9B2335","None":"#6B6280"}
        for s in stk:
            rc = role_colors.get(s["role"],"#6B6280")
            rb = role_bg.get(s["role"],"#EAE6E0")
            ec = eng_colors.get(s.get("engagement_level",""),"#6B6280")
            st.markdown(f"""<div class="card">
                <div style="display:flex;justify-content:space-between;align-items:flex-start">
                    <div>
                        <span style="font-weight:700;color:#1B1040;font-size:0.95rem">{s['name']}</span>
                        <div style="font-size:0.80rem;color:#6B6280;margin-top:1px">{s['title']}</div>
                    </div>
                    <span style="font-size:0.72rem;color:{ec};font-weight:700">{s.get('engagement_level','?')} engagement</span>
                </div>
                <div style="margin-top:6px;display:flex;align-items:center;gap:8px">
                    <span style="background:{rb};color:{rc};font-size:0.72rem;font-weight:700;padding:2px 8px;border-radius:20px">{s['role']}</span>
                    <span style="color:#6B6280;font-size:0.72rem">{s['email']}</span>
                </div>
            </div>""", unsafe_allow_html=True)

    with tab_notes:
        st.markdown("<div style='font-size:0.72rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.10em;margin:14px 0 6px'>Meeting Notes</div>", unsafe_allow_html=True)
        sent_colors = {"Positive":"#2D5A3D","Neutral":"#6B6280","Negative":"#9B2335"}
        for n in notes:
            sc = sent_colors.get(n.get("sentiment_signal",""),"#6B6280")
            import json as _json
            try:
                actions = _json.loads(n.get("action_items","[]")) if n.get("action_items") else []
            except Exception:
                actions = []
            sent_bg = {"Positive":"#EBF2EE","Neutral":"#EFEBE5","Negative":"#F5ECEC"}.get(n.get('sentiment_signal',''),'#EFEBE5')
            st.markdown(f"""<div class="card">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <span style="color:#6B6280;font-size:0.75rem">{n['date'][:10]} · <b style="color:#3D3458">{n.get('meeting_type','?')}</b></span>
                    <span style="background:{sent_bg};color:{sc};font-size:0.70rem;font-weight:700;padding:2px 8px;border-radius:20px">{n.get('sentiment_signal','?')}</span>
                </div>
                <div style="color:#1B1040;font-size:0.88rem;margin-top:6px;line-height:1.5">{n['summary']}</div>
                <div style="color:#6B6280;font-size:0.72rem;margin-top:4px">Attendees: {n.get('attendees_internal','?')} · {n.get('attendees_customer','?')}</div>
                {('<div style="margin-top:6px">' + ''.join(f'<div style="font-size:0.75rem;color:#3D3458;margin-top:2px">→ {a}</div>' for a in actions) + '</div>') if actions else ''}
            </div>""", unsafe_allow_html=True)

    with tab_renew:
        if renewal:
            rc_color = "#9B2335" if c.get("renewal_risk_score",0) > 0.6 else "#7A5C1E" if c.get("renewal_risk_score",0) > 0.3 else "#2D5A3D"
            r1, r2, r3, r4 = st.columns(4)
            with r1: st.metric("Days to Renewal", renewal.get("days_to_renewal","?"))
            with r2: st.metric("Renewal Stage", renewal.get("renewal_stage","?"))
            with r3: st.metric("Current ARR", f"${renewal.get('current_arr',0):,}")
            with r4: st.metric("Expansion Opp.", f"${renewal.get('expansion_arr',0):,}")

            st.markdown(f"""<div class="card">
                <div style="font-size:0.75rem;color:#6B6280;margin-bottom:4px">RENEWAL DETAILS</div>
                <div>Forecast: <b style="color:{rc_color}">{renewal.get('forecast_category','?')}</b></div>
                <div style="margin-top:4px">Risk Score: <b style="color:{rc_color}">{c.get('renewal_risk_score',0):.0%}</b></div>
                <div style="margin-top:4px">Commercial Note: {renewal.get('commercial_terms_note','?')}</div>
                <div style="margin-top:4px;color:#6B6280">Procurement Contact: {renewal.get('procurement_contact','?')}</div>
                <div style="color:#6B6280">Exec Involvement Required: {'Yes' if renewal.get('requires_exec_involvement') else 'No'}</div>
            </div>""", unsafe_allow_html=True)

            if st.button("Generate CEO Briefing for Renewal", type="primary"):
                with st.spinner("Generating CEO Briefing (Sonnet)..."):
                    result = call_agent("BriefingAgent", cid)
                st.session_state[f"360_result_{cid}_BriefingAgent"] = result
                st.session_state[f"360_last_{cid}"] = "BriefingAgent"
                st.toast("Briefing ready — see the AI Agents tab.")
                st.rerun()
        else:
            st.caption("No renewal record found within 180-day window.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: CSM PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════

elif page == "CSM Performance":
    page_header("CSM Performance", "Portfolio health, ARR, renewals and expansion by Customer Success Manager")
    customers = fetch_customers()
    if not customers:
        st.error("No customers loaded.")
        st.stop()

    today = datetime.now().date()
    csm_stats = {}
    for c in customers:
        owner = c.get("csm_owner", "Unassigned")
        s = csm_stats.setdefault(owner, {
            "accounts": 0, "arr": 0, "health_sum": 0, "high": 0, "med": 0, "low": 0,
            "expansion": 0, "renewals_90": 0, "nrr_sum": 0,
        })
        s["accounts"]  += 1
        s["arr"]       += c["arr"]
        s["health_sum"] += c["health_score"]
        s["nrr_sum"]   += c.get("nrr_pct", 0)
        s["expansion"] += c.get("expansion_pipeline_arr", 0)
        s[{"High": "high", "Medium": "med", "Low": "low"}[c["risk_level"]]] += 1
        try:
            d = (datetime.strptime(c["renewal_date"], "%Y-%m-%d").date() - today).days
            if 0 <= d <= 90:
                s["renewals_90"] += 1
        except Exception:
            pass

    # Summary KPI row across the CS team
    team = st.columns(4)
    team[0].markdown(kpi_card("CS Managers", str(len(csm_stats))), unsafe_allow_html=True)
    team[1].markdown(kpi_card("Avg Accounts / CSM", f"{len(customers)/max(len(csm_stats),1):.0f}"), unsafe_allow_html=True)
    team[2].markdown(kpi_card("Avg ARR / CSM", f"${sum(s['arr'] for s in csm_stats.values())/max(len(csm_stats),1)/1e6:.1f}M"), unsafe_allow_html=True)
    team[3].markdown(kpi_card("Total Expansion Pipeline", f"${sum(s['expansion'] for s in csm_stats.values())/1e6:.1f}M"), unsafe_allow_html=True)

    st.markdown("<div style='margin:14px 0 8px'></div>", unsafe_allow_html=True)

    # Per-CSM cards, sorted by portfolio health
    ranked = sorted(csm_stats.items(), key=lambda kv: kv[1]["health_sum"]/kv[1]["accounts"], reverse=True)
    for owner, s in ranked:
        avg_h   = s["health_sum"] / s["accounts"]
        avg_nrr = s["nrr_sum"] / s["accounts"]
        hc      = health_color(avg_h)
        tot     = s["accounts"]
        hp, mp, lp = s["high"]/tot*100, s["med"]/tot*100, s["low"]/tot*100
        st.markdown(f"""
<div style="background:#FFFFFF;border:1px solid #E8E4DC;border-radius:10px;padding:13px 16px;margin-bottom:9px">
  <div style="display:flex;align-items:center;gap:14px">
    <div style="flex:0 0 150px">
      <div style="font-weight:700;color:#1B1040;font-size:0.92rem">{owner}</div>
      <div style="font-size:0.68rem;color:#6B6280">{s['accounts']} accounts · ${s['arr']/1e6:.1f}M ARR</div>
    </div>
    <div style="flex:0 0 70px;text-align:center">
      <div style="font-size:1.3rem;font-weight:800;color:{hc};line-height:1">{avg_h:.0f}</div>
      <div style="font-size:0.56rem;color:#6B6280;text-transform:uppercase;letter-spacing:0.08em">Avg Health</div>
    </div>
    <div style="flex:1">
      <div style="display:flex;height:8px;border-radius:50px;overflow:hidden;gap:2px">
        <div style="width:{hp:.1f}%;background:#9B2335"></div>
        <div style="width:{mp:.1f}%;background:#C9952A"></div>
        <div style="width:{lp:.1f}%;background:#2D5A3D"></div>
      </div>
      <div style="display:flex;gap:12px;margin-top:5px;font-size:0.66rem;color:#6B6280">
        <span style="color:#9B2335;font-weight:600">{s['high']} high</span>
        <span style="color:#7A5C1E;font-weight:600">{s['med']} med</span>
        <span style="color:#2D5A3D;font-weight:600">{s['low']} healthy</span>
      </div>
    </div>
    <div style="flex:0 0 90px;text-align:center;border-left:1px solid #E8E4DC;padding-left:12px">
      <div style="font-size:0.95rem;font-weight:800;color:#1B1040;line-height:1.2">{avg_nrr:.0f}%</div>
      <div style="font-size:0.56rem;color:#6B6280;text-transform:uppercase;letter-spacing:0.08em">Avg NRR</div>
    </div>
    <div style="flex:0 0 100px;text-align:center;border-left:1px solid #E8E4DC;padding-left:12px">
      <div style="font-size:0.95rem;font-weight:800;color:#2D5A3D;line-height:1.2">${s['expansion']/1e3:.0f}K</div>
      <div style="font-size:0.56rem;color:#6B6280;text-transform:uppercase;letter-spacing:0.08em">Expansion</div>
    </div>
    <div style="flex:0 0 80px;text-align:center;border-left:1px solid #E8E4DC;padding-left:12px">
      <div style="font-size:0.95rem;font-weight:800;color:#1B1040;line-height:1.2">{s['renewals_90']}</div>
      <div style="font-size:0.56rem;color:#6B6280;text-transform:uppercase;letter-spacing:0.08em">Renewals 90d</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: AGENT CONSOLE
# ══════════════════════════════════════════════════════════════════════════════

elif page == "Agent Console":
    page_header("Agent Console", "Run any agent, inspect model routing rationale, cost, and structured output in real time.")

    customers = fetch_customers()
    cmap = {c["id"]: c for c in customers}

    # Ordered by workflow group: Assess → Grow → Communicate & Respond → Verify → Portfolio
    AGENT_INFO = {
        "CustomerHealthAgent":       ("Assess",      "haiku",  "Scanning & risk scoring"),
        "ImplementationAgent":       ("Assess",      "sonnet", "Milestone synthesis & planning"),
        "ExpansionOpportunityAgent": ("Grow",        "sonnet", "Upsell discovery & ARR uplift"),
        "QBRPreparationAgent":       ("Grow",        "sonnet", "Quarterly business review prep"),
        "SuccessPlanAgent":          ("Grow",        "sonnet", "30/60/90 success planning"),
        "BriefingAgent":             ("Communicate", "sonnet", "Executive briefing generation"),
        "EscalationCommanderAgent":  ("Respond",     "opus",   "Crisis management & battle plan"),
        "SkeptikQAAgent":            ("Verify",      "opus",   "Adversarial output review"),
        "VPChiefOfStaffAgent":       ("Portfolio",   "opus",   "Weekly portfolio operating review"),
    }

    left_col, right_col = st.columns([1, 2])

    with left_col:
        st.markdown("<div style='font-size:0.72rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.10em;margin-bottom:6px'>Configure</div>", unsafe_allow_html=True)
        selected_agent = st.selectbox(
            "Agent",
            list(AGENT_INFO.keys()),
            format_func=lambda x: f"{AGENT_INFO[x][0]} · {agent_display_name(x)} — {AGENT_INFO[x][1].capitalize()}",
        )
        group, tier, desc = AGENT_INFO[selected_agent]
        color = tier_color(tier)

        needs_cust = selected_agent != "VPChiefOfStaffAgent"
        sel_cid = None
        if needs_cust:
            sel_cid = st.selectbox("Customer", list(cmap.keys()),
                                   format_func=lambda x: f"{cmap[x]['name']} · {risk_icon(cmap[x].get('risk_level','?'))}")

        st.markdown(f"""<div class="card" style="margin-top:8px;border-left:3px solid {color};padding:9px 12px">
            <div class="kpi-label">ROUTED TO</div>
            <div style="color:{color};font-weight:800;font-size:0.95rem">{tier.capitalize()}</div>
            <div style="color:#6B6280;font-size:0.72rem;margin-top:1px">{desc}</div>
            <div style="color:#9B93A8;font-size:0.66rem;margin-top:4px;text-transform:uppercase;letter-spacing:0.08em">{group} workflow</div>
        </div>""", unsafe_allow_html=True)

        run_btn = st.button(f"Run {agent_display_name(selected_agent)}", use_container_width=True, type="primary")

        # Quick run info
        if selected_agent == "SkeptikQAAgent":
            st.caption("Skeptik requires a prior agent run for the selected customer.")
        if selected_agent == "VPChiefOfStaffAgent":
            st.caption("Portfolio-wide — no customer selection needed.")

    with right_col:
        if run_btn:
            with st.spinner(f"Running {selected_agent} ({tier.capitalize()})..."):
                result = call_agent(selected_agent, sel_cid)
            st.session_state["console_result"] = result

        if "console_result" in st.session_state:
            r = st.session_state["console_result"]
            render_agent_output(r)
            if r.get("output_text"):
                export_button(r["output_text"],
                              f"{selected_agent}_{datetime.now().strftime('%Y%m%d_%H%M')}.md")
        else:
            st.markdown("""<div style="border:2px dashed #D8D3C8;border-radius:14px;padding:48px;text-align:center;background:#FFFFFF">
                <div style="font-size:0.95rem;font-weight:600;color:#1B1040">Configure an agent and click Run</div>
                <div style="margin-top:4px;font-size:0.80rem;color:#6B6280">Model routing rationale, cost, and confidence will appear here</div>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: BRIEFINGS
# ══════════════════════════════════════════════════════════════════════════════

elif page == "Briefings":
    page_header("Briefings")
    customers = fetch_customers()
    cmap = {c["id"]: c for c in customers}

    tab_ceo, tab_vp, tab_hist = st.tabs(["CEO Briefings", "Weekly VP CX Review", "History"])

    with tab_ceo:
        gen_col, _ = st.columns([1, 2])
        with gen_col:
            sel_cid = st.selectbox(
                "Customer for briefing",
                [c["id"] for c in customers],
                format_func=lambda x: f"{cmap[x]['name']} — ${cmap[x]['arr']:,} · {risk_icon(cmap[x].get('risk_level','?'))}",
                key="brief_cid",
            )
            if st.button("Generate CEO Briefing", use_container_width=True, type="primary"):
                with st.spinner("Generating CEO Briefing (Sonnet)..."):
                    result = call_agent("BriefingAgent", sel_cid)
                st.session_state["ceo_briefing"] = result

            if "ceo_briefing" in st.session_state:
                r = st.session_state["ceo_briefing"]
                if not r.get("error"):
                    # Then offer Skeptik review
                    if st.button("Review with Skeptik Agent", use_container_width=True):
                        with st.spinner("Running Skeptik QA (Opus)..."):
                            skeptik = call_agent("SkeptikQAAgent", sel_cid)
                        st.session_state["ceo_skeptik"] = skeptik

        if "ceo_briefing" in st.session_state:
            r = st.session_state["ceo_briefing"]

            if "ceo_skeptik" in st.session_state:
                bc, ac = st.columns(2)
                with bc:
                    st.markdown("<div style='font-size:0.72rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.10em;margin-bottom:6px'>Original Briefing</div>", unsafe_allow_html=True)
                    render_meta_pills(r)
                    with st.container(border=True):
                        st.markdown("<span class='agent-report-marker'></span>", unsafe_allow_html=True)
                        st.markdown(r.get("output_text", ""), unsafe_allow_html=False)
                with ac:
                    st.markdown("<div style='font-size:0.72rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.10em;margin-bottom:6px'>Skeptik QA Review</div>", unsafe_allow_html=True)
                    skeptik = st.session_state["ceo_skeptik"]
                    render_meta_pills(skeptik)
                    with st.container(border=True):
                        st.markdown("<span class='agent-report-marker'></span>", unsafe_allow_html=True)
                        st.markdown(skeptik.get("output_text", ""), unsafe_allow_html=False)

                if r.get("output_text"):
                    export_button(r["output_text"] + "\n\n---\n\n## Skeptik QA Review\n\n" + skeptik.get("output_text",""),
                                  f"CEO_Briefing_{sel_cid}_{datetime.now().strftime('%Y%m%d')}.md",
                                  "Export Briefing + QA Review")
            else:
                render_agent_output(r)
                if r.get("output_text"):
                    export_button(r["output_text"], f"CEO_Briefing_{sel_cid}_{datetime.now().strftime('%Y%m%d')}.md")

    with tab_vp:
        if st.button("Generate Weekly VP CX Review", use_container_width=True, type="primary"):
            with st.spinner("Running VP Chief of Staff Agent (Opus)..."):
                result = call_agent("VPChiefOfStaffAgent")
            st.session_state["vp_review"] = result

        if "vp_review" in st.session_state:
            r = st.session_state["vp_review"]
            render_agent_output(r)
            if r.get("output_text"):
                export_button(r["output_text"], f"VP_CX_Review_{datetime.now().strftime('%Y%m%d')}.md")

    with tab_hist:
        st.markdown("<div style='font-size:0.72rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.10em;margin-bottom:8px'>Recent CEO Briefings</div>", unsafe_allow_html=True)
        ceo_briefs = fetch_briefings("CEO")
        if not ceo_briefs:
            st.caption("No CEO briefings generated yet.")
        for b in ceo_briefs:
            label = f"{b.get('customer_name','?')} · {b['created_at'][:16].replace('T',' ')} UTC"
            with st.expander(label):
                st.markdown(b["content"])
                export_button(b["content"], f"CEO_Briefing_{b.get('customer_id','?')}_{b['created_at'][:10]}.md")

        st.markdown("---")
        st.markdown("<div style='font-size:0.72rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.10em;margin-bottom:8px'>Recent VP CX Reviews</div>", unsafe_allow_html=True)
        vp_briefs = fetch_briefings("VP_CX")
        if not vp_briefs:
            st.caption("No VP CX reviews generated yet.")
        for b in vp_briefs:
            with st.expander(f"Weekly Review · {b['created_at'][:16].replace('T',' ')} UTC"):
                st.markdown(b["content"])
                export_button(b["content"], f"VP_CX_Review_{b['created_at'][:10]}.md")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: IMPLEMENTATION DIGEST
# ══════════════════════════════════════════════════════════════════════════════

elif page == "Implementation Digest":
    page_header("Implementation Digest", "Delivery health and timeline across all active implementations")

    conf_colors = {"Very Low": "#9B2335", "Low": "#C8642A", "Medium": "#7A5C1E", "High": "#2D5A3D"}

    # Pure-SQL overview — instant, no LLM calls. The AI narrative is on demand below.
    rows = get_implementation_overview()

    if not rows:
        st.info("No active implementations found.")
    else:
        n        = len(rows)
        at_risk  = sum(1 for r in rows if r["launch_confidence"] in ("Very Low", "Low"))
        medium   = sum(1 for r in rows if r["launch_confidence"] == "Medium")
        on_track = sum(1 for r in rows if r["launch_confidence"] == "High")
        avg_pct  = int(sum(r["pct_complete"] for r in rows) / max(n, 1))
        not_kicked = sum(1 for r in rows if not r["kicked_off"])

        # ── KPI bar ────────────────────────────────────────────────────────────
        kpis = [
            ("Active Projects", str(n),         "#1B1040", "#FFFFFF", "#E8E4DC"),
            ("At Risk",         str(at_risk),   "#9B2335", "#FDF1F2", "#F0C8CC"),
            ("Medium Conf.",    str(medium),    "#7A5C1E", "#FDFAF0", "#E8DCA0"),
            ("On Track",        str(on_track),  "#2D5A3D", "#F0FAF4", "#A8D8B8"),
            ("Avg Completion",  f"{avg_pct}%",  "#1B1040", "#FFFFFF", "#E8E4DC"),
            ("Not Kicked Off",  str(not_kicked),"#6B6280", "#FFFFFF", "#E8E4DC"),
        ]
        cells = "".join(
            f"<div style='flex:1;background:{bg};border:1px solid {bd};border-radius:10px;padding:14px 16px'>"
            f"<div style='font-size:0.64rem;font-weight:700;color:{c};text-transform:uppercase;letter-spacing:0.08em'>{label}</div>"
            f"<div style='font-size:1.5rem;font-weight:800;color:{c};margin-top:4px'>{val}</div></div>"
            for label, val, c, bg, bd in kpis
        )
        st.markdown(f"<div style='display:flex;gap:10px;margin:14px 0 18px'>{cells}</div>", unsafe_allow_html=True)

        # ── Single clean table — sorted by risk ─────────────────────────────────
        st.markdown(
            "<div style='font-size:0.72rem;font-weight:700;color:#6B6280;text-transform:uppercase;"
            "letter-spacing:0.10em;margin-bottom:8px'>Project Status "
            "<span style='font-weight:400;text-transform:none;letter-spacing:0'>— sorted by risk; select a row for the AI analysis</span></div>",
            unsafe_allow_html=True,
        )

        conf_badge = {"Very Low": "Very Low", "Low": "Low", "Medium": "Medium", "High": "High"}
        table_rows = []
        for r in rows:
            kickoff = r["kickoff_date"] or ("In progress" if r["kicked_off"] else "Not started")
            dps     = f"{r['days_post_signature']}d" if r["days_post_signature"] is not None else "—"
            dtg     = (f"{r['days_to_go_live']}d" if r["days_to_go_live"] is not None and r["days_to_go_live"] >= 0
                       else (f"{abs(r['days_to_go_live'])}d overdue" if r["days_to_go_live"] is not None else "—"))
            behind  = "On time" if r["days_behind_schedule"] == 0 else f"{r['days_behind_schedule']}d behind"
            table_rows.append({
                "Customer":        r["customer_name"],
                "Risk":            conf_badge.get(r["launch_confidence"], r["launch_confidence"]),
                "Status":          r["overall_status"],
                "Complete":        int(r["pct_complete"]),
                "Milestones":      f"{r['milestones_complete']}/{r['milestones_total']}",
                "Kickoff":         kickoff,
                "Contract Age":    dps,
                "Go-Live Target":  r["go_live_target"] or "—",
                "To Go-Live":      dtg,
                "Schedule":        behind,
                "Owner":           r["implementation_owner"],
            })
        df = pd.DataFrame(table_rows)

        sel = st.dataframe(
            df, use_container_width=True, hide_index=True, height=min(70 + 36 * n, 520),
            on_select="rerun", selection_mode="single-row",
            column_config={
                "Complete": st.column_config.ProgressColumn(
                    "Complete", min_value=0, max_value=100, format="%d%%", width="small"),
                "Customer": st.column_config.TextColumn("Customer", width="medium"),
                "Risk":     st.column_config.TextColumn("Launch Confidence", width="small"),
                "Go-Live Target": st.column_config.TextColumn("Go-Live", width="small"),
                "Contract Age":   st.column_config.TextColumn("Contract Age", help="Days since the contract was signed"),
                "To Go-Live":     st.column_config.TextColumn("To Go-Live", help="Days remaining until the go-live target"),
            },
        )

        # ── Selected project: detail panel + on-demand AI analysis ───────────────
        sel_idx = sel["selection"]["rows"][0] if sel and sel.get("selection", {}).get("rows") else None
        if sel_idx is not None:
            r  = rows[sel_idx]
            cc = conf_colors.get(r["launch_confidence"], "#1B1040")

            done = ", ".join(r["completed_milestones"]) or "None yet"
            wip  = ", ".join(r["in_progress_milestones"]) or "—"
            blk  = " · ".join(r["active_blockers"]) if r["active_blockers"] else "None recorded"

            st.markdown(f"""
<div style="background:#FFFFFF;border:1px solid #E8E4DC;border-left:4px solid {cc};border-radius:12px;padding:16px 20px;margin-top:6px">
  <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:10px">
    <div style="font-size:1.05rem;font-weight:800;color:#1B1040">{r['customer_name']}</div>
    <div style="font-size:0.8rem;font-weight:700;color:{cc}">{r['launch_confidence']} launch confidence · {r['overall_status']}</div>
  </div>
  <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:12px">
    <div style="background:#F5F2EE;border-radius:8px;padding:7px 13px"><div style="font-size:0.58rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.08em">Kicked Off</div><div style="font-size:0.92rem;font-weight:800;color:#1B1040">{('Yes · '+r['kickoff_date']) if r['kickoff_date'] else ('In progress' if r['kicked_off'] else 'Not started')}</div></div>
    <div style="background:#F5F2EE;border-radius:8px;padding:7px 13px"><div style="font-size:0.58rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.08em">Contract Age</div><div style="font-size:0.92rem;font-weight:800;color:#1B1040">{(str(r['days_post_signature'])+' days') if r['days_post_signature'] is not None else '—'}</div></div>
    <div style="background:#F5F2EE;border-radius:8px;padding:7px 13px"><div style="font-size:0.58rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.08em">Go-Live Target</div><div style="font-size:0.92rem;font-weight:800;color:#1B1040">{r['go_live_target'] or '—'}</div></div>
    <div style="background:#F5F2EE;border-radius:8px;padding:7px 13px"><div style="font-size:0.58rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.08em">To Go-Live</div><div style="font-size:0.92rem;font-weight:800;color:#1B1040">{(str(r['days_to_go_live'])+' days') if r['days_to_go_live'] is not None else '—'}</div></div>
    <div style="background:#F5F2EE;border-radius:8px;padding:7px 13px"><div style="font-size:0.58rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.08em">Schedule</div><div style="font-size:0.92rem;font-weight:800;color:{'#2D5A3D' if r['days_behind_schedule']==0 else '#9B2335'}">{'On time' if r['days_behind_schedule']==0 else str(r['days_behind_schedule'])+'d behind'}</div></div>
    <div style="background:#F5F2EE;border-radius:8px;padding:7px 13px"><div style="font-size:0.58rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.08em">Milestones</div><div style="font-size:0.92rem;font-weight:800;color:#1B1040">{r['milestones_complete']} / {r['milestones_total']} complete</div></div>
  </div>
  <div style="font-size:0.78rem;color:#3D3458;line-height:1.5"><b style="color:#2D5A3D">Implemented:</b> {done}</div>
  <div style="font-size:0.78rem;color:#3D3458;line-height:1.5;margin-top:3px"><b style="color:#7A5C1E">In progress:</b> {wip}</div>
  <div style="font-size:0.78rem;color:#3D3458;line-height:1.5;margin-top:3px"><b style="color:#9B2335">Blockers:</b> {blk}</div>
</div>""", unsafe_allow_html=True)

            ai_key = f"impl_ai_{r['customer_id']}"
            if st.button("Generate AI analysis", type="primary", key=f"impl_ai_btn_{r['customer_id']}"):
                with st.spinner(f"Analysing {r['customer_name']}…"):
                    st.session_state[ai_key] = call_agent("ImplementationAgent", r["customer_id"])
            if ai_key in st.session_state:
                res = st.session_state[ai_key]
                render_agent_output(res)
                export_button(res.get("output_text", ""),
                              f"Impl_{r['customer_name'].replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.md")
        else:
            st.caption("Select a project row above to see its full timeline and generate the AI analysis on demand.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: AUDIT TRAIL & COSTS
# ══════════════════════════════════════════════════════════════════════════════

elif page == "Audit Trail & Costs":
    page_header("Audit Trail & Cost Tracking")

    costs = fetch_costs()
    runs  = fetch_audit(limit=100)

    # ── Cost summary ──────────────────────────────────────────────────────────
    mock_count = sum(1 for r in runs if not r.get("model_used",""))
    cc = st.columns(4)
    cc[0].markdown(kpi_card("Total Spend", f"${costs.get('grand_total',0):.4f}", "all agent runs"), unsafe_allow_html=True)
    cc[1].markdown(kpi_card("Total Runs", str(len(runs)), "last 100 shown"), unsafe_allow_html=True)
    cc[2].markdown(kpi_card("Avg Cost / Run", f"${costs.get('grand_total',0)/max(len(runs),1):.5f}"), unsafe_allow_html=True)
    cc[3].markdown(kpi_card("Live / Mock", f"{len(runs)-mock_count} / {len(runs)}", "runs using real API"), unsafe_allow_html=True)

    # ── By model ──────────────────────────────────────────────────────────────
    st.markdown("<div style='font-size:0.72rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.10em;margin:16px 0 8px'>Spend by Model</div>", unsafe_allow_html=True)
    by_model = costs.get("by_model", [])
    if by_model:
        mrows = []
        for row in by_model:
            tier = model_tier_from_id(row.get("model_used",""))
            total_tok = (row.get("total_input_tokens") or 0) + (row.get("total_output_tokens") or 0)
            mrows.append({
                "Tier":   tier.capitalize(),
                "Model":  row.get("model_used",""),
                "Runs":   row.get("run_count",0),
                "Tokens": f"{total_tok:,}",
                "Cost":   f"${row.get('total_cost',0) or 0:.5f}",
            })
        st.dataframe(pd.DataFrame(mrows), use_container_width=True, hide_index=True,
                     height=45 + 36 * len(mrows))
    else:
        st.caption("No live runs recorded yet.")

    # ── Filter bar ────────────────────────────────────────────────────────────
    st.markdown("---")
    f1, f2, f3 = st.columns(3)
    with f1:
        filter_agent = st.selectbox("Filter by agent", ["All"] + list({r["agent_name"] for r in runs}))
    with f2:
        customers = fetch_customers()
        cmap = {c["id"]: c["name"] for c in customers}
        filter_cust = st.selectbox("Filter by customer", ["All"] + [c["name"] for c in customers])
    with f3:
        st.markdown("&nbsp;")

    filtered = runs
    if filter_agent != "All":
        filtered = [r for r in filtered if r["agent_name"] == filter_agent]
    if filter_cust != "All":
        filtered = [r for r in filtered if r.get("customer_name") == filter_cust]

    st.markdown(f"<div style='font-size:0.72rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.10em;margin-bottom:8px'>Run History <span style=\"font-weight:400\">({len(filtered)} records)</span></div>", unsafe_allow_html=True)

    for run in filtered:
        tier   = model_tier_from_id(run.get("model_used",""))
        color  = tier_color(tier)
        label  = (f"#{run['id']} · {run['agent_name']} · "
                  f"{run.get('customer_name','Portfolio')} · "
                  f"{run['created_at'][:16].replace('T',' ')} UTC")

        with st.expander(label):
            rc1, rc2, rc3, rc4 = st.columns(4)
            with rc1:
                st.markdown(f"<span style='color:{color};font-weight:700'>{tier.capitalize()}</span>", unsafe_allow_html=True)
                st.caption(run.get("model_used",""))
            with rc2: st.metric("Cost", f"${run.get('estimated_cost_usd',0):.5f}")
            with rc3: st.metric("Confidence", f"{run.get('confidence_score',0):.0%}")
            with rc4: st.metric("Tokens", f"{run.get('input_tokens',0):,}+{run.get('output_tokens',0):,}")

            st.markdown(f"*{run.get('model_rationale','')}*")
            st.markdown("---")
            st.markdown(run.get("output_text",""))

            if run.get("output_text"):
                fn = f"AgentRun_{run['id']}_{run['agent_name']}.md"
                export_button(run["output_text"], fn, "Export")
