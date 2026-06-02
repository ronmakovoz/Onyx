"""
VP CX Agent OS — Streamlit Frontend v2
Run: streamlit run frontend/app.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import requests
import pandas as pd
from datetime import datetime

API = "http://localhost:8000"

st.set_page_config(
    page_title="VP CX Agent OS",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global styles — Onyx brand (light, pink-lavender, dark navy) ───────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

* { font-family: 'Inter', sans-serif !important; }

/* Page background */
[data-testid="stAppViewContainer"] {
    background: #F5F2EE !important;
    min-height: 100vh;
}
[data-testid="stMain"] { background: transparent !important; }

/* Tighter main content padding */
[data-testid="stMainBlockContainer"] { padding: 1rem 1.8rem 2rem !important; max-width: 1500px; }
[data-testid="stVerticalBlockBorderWrapper"] > div { gap: 0.35rem !important; }

/* Sidebar — compact */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E8E4DC !important;
    box-shadow: 2px 0 12px rgba(27,16,64,0.06) !important;
}
[data-testid="stSidebar"] > div { padding: 1rem 0.8rem !important; }
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span { color: #3D3458 !important; }
[data-testid="stSidebar"] .stRadio label { color: #1B1040 !important; font-weight: 500 !important; font-size: 0.82rem !important; }

/* Hide decorations */
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stHeader"] { background: transparent !important; }

/* Typography — tighter */
h1 { color: #1B1040 !important; font-weight: 800 !important; font-size: 1.6rem !important; letter-spacing: -0.03em !important; margin-bottom: 0 !important; }
h2 { color: #1B1040 !important; font-weight: 700 !important; font-size: 1.1rem !important; letter-spacing: -0.02em !important; margin: 0 !important; }
h3 { color: #1B1040 !important; font-weight: 600 !important; font-size: 0.95rem !important; margin: 0 !important; }
p, li { color: #3D3458; font-size: 0.85rem; margin: 0; }
.stMarkdown p { color: #3D3458; font-size: 0.85rem; }

/* Cards — compact */
.card {
    background: #FFFFFF;
    border: 1px solid #E8E4DC;
    border-radius: 10px;
    padding: 11px 14px;
    margin-bottom: 6px;
    box-shadow: 0 1px 4px rgba(27,16,64,0.05);
}
.card-red    { border-left: 3px solid #9B2335; }
.card-yellow { border-left: 3px solid #7A5C1E; }
.card-green  { border-left: 3px solid #2D5A3D; }

/* KPI cards — compact */
.kpi-card {
    background: #FFFFFF;
    border: 1px solid #E8E4DC;
    border-radius: 10px;
    padding: 12px 14px;
    box-shadow: 0 1px 4px rgba(27,16,64,0.05);
}
.kpi-label {
    font-size: 0.62rem; color: #6B6280; text-transform: uppercase;
    letter-spacing: 0.10em; margin-bottom: 2px; font-weight: 700;
}
.kpi-value { font-size: 1.55rem; font-weight: 800; color: #1B1040; line-height: 1.1; }
.kpi-sub   { font-size: 0.68rem; color: #6B6280; margin-top: 1px; }

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
    padding: 0.32rem 1.1rem !important;
    height: auto !important;
    min-height: 0 !important;
    line-height: 1.4 !important;
    transition: all 0.15s ease !important;
    white-space: nowrap !important;
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
    font-size: 0.75rem !important;
    padding: 4px 12px !important;
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
[data-testid="stSidebar"] .stRadio > div { gap: 2px !important; }
[data-testid="stSidebar"] .stRadio > div > label {
    border-radius: 6px !important;
    padding: 7px 10px !important;
    margin-bottom: 0 !important;
    transition: background 0.12s ease !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    color: #3D3458 !important;
    display: flex !important;
    align-items: center !important;
    cursor: pointer !important;
}
[data-testid="stSidebar"] .stRadio > div > label:hover { background: #EDE9E4 !important; color: #1B1040 !important; }
/* Hide the actual radio circle */
[data-testid="stSidebar"] .stRadio > div > label > div:first-child { display: none !important; }
/* Highlight selected item */
[data-testid="stSidebar"] .stRadio > div > label[data-baseweb="radio"]:has(input:checked),
[data-testid="stSidebar"] .stRadio [aria-checked="true"] ~ label,
[data-testid="stSidebar"] .stRadio > div > label:has(input[type="radio"]:checked) {
    background: #E8E4DC !important;
    color: #1B1040 !important;
    font-weight: 700 !important;
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

/* Spinner */
[data-testid="stSpinner"] > div { border-top-color: #1B1040 !important; }

/* Caption */
.stCaption { color: #6B6280 !important; font-size: 0.70rem !important; }

/* Progress bar */
.stProgress > div > div > div > div { background: #1B1040 !important; border-radius: 4px !important; }
.stProgress > div > div > div { background: #E8E4DC !important; border-radius: 4px !important; }
.stProgress { margin: 4px 0 !important; }

/* Line chart */
[data-testid="stVegaLiteChart"] { background: #FFFFFF !important; border-radius: 10px !important; border: 1px solid #E8E4DC !important; padding: 6px !important; }

/* Reduce vertical gaps between streamlit elements */
.element-container { margin-bottom: 0.3rem !important; }
.stVerticalBlock { gap: 0.4rem !important; }
div[data-testid="column"] > div { gap: 0.4rem !important; }
</style>
""", unsafe_allow_html=True)


# ── API helpers ───────────────────────────────────────────────────────────────

@st.cache_data(ttl=20)
def fetch_customers():
    try:
        return requests.get(f"{API}/customers", timeout=5).json()
    except Exception:
        return []

@st.cache_data(ttl=20)
def fetch_summary():
    try:
        return requests.get(f"{API}/portfolio/summary", timeout=5).json()
    except Exception:
        return {}

def fetch_360(cid):
    try:
        return requests.get(f"{API}/customers/{cid}/360", timeout=5).json()
    except Exception:
        return {}

def call_agent(agent_name, customer_id=None):
    try:
        params = {"agent_name": agent_name}
        if customer_id:
            params["customer_id"] = customer_id
        return requests.post(f"{API}/agents/run", params=params, timeout=60).json()
    except Exception as e:
        return {"error": str(e)}

def call_portfolio_health():
    try:
        return requests.post(f"{API}/agents/run-portfolio-health", timeout=120).json()
    except Exception as e:
        return {"error": str(e)}

def call_impl_digest():
    try:
        return requests.post(f"{API}/agents/run-implementation-digest", timeout=120).json()
    except Exception as e:
        return {"error": str(e)}

def fetch_audit(limit=50, agent_name=None, customer_id=None):
    try:
        params = {"limit": limit}
        if agent_name:   params["agent_name"]  = agent_name
        if customer_id:  params["customer_id"] = customer_id
        return requests.get(f"{API}/audit-log", params=params, timeout=5).json()
    except Exception:
        return []

def fetch_briefings(btype=None, cid=None):
    try:
        params = {}
        if btype: params["briefing_type"] = btype
        if cid:   params["customer_id"]   = cid
        return requests.get(f"{API}/briefings", params=params, timeout=5).json()
    except Exception:
        return []

def fetch_costs():
    try:
        return requests.get(f"{API}/costs", timeout=5).json()
    except Exception:
        return {}


# ── UI utilities ──────────────────────────────────────────────────────────────

def risk_icon(level):
    return {"High": "🔴", "Medium": "🟡", "Low": "🟢",
            "Critical": "🔴", "At Risk": "🟡", "Healthy": "🟢"}.get(level, "⚪")

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

def render_model_meta(result, expanded=False, nested=False):
    """Renders the model/cost/confidence/tokens strip + routing rationale."""
    tier  = result.get("model_tier") or model_tier_from_id(result.get("model_used",""))
    color = tier_color(tier)
    conf  = result.get("confidence_score", 0)
    conf_color = "#2D5A3D" if conf >= 0.75 else "#7A5C1E" if conf >= 0.55 else "#9B2335"
    disp  = result.get("model_display") or result.get("model_used","?")

    meta_html = f"""<div style="display:flex;gap:0;background:#FFFFFF;border:1px solid #E8E4DC;border-radius:8px;padding:8px 14px;margin-bottom:6px;align-items:center">
        <div style="flex:1;border-right:1px solid #E8E4DC;padding-right:14px;margin-right:14px">
            <div class="kpi-label">Model</div>
            <div style="color:{color};font-weight:700;font-size:0.88rem">{disp}</div>
        </div>
        <div style="flex:1;border-right:1px solid #E8E4DC;padding-right:14px;margin-right:14px">
            <div class="kpi-label">Est. Cost</div>
            <div style="color:#1B1040;font-weight:700;font-size:0.88rem">${result.get('estimated_cost_usd',0):.5f}</div>
        </div>
        <div style="flex:1;border-right:1px solid #E8E4DC;padding-right:14px;margin-right:14px">
            <div class="kpi-label">Confidence</div>
            <div style="color:{conf_color};font-weight:700;font-size:0.88rem">{conf:.0%}</div>
        </div>
        <div style="flex:1">
            <div class="kpi-label">Tokens</div>
            <div style="color:#6B6280;font-size:0.80rem">{result.get('input_tokens',0):,} in · {result.get('output_tokens',0):,} out</div>
        </div>
    </div>"""
    st.markdown(meta_html, unsafe_allow_html=True)

    if result.get("is_mock"):
        st.info("Mock mode active — set `ANTHROPIC_API_KEY` for live Claude responses.", icon="ℹ️")

    rationale = result.get("model_rationale", "")
    if rationale:
        if nested:
            st.markdown(f"<div style='font-size:0.75rem;color:#6B6280;font-style:italic;margin:2px 0 6px'><b style='color:#3D3458'>Routing:</b> {rationale}</div>", unsafe_allow_html=True)
        else:
            with st.expander("Model Routing Rationale", expanded=expanded):
                st.markdown(f"<div style='color:#6B6280;font-size:0.85rem;font-style:italic'>{rationale}</div>", unsafe_allow_html=True)

def render_agent_output(result, show_structured=True, nested=False):
    """Full agent result renderer: meta strip + markdown output.

    Set nested=True when rendered inside an st.expander to avoid nesting
    expanders (which Streamlit disallows).
    """
    if "error" in result:
        st.error(f"Agent error: {result['error']}")
        return

    render_model_meta(result, nested=nested)
    st.markdown("---")

    # Structured output panel
    if show_structured and result.get("structured"):
        if nested:
            st.json(result["structured"], expanded=False)
        else:
            with st.expander("Structured Output (parsed)", expanded=False):
                st.json(result["structured"])

    st.markdown(result.get("output_text",""), unsafe_allow_html=False)
    ts = result.get("created_at","")[:16].replace("T"," ")
    st.caption(f"Generated {ts} UTC · Run ID #{result.get('run_id','?')} · {result.get('agent_name','?')}")


def page_header(title, subtitle=""):
    sub = f"<div style='color:#6B6280;font-size:0.82rem;margin-bottom:14px'>{subtitle}</div>" if subtitle else "<div style='margin-bottom:8px'></div>"
    st.markdown(f"<h1 style='margin-bottom:2px'>{title}</h1>{sub}", unsafe_allow_html=True)


_export_counter = [0]
def export_button(content: str, filename: str, label: str = "⬇️ Export"):
    _export_counter[0] += 1
    st.download_button(label=label, data=content, file_name=filename,
                       mime="text/markdown", key=f"dl_{_export_counter[0]}_{filename[:20]}")


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    if st.button("About the Agents", use_container_width=True, key="sb_about", type="secondary"):
        st.session_state["show_agent_guide"] = True

    st.markdown("<div style='padding:8px 0 4px'><span style='font-size:1.3rem;font-weight:900;color:#1B1040;letter-spacing:-0.04em'>ONYX</span><span style='font-size:0.65rem;font-weight:700;color:#6B6280;letter-spacing:0.12em;margin-left:8px;vertical-align:middle'>CX AGENT OS</span></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.72rem;color:#6B6280;margin-bottom:4px'>Executive Demo · AI-Powered Customer OS</div>", unsafe_allow_html=True)
    st.markdown("---")

    _pages = ["Portfolio Dashboard", "Customer 360", "Agent Console",
              "Briefings", "Implementation Digest", "Audit Trail & Costs"]
    _default_idx = _pages.index(st.session_state.get("nav_page", "Portfolio Dashboard")) \
                   if st.session_state.get("nav_page") in _pages else 0
    page = st.radio(
        "",
        _pages,
        index=_default_idx,
        label_visibility="collapsed",
        key="nav_radio"
    )
    st.session_state["nav_page"] = page

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

    st.markdown("<div style='margin-top:8px;font-size:0.68rem;color:#9B93A8'>API · localhost:8000</div>", unsafe_allow_html=True)


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
            "when": "Weekly — generates the VP CX operating review across the full 25-customer portfolio.",
            "what": "Synthesizes the entire portfolio into a board-ready weekly review: top 5 risks, ARR at risk, renewal watchlist, implementation bottlenecks, product feedback themes, support burden, cross-functional asks, and a CEO-ready paragraph summary.",
            "outputs": ["Portfolio health summary", "Top 5 risks + actions", "ARR at risk breakdown", "Renewals watchlist", "Impl bottlenecks", "Product feedback themes", "Cross-functional asks", "CEO-ready paragraph"],
        },
    ]

    st.markdown("<div style='color:#6B6280;font-size:0.82rem;margin-bottom:16px'>Six AI agents run your post-sale org. Each is routed to the optimal Claude model based on task complexity.</div>", unsafe_allow_html=True)

    for a in AGENTS:
        st.markdown(f"""
        <div style="background:#FFFFFF;border:1px solid #E8E4DC;border-radius:10px;padding:14px 16px;margin-bottom:10px;box-shadow:0 1px 4px rgba(27,16,64,0.05)">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
                <span style="font-size:1.2rem">{a['icon']}</span>
                <span style="font-size:0.95rem;font-weight:700;color:#1B1040">{a['name']}</span>
                <span style="background:{a['model_bg']};color:{a['model_color']};font-size:0.65rem;font-weight:700;padding:2px 8px;border-radius:20px;margin-left:auto">{a['model']}</span>
            </div>
            <div style="font-size:0.80rem;color:#3D3458;line-height:1.5;margin-bottom:6px">{a['what']}</div>
            <div style="font-size:0.72rem;color:#6B6280;font-style:italic;margin-bottom:8px">💡 {a['when']}</div>
            <div style="display:flex;flex-wrap:wrap;gap:4px">
                {''.join(f'<span style="background:#EDEAF4;color:#3D3458;font-size:0.68rem;font-weight:600;padding:2px 8px;border-radius:20px">{o}</span>' for o in a['outputs'])}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='font-size:0.75rem;color:#6B6280;margin-top:4px;text-align:center'>Haiku → fast scanning &nbsp;·&nbsp; Sonnet → synthesis &nbsp;·&nbsp; Opus → judgment & adversarial review</div>", unsafe_allow_html=True)


# Show agent guide dialog
if st.session_state.pop("show_agent_guide", False):
    show_agent_guide()


# Handle quick run from sidebar
if "quick_run" in st.session_state:
    agent_name, cid = st.session_state.pop("quick_run")
    with st.spinner(f"Running {agent_name}..."):
        result = call_agent(agent_name, cid)
    st.session_state["console_result"] = result
    st.session_state["nav_page"] = "Agent Console"
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

if page == "Portfolio Dashboard":
    page_header("Portfolio Dashboard", "Real-time view of all 25 enterprise customers")

    summary   = fetch_summary()
    customers = fetch_customers()

    if not summary or not customers:
        st.error("❌ Cannot reach backend. Run: `uvicorn backend.main:app --port 8000`")
        st.stop()

    # ── KPI row ───────────────────────────────────────────────────────────────
    total_arr   = summary.get('total_arr', 0)
    arr_risk    = summary.get('arr_at_risk', 0)
    arr_pct     = arr_risk / max(total_arr, 1) * 100
    hi_c        = summary.get('critical_count', 0)
    med_c       = summary.get('at_risk_count', 0)
    ok_c        = summary.get('healthy_count', 0)
    total_c     = max(summary.get('total_customers', 1), 1)

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    kpis = [
        ("Total Customers",  str(summary.get("total_customers", 0)),  ""),
        ("Total ARR",        f"${total_arr/1e6:.1f}M",                ""),
        ("ARR at Risk",      f"${arr_risk/1e6:.1f}M",                 f"{arr_pct:.0f}% of portfolio"),
        ("Open Escalations", str(summary.get("open_escalations", 0)), "active"),
        ("Renewals (90d)",   str(summary.get("renewals_next_90_days", 0)), "due"),
        ("Avg Health Score", str(summary.get("avg_health_score", 0)), "/ 100"),
    ]
    for col, (label, val, sub) in zip([k1,k2,k3,k4,k5,k6], kpis):
        with col:
            st.markdown(f"<div class='kpi-card'><div class='kpi-label'>{label}</div><div class='kpi-value'>{val}</div><div class='kpi-sub'>{sub}</div></div>", unsafe_allow_html=True)

    # ── Health distribution bar ───────────────────────────────────────────────
    h_pct = hi_c  / total_c * 100
    m_pct = med_c / total_c * 100
    l_pct = ok_c  / total_c * 100
    st.markdown(f"""
    <div style="margin:14px 0 16px">
      <div style="display:flex;height:10px;border-radius:50px;overflow:hidden;gap:2px">
        <div style="width:{h_pct:.1f}%;background:#9B2335;border-radius:50px 0 0 50px"></div>
        <div style="width:{m_pct:.1f}%;background:#C9952A"></div>
        <div style="width:{l_pct:.1f}%;background:#2D5A3D;border-radius:0 50px 50px 0"></div>
      </div>
      <div style="display:flex;gap:18px;margin-top:6px">
        <span style="font-size:0.70rem;color:#9B2335;font-weight:600">
          <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#9B2335;margin-right:4px;vertical-align:middle"></span>
          High Risk &nbsp;{hi_c}
        </span>
        <span style="font-size:0.70rem;color:#7A5C1E;font-weight:600">
          <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#C9952A;margin-right:4px;vertical-align:middle"></span>
          Medium Risk &nbsp;{med_c}
        </span>
        <span style="font-size:0.70rem;color:#2D5A3D;font-weight:600">
          <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#2D5A3D;margin-right:4px;vertical-align:middle"></span>
          Healthy &nbsp;{ok_c}
        </span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Scan button row ───────────────────────────────────────────────────────
    scan_col, status_col = st.columns([1, 4])
    with scan_col:
        if st.button("Scan Full Portfolio", use_container_width=True, type="primary",
                     help="Run CustomerHealthAgent on all 25 customers using Claude Haiku"):
            with st.spinner("Scanning all 25 customers..."):
                scan = call_portfolio_health()
            st.session_state["portfolio_scan"] = scan
    with status_col:
        if "portfolio_scan" in st.session_state:
            scan = st.session_state["portfolio_scan"]
            if "error" not in scan:
                st.markdown(
                    f"<div style='margin-top:8px;font-size:0.78rem;color:#2D5A3D;font-weight:600'>"
                    f"Scanned {scan.get('customers_scanned',0)} customers &nbsp;·&nbsp; "
                    f"Total cost: ${scan.get('total_cost_usd',0):.4f} &nbsp;·&nbsp; "
                    f"<span style='color:#6B6280;font-weight:400'>Claude Haiku</span></div>",
                    unsafe_allow_html=True
                )

    st.markdown("<div style='margin:12px 0'></div>", unsafe_allow_html=True)

    # ── Customer table + escalations ──────────────────────────────────────────
    left_col, right_col = st.columns([3, 1])

    with left_col:
        st.markdown(
            "<div style='font-size:0.72rem;font-weight:700;color:#6B6280;text-transform:uppercase;"
            "letter-spacing:0.10em;margin-bottom:8px'>Customer Portfolio"
            " <span style=\"font-weight:400;text-transform:none;letter-spacing:0\">— select a row to drill in</span></div>",
            unsafe_allow_html=True
        )
        df = pd.DataFrame(customers)
        df["Risk"]     = df["risk_level"].map({"High": "High", "Medium": "Medium", "Low": "Healthy"})
        df["ARR"]      = df["arr"].map(lambda x: f"${x:,.0f}")
        df["Health"]   = df["health_score"]
        df["Trend"]    = df.get("health_trend", pd.Series([""] * len(df)))
        df["Renewal"]  = df["renewal_date"]
        df["Champion"] = df["champion_status"]
        disp = df[["name","industry","ARR","Health","Trend","Renewal","Champion","Risk"]].rename(
            columns={"name": "Customer", "industry": "Industry"}
        )
        disp = disp.sort_values("Health")

        sel = st.dataframe(disp, use_container_width=True, height=480,
                           on_select="rerun", selection_mode="single-row")
        if sel and sel.get("selection", {}).get("rows"):
            ridx   = sel["selection"]["rows"][0]
            chosen = customers[disp.index[ridx]]
            st.session_state["selected_cid"]   = chosen["id"]
            st.session_state["selected_cname"] = chosen["name"]
            st.markdown(
                f"<div style='margin-top:6px;font-size:0.78rem;color:#2D5A3D;font-weight:600'>"
                f"Selected <b>{chosen['name']}</b> ({chosen['risk_level']} risk) — navigate to Customer 360</div>",
                unsafe_allow_html=True
            )

    with right_col:
        st.markdown(
            "<div style='font-size:0.72rem;font-weight:700;color:#6B6280;text-transform:uppercase;"
            "letter-spacing:0.10em;margin-bottom:8px'>Top Escalations</div>",
            unsafe_allow_html=True
        )
        for esc in summary.get("top_escalations", []):
            is_crit   = esc.get("severity") == "Critical"
            sev_color = "#9B2335" if is_crit else "#7A5C1E"
            sev_bg    = "#FDF1F2" if is_crit else "#FDF8EE"
            cname     = next((c["name"] for c in customers if c["id"] == esc.get("customer_id")), "?")
            st.markdown(f"""
<div style="background:{sev_bg};border:1px solid {'#F5C6CB' if is_crit else '#EDD9A3'};
     border-left:3px solid {sev_color};border-radius:8px;padding:9px 11px;margin-bottom:7px">
  <div style="font-size:0.60rem;color:{sev_color};font-weight:700;text-transform:uppercase;
       letter-spacing:0.07em">{esc.get('severity','?')} · {cname.upper()}</div>
  <div style="font-size:0.78rem;color:#1B1040;margin-top:3px;font-weight:600;line-height:1.35">
    {esc.get('title','')[:65]}</div>
  <div style="font-size:0.68rem;color:#6B6280;margin-top:3px">{esc.get('owner','')}</div>
</div>""", unsafe_allow_html=True)

    # ── Portfolio scan results ────────────────────────────────────────────────
    if "portfolio_scan" in st.session_state and "error" not in st.session_state["portfolio_scan"]:
        scan = st.session_state["portfolio_scan"]
        st.markdown("<div style='margin:16px 0 8px'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div style='font-size:0.72rem;font-weight:700;color:#6B6280;text-transform:uppercase;"
            "letter-spacing:0.10em;margin-bottom:8px'>AI Health Scan Results"
            " <span style=\"font-weight:400;text-transform:none;letter-spacing:0;color:#9B93A8\">"
            "— CustomerHealthAgent · Claude Haiku</span></div>",
            unsafe_allow_html=True
        )
        scan_df = pd.DataFrame(scan["results"])
        scan_df["Score"]    = scan_df["health_score"]
        scan_df["Risk"]     = scan_df["risk_level"]
        scan_df["Conf"]     = scan_df["confidence_score"].map(lambda x: f"{x:.0%}")
        scan_df["Cost"]     = scan_df["estimated_cost_usd"].map(lambda x: f"${x:.5f}")
        scan_df["Top Risk"] = scan_df["top_risk_drivers"].map(lambda x: x[0][:55] if x else "")
        st.dataframe(
            scan_df[["customer_name","Score","Risk","Conf","Cost","Top Risk"]].rename(
                columns={"customer_name": "Customer"}
            ),
            use_container_width=True, height=300
        )


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
        format_func=lambda x: f"{risk_icon(cmap[x].get('risk_level','?'))} {cmap[x]['name']} — {cmap[x]['industry']} · ${cmap[x]['arr']:,}",
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
            {c['industry']} &nbsp;·&nbsp; {c.get('employee_count','?'):,} employees &nbsp;·&nbsp;
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
          <div style="font-size:0.60rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.08em">Open Tickets</div>
          <div style="font-size:1.05rem;font-weight:800;color:#1B1040;line-height:1.3">{open_tickets}</div>
        </div>
        <div style="background:#F5F2EE;border-radius:8px;padding:7px 14px;text-align:center;min-width:80px">
          <div style="font-size:0.60rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.08em">Escalations</div>
          <div style="font-size:1.05rem;font-weight:800;color:{'#9B2335' if escs else '#2D5A3D'};line-height:1.3">{len(escs)}</div>
        </div>
        <div style="background:#F5F2EE;border-radius:8px;padding:7px 14px;text-align:center;min-width:80px">
          <div style="font-size:0.60rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.08em">Renewal</div>
          <div style="font-size:1.05rem;font-weight:800;color:#1B1040;line-height:1.3">{renewal_days}d</div>
        </div>
        <div style="background:#F5F2EE;border-radius:8px;padding:7px 14px;text-align:center;min-width:90px">
          <div style="font-size:0.60rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.08em">Champion</div>
          <div style="font-size:0.82rem;font-weight:700;color:{champ_color};line-height:1.4">{champ_status}</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Agent action bar ──────────────────────────────────────────────────────
    st.markdown("<div style='font-size:0.68rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.10em;margin-bottom:6px'>Run Agents</div>", unsafe_allow_html=True)
    ab1, ab2, ab3, ab4, ab5 = st.columns(5)
    triggered = None
    btns = [
        (ab1, "CustomerHealthAgent",      "Health Assessment",      "secondary"),
        (ab2, "ImplementationAgent",      "Implementation Report",  "secondary"),
        (ab3, "BriefingAgent",            "Generate CEO Briefing",  "primary"),
        (ab4, "EscalationCommanderAgent", "Escalation Commander",   "primary"),
        (ab5, "SkeptikQAAgent",           "Skeptik QA Review",      "secondary"),
    ]
    for col, aname, label, btype in btns:
        with col:
            if st.button(label, use_container_width=True, type=btype, key=f"360_{aname}"):
                triggered = aname

    if triggered:
        with st.spinner(f"Running {triggered}..."):
            result = call_agent(triggered, cid)
        st.session_state[f"360_result_{cid}_{triggered}"] = result

    # Show most recent result for this customer
    recent_key = next(
        (k for k in reversed(list(st.session_state.keys()))
         if k.startswith(f"360_result_{cid}_")), None
    )
    if recent_key:
        result = st.session_state[recent_key]
        agent_label = recent_key.split("_")[-1]
        st.markdown(f"<div style='font-size:0.72rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.10em;margin:10px 0 6px'>{agent_label} Output</div>", unsafe_allow_html=True)

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
                    with st.container():
                        st.markdown(f"<div class='skeptik-before'>", unsafe_allow_html=True)
                        prior = st.session_state[prior_key]
                        st.markdown(prior.get("output_text","")[:1200] + "...", unsafe_allow_html=False)
                        st.markdown("</div>", unsafe_allow_html=True)
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

    st.markdown("---")

    # ── Tabbed detail view ────────────────────────────────────────────────────
    tab_use, tab_impl, tab_tick, tab_escs, tab_stk, tab_notes, tab_renew = st.tabs(
        ["Usage & Health", "Implementation", "Tickets", "Escalations", "Stakeholders", "Notes", "Renewal"]
    )

    with tab_use:
        mrow = metrics[0] if metrics else {}
        if mrow:
            dau_trend = mrow.get('dau_trend_30d', 0)
            trend_color = "#2D5A3D" if dau_trend >= 0 else "#9B2335"
            trend_sign  = "+" if dau_trend >= 0 else ""
            usage_items = [
                ("Daily Active Users", str(int(mrow.get("dau",0))),
                 f"<span style='color:{trend_color};font-size:0.68rem'>{trend_sign}{dau_trend:.0%} vs 30d</span>"),
                ("Asset Coverage",    f"{int(mrow.get('asset_coverage_pct',0))}%", ""),
                ("Features Active",   f"{int(mrow.get('features_enabled',0))}/18", ""),
                ("False Positive Rate", f"{mrow.get('false_positive_rate',0):.0%}", ""),
                ("API Calls (30d)",   f"{int(mrow.get('api_calls_last_30d',0)):,}", ""),
                ("Alerts (30d)",      str(int(mrow.get("alerts_generated_last_30d",0))), ""),
                ("Logins (7d)",       str(int(mrow.get("unique_logins_last_7d",0))), ""),
                ("Agents Deployed",   str(int(mrow.get("agents_deployed",0))), ""),
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
            hdf = pd.DataFrame(history)[["date","health_score"]].copy()
            hdf["date"] = pd.to_datetime(hdf["date"])
            hdf = hdf.sort_values("date")
            st.line_chart(hdf.set_index("date")["health_score"], height=140, use_container_width=True)

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
        open_t    = [t for t in tickets if t["status"] != "Resolved"]
        closed_t  = [t for t in tickets if t["status"] == "Resolved"]
        st.markdown(f"<div style='font-size:0.78rem;font-weight:700;color:#1B1040;margin-bottom:6px'>{len(open_t)} Open <span style=\"color:#6B6280;font-weight:400\">· {len(closed_t)} Resolved</span></div>", unsafe_allow_html=True)
        for t in sorted(tickets, key=lambda x: ("P1P2P3P4".index(x["severity"]) if x["severity"] in "P1P2P3P4" else 9, x["status"] == "Resolved")):
            sc = {"P1":"#9B2335","P2":"#7A5C1E","P3":"#5C4A1E","P4":"#6B6280"}.get(t["severity"],"#6B6280")
            si = "🔴" if t["status"]=="Open" else "🔄" if t["status"]=="In Progress" else "✅"
            st.markdown(f"""<div class="card">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <span style="background:{sc}18;color:{sc};font-weight:700;font-size:0.72rem;padding:2px 8px;border-radius:20px;border:1px solid {sc}44">{t['severity']}</span>
                    <span style="color:#6B6280;font-size:0.75rem">{si} {t['status']}</span>
                </div>
                <div style="color:#1B1040;font-size:0.88rem;margin-top:6px;font-weight:500">{t['title']}</div>
                <div style="color:#6B6280;font-size:0.72rem;margin-top:3px">Opened {t['opened_at'][:10]} · Assignee: {t.get('assignee','?')}</div>
                {f'<div style="color:#7A5C1E;font-size:0.72rem;margin-top:2px">⚠️ {t["escalation_reference"]}</div>' if t.get("escalation_reference") else ''}
            </div>""", unsafe_allow_html=True)

    with tab_escs:
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
        role_colors = {"Champion":"#1B1040","Technical Sponsor":"#3D3458","Business Sponsor":"#5C4A1E",
                       "Executive Sponsor":"#2D3A4A","Economic Buyer":"#9B2335"}
        role_bg = {"Champion":"#EAE6E0","Technical Sponsor":"#EDEAF4","Business Sponsor":"#F0EBE0",
                   "Executive Sponsor":"#E8EBF0","Economic Buyer":"#F5ECEC"}
        eng_icons = {"High":"🟢","Medium":"🟡","Low":"🔴","None":"⚫"}
        for s in stk:
            rc = role_colors.get(s["role"],"#6B6280")
            rb = role_bg.get(s["role"],"#EAE6E0")
            ei = eng_icons.get(s.get("engagement_level",""),"?")
            st.markdown(f"""<div class="card">
                <div style="display:flex;justify-content:space-between;align-items:flex-start">
                    <div>
                        <span style="font-weight:700;color:#1B1040;font-size:0.95rem">{s['name']}</span>
                        <div style="font-size:0.80rem;color:#6B6280;margin-top:1px">{s['title']}</div>
                    </div>
                    <span style="font-size:0.72rem;color:#6B6280">{ei} {s.get('engagement_level','?')}</span>
                </div>
                <div style="margin-top:6px;display:flex;align-items:center;gap:8px">
                    <span style="background:{rb};color:{rc};font-size:0.72rem;font-weight:700;padding:2px 8px;border-radius:20px">{s['role']}</span>
                    <span style="color:#6B6280;font-size:0.72rem">{s['email']}</span>
                </div>
            </div>""", unsafe_allow_html=True)

    with tab_notes:
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
                <div style="color:#6B6280;font-size:0.72rem;margin-top:4px">👥 {n.get('attendees_internal','?')} · {n.get('attendees_customer','?')}</div>
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
                <div style="color:#6B6280">Exec Involvement Required: {'✅ Yes' if renewal.get('requires_exec_involvement') else 'No'}</div>
            </div>""", unsafe_allow_html=True)

            if st.button("Generate CEO Briefing for Renewal", type="primary"):
                with st.spinner("Generating CEO Briefing (Sonnet)..."):
                    result = call_agent("BriefingAgent", cid)
                st.session_state[f"360_result_{cid}_BriefingAgent"] = result
                st.rerun()
        else:
            st.caption("No renewal record found within 180-day window.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: AGENT CONSOLE
# ══════════════════════════════════════════════════════════════════════════════

elif page == "Agent Console":
    page_header("Agent Console", "Run any agent, inspect model routing rationale, cost, and structured output in real time.")

    customers = fetch_customers()
    cmap = {c["id"]: c for c in customers}

    AGENT_INFO = {
        "CustomerHealthAgent":      ("🩺", "haiku",  "Scanning & risk scoring"),
        "ImplementationAgent":      ("🔧", "sonnet", "Milestone synthesis & planning"),
        "BriefingAgent":            ("📋", "sonnet", "Executive briefing generation"),
        "EscalationCommanderAgent": ("🚨", "opus",   "Crisis management & battle plan"),
        "SkeptikQAAgent":           ("🔍", "opus",   "Adversarial output review"),
        "VPChiefOfStaffAgent":      ("📊", "opus",   "Weekly portfolio operating review"),
    }

    left_col, right_col = st.columns([1, 2])

    with left_col:
        st.markdown("<div style='font-size:0.72rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.10em;margin-bottom:6px'>Configure</div>", unsafe_allow_html=True)
        selected_agent = st.selectbox(
            "Agent",
            list(AGENT_INFO.keys()),
            format_func=lambda x: f"{AGENT_INFO[x][0]} {x} — {AGENT_INFO[x][1].capitalize()}",
        )
        emoji, tier, desc = AGENT_INFO[selected_agent]
        color = tier_color(tier)

        needs_cust = selected_agent != "VPChiefOfStaffAgent"
        sel_cid = None
        if needs_cust:
            sel_cid = st.selectbox("Customer", list(cmap.keys()),
                                   format_func=lambda x: f"{risk_icon(cmap[x].get('risk_level','?'))} {cmap[x]['name']}")

        st.markdown(f"""<div class="card" style="margin-top:8px;border-left:3px solid {color};padding:9px 12px">
            <div class="kpi-label">ROUTED TO</div>
            <div style="color:{color};font-weight:800;font-size:0.95rem">{tier.capitalize()}</div>
            <div style="color:#6B6280;font-size:0.72rem;margin-top:1px">{desc}</div>
        </div>""", unsafe_allow_html=True)

        run_btn = st.button(f"▶ Run {selected_agent}", use_container_width=True, type="primary")

        # Quick run info
        if selected_agent == "SkeptikQAAgent":
            st.info("ℹ️ Skeptik requires a prior agent run for the selected customer.", icon="🔍")
        if selected_agent == "VPChiefOfStaffAgent":
            st.info("ℹ️ Portfolio-wide — no customer selection needed.", icon="📊")

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
                format_func=lambda x: f"{risk_icon(cmap[x].get('risk_level','?'))} {cmap[x]['name']} — ${cmap[x]['arr']:,}",
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
                    render_model_meta(r)
                    st.markdown("---")
                    st.markdown(f"<div class='skeptik-before'>{r.get('output_text','')}</div>", unsafe_allow_html=True)
                with ac:
                    st.markdown("<div style='font-size:0.72rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.10em;margin-bottom:6px'>Skeptik QA Review</div>", unsafe_allow_html=True)
                    skeptik = st.session_state["ceo_skeptik"]
                    render_model_meta(skeptik)
                    st.markdown("---")
                    st.markdown(f"<div class='skeptik-after'>{skeptik.get('output_text','')}</div>", unsafe_allow_html=True)

                if r.get("output_text"):
                    export_button(r["output_text"] + "\n\n---\n\n## Skeptik QA Review\n\n" + skeptik.get("output_text",""),
                                  f"CEO_Briefing_{sel_cid}_{datetime.now().strftime('%Y%m%d')}.md",
                                  "⬇️ Export Briefing + QA Review")
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
    page_header("Implementation Digest", "Weekly implementation health across all active projects — powered by ImplementationAgent (Sonnet)")

    if st.button("🔧 Run Weekly Implementation Digest", use_container_width=False, type="primary"):
        with st.spinner("Running ImplementationAgent on all active projects (Sonnet)..."):
            digest = call_impl_digest()
        st.session_state["impl_digest"] = digest

    if "impl_digest" in st.session_state:
        digest = st.session_state["impl_digest"]
        if "error" in digest:
            st.error(f"Error: {digest['error']}")
        else:
            results = digest.get("results", [])
            st.success(f"Reviewed {digest.get('projects_reviewed',0)} implementation projects · Total cost: ${digest.get('total_cost_usd',0):.4f}")

            conf_order = {"Very Low": 0, "Low": 1, "Medium": 2, "High": 3}
            conf_colors = {"Very Low":"#9B2335","Low":"#7A5C1E","Medium":"#5C4A1E","High":"#2D5A3D"}

            # Summary metrics
            c1, c2, c3, c4 = st.columns(4)
            at_risk = sum(1 for r in results if r["launch_confidence"] in ("Very Low","Low"))
            on_track = sum(1 for r in results if r["launch_confidence"] == "High")
            with c1: st.metric("Projects Reviewed", len(results))
            with c2: st.metric("At Risk", at_risk, delta_color="inverse")
            with c3: st.metric("On Track", on_track)
            with c4: st.metric("Cost", f"${digest.get('total_cost_usd',0):.4f}")

            st.markdown("---")
            st.markdown("<div style='font-size:0.72rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.10em;margin-bottom:6px'>Project Status Overview <span style=\"font-weight:400\">— sorted by launch confidence risk</span></div>", unsafe_allow_html=True)

            for r in sorted(results, key=lambda x: conf_order.get(x["launch_confidence"], 2)):
                cc = conf_colors.get(r["launch_confidence"], "#1B1040")
                blockers_html = "".join(
                    f"<div style='font-size:0.78rem;color:#7A5C1E;margin-top:2px'>⚠️ {b[:80]}</div>"
                    for b in r.get("active_blockers", [])
                )
                with st.expander(
                    f"{r['customer_name']} — {r['overall_status']} · {r['pct_complete']}% complete",
                    expanded=r["launch_confidence"] in ("Very Low","Low")
                ):
                    col_a, col_b = st.columns([1, 2])
                    with col_a:
                        st.markdown(f"<div class='card'><div class='kpi-label'>Launch Confidence</div>"
                                    f"<div style='color:{cc};font-weight:800;font-size:1.2rem'>{r['launch_confidence']}</div>"
                                    f"<div style='margin-top:8px;font-size:0.82rem;color:#3D3458'>{r.get('recommended_intervention','')[:120]}</div>"
                                    f"{blockers_html}</div>", unsafe_allow_html=True)
                    with col_b:
                        with st.spinner("Loading full analysis..."):
                            cust_result = call_agent("ImplementationAgent", r["customer_id"])
                        render_agent_output(cust_result, show_structured=False, nested=True)
                        export_button(cust_result.get("output_text",""),
                                      f"Impl_{r['customer_name'].replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.md")
    else:
        st.markdown("""<div style="border:2px dashed #D8D3C8;border-radius:14px;padding:40px;text-align:center;background:#FFFFFF">
            <div style="margin-top:2px;font-size:0.9rem;font-weight:600;color:#1B1040">Generate the weekly implementation digest</div>
            <div style="margin-top:4px;font-size:0.78rem;color:#6B6280">Runs ImplementationAgent (Sonnet) on all active implementation projects</div>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: AUDIT TRAIL & COSTS
# ══════════════════════════════════════════════════════════════════════════════

elif page == "Audit Trail & Costs":
    page_header("Audit Trail & Cost Tracking")

    costs = fetch_costs()
    runs  = fetch_audit(limit=100)

    # ── Cost summary ──────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Total Spend", f"${costs.get('grand_total',0):.4f}")
    with c2: st.metric("Total Runs", len(runs))
    with c3: st.metric("Avg Cost / Run", f"${costs.get('grand_total',0)/max(len(runs),1):.5f}")
    with c4:
        mock_count = sum(1 for r in runs if not r.get("model_used",""))
        st.metric("Live / Mock", f"{len(runs)-mock_count} / {len(runs)}")

    # ── By model ──────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("<div style='font-size:0.72rem;font-weight:700;color:#6B6280;text-transform:uppercase;letter-spacing:0.10em;margin-bottom:8px'>Spend by Model</div>", unsafe_allow_html=True)
    by_model = costs.get("by_model", [])
    if by_model:
        for row in by_model:
            tier   = model_tier_from_id(row.get("model_used",""))
            color  = tier_color(tier)
            mc1, mc2, mc3, mc4 = st.columns([3, 1, 1, 1])
            with mc1:
                st.markdown(f"<span style='color:{color};font-weight:700'>{tier.capitalize()}</span> "
                            f"<span style='color:#6B6280;font-size:0.75rem'>{row.get('model_used','')}</span>",
                            unsafe_allow_html=True)
            with mc2: st.metric("Runs", row.get("run_count",0))
            with mc3:
                total_tok = (row.get("total_input_tokens") or 0) + (row.get("total_output_tokens") or 0)
                st.metric("Tokens", f"{total_tok:,}")
            with mc4: st.metric("Cost", f"${row.get('total_cost',0) or 0:.5f}")

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
                export_button(run["output_text"], fn, "⬇️ Export")
