import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from typing import Optional

from backend.crud import (
    get_all_customers, get_customer, get_customer_360, get_portfolio_summary,
    save_agent_run, save_briefing, get_agent_runs, get_briefings, get_cost_summary
)
from backend.context_builder import build_customer_context, build_portfolio_context
from agents.agents import AGENT_REGISTRY, AGENT_DESCRIPTIONS, AGENT_MODEL_TIER
from agents.model_router import route

app = FastAPI(title="VP CX Agent OS", version="2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/")
def root():
    return {"status": "VP CX Agent OS v2.0 running", "agents": list(AGENT_REGISTRY.keys())}


# ── Customer endpoints ────────────────────────────────────────────────────────

@app.get("/customers")
def list_customers():
    return get_all_customers()


@app.get("/customers/{customer_id}")
def customer_detail(customer_id: int):
    c = get_customer(customer_id)
    if not c:
        raise HTTPException(404, "Customer not found")
    return c


@app.get("/customers/{customer_id}/360")
def customer_360(customer_id: int):
    data = get_customer_360(customer_id)
    if not data["customer"]:
        raise HTTPException(404, "Customer not found")
    return data


# ── Portfolio endpoints ───────────────────────────────────────────────────────

@app.get("/portfolio/summary")
def portfolio_summary():
    return get_portfolio_summary()


# ── Agent execution ───────────────────────────────────────────────────────────

@app.post("/agents/run")
def run_agent(agent_name: str, customer_id: Optional[int] = None):
    if agent_name not in AGENT_REGISTRY:
        raise HTTPException(400, f"Unknown agent: {agent_name}. Available: {list(AGENT_REGISTRY.keys())}")

    agent = AGENT_REGISTRY[agent_name]()

    if agent_name == "VPChiefOfStaffAgent":
        context = build_portfolio_context()
        cid = None

    elif agent_name == "SkeptikQAAgent":
        if not customer_id:
            raise HTTPException(400, "SkeptikQAAgent requires a customer_id")
        runs = get_agent_runs(20)
        # Find most recent non-Skeptik run for this customer
        prior = next(
            (r for r in runs if r.get("customer_id") == customer_id
             and r["agent_name"] != "SkeptikQAAgent"),
            None
        )
        if not prior:
            raise HTTPException(400, "No prior agent output found for this customer. Run another agent first.")
        context = build_customer_context(customer_id)
        context["prior_agent"]      = prior["agent_name"]
        context["prior_output"]     = prior["output_text"]
        context["prior_confidence"] = prior.get("confidence_score", 0.75)
        cid = customer_id

    else:
        if not customer_id:
            raise HTTPException(400, f"{agent_name} requires a customer_id")
        context = build_customer_context(customer_id)
        cid = customer_id

    result = agent.run(context, customer_id=cid)
    run_id = save_agent_run(result)

    # Persist briefings to their own table
    if agent_name in ("BriefingAgent", "VPChiefOfStaffAgent"):
        briefing_type = "CEO" if agent_name == "BriefingAgent" else "VP_CX"
        save_briefing(briefing_type, cid, result.output_text, run_id)

    routing = route(agent_name)

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


@app.post("/agents/run-portfolio-health")
def run_portfolio_health():
    """Run CustomerHealthAgent on every customer and return a ranked list."""
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


@app.post("/agents/run-implementation-digest")
def run_implementation_digest():
    """Run ImplementationAgent on all at-risk implementations and return a digest."""
    from backend.database import fetchall
    impls     = fetchall("SELECT DISTINCT customer_id FROM implementations")
    agent     = AGENT_REGISTRY["ImplementationAgent"]()
    results   = []

    for row in impls:
        cid     = row["customer_id"]
        context = build_customer_context(cid)
        result  = agent.run(context, customer_id=cid)
        run_id  = save_agent_run(result)
        results.append({
            "customer_id":         cid,
            "customer_name":       context["customer_name"],
            "overall_status":      result.structured.overall_status if result.structured else context.get("impl_status","?"),
            "pct_complete":        result.structured.pct_complete if result.structured else context.get("impl_progress",0),
            "launch_confidence":   result.structured.launch_confidence if result.structured else "Unknown",
            "active_blockers":     result.structured.active_blockers[:2] if result.structured else [],
            "recommended_intervention": result.structured.recommended_intervention if result.structured else "",
            "run_id":              run_id,
            "estimated_cost_usd":  result.estimated_cost_usd,
        })

    results.sort(key=lambda r: {"Very Low": 0, "Low": 1, "Medium": 2, "High": 3}.get(r["launch_confidence"], 2))
    return {
        "digest_date":       results[0]["customer_name"] and result.created_at if results else "",
        "projects_reviewed": len(results),
        "total_cost_usd":    round(sum(r["estimated_cost_usd"] for r in results), 6),
        "results":           results,
    }


# ── History & reporting ───────────────────────────────────────────────────────

@app.get("/audit-log")
def audit_log(limit: int = 50, agent_name: Optional[str] = None, customer_id: Optional[int] = None):
    runs = get_agent_runs(limit)
    if agent_name:
        runs = [r for r in runs if r["agent_name"] == agent_name]
    if customer_id:
        runs = [r for r in runs if r.get("customer_id") == customer_id]
    return runs


@app.get("/briefings")
def list_briefings(briefing_type: Optional[str] = None, customer_id: Optional[int] = None):
    return get_briefings(briefing_type, customer_id)


@app.get("/briefings/{briefing_id}/export", response_class=PlainTextResponse)
def export_briefing(briefing_id: int):
    from backend.crud import get_briefings
    from backend.database import fetchone
    b = fetchone("SELECT * FROM briefings WHERE id = ?", (briefing_id,))
    if not b:
        raise HTTPException(404, "Briefing not found")
    return b["content"]


@app.get("/costs")
def cost_summary():
    return get_cost_summary()


@app.get("/agents")
def list_agents():
    return [
        {
            "name":        name,
            "description": AGENT_DESCRIPTIONS[name],
            "model_tier":  AGENT_MODEL_TIER[name],
            "model_id":    route(name).model_id,
            "model_display": route(name).model_display,
            "rationale":   route(name).rationale,
        }
        for name in AGENT_REGISTRY
    ]
