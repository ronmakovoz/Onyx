from backend.database import fetchall, fetchone, execute
from datetime import datetime


def get_all_customers():
    return fetchall("SELECT * FROM customers ORDER BY health_score ASC")


def get_customer(customer_id: int):
    return fetchone("SELECT * FROM customers WHERE id = ?", (customer_id,))


def get_customer_360(customer_id: int):
    return {
        "customer":      fetchone("SELECT * FROM customers WHERE id = ?", (customer_id,)),
        "tickets":       fetchall("SELECT * FROM support_tickets WHERE customer_id = ? ORDER BY opened_at DESC", (customer_id,)),
        "escalations":   fetchall("SELECT * FROM escalations WHERE customer_id = ?", (customer_id,)),
        "stakeholders":  fetchall("SELECT * FROM stakeholders WHERE customer_id = ?", (customer_id,)),
        "metrics":       fetchall("SELECT * FROM usage_metrics WHERE customer_id = ?", (customer_id,)),
        "milestones":    fetchall(
            """SELECT im.* FROM implementation_milestones im
               JOIN implementations i ON im.implementation_id = i.id
               WHERE im.customer_id = ?
               ORDER BY im.planned_days_from_start""",
            (customer_id,)
        ),
        "implementation": fetchone("SELECT * FROM implementations WHERE customer_id = ?", (customer_id,)),
        "meeting_notes": fetchall("SELECT * FROM meeting_notes WHERE customer_id = ? ORDER BY date DESC LIMIT 6", (customer_id,)),
        "renewal":       fetchone("SELECT * FROM renewals WHERE customer_id = ?", (customer_id,)),
        "health_history":fetchall("SELECT * FROM health_history WHERE customer_id = ? ORDER BY date ASC", (customer_id,)),
    }


def get_portfolio_summary():
    customers   = fetchall("SELECT * FROM customers")
    escalations = fetchall("SELECT * FROM escalations WHERE status != 'Resolved'")

    total_arr   = sum(c["arr"] for c in customers)
    critical    = [c for c in customers if c["risk_level"] == "High"]
    at_risk     = [c for c in customers if c["risk_level"] == "Medium"]
    healthy     = [c for c in customers if c["risk_level"] == "Low"]
    arr_at_risk = sum(c["arr"] for c in critical + at_risk)

    today = datetime.now().date()
    renewals_90 = sum(
        1 for c in customers
        if 0 <= (datetime.strptime(c["renewal_date"], "%Y-%m-%d").date() - today).days <= 90
    )
    avg_health = sum(c["health_score"] for c in customers) / len(customers) if customers else 0
    top_escalations = sorted(escalations, key=lambda e: (e["severity"] == "Critical", e["arr_at_risk"] or 0), reverse=True)[:5]

    # ── Retention & expansion metrics (ARR-weighted) ──────────────────────────
    def _wavg(field):
        if not total_arr:
            return 0.0
        return sum((c.get(field) or 0) * c["arr"] for c in customers) / total_arr

    nrr = round(_wavg("nrr_pct"), 1)
    grr = round(_wavg("grr_pct"), 1)
    expansion_pipeline_arr = sum(c.get("expansion_pipeline_arr") or 0 for c in customers)

    # Renewal forecast = ARR-weighted (1 - renewal_risk) across accounts renewing in 90d
    upcoming = [c for c in customers
                if 0 <= (datetime.strptime(c["renewal_date"], "%Y-%m-%d").date() - today).days <= 90]
    upcoming_arr = sum(c["arr"] for c in upcoming)
    renewal_forecast_arr = sum(c["arr"] * (1 - (c.get("renewal_risk_score") or 0)) for c in upcoming)
    renewal_forecast_pct = round(renewal_forecast_arr / upcoming_arr * 100, 1) if upcoming_arr else 100.0

    churn_risk_pct = round(len(critical) / len(customers) * 100, 1) if customers else 0.0
    avg_nps = round(sum(c.get("nps") or 0 for c in customers) / len(customers), 1) if customers else 0
    avg_adoption = round(sum(c.get("adoption_score") or 0 for c in customers) / len(customers), 1) if customers else 0
    ttv_vals = [c["time_to_first_value_days"] for c in customers if c.get("time_to_first_value_days")]
    avg_ttv = round(sum(ttv_vals) / len(ttv_vals), 0) if ttv_vals else 0

    return {
        "total_customers":       len(customers),
        "total_arr":             total_arr,
        "arr_at_risk":           arr_at_risk,
        "critical_count":        len(critical),
        "at_risk_count":         len(at_risk),
        "healthy_count":         len(healthy),
        "open_escalations":      len(escalations),
        "renewals_next_90_days": renewals_90,
        "avg_health_score":      round(avg_health, 1),
        "top_escalations":       top_escalations,
        # New executive CS metrics
        "nrr_pct":               nrr,
        "grr_pct":               grr,
        "expansion_pipeline_arr": expansion_pipeline_arr,
        "renewal_forecast_pct":  renewal_forecast_pct,
        "renewal_forecast_arr":  round(renewal_forecast_arr),
        "upcoming_renewal_arr":  upcoming_arr,
        "churn_risk_pct":        churn_risk_pct,
        "avg_nps":               avg_nps,
        "avg_adoption":          avg_adoption,
        "avg_time_to_value_days": int(avg_ttv),
    }


def get_implementation_overview():
    """Fast, LLM-free implementation health across all active projects.

    Returns one row per implementation with the timeline + delivery KPIs the
    digest needs (kickoff status/date, days after signing, go-live target and
    countdown, days behind, milestones completed, launch-confidence risk).
    Pure SQL so the digest page renders instantly — the AI narrative is fetched
    on demand per project, not for the whole portfolio up front.
    """
    from datetime import date

    def _parse(d):
        if not d:
            return None
        try:
            return datetime.fromisoformat(str(d)).date()
        except Exception:
            try:
                return datetime.strptime(str(d)[:10], "%Y-%m-%d").date()
            except Exception:
                return None

    today = date.today()
    impls = fetchall("SELECT * FROM implementations")
    out = []
    for im in impls:
        cust  = fetchone("SELECT * FROM customers WHERE id = ?", (im["customer_id"],)) or {}
        miles = fetchall(
            "SELECT * FROM implementation_milestones WHERE implementation_id = ? "
            "ORDER BY planned_days_from_start", (im["id"],)
        )

        total_ms     = len(miles)
        completed_ms = [m for m in miles if m["status"] == "Complete"]
        done_names   = [m["milestone_name"] for m in completed_ms]
        in_progress  = [m["milestone_name"] for m in miles if m["status"] == "In Progress"]
        blockers     = [m["blocker"] for m in miles if m.get("blocker")]

        # Kickoff = the earliest milestone (typically "Kickoff & Scoping")
        kickoff      = miles[0] if miles else None
        kicked_off   = bool(kickoff and kickoff["status"] in ("Complete", "In Progress"))
        kickoff_date = _parse(kickoff["completed_at"]) if (kickoff and kickoff["status"] == "Complete") else None

        sig_date  = _parse(cust.get("contract_start_date"))
        days_post_signature = (kickoff_date - sig_date).days if (kickoff_date and sig_date) else None
        # Guard against synthetic date inconsistencies (kickoff logged before signing)
        if days_post_signature is not None and days_post_signature < 0:
            days_post_signature = None

        go_live   = _parse(im.get("go_live_target"))
        days_to_go_live = (go_live - today).days if go_live else None

        behind = im.get("days_behind_schedule", 0) or 0
        status = im.get("overall_status", "Unknown")
        pct    = im.get("pct_complete", 0) or 0

        # Launch-confidence risk model (LLM-free heuristic)
        if behind > 30 or status == "Stalled":
            conf = "Very Low"
        elif behind > 14:
            conf = "Low"
        elif behind > 3 or pct < 55:
            conf = "Medium"
        else:
            conf = "High"

        out.append({
            "customer_id":          im["customer_id"],
            "customer_name":        im.get("customer_name") or cust.get("name", "?"),
            "implementation_owner": im.get("implementation_owner", "—"),
            "overall_status":       status,
            "pct_complete":         pct,
            "days_behind_schedule": behind,
            "kicked_off":           kicked_off,
            "kickoff_date":         kickoff_date.isoformat() if kickoff_date else None,
            "days_post_signature":  days_post_signature,
            "contract_start_date":  sig_date.isoformat() if sig_date else None,
            "go_live_target":       go_live.isoformat() if go_live else None,
            "days_to_go_live":      days_to_go_live,
            "milestones_total":     total_ms,
            "milestones_complete":  len(completed_ms),
            "completed_milestones": done_names,
            "in_progress_milestones": in_progress,
            "active_blockers":      blockers,
            "launch_confidence":    conf,
        })

    conf_rank = {"Very Low": 0, "Low": 1, "Medium": 2, "High": 3}
    out.sort(key=lambda r: (conf_rank.get(r["launch_confidence"], 2), -r["days_behind_schedule"]))
    return out


def save_agent_run(result) -> int:
    run_id = execute(
        """INSERT INTO agent_runs
           (agent_name, customer_id, model_used, model_rationale, input_tokens,
            output_tokens, estimated_cost_usd, confidence_score, output_text, created_at)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (result.agent_name, result.customer_id, result.model_used, result.model_rationale,
         result.input_tokens, result.output_tokens, result.estimated_cost_usd,
         result.confidence_score, result.output_text, result.created_at)
    )
    return run_id


def save_briefing(briefing_type: str, customer_id, content: str, agent_run_id: int):
    execute(
        "INSERT INTO briefings (briefing_type, customer_id, content, agent_run_id, created_at) VALUES (?,?,?,?,?)",
        (briefing_type, customer_id, content, agent_run_id, datetime.now().isoformat())
    )


def get_agent_runs(limit: int = 50):
    return fetchall(
        """SELECT ar.*, c.name as customer_name
           FROM agent_runs ar
           LEFT JOIN customers c ON ar.customer_id = c.id
           ORDER BY ar.created_at DESC LIMIT ?""",
        (limit,)
    )


def get_briefings(briefing_type: str = None, customer_id: int = None):
    query  = "SELECT b.*, c.name as customer_name FROM briefings b LEFT JOIN customers c ON b.customer_id = c.id"
    conds, params = [], []
    if briefing_type:
        conds.append("b.briefing_type = ?"); params.append(briefing_type)
    if customer_id:
        conds.append("b.customer_id = ?");   params.append(customer_id)
    if conds:
        query += " WHERE " + " AND ".join(conds)
    query += " ORDER BY b.created_at DESC LIMIT 20"
    return fetchall(query, params)


def get_cost_summary():
    rows  = fetchall(
        """SELECT model_used,
           COUNT(*) as run_count,
           SUM(input_tokens) as total_input_tokens,
           SUM(output_tokens) as total_output_tokens,
           SUM(estimated_cost_usd) as total_cost
           FROM agent_runs GROUP BY model_used"""
    )
    total = fetchone("SELECT SUM(estimated_cost_usd) as total FROM agent_runs")
    return {
        "by_model":    rows,
        "grand_total": total["total"] if total and total["total"] else 0.0,
    }


# ── Recommendation / action-outcome layer ────────────────────────────────────
# Tracks whether the AI's recommended action for each account was acted on,
# so the app can show ROI on the AI itself (not just generate analysis).

VALID_ACTION_STATUSES = ("Open", "In Progress", "Done", "Dismissed")


def _ensure_action_table():
    execute(
        """CREATE TABLE IF NOT EXISTS recommendation_actions (
               customer_id INTEGER PRIMARY KEY,
               status      TEXT NOT NULL DEFAULT 'Open',
               note        TEXT DEFAULT '',
               updated_at  TEXT
           )"""
    )


def get_action_status(customer_id: int) -> dict:
    _ensure_action_table()
    row = fetchone("SELECT * FROM recommendation_actions WHERE customer_id = ?", (customer_id,))
    return row or {"customer_id": customer_id, "status": "Open", "note": "", "updated_at": None}


def set_action_status(customer_id: int, status: str, note: str = "") -> None:
    _ensure_action_table()
    if status not in VALID_ACTION_STATUSES:
        status = "Open"
    execute(
        """INSERT INTO recommendation_actions (customer_id, status, note, updated_at)
           VALUES (?,?,?,?)
           ON CONFLICT(customer_id) DO UPDATE SET
               status=excluded.status, note=excluded.note, updated_at=excluded.updated_at""",
        (customer_id, status, note, datetime.now().isoformat())
    )


def get_action_summary() -> dict:
    """Portfolio-wide outcome metrics for the AI recommendations."""
    _ensure_action_table()
    customers = fetchall("SELECT id, arr, risk_level FROM customers")
    actions   = {a["customer_id"]: a for a in fetchall("SELECT * FROM recommendation_actions")}

    at_risk = [c for c in customers if c["risk_level"] in ("High", "Medium")]
    at_risk_total_arr = sum(c["arr"] for c in at_risk)

    closed = in_progress = dismissed = 0
    arr_protected = 0
    for c in at_risk:
        a = actions.get(c["id"])
        if not a:
            continue
        if a["status"] == "Done":
            closed += 1
            arr_protected += c["arr"]
        elif a["status"] == "In Progress":
            in_progress += 1
            arr_protected += c["arr"]
        elif a["status"] == "Dismissed":
            dismissed += 1

    actioned = closed + in_progress
    coverage_pct = round(actioned / len(at_risk) * 100, 1) if at_risk else 0.0
    return {
        "at_risk_accounts":   len(at_risk),
        "at_risk_total_arr":  at_risk_total_arr,
        "actions_closed":     closed,
        "actions_in_progress": in_progress,
        "actions_dismissed":  dismissed,
        "actions_actioned":   actioned,
        "coverage_pct":       coverage_pct,
        "arr_protected":      arr_protected,
    }

