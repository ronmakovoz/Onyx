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

# ── Global styles ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0d1117; }
[data-testid="stSidebar"] { background: #161b22; border-right: 1px solid #30363d; }
[data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: #c9d1d9 !important; }
h1, h2, h3 { color: #e6edf3 !important; }
p, li { color: #c9d1d9; }
.card {
    background: #161b22; border: 1px solid #30363d; border-radius: 10px;
    padding: 16px 20px; margin-bottom: 10px;
}
.card-red    { border-left: 4px solid #ff4b4b; }
.card-yellow { border-left: 4px solid #ffa726; }
.card-green  { border-left: 4px solid #4caf50; }
.badge {
    display: inline-block; padding: 2px 10px; border-radius: 20px;
    font-size: 0.72rem; font-weight: 700; margin-right: 6px; vertical-align: middle;
}
.badge-haiku  { background: #0d2a3a; color: #4fc3f7; border: 1px solid #4fc3f7; }
.badge-sonnet { background: #1a1a3a; color: #9c88ff; border: 1px solid #9c88ff; }
.badge-opus   { background: #2a1a3a; color: #ce93d8; border: 1px solid #ce93d8; }
.badge-mock   { background: #2a2a0a; color: #ffd54f; border: 1px solid #ffd54f; }
.badge-risk-high   { background: #3a1010; color: #ff6b6b; border: 1px solid #ff4b4b; }
.badge-risk-medium { background: #3a2510; color: #ffa726; border: 1px solid #ffa726; }
.badge-risk-low    { background: #0a2a1a; color: #66bb6a; border: 1px solid #4caf50; }
.kpi-label { font-size: 0.72rem; color: #8b949e; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 2px; }
.kpi-value { font-size: 1.9rem; font-weight: 800; color: #e6edf3; line-height: 1; }
.kpi-sub   { font-size: 0.78rem; color: #8b949e; margin-top: 2px; }
hr { border-color: #30363d !important; }
.stButton > button { border-radius: 6px !important; font-weight: 600 !important; }
[data-testid="stMetricLabel"] { color: #8b949e !important; font-size: 0.78rem !important; }
[data-testid="stMetricValue"] { color: #e6edf3 !important; }
.output-box {
    background: #0d1117; border: 1px solid #30363d; border-radius: 8px;
    padding: 20px; font-family: inherit;
}
.skeptik-before { border-left: 4px solid #9c88ff; padding-left: 12px; }
.skeptik-after  { border-left: 4px solid #4caf50; padding-left: 12px; }
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
    if score < 40: return "#ff4b4b"
    if score < 60: return "#ffa726"
    return "#4caf50"

def model_tier_from_id(model_id):
    if "haiku" in model_id.lower(): return "haiku"
    if "opus"  in model_id.lower(): return "opus"
    return "sonnet"

def tier_color(tier):
    return {"haiku": "#4fc3f7", "sonnet": "#9c88ff", "opus": "#ce93d8"}.get(tier, "#fff")

def render_model_meta(result, expanded=False):
    """Renders the model/cost/confidence/tokens strip + routing rationale."""
    tier  = result.get("model_tier") or model_tier_from_id(result.get("model_used",""))
    color = tier_color(tier)
    conf  = result.get("confidence_score", 0)
    conf_color = "#4caf50" if conf >= 0.75 else "#ffa726" if conf >= 0.55 else "#ff4b4b"
    disp  = result.get("model_display") or result.get("model_used","?")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"<div class='kpi-label'>Model</div><div style='color:{color};font-weight:700;font-size:1rem'>{disp}</div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='kpi-label'>Est. Cost</div><div style='color:#4caf50;font-weight:700;font-size:1rem'>${result.get('estimated_cost_usd',0):.5f}</div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='kpi-label'>Confidence</div><div style='color:{conf_color};font-weight:700;font-size:1rem'>{conf:.0%}</div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div class='kpi-label'>Tokens</div><div style='color:#8b949e;font-size:0.9rem'>{result.get('input_tokens',0):,} in · {result.get('output_tokens',0):,} out</div>", unsafe_allow_html=True)

    if result.get("is_mock"):
        st.info("🟡 **Mock mode active** — set `ANTHROPIC_API_KEY` for live Claude responses.", icon="ℹ️")

    with st.expander("🔀 Model Routing Rationale", expanded=expanded):
        st.markdown(f"<div style='color:#8b949e;font-size:0.85rem;font-style:italic'>{result.get('model_rationale','')}</div>", unsafe_allow_html=True)

def render_agent_output(result, show_structured=True):
    """Full agent result renderer: meta strip + markdown output."""
    if "error" in result:
        st.error(f"Agent error: {result['error']}")
        return

    render_model_meta(result)
    st.markdown("---")

    # Structured output panel (collapsible)
    if show_structured and result.get("structured"):
        with st.expander("📊 Structured Output (parsed)", expanded=False):
            st.json(result["structured"])

    st.markdown(result.get("output_text",""), unsafe_allow_html=False)
    ts = result.get("created_at","")[:16].replace("T"," ")
    st.caption(f"Generated {ts} UTC · Run ID #{result.get('run_id','?')} · {result.get('agent_name','?')}")


def export_button(content: str, filename: str, label: str = "⬇️ Export Markdown"):
    st.download_button(label=label, data=content, file_name=filename, mime="text/markdown")


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🛡️ VP CX Agent OS")
    st.markdown("<small style='color:#8b949e'>Onyx Security · Executive Demo</small>", unsafe_allow_html=True)
    st.markdown("---")

    page = st.radio(
        "",
        ["🏠 Portfolio Dashboard",
         "👤 Customer 360",
         "🤖 Agent Console",
         "📋 Briefings",
         "📊 Implementation Digest",
         "🔍 Audit Trail & Costs"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    summary = fetch_summary()
    if summary:
        st.markdown("**Portfolio**")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"🔴 High **{summary.get('critical_count',0)}**")
            st.markdown(f"🟡 Med **{summary.get('at_risk_count',0)}**")
            st.markdown(f"🟢 OK **{summary.get('healthy_count',0)}**")
        with col_b:
            arr_risk = summary.get('arr_at_risk',0)
            total    = summary.get('total_arr',1)
            st.markdown(f"${arr_risk/1e6:.1f}M")
            st.markdown("at risk")
            st.markdown(f"{arr_risk/total*100:.0f}%")

    st.markdown("---")

    # Quick agent run shortcuts
    customers = fetch_customers()
    if customers:
        st.markdown("**Quick Run**")
        qcust = st.selectbox("Customer", [c["id"] for c in customers],
                             format_func=lambda x: next((c["name"] for c in customers if c["id"]==x), str(x)),
                             key="sidebar_cust", label_visibility="collapsed")
        if st.button("🩺 Health Check", use_container_width=True, key="sb_health"):
            st.session_state["quick_run"] = ("CustomerHealthAgent", qcust)
            st.rerun()

    st.markdown("---")
    st.markdown("<small style='color:#8b949e'>API: localhost:8000</small>", unsafe_allow_html=True)


# Handle quick run from sidebar
if "quick_run" in st.session_state:
    agent_name, cid = st.session_state.pop("quick_run")
    with st.spinner(f"Running {agent_name}..."):
        result = call_agent(agent_name, cid)
    st.session_state["quick_result"] = result


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: PORTFOLIO DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

if page == "🏠 Portfolio Dashboard":
    st.markdown("# Portfolio Dashboard")
    st.caption("Real-time view of all 25 enterprise customers")

    summary   = fetch_summary()
    customers = fetch_customers()

    if not summary or not customers:
        st.error("❌ Cannot reach backend. Run: `uvicorn backend.main:app --port 8000`")
        st.stop()

    # ── KPI row ───────────────────────────────────────────────────────────────
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    metrics_row = [
        ("Customers",       str(summary.get("total_customers",0)),         ""),
        ("Total ARR",       f"${summary.get('total_arr',0)/1e6:.1f}M",     ""),
        ("ARR at Risk",     f"${summary.get('arr_at_risk',0)/1e6:.1f}M",   f"{summary.get('arr_at_risk',0)/max(summary.get('total_arr',1),1)*100:.0f}% of portfolio"),
        ("Escalations",     str(summary.get("open_escalations",0)),         "open"),
        ("Renewals (90d)",  str(summary.get("renewals_next_90_days",0)),    "due"),
        ("Avg Health",      str(summary.get("avg_health_score",0)),         "/ 100"),
    ]
    for col, (label, val, sub) in zip([k1,k2,k3,k4,k5,k6], metrics_row):
        with col:
            st.markdown(f"<div class='card'><div class='kpi-label'>{label}</div><div class='kpi-value'>{val}</div><div class='kpi-sub'>{sub}</div></div>", unsafe_allow_html=True)

    # ── Health bar ────────────────────────────────────────────────────────────
    total = max(summary.get("total_customers",1), 1)
    h_pct = summary.get("critical_count",0) / total * 100
    m_pct = summary.get("at_risk_count",0)  / total * 100
    l_pct = summary.get("healthy_count",0)  / total * 100
    st.markdown(f"""
    <div style="margin:8px 0 4px">
        <div style="display:flex;height:20px;border-radius:6px;overflow:hidden;gap:2px">
            <div style="width:{h_pct:.0f}%;background:#ff4b4b;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:white">{summary.get('critical_count',0)}</div>
            <div style="width:{m_pct:.0f}%;background:#ffa726;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:white">{summary.get('at_risk_count',0)}</div>
            <div style="width:{l_pct:.0f}%;background:#4caf50;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:white">{summary.get('healthy_count',0)}</div>
        </div>
        <div style="display:flex;gap:16px;margin-top:5px;font-size:12px;color:#8b949e">
            <span>🔴 High Risk</span><span>🟡 Medium Risk</span><span>🟢 Healthy</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Portfolio health scan ─────────────────────────────────────────────────
    col_scan, col_info = st.columns([1, 3])
    with col_scan:
        if st.button("🔍 Scan Full Portfolio", use_container_width=True, type="primary", help="Run CustomerHealthAgent on all 25 customers using Claude Haiku"):
            with st.spinner("Running CustomerHealthAgent on all 25 customers (Haiku)..."):
                scan = call_portfolio_health()
            st.session_state["portfolio_scan"] = scan
    with col_info:
        if "portfolio_scan" in st.session_state:
            scan = st.session_state["portfolio_scan"]
            if "error" not in scan:
                st.success(f"Scanned {scan.get('customers_scanned',0)} customers · Total cost: ${scan.get('total_cost_usd',0):.4f} (Haiku)")

    # ── Customer table ────────────────────────────────────────────────────────
    left_col, right_col = st.columns([3, 1])

    with left_col:
        st.markdown("**Customer Portfolio** — select a row to drill in →")
        df = pd.DataFrame(customers)
        df["Risk"]    = df["risk_level"].map({"High":"🔴 High","Medium":"🟡 Medium","Low":"🟢 Healthy"})
        df["ARR"]     = df["arr"].map(lambda x: f"${x:,.0f}")
        df["Health"]  = df["health_score"]
        df["Trend"]   = df.get("health_trend", pd.Series([""] * len(df)))
        df["Renewal"] = df["renewal_date"]
        df["Champion"]= df["champion_status"]
        disp = df[["name","industry","ARR","Health","Trend","Renewal","Champion","Risk"]].rename(columns={"name":"Customer","industry":"Industry"})
        disp = disp.sort_values("Health")

        sel = st.dataframe(disp, use_container_width=True, height=500,
                           on_select="rerun", selection_mode="single-row")
        if sel and sel.get("selection",{}).get("rows"):
            ridx = sel["selection"]["rows"][0]
            chosen = customers[disp.index[ridx]]
            st.session_state["selected_cid"]  = chosen["id"]
            st.session_state["selected_cname"] = chosen["name"]
            st.success(f"Selected **{chosen['name']}** ({chosen['risk_level']} risk) → go to Customer 360")

    with right_col:
        st.markdown("**Top Escalations**")
        for esc in summary.get("top_escalations", []):
            sev_color = "#ff4b4b" if esc.get("severity") == "Critical" else "#ffa726"
            cname = next((c["name"] for c in customers if c["id"] == esc.get("customer_id")), "?")
            st.markdown(f"""<div class="card card-{'red' if esc.get('severity')=='Critical' else 'yellow'}">
                <div style="font-size:0.72rem;color:{sev_color};font-weight:700">{esc.get('severity','?')} · {cname}</div>
                <div style="font-size:0.82rem;color:#e6edf3;margin-top:3px">{esc.get('title','')[:60]}</div>
                <div style="font-size:0.72rem;color:#8b949e;margin-top:2px">{esc.get('owner','')}</div>
            </div>""", unsafe_allow_html=True)

    # Show portfolio scan results if available
    if "portfolio_scan" in st.session_state and "error" not in st.session_state["portfolio_scan"]:
        scan = st.session_state["portfolio_scan"]
        st.markdown("---")
        st.markdown("**Portfolio Health Scan Results** (CustomerHealthAgent · Haiku)")
        scan_df = pd.DataFrame(scan["results"])
        scan_df["Risk"]  = scan_df["risk_level"]
        scan_df["Score"] = scan_df["health_score"]
        scan_df["Conf"]  = scan_df["confidence_score"].map(lambda x: f"{x:.0%}")
        scan_df["Cost"]  = scan_df["estimated_cost_usd"].map(lambda x: f"${x:.5f}")
        scan_df["Top Risk"] = scan_df["top_risk_drivers"].map(lambda x: x[0][:50] if x else "")
        st.dataframe(
            scan_df[["customer_name","Score","Risk","Conf","Cost","Top Risk"]].rename(columns={"customer_name":"Customer"}),
            use_container_width=True, height=320
        )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: CUSTOMER 360
# ══════════════════════════════════════════════════════════════════════════════

elif page == "👤 Customer 360":
    st.markdown("# Customer 360")
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
    risk_color = {"High":"#ff4b4b","Medium":"#ffa726","Low":"#4caf50"}.get(c.get("risk_level",""), "#fff")
    st.markdown(f"""
    <div class="card" style="margin-bottom:16px">
        <div style="display:flex;align-items:flex-start;gap:20px">
            <div style="flex:1">
                <div style="font-size:1.6rem;font-weight:800;color:#e6edf3">{c['name']}</div>
                <div style="color:#8b949e;margin-top:2px">{c['industry']} · {c.get('employee_count','?'):,} employees · ${c['arr']:,} ARR</div>
                <div style="margin-top:8px;color:#c9d1d9;font-size:0.85rem">
                    <b>Primary Risk:</b> {c.get('primary_risk_reason','')}
                </div>
                <div style="margin-top:4px;color:#4fc3f7;font-size:0.85rem">
                    <b>Next Action:</b> {c.get('recommended_next_action','')}
                </div>
            </div>
            <div style="text-align:center;min-width:80px">
                <div style="font-size:2.8rem;font-weight:900;color:{risk_color}">{c['health_score']}</div>
                <div style="font-size:0.72rem;color:#8b949e">HEALTH</div>
                <div style="font-size:0.85rem;font-weight:700;color:{risk_color};margin-top:4px">{c.get('risk_level','?')} Risk</div>
                <div style="font-size:0.78rem;color:#8b949e">{c.get('health_trend','?')}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Quick metrics row ─────────────────────────────────────────────────────
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    renewal_days = renewal.get("days_to_renewal", "?")
    with m1: st.metric("Adoption", f"{c.get('adoption_score',0)}/100")
    with m2: st.metric("Churn Risk", f"{c.get('renewal_risk_score',0):.0%}", delta_color="inverse")
    with m3: st.metric("Open Tickets", sum(1 for t in tickets if t["status"] != "Resolved"), delta_color="inverse")
    with m4: st.metric("Escalations", len(escs), delta_color="inverse")
    with m5: st.metric("Renewal", f"{renewal_days}d" if isinstance(renewal_days, int) else "?")
    with m6:
        champ_icon = {"Active":"✅","Disengaged":"⚠️","Left Company":"❌"}.get(c.get("champion_status",""),"?")
        st.metric("Champion", f"{champ_icon} {c.get('champion_status','?')}")

    # ── Agent action bar ──────────────────────────────────────────────────────
    st.markdown("**Run Agents**")
    ab1, ab2, ab3, ab4, ab5 = st.columns(5)
    triggered = None
    btns = [
        (ab1, "CustomerHealthAgent",      "🩺 Health Assessment",      "secondary"),
        (ab2, "ImplementationAgent",      "🔧 Implementation Report",  "secondary"),
        (ab3, "BriefingAgent",            "📋 Generate CEO Briefing",  "primary"),
        (ab4, "EscalationCommanderAgent", "🚨 Escalation Commander",   "primary"),
        (ab5, "SkeptikQAAgent",           "🔍 Skeptik QA Review",      "secondary"),
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
        st.markdown(f"### {agent_label} Output")

        # Skeptik shows before/after
        if "SkeptikQAAgent" in recent_key:
            prior_key = next(
                (k for k in reversed(list(st.session_state.keys()))
                 if k.startswith(f"360_result_{cid}_") and "Skeptik" not in k), None
            )
            if prior_key:
                bc, ac = st.columns(2)
                with bc:
                    st.markdown("**Before — Original Output**")
                    with st.container():
                        st.markdown(f"<div class='skeptik-before'>", unsafe_allow_html=True)
                        prior = st.session_state[prior_key]
                        st.markdown(prior.get("output_text","")[:1200] + "...", unsafe_allow_html=False)
                        st.markdown("</div>", unsafe_allow_html=True)
                with ac:
                    st.markdown("**After — Skeptik Review**")
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
        ["📊 Usage & Health", "🎯 Implementation", "🎫 Tickets", "🚨 Escalations", "👥 Stakeholders", "📝 Notes", "💰 Renewal"]
    )

    with tab_use:
        mrow = metrics[0] if metrics else {}
        if mrow:
            u1, u2, u3, u4 = st.columns(4)
            with u1: st.metric("Daily Active Users", int(mrow.get("dau",0)), delta=f"{mrow.get('dau_trend_30d',0):+.0%} vs 30d")
            with u2: st.metric("Asset Coverage", f"{int(mrow.get('asset_coverage_pct',0))}%")
            with u3: st.metric("Features Active", f"{int(mrow.get('features_enabled',0))}/18")
            with u4: st.metric("False Positive Rate", f"{mrow.get('false_positive_rate',0):.0%}", delta_color="inverse")
            u5, u6, u7, u8 = st.columns(4)
            with u5: st.metric("API Calls (30d)", f"{int(mrow.get('api_calls_last_30d',0)):,}")
            with u6: st.metric("Alerts (30d)", int(mrow.get("alerts_generated_last_30d",0)))
            with u7: st.metric("Logins (7d)", int(mrow.get("unique_logins_last_7d",0)))
            with u8: st.metric("Agents Deployed", int(mrow.get("agents_deployed",0)))

        # Health trend chart
        if history:
            st.markdown("**30-Day Health Trend**")
            hdf = pd.DataFrame(history)[["date","health_score"]].copy()
            hdf["date"] = pd.to_datetime(hdf["date"])
            hdf = hdf.sort_values("date")
            st.line_chart(hdf.set_index("date")["health_score"], height=150, use_container_width=True)

        sec_icon = {"Complete":"🟢","In Progress":"🟡","Blocked":"🔴","Not Started":"⚫"}.get(c.get("security_review_status",""),"⚪")
        st.info(f"**Security Review:** {sec_icon} {c.get('security_review_status','?')} · "
                f"**Onboarding:** {c.get('onboarding_status','?')} · "
                f"**Sentiment:** {c.get('sentiment','?')}")

    with tab_impl:
        if impl:
            behind = impl.get("days_behind_schedule",0)
            sc = "#ff4b4b" if impl.get("overall_status") in ("Stalled","Behind Schedule") else "#ffa726" if impl.get("overall_status") == "Slight Delay" else "#4caf50"
            pct = impl.get("pct_complete",0)
            st.markdown(f"**Status:** <span style='color:{sc};font-weight:700'>{impl.get('overall_status','?')}</span>"
                        + (f" · <span style='color:#ff4b4b'>⚠️ {behind} days behind</span>" if behind > 0 else ""),
                        unsafe_allow_html=True)
            st.progress(pct / 100)
            st.caption(f"{pct}% complete · Implementation Owner: {impl.get('implementation_owner','?')} · Go-live target: {impl.get('go_live_target','?')}")
        else:
            st.caption("No implementation record found.")

        for m in milestones:
            icon = {"Complete":"✅","In Progress":"🔄","Not Started":"⬜"}.get(m.get("status",""),"?")
            mname = m.get("milestone_name") or m.get("name","?")
            blocker = m.get("blocker")
            st.markdown(f"{icon} **{mname}**" + (f" — ⚠️ *{blocker}*" if blocker else ""))

    with tab_tick:
        open_t    = [t for t in tickets if t["status"] != "Resolved"]
        closed_t  = [t for t in tickets if t["status"] == "Resolved"]
        st.markdown(f"**{len(open_t)} Open · {len(closed_t)} Resolved**")
        for t in sorted(tickets, key=lambda x: ("P1P2P3P4".index(x["severity"]) if x["severity"] in "P1P2P3P4" else 9, x["status"] == "Resolved")):
            sc = {"P1":"#ff4b4b","P2":"#ffa726","P3":"#ffd54f","P4":"#8b949e"}.get(t["severity"],"#fff")
            si = "🔴" if t["status"]=="Open" else "🔄" if t["status"]=="In Progress" else "✅"
            st.markdown(f"""<div class="card">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <span style="color:{sc};font-weight:700;font-size:0.75rem">{t['severity']}</span>
                    <span style="color:#8b949e;font-size:0.75rem">{si} {t['status']}</span>
                </div>
                <div style="color:#e6edf3;font-size:0.88rem;margin-top:3px">{t['title']}</div>
                <div style="color:#8b949e;font-size:0.72rem;margin-top:2px">Opened {t['opened_at'][:10]} · Assignee: {t.get('assignee','?')}</div>
                {f'<div style="color:#ffa726;font-size:0.72rem;margin-top:2px">⚠️ {t["escalation_reference"]}</div>' if t.get("escalation_reference") else ''}
            </div>""", unsafe_allow_html=True)

    with tab_escs:
        if not escs:
            st.success("No active escalations.")
        for e in escs:
            sc = "#ff4b4b" if e["severity"] == "Critical" else "#ffa726"
            exec_aware = "🔔 Exec aware" if e.get("executive_aware") else ""
            st.markdown(f"""<div class="card card-{'red' if e['severity']=='Critical' else 'yellow'}">
                <div style="display:flex;justify-content:space-between">
                    <span style="color:{sc};font-weight:700;font-size:0.78rem">{e['severity']} · {e['status']}</span>
                    <span style="color:#8b949e;font-size:0.72rem">{exec_aware}</span>
                </div>
                <div style="color:#e6edf3;font-size:0.9rem;margin-top:4px;font-weight:600">{e['title']}</div>
                <div style="color:#8b949e;font-size:0.75rem;margin-top:2px">Owner: {e['owner']} · Opened: {e['opened_at'][:10]}</div>
                {f'<div style="color:#8b949e;font-size:0.75rem;margin-top:2px">{e["resolution_plan"]}</div>' if e.get("resolution_plan") else ''}
            </div>""", unsafe_allow_html=True)

    with tab_stk:
        role_colors = {"Champion":"#4fc3f7","Technical Sponsor":"#9c88ff","Business Sponsor":"#ffa726",
                       "Executive Sponsor":"#ce93d8","Economic Buyer":"#ff6b6b"}
        eng_icons = {"High":"🟢","Medium":"🟡","Low":"🔴","None":"⚫"}
        for s in stk:
            rc = role_colors.get(s["role"],"#8b949e")
            ei = eng_icons.get(s.get("engagement_level",""),"?")
            st.markdown(f"""<div class="card">
                <div style="display:flex;justify-content:space-between">
                    <span style="font-weight:700;color:#e6edf3">{s['name']}</span>
                    <span style="font-size:0.75rem;color:#8b949e">{ei} {s.get('engagement_level','?')} engagement</span>
                </div>
                <div style="font-size:0.82rem;color:#8b949e">{s['title']}</div>
                <div style="margin-top:4px">
                    <span style="color:{rc};font-size:0.75rem;font-weight:700">{s['role']}</span>
                    <span style="color:#8b949e;font-size:0.72rem;margin-left:8px">{s['email']}</span>
                </div>
            </div>""", unsafe_allow_html=True)

    with tab_notes:
        sent_colors = {"Positive":"#4caf50","Neutral":"#8b949e","Negative":"#ff4b4b"}
        for n in notes:
            sc = sent_colors.get(n.get("sentiment_signal",""),"#8b949e")
            import json as _json
            try:
                actions = _json.loads(n.get("action_items","[]")) if n.get("action_items") else []
            except Exception:
                actions = []
            st.markdown(f"""<div class="card">
                <div style="display:flex;justify-content:space-between">
                    <span style="color:#8b949e;font-size:0.75rem">{n['date'][:10]} · <b style="color:#c9d1d9">{n.get('meeting_type','?')}</b></span>
                    <span style="color:{sc};font-size:0.75rem;font-weight:700">{n.get('sentiment_signal','?')}</span>
                </div>
                <div style="color:#e6edf3;font-size:0.88rem;margin-top:6px">{n['summary']}</div>
                <div style="color:#8b949e;font-size:0.72rem;margin-top:4px">👥 {n.get('attendees_internal','?')} · {n.get('attendees_customer','?')}</div>
                {('<div style="margin-top:6px">' + ''.join(f'<div style="font-size:0.75rem;color:#4fc3f7">→ {a}</div>' for a in actions) + '</div>') if actions else ''}
            </div>""", unsafe_allow_html=True)

    with tab_renew:
        if renewal:
            rc_color = "#ff4b4b" if c.get("renewal_risk_score",0) > 0.6 else "#ffa726" if c.get("renewal_risk_score",0) > 0.3 else "#4caf50"
            r1, r2, r3, r4 = st.columns(4)
            with r1: st.metric("Days to Renewal", renewal.get("days_to_renewal","?"))
            with r2: st.metric("Renewal Stage", renewal.get("renewal_stage","?"))
            with r3: st.metric("Current ARR", f"${renewal.get('current_arr',0):,}")
            with r4: st.metric("Expansion Opp.", f"${renewal.get('expansion_arr',0):,}")

            st.markdown(f"""<div class="card">
                <div style="font-size:0.75rem;color:#8b949e;margin-bottom:4px">RENEWAL DETAILS</div>
                <div>Forecast: <b style="color:{rc_color}">{renewal.get('forecast_category','?')}</b></div>
                <div style="margin-top:4px">Risk Score: <b style="color:{rc_color}">{c.get('renewal_risk_score',0):.0%}</b></div>
                <div style="margin-top:4px">Commercial Note: {renewal.get('commercial_terms_note','?')}</div>
                <div style="margin-top:4px;color:#8b949e">Procurement Contact: {renewal.get('procurement_contact','?')}</div>
                <div style="color:#8b949e">Exec Involvement Required: {'✅ Yes' if renewal.get('requires_exec_involvement') else 'No'}</div>
            </div>""", unsafe_allow_html=True)

            if st.button("📋 Generate CEO Briefing for Renewal", type="primary"):
                with st.spinner("Generating CEO Briefing (Sonnet)..."):
                    result = call_agent("BriefingAgent", cid)
                st.session_state[f"360_result_{cid}_BriefingAgent"] = result
                st.rerun()
        else:
            st.caption("No renewal record found within 180-day window.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: AGENT CONSOLE
# ══════════════════════════════════════════════════════════════════════════════

elif page == "🤖 Agent Console":
    st.markdown("# Agent Console")
    st.caption("Run any agent, inspect model routing rationale, cost, and structured output in real time.")

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
        st.markdown("**Configure**")
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

        st.markdown(f"""<div class="card" style="margin-top:12px">
            <div class="kpi-label">ROUTED TO</div>
            <div style="color:{color};font-weight:800;font-size:1.1rem">{tier.capitalize()}</div>
            <div style="color:#8b949e;font-size:0.78rem;margin-top:2px">{desc}</div>
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
            st.markdown("""<div style="border:1px dashed #30363d;border-radius:10px;padding:60px;text-align:center;color:#8b949e">
                <div style="font-size:2.5rem">🤖</div>
                <div style="margin-top:8px;font-size:0.9rem">Configure an agent and click Run</div>
                <div style="margin-top:4px;font-size:0.78rem">Model routing rationale, cost, and confidence will appear here</div>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: BRIEFINGS
# ══════════════════════════════════════════════════════════════════════════════

elif page == "📋 Briefings":
    st.markdown("# Briefings")
    customers = fetch_customers()
    cmap = {c["id"]: c for c in customers}

    tab_ceo, tab_vp, tab_hist = st.tabs(["📋 CEO Briefings", "📊 Weekly VP CX Review", "🗄️ History"])

    with tab_ceo:
        gen_col, _ = st.columns([1, 2])
        with gen_col:
            sel_cid = st.selectbox(
                "Customer for briefing",
                [c["id"] for c in customers],
                format_func=lambda x: f"{risk_icon(cmap[x].get('risk_level','?'))} {cmap[x]['name']} — ${cmap[x]['arr']:,}",
                key="brief_cid",
            )
            if st.button("📋 Generate CEO Briefing", use_container_width=True, type="primary"):
                with st.spinner("Generating CEO Briefing (Sonnet)..."):
                    result = call_agent("BriefingAgent", sel_cid)
                st.session_state["ceo_briefing"] = result

            if "ceo_briefing" in st.session_state:
                r = st.session_state["ceo_briefing"]
                if not r.get("error"):
                    # Then offer Skeptik review
                    if st.button("🔍 Review with Skeptik Agent", use_container_width=True):
                        with st.spinner("Running Skeptik QA (Opus)..."):
                            skeptik = call_agent("SkeptikQAAgent", sel_cid)
                        st.session_state["ceo_skeptik"] = skeptik

        if "ceo_briefing" in st.session_state:
            r = st.session_state["ceo_briefing"]

            if "ceo_skeptik" in st.session_state:
                bc, ac = st.columns(2)
                with bc:
                    st.markdown("**Original Briefing**")
                    render_model_meta(r)
                    st.markdown("---")
                    st.markdown(f"<div class='skeptik-before'>{r.get('output_text','')}</div>", unsafe_allow_html=True)
                with ac:
                    st.markdown("**Skeptik QA Review**")
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
        if st.button("📊 Generate Weekly VP CX Review", use_container_width=True, type="primary"):
            with st.spinner("Running VP Chief of Staff Agent (Opus)..."):
                result = call_agent("VPChiefOfStaffAgent")
            st.session_state["vp_review"] = result

        if "vp_review" in st.session_state:
            r = st.session_state["vp_review"]
            render_agent_output(r)
            if r.get("output_text"):
                export_button(r["output_text"], f"VP_CX_Review_{datetime.now().strftime('%Y%m%d')}.md")

    with tab_hist:
        st.markdown("**Recent CEO Briefings**")
        ceo_briefs = fetch_briefings("CEO")
        if not ceo_briefs:
            st.caption("No CEO briefings generated yet.")
        for b in ceo_briefs:
            label = f"{b.get('customer_name','?')} · {b['created_at'][:16].replace('T',' ')} UTC"
            with st.expander(label):
                st.markdown(b["content"])
                export_button(b["content"], f"CEO_Briefing_{b.get('customer_id','?')}_{b['created_at'][:10]}.md")

        st.markdown("---")
        st.markdown("**Recent VP CX Reviews**")
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

elif page == "📊 Implementation Digest":
    st.markdown("# Implementation Digest")
    st.caption("Weekly implementation health across all active projects — powered by ImplementationAgent (Sonnet)")

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
            conf_colors = {"Very Low":"#ff4b4b","Low":"#ffa726","Medium":"#ffd54f","High":"#4caf50"}

            # Summary metrics
            c1, c2, c3, c4 = st.columns(4)
            at_risk = sum(1 for r in results if r["launch_confidence"] in ("Very Low","Low"))
            on_track = sum(1 for r in results if r["launch_confidence"] == "High")
            with c1: st.metric("Projects Reviewed", len(results))
            with c2: st.metric("At Risk", at_risk, delta_color="inverse")
            with c3: st.metric("On Track", on_track)
            with c4: st.metric("Cost", f"${digest.get('total_cost_usd',0):.4f}")

            st.markdown("---")
            st.markdown("**Project Status Overview** — sorted by launch confidence risk")

            for r in sorted(results, key=lambda x: conf_order.get(x["launch_confidence"], 2)):
                cc = conf_colors.get(r["launch_confidence"], "#fff")
                blockers_html = "".join(
                    f"<div style='font-size:0.78rem;color:#ffa726;margin-top:2px'>⚠️ {b[:80]}</div>"
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
                                    f"<div style='margin-top:8px;font-size:0.82rem;color:#c9d1d9'>{r.get('recommended_intervention','')[:120]}</div>"
                                    f"{blockers_html}</div>", unsafe_allow_html=True)
                    with col_b:
                        with st.spinner("Loading full analysis..."):
                            cust_result = call_agent("ImplementationAgent", r["customer_id"])
                        render_agent_output(cust_result, show_structured=False)
                        export_button(cust_result.get("output_text",""),
                                      f"Impl_{r['customer_name'].replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.md")
    else:
        st.markdown("""<div style="border:1px dashed #30363d;border-radius:10px;padding:40px;text-align:center;color:#8b949e">
            <div style="font-size:2rem">🔧</div>
            <div style="margin-top:8px">Click the button above to generate the weekly implementation digest</div>
            <div style="margin-top:4px;font-size:0.78rem">Runs ImplementationAgent (Sonnet) on all active implementation projects</div>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: AUDIT TRAIL & COSTS
# ══════════════════════════════════════════════════════════════════════════════

elif page == "🔍 Audit Trail & Costs":
    st.markdown("# Audit Trail & Cost Tracking")

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
    st.markdown("**Spend by Model**")
    by_model = costs.get("by_model", [])
    if by_model:
        for row in by_model:
            tier   = model_tier_from_id(row.get("model_used",""))
            color  = tier_color(tier)
            mc1, mc2, mc3, mc4 = st.columns([3, 1, 1, 1])
            with mc1:
                st.markdown(f"<span style='color:{color};font-weight:700'>{tier.capitalize()}</span> "
                            f"<span style='color:#8b949e;font-size:0.75rem'>{row.get('model_used','')}</span>",
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

    st.markdown(f"**Run History** ({len(filtered)} records)")

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
