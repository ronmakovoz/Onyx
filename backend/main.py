import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from backend.crud import (
    get_all_customers, get_customer, get_customer_360, get_portfolio_summary,
    save_agent_run, save_briefing, get_agent_runs, get_briefings, get_cost_summary
)
from backend.context_builder import build_customer_context, build_portfolio_context
from agents.agents import AGENT_REGISTRY

app = FastAPI(title="VP CX Agent OS", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/")
def root():
    return {"status": "VP CX Agent OS running"}


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


@app.get("/portfolio/summary")
def portfolio_summary():
    return get_portfolio_summary()


@app.post("/agents/run")
def run_agent(agent_name: str, customer_id: Optional[int] = None):
    if agent_name not in AGENT_REGISTRY:
        raise HTTPException(400, f"Unknown agent: {agent_name}. Available: {list(AGENT_REGISTRY.keys())}")

    agent_cls = AGENT_REGISTRY[agent_name]
    agent = agent_cls()

    if agent_name == "VPChiefOfStaffAgent":
        context = build_portfolio_context()
        cid = None
    elif agent_name == "SkeptikQAAgent":
        # Requires prior output — get the most recent agent run for this customer
        runs = get_agent_runs(10)
        prior = next((r for r in runs if r.get("customer_id") == customer_id and r["agent_name"] != "SkeptikQAAgent"), None)
        if not prior:
            raise HTTPException(400, "No prior agent output found to review for this customer")
        context = build_customer_context(customer_id)
        context["prior_agent"] = prior["agent_name"]
        context["prior_output"] = prior["output_text"]
        cid = customer_id
    else:
        if not customer_id:
            raise HTTPException(400, f"{agent_name} requires a customer_id")
        context = build_customer_context(customer_id)
        cid = customer_id

    result = agent.run(context, customer_id=cid)
    run_id = save_agent_run(result)

    if agent_name in ("BriefingAgent", "VPChiefOfStaffAgent"):
        briefing_type = "CEO" if agent_name == "BriefingAgent" else "VP_CX"
        save_briefing(briefing_type, cid, result.output_text, run_id)

    return {
        "run_id": run_id,
        "agent_name": result.agent_name,
        "customer_id": result.customer_id,
        "model_used": result.model_used,
        "model_rationale": result.model_rationale,
        "input_tokens": result.input_tokens,
        "output_tokens": result.output_tokens,
        "estimated_cost_usd": result.estimated_cost_usd,
        "confidence_score": result.confidence_score,
        "output_text": result.output_text,
        "created_at": result.created_at,
        "is_mock": result.is_mock,
    }


@app.get("/audit-log")
def audit_log(limit: int = 50):
    return get_agent_runs(limit)


@app.get("/briefings")
def list_briefings(briefing_type: Optional[str] = None, customer_id: Optional[int] = None):
    return get_briefings(briefing_type, customer_id)


@app.get("/costs")
def cost_summary():
    return get_cost_summary()
