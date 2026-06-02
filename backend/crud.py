from backend.database import fetchall, fetchone, execute
from datetime import datetime


def get_all_customers():
    return fetchall("SELECT * FROM customers ORDER BY health_score ASC")


def get_customer(customer_id: int):
    return fetchone("SELECT * FROM customers WHERE id = ?", (customer_id,))


def get_customer_360(customer_id: int):
    return {
        "customer": fetchone("SELECT * FROM customers WHERE id = ?", (customer_id,)),
        "tickets": fetchall("SELECT * FROM support_tickets WHERE customer_id = ? ORDER BY opened_at DESC", (customer_id,)),
        "escalations": fetchall("SELECT * FROM escalations WHERE customer_id = ?", (customer_id,)),
        "stakeholders": fetchall("SELECT * FROM stakeholders WHERE customer_id = ?", (customer_id,)),
        "metrics": fetchall("SELECT * FROM usage_metrics WHERE customer_id = ?", (customer_id,)),
        "milestones": fetchall("SELECT * FROM implementation_milestones WHERE customer_id = ?", (customer_id,)),
        "meeting_notes": fetchall("SELECT * FROM meeting_notes WHERE customer_id = ? ORDER BY date DESC LIMIT 5", (customer_id,)),
    }


def get_portfolio_summary():
    customers = fetchall("SELECT * FROM customers")
    escalations = fetchall("SELECT * FROM escalations WHERE status != 'Resolved'")

    total_arr = sum(c["arr"] for c in customers)
    critical = [c for c in customers if c["risk_label"] == "Critical"]
    at_risk = [c for c in customers if c["risk_label"] == "At Risk"]
    healthy = [c for c in customers if c["risk_label"] == "Healthy"]
    arr_at_risk = sum(c["arr"] for c in critical + at_risk)

    today = datetime.now().date()
    renewals_90 = sum(
        1 for c in customers
        if 0 <= (datetime.strptime(c["renewal_date"], "%Y-%m-%d").date() - today).days <= 90
    )
    avg_health = sum(c["health_score"] for c in customers) / len(customers) if customers else 0

    top_escalations = sorted(escalations, key=lambda e: e["severity"], reverse=True)[:5]

    return {
        "total_customers": len(customers),
        "total_arr": total_arr,
        "arr_at_risk": arr_at_risk,
        "critical_count": len(critical),
        "at_risk_count": len(at_risk),
        "healthy_count": len(healthy),
        "open_escalations": len(escalations),
        "renewals_next_90_days": renewals_90,
        "avg_health_score": round(avg_health, 1),
        "top_escalations": top_escalations,
    }


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
    query = "SELECT b.*, c.name as customer_name FROM briefings b LEFT JOIN customers c ON b.customer_id = c.id"
    conditions, params = [], []
    if briefing_type:
        conditions.append("b.briefing_type = ?")
        params.append(briefing_type)
    if customer_id:
        conditions.append("b.customer_id = ?")
        params.append(customer_id)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY b.created_at DESC LIMIT 20"
    return fetchall(query, params)


def get_cost_summary():
    rows = fetchall(
        """SELECT model_used,
           COUNT(*) as run_count,
           SUM(input_tokens) as total_input_tokens,
           SUM(output_tokens) as total_output_tokens,
           SUM(estimated_cost_usd) as total_cost
           FROM agent_runs GROUP BY model_used"""
    )
    total = fetchone("SELECT SUM(estimated_cost_usd) as total FROM agent_runs")
    return {
        "by_model": rows,
        "grand_total": total["total"] if total and total["total"] else 0.0,
    }
