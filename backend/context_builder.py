"""
Builds rich context dicts from DB data to feed into agent prompts.
"""

import json
from datetime import datetime
from backend.crud import get_customer_360, get_all_customers, get_portfolio_summary


def build_customer_context(customer_id: int) -> dict:
    data  = get_customer_360(customer_id)
    c     = data["customer"]
    today = datetime.now().date()
    renewal = datetime.strptime(c["renewal_date"], "%Y-%m-%d").date()
    renewal_days = (renewal - today).days

    open_tickets   = [t for t in data["tickets"]   if t["status"] != "Resolved"]
    open_escalations = data["escalations"]

    milestones  = data.get("milestones", [])
    done        = sum(1 for m in milestones if m["status"] == "Complete")
    impl_progress = int(done / len(milestones) * 100) if milestones else 0

    impl = data.get("implementation") or {}
    milestones_str = "\n".join(
        f"- {m['milestone_name']}: {m['status']}"
        + (f" [BLOCKED: {m['blocker']}]" if m.get("blocker") else "")
        for m in milestones
    ) or "No milestones recorded"

    notes_str = "\n".join(
        f"- [{n['date'][:10]}] ({n['meeting_type']}, {n['sentiment_signal']}) {n['summary'][:160]}"
        for n in data.get("meeting_notes", [])[:3]
    ) or "No recent meeting notes"

    escalation_summary = "\n".join(
        f"- [{e['severity']}] {e['title']} (Owner: {e['owner']}, Status: {e['status']}, Exec Aware: {bool(e.get('executive_aware'))})"
        for e in open_escalations
    ) or "No active escalations"

    # Metrics row uses direct column names in the new schema
    mrow = data["metrics"][0] if data.get("metrics") else {}
    metrics = mrow  # direct column dict

    renewal_data = data.get("renewal") or {}

    return {
        "customer_name":           c["name"],
        "industry":                c["industry"],
        "arr":                     c["arr"],
        "employee_count":          c.get("employee_count", "?"),
        "renewal_date":            c["renewal_date"],
        "renewal_days":            renewal_days,
        "health_score":            c["health_score"],
        "health_trend":            c.get("health_trend", "Unknown"),
        "lifecycle_stage":         c.get("lifecycle_stage", "Mature"),
        "onboarding_status":       c.get("onboarding_status", "Unknown"),
        "adoption_score":          c.get("adoption_score", 0),
        "champion_name":           c.get("champion_name", "Unknown"),
        "champion_title":          c.get("champion_title", "Unknown"),
        "champion_status":         c.get("champion_status", "Unknown"),
        "technical_sponsor":       c.get("technical_sponsor", "Unknown"),
        "business_sponsor":        c.get("business_sponsor", "Unknown"),
        "sentiment":               c.get("sentiment", "Unknown"),
        "renewal_risk":            c.get("renewal_risk_score", 0),
        "security_review_status":  c.get("security_review_status", "Unknown"),
        "risk_label":              c.get("risk_level", "Unknown"),
        "risk_level":              c.get("risk_level", "Unknown"),
        "primary_risk_reason":     c.get("primary_risk_reason", ""),
        "recommended_next_action": c.get("recommended_next_action", ""),
        "csm_owner":               c.get("csm_owner", "Unassigned"),
        "implementation_owner":    c.get("implementation_owner", impl.get("implementation_owner", "Unassigned")),
        "open_tickets":            len(open_tickets),
        "open_escalations":        len(open_escalations),
        "escalation_summary":      escalation_summary,
        "milestones":              milestones_str,
        "impl_progress":           impl_progress,
        "impl_status":             impl.get("overall_status", "N/A"),
        "days_behind":             impl.get("days_behind_schedule", 0),
        "go_live_target":          impl.get("go_live_target", "Not set"),
        "meeting_notes":           notes_str,
        "renewal_stage":           renewal_data.get("renewal_stage", "Not Started"),
        "expansion_arr":           renewal_data.get("expansion_arr", 0),
        # ── New CS / retention / expansion signals ───────────────────────────
        "customer_tier":           c.get("customer_tier", "Enterprise"),
        "region":                  c.get("region", "NA"),
        "nrr_pct":                 c.get("nrr_pct", 0),
        "grr_pct":                 c.get("grr_pct", 0),
        "nps":                     c.get("nps", 0),
        "nps_trend":               c.get("nps_trend", "flat"),
        "utilization_pct":         c.get("utilization_pct", 0),
        "time_to_first_value_days":c.get("time_to_first_value_days"),
        "time_to_production_days": c.get("time_to_production_days"),
        "executive_engagement":    c.get("executive_engagement", "Unknown"),
        "qbr_completion":          c.get("qbr_completion", "Unknown"),
        "usage_trend":             c.get("usage_trend", "Steady"),
        "expansion_pipeline_arr":  c.get("expansion_pipeline_arr", 0),
        "upsell_likelihood":       c.get("upsell_likelihood", 0),
        "roi_outcome":             c.get("roi_outcome", ""),
        "cost_to_serve":           c.get("cost_to_serve", 0),
    }


def build_portfolio_context() -> dict:
    summary   = get_portfolio_summary()
    customers = get_all_customers()

    critical  = [c for c in customers if c["risk_level"] == "High"]
    at_risk   = [c for c in customers if c["risk_level"] == "Medium"]
    healthy   = [c for c in customers if c["risk_level"] == "Low"]

    critical_arr = sum(c["arr"] for c in critical)
    at_risk_arr  = sum(c["arr"] for c in at_risk)
    healthy_arr  = sum(c["arr"] for c in healthy)

    today = datetime.now().date()

    top_at_risk_str = "\n".join(
        f"- {c['name']} (${c['arr']:,}, Health: {c['health_score']}, "
        f"Renewal: {c['renewal_date']}, Risk: {c.get('primary_risk_reason','')[:60]})"
        for c in sorted(critical + at_risk, key=lambda x: x["health_score"])[:5]
    )

    recent_wins = [c for c in healthy if c.get("adoption_score", 0) > 75][:3]
    wins_str = "\n".join(
        f"- {c['name']}: adoption {c.get('adoption_score',0)}/100, health {c['health_score']}, trend {c.get('health_trend','')}"
        for c in recent_wins
    ) or "No standout wins this week"

    renewals_90 = [
        c for c in customers
        if 0 <= (datetime.strptime(c["renewal_date"], "%Y-%m-%d").date() - today).days <= 90
    ]
    renewal_pipeline_str = (
        f"{len(renewals_90)} renewals totaling ${sum(c['arr'] for c in renewals_90):,} ARR due within 90 days. "
        f"{sum(1 for c in renewals_90 if c['risk_level']=='High')} are high-risk."
    )

    return {
        "total_customers":  summary["total_customers"],
        "total_arr":        summary["total_arr"],
        "critical_count":   summary["critical_count"],
        "critical_arr":     critical_arr,
        "at_risk_count":    summary["at_risk_count"],
        "at_risk_arr":      at_risk_arr,
        "healthy_count":    summary["healthy_count"],
        "healthy_arr":      healthy_arr,
        "open_escalations": summary["open_escalations"],
        "renewals_90d":     len(renewals_90),
        "top_at_risk":      top_at_risk_str,
        "recent_wins":      wins_str,
        "renewal_pipeline": renewal_pipeline_str,
        "arr_at_risk":      summary["arr_at_risk"],
        "risk_pct":         round(summary["arr_at_risk"] / summary["total_arr"] * 100, 1) if summary["total_arr"] else 0,
        # ── Retention & expansion KPIs ───────────────────────────────────────
        "nrr_pct":              summary.get("nrr_pct", 0),
        "grr_pct":              summary.get("grr_pct", 0),
        "expansion_pipeline_arr": summary.get("expansion_pipeline_arr", 0),
        "renewal_forecast_pct": summary.get("renewal_forecast_pct", 0),
        "churn_risk_pct":       summary.get("churn_risk_pct", 0),
        "avg_nps":              summary.get("avg_nps", 0),
        "avg_adoption":         summary.get("avg_adoption", 0),
    }
