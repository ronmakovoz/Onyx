"""
Builds rich context dicts from DB data to feed into agent prompts.
"""

from datetime import datetime
from backend.crud import get_customer_360, get_all_customers, get_portfolio_summary


def build_customer_context(customer_id: int) -> dict:
    data = get_customer_360(customer_id)
    c = data["customer"]
    today = datetime.now().date()
    renewal = datetime.strptime(c["renewal_date"], "%Y-%m-%d").date()
    renewal_days = (renewal - today).days

    open_tickets = [t for t in data["tickets"] if t["status"] != "Resolved"]
    open_escalations = data["escalations"]

    milestone_done = sum(1 for m in data["milestones"] if m["status"] == "Complete")
    milestone_total = len(data["milestones"])
    impl_progress = int(milestone_done / milestone_total * 100) if milestone_total else 0

    milestones_str = "\n".join(
        f"- {m['name']}: {m['status']}" for m in data["milestones"]
    ) or "No milestones recorded"

    notes_str = "\n".join(
        f"- [{n['date'][:10]}] {n['summary']}" for n in data["meeting_notes"][:3]
    ) or "No recent meeting notes"

    escalation_summary = "\n".join(
        f"- [{e['severity']}] {e['title']} (Owner: {e['owner']}, Status: {e['status']})"
        for e in open_escalations
    ) or "No active escalations"

    return {
        "customer_name": c["name"],
        "industry": c["industry"],
        "arr": c["arr"],
        "renewal_date": c["renewal_date"],
        "renewal_days": renewal_days,
        "health_score": c["health_score"],
        "onboarding_status": c["onboarding_status"],
        "adoption_score": c["adoption_score"],
        "champion_name": c["champion_name"],
        "champion_status": c["champion_status"],
        "sentiment": c["sentiment"],
        "renewal_risk": c["renewal_risk"],
        "security_review_status": c["security_review_status"],
        "risk_label": c["risk_label"],
        "open_tickets": len(open_tickets),
        "open_escalations": len(open_escalations),
        "escalation_summary": escalation_summary,
        "milestones": milestones_str,
        "impl_progress": impl_progress,
        "meeting_notes": notes_str,
    }


def build_portfolio_context() -> dict:
    summary = get_portfolio_summary()
    customers = get_all_customers()

    critical = [c for c in customers if c["risk_label"] == "Critical"]
    at_risk = [c for c in customers if c["risk_label"] == "At Risk"]
    healthy = [c for c in customers if c["risk_label"] == "Healthy"]

    critical_arr = sum(c["arr"] for c in critical)
    at_risk_arr = sum(c["arr"] for c in at_risk)
    healthy_arr = sum(c["arr"] for c in healthy)

    top_at_risk_str = "\n".join(
        f"- {c['name']} (${c['arr']:,}, Health: {c['health_score']}, Renewal: {c['renewal_date']})"
        for c in sorted(critical + at_risk, key=lambda x: x["health_score"])[:5]
    )

    recent_wins = [c for c in healthy if c["adoption_score"] > 80][:3]
    wins_str = "\n".join(
        f"- {c['name']}: adoption {c['adoption_score']}/100, health {c['health_score']}"
        for c in recent_wins
    ) or "No standout wins this week"

    today = datetime.now().date()
    renewals_90 = [
        c for c in customers
        if 0 <= (datetime.strptime(c["renewal_date"], "%Y-%m-%d").date() - today).days <= 90
    ]
    renewal_pipeline_str = f"{len(renewals_90)} renewals totaling ${sum(c['arr'] for c in renewals_90):,} ARR due within 90 days"

    return {
        "total_customers": summary["total_customers"],
        "total_arr": summary["total_arr"],
        "critical_count": summary["critical_count"],
        "critical_arr": critical_arr,
        "at_risk_count": summary["at_risk_count"],
        "at_risk_arr": at_risk_arr,
        "healthy_count": summary["healthy_count"],
        "healthy_arr": healthy_arr,
        "open_escalations": summary["open_escalations"],
        "renewals_90d": len(renewals_90),
        "top_at_risk": top_at_risk_str,
        "recent_wins": wins_str,
        "renewal_pipeline": renewal_pipeline_str,
        # For mock output
        "arr_at_risk": summary["arr_at_risk"],
        "risk_pct": round(summary["arr_at_risk"] / summary["total_arr"] * 100, 1) if summary["total_arr"] else 0,
    }
