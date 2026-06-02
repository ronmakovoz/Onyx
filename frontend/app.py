"""
VP CX Agent OS — Streamlit Frontend
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

# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0f1117; }
[data-testid="stSidebar"] { background: #161b22; }
.metric-card {
    background: #1c2128; border: 1px solid #30363d; border-radius: 10px;
    padding: 16px 20px; margin-bottom: 8px;
}
.risk-critical { color: #ff4b4b; font-weight: 700; }
.risk-at-risk  { color: #ffa726; font-weight: 700; }
.risk-healthy  { color: #4caf50; font-weight: 700; }
.agent-badge {
    display: inline-block; padding: 3px 10px; border-radius: 20px;
    font-size: 0.75rem; font-weight: 600; margin-right: 6px;
}
.badge-haiku  { background: #1a3a4a; color: #4fc3f7; border: 1px solid #4fc3f7; }
.badge-sonnet { background: #1a2a3a; color: #9c88ff; border: 1px solid #9c88ff; }
.badge-opus   { background: #2a1a3a; color: #ce93d8; border: 1px solid #ce93d8; }
.mock-badge   { background: #2a2a1a; color: #ffd54f; border: 1px solid #ffd54f; }
.section-header {
    font-size: 1.1rem; font-weight: 700; color: #e6edf3;
    border-bottom: 1px solid #30363d; padding-bottom: 8px; margin-bottom: 12px;
}
.stButton > button {
    border-radius: 8px; font-weight: 600;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def get_customers():
    try:
        return requests.get(f"{API}/customers").json()
    except Exception:
        return []

@st.cache_data(ttl=30)
def get_summary():
    try:
        return requests.get(f"{API}/portfolio/summary").json()
    except Exception:
        return {}

def get_360(cid):
    try:
        return requests.get(f"{API}/customers/{cid}/360").json()
    except Exception:
        return {}

def run_agent(agent_name, customer_id=None):
    try:
        params = {"agent_name": agent_name}
        if customer_id:
            params["customer_id"] = customer_id
        return requests.post(f"{API}/agents/run", params=params).json()
    except Exception as e:
        return {"error": str(e)}

def get_audit_log():
    try:
        return requests.get(f"{API}/audit-log").json()
    except Exception:
        return []

def get_costs():
    try:
        return requests.get(f"{API}/costs").json()
    except Exception:
        return {}

def risk_badge(label):
    colors = {"Critical": "🔴", "At Risk": "🟡", "Healthy": "🟢",
              "High": "🔴", "Medium": "🟡", "Low": "🟢"}
    return colors.get(label, "⚪")

def health_color(score):
    if score < 40: return "#ff4b4b"
    if score < 60: return "#ffa726"
    return "#4caf50"

def model_tier(model_id):
    if "haiku" in model_id.lower(): return "haiku"
    if "opus" in model_id.lower(): return "opus"
    return "sonnet"

def model_badge_html(model_id, is_mock=False):
    tier = model_tier(model_id)
    short = {"haiku": "Haiku", "sonnet": "Sonnet", "opus": "Opus"}.get(tier, "?")
    cls = f"badge-{tier}"
    mock = '<span class="agent-badge mock-badge">MOCK</span>' if is_mock else ""
    return f'<span class="agent-badge {cls}">{short}</span>{mock}'

def render_agent_result(result):
    if "error" in result:
        st.error(f"Agent error: {result['error']}")
        return

    col1, col2, col3, col4 = st.columns(4)
    tier = model_tier(result.get("model_used", ""))
    tier_colors = {"haiku": "#4fc3f7", "sonnet": "#9c88ff", "opus": "#ce93d8"}
    color = tier_colors.get(tier, "#fff")

    with col1:
        st.markdown(f"**Model**")
        st.markdown(f"<span style='color:{color};font-weight:700'>{result.get('model_used','?').split('-')[1].capitalize() if '-' in result.get('model_used','') else result.get('model_used','?')}</span>", unsafe_allow_html=True)
    with col2:
        st.markdown("**Est. Cost**")
        st.markdown(f"<span style='color:#4caf50;font-weight:700'>${result.get('estimated_cost_usd', 0):.4f}</span>", unsafe_allow_html=True)
    with col3:
        st.markdown("**Confidence**")
        conf = result.get("confidence_score", 0)
        conf_color = "#4caf50" if conf > 0.75 else "#ffa726" if conf > 0.6 else "#ff4b4b"
        st.markdown(f"<span style='color:{conf_color};font-weight:700'>{conf:.0%}</span>", unsafe_allow_html=True)
    with col4:
        st.markdown("**Tokens**")
        st.markdown(f"<span style='color:#8b949e'>{result.get('input_tokens',0):,} in / {result.get('output_tokens',0):,} out</span>", unsafe_allow_html=True)

    if result.get("is_mock"):
        st.info("🟡 Running in **mock mode** — set `ANTHROPIC_API_KEY` environment variable for live Claude responses.", icon="ℹ️")

    with st.expander("Model Routing Rationale", expanded=False):
        st.markdown(f"*{result.get('model_rationale', '')}*")

    st.markdown("---")
    st.markdown(result.get("output_text", ""), unsafe_allow_html=False)
    ts = result.get("created_at", "")[:16].replace("T", " ")
    st.caption(f"Generated {ts} · Run ID #{result.get('run_id', '?')}")


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛡️ VP CX Agent OS")
    st.markdown("<small style='color:#8b949e'>Onyx Security — Internal Demo</small>", unsafe_allow_html=True)
    st.markdown("---")
    page = st.radio(
        "Navigate",
        ["Portfolio Dashboard", "Customer 360", "Agent Console", "Briefings", "Audit Trail & Costs"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    summary = get_summary()
    if summary:
        st.markdown("**Portfolio at a Glance**")
        st.markdown(f"🔴 Critical: **{summary.get('critical_count', 0)}**")
        st.markdown(f"🟡 At Risk: **{summary.get('at_risk_count', 0)}**")
        st.markdown(f"🟢 Healthy: **{summary.get('healthy_count', 0)}**")
        arr_risk = summary.get("arr_at_risk", 0)
        st.markdown(f"💰 ARR at Risk: **${arr_risk:,.0f}**")
    st.markdown("---")
    st.markdown("<small style='color:#8b949e'>API: localhost:8000</small>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1: PORTFOLIO DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "Portfolio Dashboard":
    st.markdown("# Portfolio Dashboard")
    st.markdown("<small style='color:#8b949e'>Real-time view of your entire customer portfolio</small>", unsafe_allow_html=True)

    summary = get_summary()
    customers = get_customers()

    if not summary or not customers:
        st.error("Cannot reach backend. Make sure FastAPI is running on localhost:8000.")
        st.stop()

    # Top KPI row
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.metric("Total Customers", summary.get("total_customers", 0))
    with k2:
        st.metric("Total ARR", f"${summary.get('total_arr', 0)/1e6:.1f}M")
    with k3:
        st.metric("ARR at Risk", f"${summary.get('arr_at_risk', 0)/1e6:.1f}M",
                  delta=f"{summary.get('arr_at_risk',0)/summary.get('total_arr',1)*100:.0f}% of portfolio",
                  delta_color="inverse")
    with k4:
        st.metric("Open Escalations", summary.get("open_escalations", 0), delta_color="inverse")
    with k5:
        st.metric("Renewals (90d)", summary.get("renewals_next_90_days", 0))

    st.markdown("---")

    # Health distribution bar
    total = summary.get("total_customers", 1)
    col_h, col_info = st.columns([3, 1])
    with col_h:
        st.markdown("**Portfolio Health Distribution**")
        crit_pct = summary.get("critical_count", 0) / total * 100
        risk_pct = summary.get("at_risk_count", 0) / total * 100
        healthy_pct = summary.get("healthy_count", 0) / total * 100
        bar_html = f"""
        <div style="display:flex;height:24px;border-radius:6px;overflow:hidden;gap:2px;">
            <div style="width:{crit_pct:.0f}%;background:#ff4b4b;display:flex;align-items:center;justify-content:center;font-size:11px;color:white;font-weight:700">{summary.get('critical_count',0)}</div>
            <div style="width:{risk_pct:.0f}%;background:#ffa726;display:flex;align-items:center;justify-content:center;font-size:11px;color:white;font-weight:700">{summary.get('at_risk_count',0)}</div>
            <div style="width:{healthy_pct:.0f}%;background:#4caf50;display:flex;align-items:center;justify-content:center;font-size:11px;color:white;font-weight:700">{summary.get('healthy_count',0)}</div>
        </div>
        <div style="display:flex;gap:16px;margin-top:6px;font-size:12px;color:#8b949e">
            <span>🔴 Critical</span><span>🟡 At Risk</span><span>🟢 Healthy</span>
        </div>
        """
        st.markdown(bar_html, unsafe_allow_html=True)

    st.markdown("---")

    # Customer table
    left, right = st.columns([2, 1])

    with left:
        st.markdown("**All Customers — Click a row to drill in**")
        df = pd.DataFrame(customers)
        df["Status"] = df["risk_level"].map({"High": "🔴 High Risk", "Medium": "🟡 Medium Risk", "Low": "🟢 Healthy"})
        df["ARR"] = df["arr"].map(lambda x: f"${x:,.0f}")
        df["Health"] = df["health_score"]
        df["Renewal"] = df["renewal_date"]
        churn_col = "renewal_risk_score" if "renewal_risk_score" in df.columns else "renewal_risk"
        df["Churn Risk"] = df[churn_col].map(lambda x: f"{x:.0%}" if x else "N/A")
        display_df = df[["name", "industry", "ARR", "Health", "Renewal", "Churn Risk", "Status"]].rename(
            columns={"name": "Customer", "industry": "Industry"}
        )
        display_df = display_df.sort_values("Health")

        selected = st.dataframe(
            display_df,
            use_container_width=True,
            height=480,
            on_select="rerun",
            selection_mode="single-row",
        )

        if selected and selected.get("selection", {}).get("rows"):
            row_idx = selected["selection"]["rows"][0]
            selected_customer = customers[display_df.index[row_idx]]
            st.session_state["selected_customer_id"] = selected_customer["id"]
            st.session_state["selected_customer_name"] = selected_customer["name"]
            st.success(f"Selected: **{selected_customer['name']}** — navigate to Customer 360 →")

    with right:
        st.markdown("**Active Escalations**")
        escalations = summary.get("top_escalations", [])
        if not escalations:
            st.markdown("<span style='color:#8b949e'>No open escalations</span>", unsafe_allow_html=True)
        for esc in escalations:
            sev_color = "#ff4b4b" if esc["severity"] == "Critical" else "#ffa726"
            # Find customer name
            cust = next((c for c in customers if c["id"] == esc.get("customer_id")), {})
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size:0.8rem;color:{sev_color};font-weight:700">{esc['severity']} · {cust.get('name','?')}</div>
                <div style="font-size:0.85rem;color:#e6edf3;margin-top:4px">{esc['title']}</div>
                <div style="font-size:0.75rem;color:#8b949e;margin-top:2px">Owner: {esc['owner']}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("**Avg Portfolio Health**")
        avg = summary.get("avg_health_score", 0)
        color = health_color(avg)
        st.markdown(f"<div style='font-size:2.5rem;font-weight:800;color:{color}'>{avg}</div><div style='color:#8b949e;font-size:0.8rem'>out of 100</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2: CUSTOMER 360
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Customer 360":
    st.markdown("# Customer 360")

    customers = get_customers()
    customer_names = {c["id"]: f"{risk_badge(c.get('risk_level', c.get('risk_label','Unknown')))} {c['name']}" for c in customers}
    customer_ids = list(customer_names.keys())

    default_id = st.session_state.get("selected_customer_id", customer_ids[0])
    if default_id not in customer_ids:
        default_id = customer_ids[0]

    selected_id = st.selectbox(
        "Select Customer",
        options=customer_ids,
        format_func=lambda x: customer_names[x],
        index=customer_ids.index(default_id),
    )

    data = get_360(selected_id)
    if not data or not data.get("customer"):
        st.error("Could not load customer data.")
        st.stop()

    c = data["customer"]
    tickets = data.get("tickets", [])
    escalations = data.get("escalations", [])
    stakeholders = data.get("stakeholders", [])
    metrics = data.get("metrics", [])
    milestones = data.get("milestones", [])
    notes = data.get("meeting_notes", [])

    # Header
    risk_color = {"Critical": "#ff4b4b", "At Risk": "#ffa726", "Healthy": "#4caf50"}.get(c.get('risk_level', c.get('risk_label','Unknown')), "#fff")
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:16px;margin-bottom:16px">
        <div>
            <div style="font-size:1.8rem;font-weight:800;color:#e6edf3">{c['name']}</div>
            <div style="color:#8b949e">{c['industry']} · ${c['arr']:,} ARR · Renewal: {c['renewal_date']}</div>
        </div>
        <div style="margin-left:auto;text-align:center">
            <div style="font-size:2.5rem;font-weight:800;color:{risk_color}">{c['health_score']}</div>
            <div style="color:#8b949e;font-size:0.8rem">Health Score</div>
        </div>
        <div style="text-align:center">
            <div style="font-size:1.5rem;font-weight:700;color:{risk_color}">{c.get('risk_level', c.get('risk_label','Unknown'))}</div>
            <div style="color:#8b949e;font-size:0.8rem">Risk Level</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Agent action buttons
    st.markdown("**Run Agents**")
    btn_cols = st.columns(5)
    agent_buttons = [
        ("CustomerHealthAgent", "🩺 Health Assessment"),
        ("BriefingAgent", "📋 CEO Briefing"),
        ("EscalationCommanderAgent", "🚨 Escalation Commander"),
        ("ImplementationAgent", "🔧 Implementation Report"),
        ("SkeptikQAAgent", "🔍 Skeptik QA Review"),
    ]
    triggered_agent = None
    for i, (agent_name, label) in enumerate(agent_buttons):
        with btn_cols[i]:
            if st.button(label, use_container_width=True, key=f"btn_{agent_name}"):
                triggered_agent = agent_name

    if triggered_agent:
        with st.spinner(f"Running {triggered_agent}..."):
            result = run_agent(triggered_agent, selected_id)
        st.markdown(f"### {triggered_agent} Output")
        render_agent_result(result)
        st.markdown("---")

    # Core metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Adoption Score", f"{c['adoption_score']}/100")
    with col2:
        st.metric("Renewal Risk", f"{c['renewal_risk']:.0%}", delta_color="inverse")
    with col3:
        status_icon = {"Active": "✅", "Left Company": "❌", "Disengaged": "⚠️"}.get(c["champion_status"], "?")
        st.metric("Champion", f"{status_icon} {c['champion_status']}")
    with col4:
        sent_icon = {"Positive": "😊", "Neutral": "😐", "Negative": "😟"}.get(c["sentiment"], "?")
        st.metric("Sentiment", f"{sent_icon} {c['sentiment']}")

    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Usage", "🎯 Milestones", "🎫 Tickets", "👥 Stakeholders", "📝 Notes"])

    with tab1:
        if metrics:
            # New schema: metrics is a list of dicts with direct column names
            mrow = metrics[0] if metrics else {}
            # Support both old (metric_name/value) and new (direct column) schemas
            if "metric_name" in mrow:
                metrics_dict = {m["metric_name"]: m["value"] for m in metrics}
                dau_val   = int(metrics_dict.get("dau", 0))
                feat_val  = int(metrics_dict.get("features_enabled", 0))
                api_val   = int(metrics_dict.get("api_calls_last_30d", 0))
                integ_val = int(metrics_dict.get("integrations_active", 0))
                alert_val = int(metrics_dict.get("alerts_generated_last_30d", 0))
                rep_val   = int(metrics_dict.get("reports_exported_last_30d", 0))
                login_val = int(metrics_dict.get("login_last_7d_unique_users", 0))
                cov_val   = int(metrics_dict.get("asset_coverage_pct", 0))
                trend_val = float(metrics_dict.get("dau_trend_30d", 0))
                fp_val    = float(metrics_dict.get("false_positive_rate", 0))
            else:
                dau_val   = int(mrow.get("dau", 0))
                feat_val  = int(mrow.get("features_enabled", 0))
                api_val   = int(mrow.get("api_calls_last_30d", 0))
                integ_val = int(mrow.get("integrations_active", 0))
                alert_val = int(mrow.get("alerts_generated_last_30d", 0))
                rep_val   = int(mrow.get("reports_exported_last_30d", 0))
                login_val = int(mrow.get("unique_logins_last_7d", 0))
                cov_val   = int(mrow.get("asset_coverage_pct", 0))
                trend_val = float(mrow.get("dau_trend_30d", 0))
                fp_val    = float(mrow.get("false_positive_rate", 0))

            m1, m2, m3, m4 = st.columns(4)
            with m1: st.metric("Daily Active Users", dau_val, delta=f"{trend_val:+.0%} vs 30d ago")
            with m2: st.metric("Features Enabled", f"{feat_val}/18")
            with m3: st.metric("API Calls (30d)", f"{api_val:,}")
            with m4: st.metric("Active Integrations", integ_val)

            m5, m6, m7, m8 = st.columns(4)
            with m5: st.metric("Alerts (30d)", alert_val)
            with m6: st.metric("False Positive Rate", f"{fp_val:.0%}", delta_color="inverse")
            with m7: st.metric("Unique Logins (7d)", login_val)
            with m8: st.metric("Asset Coverage", f"{cov_val}%")

            # Health trend chart
            health_hist = data.get("health_history", [])
            if health_hist:
                st.markdown("**30-Day Health Trend**")
                hist_df = pd.DataFrame(health_hist)[["date", "health_score"]]
                hist_df["date"] = pd.to_datetime(hist_df["date"])
                hist_df = hist_df.sort_values("date")
                st.line_chart(hist_df.set_index("date")["health_score"], height=140, use_container_width=True)

            # Security review status
            sec_colors = {"Complete": "🟢", "In Progress": "🟡", "Not Started": "🔴", "Blocked": "🚫"}
            sec_icon = sec_colors.get(c.get("security_review_status",""), "⚪")
            st.info(f"**Security Review:** {sec_icon} {c.get('security_review_status','?')} · **Onboarding:** {c.get('onboarding_status','?')} · **Health Trend:** {c.get('health_trend','?')}")

    with tab2:
        impl_info = data.get("implementation") or {}
        done = sum(1 for m in milestones if m["status"] == "Complete")
        total_m = len(milestones)
        pct = int(done / total_m * 100) if total_m else 0
        impl_status = impl_info.get("overall_status", "N/A")
        days_behind = impl_info.get("days_behind_schedule", 0)
        status_color = "#ff4b4b" if impl_status in ("Stalled","Behind Schedule") else "#ffa726" if impl_status == "Slight Delay" else "#4caf50"
        st.markdown(f"**Implementation: <span style='color:{status_color}'>{impl_status}</span> · {pct}% complete ({done}/{total_m} milestones)**"
                    + (f" · <span style='color:#ff4b4b'>{days_behind} days behind</span>" if days_behind > 0 else ""),
                    unsafe_allow_html=True)
        st.progress(pct / 100)
        for m in milestones:
            icon = {"Complete": "✅", "In Progress": "🔄", "Not Started": "⬜"}.get(m["status"], "?")
            mname = m.get("milestone_name") or m.get("name", "?")
            blocker_txt = f" ⚠️ *{m['blocker']}*" if m.get("blocker") else ""
            st.markdown(f"{icon} **{mname}**{blocker_txt}")

    with tab3:
        open_t = [t for t in tickets if t["status"] != "Resolved"]
        resolved_t = [t for t in tickets if t["status"] == "Resolved"]
        st.markdown(f"**{len(open_t)} Open · {len(resolved_t)} Resolved**")
        for t in sorted(tickets, key=lambda x: (x["status"] != "Open", x["severity"])):
            sev_colors = {"P1": "#ff4b4b", "P2": "#ffa726", "P3": "#ffd54f", "P4": "#8b949e"}
            sev_color = sev_colors.get(t["severity"], "#fff")
            status_icon = "🔴" if t["status"] == "Open" else "🔄" if t["status"] == "In Progress" else "✅"
            st.markdown(f"""
            <div class="metric-card">
                <div style="display:flex;justify-content:space-between">
                    <span style="color:{sev_color};font-weight:700;font-size:0.8rem">{t['severity']}</span>
                    <span style="color:#8b949e;font-size:0.75rem">{status_icon} {t['status']}</span>
                </div>
                <div style="color:#e6edf3;font-size:0.9rem;margin-top:4px">{t['title']}</div>
                <div style="color:#8b949e;font-size:0.75rem;margin-top:2px">Opened: {t['opened_at'][:10]}</div>
            </div>
            """, unsafe_allow_html=True)

    with tab4:
        for s in stakeholders:
            role_colors = {"Champion": "#4fc3f7", "Executive Sponsor": "#9c88ff", "Economic Buyer": "#ffa726"}
            role_color = role_colors.get(s["role"], "#8b949e")
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-weight:700;color:#e6edf3">{s['name']} · <span style="color:#8b949e;font-weight:400">{s['title']}</span></div>
                <div style="font-size:0.8rem;color:{role_color};margin-top:2px">{s['role']}</div>
                <div style="font-size:0.75rem;color:#8b949e;margin-top:2px">{s['email']}</div>
            </div>
            """, unsafe_allow_html=True)

    with tab5:
        for n in notes:
            sent_colors = {"Positive": "#4caf50", "Neutral": "#8b949e", "Negative": "#ff4b4b"}
            sent_color = sent_colors.get(n["sentiment_signal"], "#8b949e")
            st.markdown(f"""
            <div class="metric-card">
                <div style="display:flex;justify-content:space-between">
                    <span style="color:#8b949e;font-size:0.8rem">{n['date'][:10]}</span>
                    <span style="color:{sent_color};font-size:0.8rem;font-weight:600">{n['sentiment_signal']}</span>
                </div>
                <div style="color:#e6edf3;font-size:0.9rem;margin-top:6px">{n['summary']}</div>
                <div style="color:#8b949e;font-size:0.75rem;margin-top:4px">👥 {n['attendees']}</div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3: AGENT CONSOLE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Agent Console":
    st.markdown("# Agent Console")
    st.markdown("<small style='color:#8b949e'>Run any agent on any customer and inspect model routing, cost, and confidence in real time.</small>", unsafe_allow_html=True)

    customers = get_customers()
    customer_map = {c["id"]: c["name"] for c in customers}

    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.markdown("**Configure Agent Run**")

        agent_descriptions = {
            "CustomerHealthAgent": "🩺 Health Agent — Haiku · Scoring & risk signals",
            "ImplementationAgent": "🔧 Implementation Agent — Sonnet · Milestones & blockers",
            "BriefingAgent": "📋 CEO Briefing Agent — Sonnet · Executive briefing",
            "EscalationCommanderAgent": "🚨 Escalation Commander — Opus · Battle plan",
            "SkeptikQAAgent": "🔍 Skeptik QA — Opus · Adversarial review",
            "VPChiefOfStaffAgent": "📊 VP Chief of Staff — Sonnet · Weekly portfolio review",
        }

        selected_agent = st.selectbox("Agent", list(agent_descriptions.keys()), format_func=lambda x: agent_descriptions[x])

        needs_customer = selected_agent != "VPChiefOfStaffAgent"
        selected_customer_id = None
        if needs_customer:
            selected_customer_id = st.selectbox(
                "Customer",
                options=list(customer_map.keys()),
                format_func=lambda x: customer_map[x],
                index=0,
            )

        # Show model routing info
        tier_map = {
            "CustomerHealthAgent": ("haiku", "claude-haiku-4-5-20251001"),
            "ImplementationAgent": ("sonnet", "claude-sonnet-4-6"),
            "BriefingAgent": ("sonnet", "claude-sonnet-4-6"),
            "EscalationCommanderAgent": ("opus", "claude-opus-4-8"),
            "SkeptikQAAgent": ("opus", "claude-opus-4-8"),
            "VPChiefOfStaffAgent": ("sonnet", "claude-sonnet-4-6"),
        }
        tier, model_id = tier_map[selected_agent]
        tier_colors = {"haiku": "#4fc3f7", "sonnet": "#9c88ff", "opus": "#ce93d8"}
        color = tier_colors[tier]

        st.markdown(f"""
        <div class="metric-card" style="margin-top:12px">
            <div style="color:#8b949e;font-size:0.75rem;margin-bottom:4px">ROUTED TO</div>
            <div style="color:{color};font-weight:700;font-size:1rem">{tier.capitalize()}</div>
            <div style="color:#8b949e;font-size:0.75rem">{model_id}</div>
        </div>
        """, unsafe_allow_html=True)

        run_clicked = st.button("▶ Run Agent", use_container_width=True, type="primary")

    with col_right:
        if run_clicked:
            with st.spinner(f"Running {selected_agent}..."):
                result = run_agent(selected_agent, selected_customer_id)
            st.markdown(f"### {selected_agent} Output")
            render_agent_result(result)
        else:
            st.markdown("""
            <div style="border:1px dashed #30363d;border-radius:10px;padding:40px;text-align:center;color:#8b949e;margin-top:20px">
                <div style="font-size:2rem">🤖</div>
                <div style="margin-top:8px">Configure an agent and click Run</div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4: BRIEFINGS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Briefings":
    st.markdown("# Briefings")

    customers = get_customers()

    tab_ceo, tab_vp = st.tabs(["CEO Briefings", "Weekly VP CX Reviews"])

    with tab_ceo:
        col_gen, col_view = st.columns([1, 2])
        with col_gen:
            customer_map = {c["id"]: f"{risk_badge(c.get('risk_level', c.get('risk_label','Unknown')))} {c['name']}" for c in customers}
            selected_id = st.selectbox("Customer", list(customer_map.keys()), format_func=lambda x: customer_map[x])
            if st.button("📋 Generate CEO Briefing", use_container_width=True, type="primary"):
                with st.spinner("Generating CEO briefing..."):
                    result = run_agent("BriefingAgent", selected_id)
                st.session_state["latest_briefing"] = result
                st.success("Briefing generated!")

        with col_view:
            if "latest_briefing" in st.session_state:
                result = st.session_state["latest_briefing"]
                render_agent_result(result)

        st.markdown("---")
        st.markdown("**Recent CEO Briefings**")
        try:
            briefings = requests.get(f"{API}/briefings?briefing_type=CEO").json()
            for b in briefings:
                with st.expander(f"{b.get('customer_name','Portfolio')} · {b['created_at'][:16].replace('T',' ')}"):
                    st.markdown(b["content"])
        except Exception:
            st.caption("No briefings yet.")

    with tab_vp:
        if st.button("📊 Generate Weekly VP CX Review", use_container_width=True, type="primary"):
            with st.spinner("Running VP Chief of Staff Agent..."):
                result = run_agent("VPChiefOfStaffAgent")
            st.session_state["latest_vp_review"] = result

        if "latest_vp_review" in st.session_state:
            result = st.session_state["latest_vp_review"]
            render_agent_result(result)

        st.markdown("---")
        st.markdown("**Recent VP CX Reviews**")
        try:
            briefings = requests.get(f"{API}/briefings?briefing_type=VP_CX").json()
            for b in briefings:
                with st.expander(f"Weekly Review · {b['created_at'][:16].replace('T',' ')}"):
                    st.markdown(b["content"])
        except Exception:
            st.caption("No reviews yet.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5: AUDIT TRAIL & COSTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Audit Trail & Costs":
    st.markdown("# Audit Trail & Cost Tracking")

    costs = get_costs()
    if costs:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Spend", f"${costs.get('grand_total', 0):.4f}")
        with col2:
            runs = get_audit_log()
            st.metric("Total Agent Runs", len(runs))
        with col3:
            avg = costs.get("grand_total", 0) / max(len(get_audit_log()), 1)
            st.metric("Avg Cost / Run", f"${avg:.4f}")

        st.markdown("---")
        st.markdown("**Cost by Model**")
        by_model = costs.get("by_model", [])
        if by_model:
            for row in by_model:
                model = row["model_used"]
                tier = model_tier(model)
                tier_colors = {"haiku": "#4fc3f7", "sonnet": "#9c88ff", "opus": "#ce93d8"}
                color = tier_colors.get(tier, "#fff")
                c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                with c1: st.markdown(f"<span style='color:{color};font-weight:700'>{tier.capitalize()}</span> <span style='color:#8b949e;font-size:0.75rem'>{model}</span>", unsafe_allow_html=True)
                with c2: st.metric("Runs", row["run_count"])
                with c3: st.metric("Tokens", f"{(row.get('total_input_tokens',0) or 0) + (row.get('total_output_tokens',0) or 0):,}")
                with c4: st.metric("Cost", f"${row.get('total_cost', 0) or 0:.4f}")

    st.markdown("---")
    st.markdown("**Full Agent Run History**")

    runs = get_audit_log()
    if not runs:
        st.info("No agent runs yet. Run some agents to see the audit trail.")
    else:
        for run in runs:
            tier = model_tier(run.get("model_used", ""))
            tier_colors = {"haiku": "#4fc3f7", "sonnet": "#9c88ff", "opus": "#ce93d8"}
            color = tier_colors.get(tier, "#fff")
            is_mock = False  # historic runs don't store this flag

            with st.expander(
                f"#{run['id']} · {run['agent_name']} · {run.get('customer_name','Portfolio')} · "
                f"{run['created_at'][:16].replace('T',' ')}"
            ):
                col_a, col_b, col_c, col_d = st.columns(4)
                with col_a:
                    st.markdown(f"**Model**")
                    st.markdown(f"<span style='color:{color};font-weight:700'>{tier.capitalize()}</span>", unsafe_allow_html=True)
                with col_b:
                    st.metric("Cost", f"${run.get('estimated_cost_usd', 0):.4f}")
                with col_c:
                    st.metric("Confidence", f"{run.get('confidence_score', 0):.0%}")
                with col_d:
                    st.metric("Tokens", f"{run.get('input_tokens',0):,}+{run.get('output_tokens',0):,}")

                st.markdown(f"*Routing rationale: {run.get('model_rationale','')}*")
                st.markdown("---")
                st.markdown(run.get("output_text", ""), unsafe_allow_html=False)
