"""
Onyx CX Agent OS — FastAPI backend.
Run from repo root: uvicorn api.main:app --port 8000
"""

import os
import sys
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Auto-seed the database on startup if missing
_DB_PATH = os.path.join(ROOT, "data", "cx_agent_os.db")
if not os.path.exists(_DB_PATH):
    subprocess.run([sys.executable, os.path.join(ROOT, "data", "generate_synthetic_data.py")], check=True)

from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from api.deck import render_kickoff_deck, render_generic_deck, render_deck_loading

from backend.crud import (
    get_all_customers, get_customer_360, get_portfolio_summary,
    save_agent_run, save_briefing, get_agent_runs, get_briefings, get_cost_summary,
    get_action_status, set_action_status, get_action_summary, get_implementation_overview,
)
from backend.context_builder import build_customer_context, build_portfolio_context
from backend.database import fetchall
from agents.agents import AGENT_REGISTRY, AGENT_DESCRIPTIONS, AGENT_MODEL_TIER
from agents.model_router import route as _route

# Capture the real key once at startup; the Mock/Live toggle mutates os.environ
# (agents read ANTHROPIC_API_KEY at run time), so this is the only safe copy.
_REAL_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
# Default to mock mode until explicitly toggled live
os.environ.pop("ANTHROPIC_API_KEY", None)

app = FastAPI(title="Onyx CX Agent OS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ModeUpdate(BaseModel):
    live: bool


@app.get("/api/mode")
def get_mode():
    return {
        "live": bool(os.environ.get("ANTHROPIC_API_KEY")),
        "available": bool(_REAL_API_KEY),
    }


@app.post("/api/mode")
def set_mode(body: ModeUpdate):
    if body.live and not _REAL_API_KEY:
        raise HTTPException(status_code=400, detail="ANTHROPIC_API_KEY not configured on the API server")
    if body.live:
        os.environ["ANTHROPIC_API_KEY"] = _REAL_API_KEY
    else:
        os.environ.pop("ANTHROPIC_API_KEY", None)
    return get_mode()


@app.get("/api/summary")
def summary():
    return get_portfolio_summary()


@app.get("/api/customers")
def customers():
    return get_all_customers()


@app.get("/api/customers/{cid}/360")
def customer_360(cid: int):
    data = get_customer_360(cid)
    if not data or not data.get("customer"):
        raise HTTPException(status_code=404, detail="Customer not found")
    return data


@app.get("/api/implementation/overview")
def implementation_overview():
    return get_implementation_overview()


@app.get("/api/audit")
def audit(limit: int = 100):
    return get_agent_runs(limit)


@app.get("/api/costs")
def costs():
    return get_cost_summary()


@app.get("/api/briefings")
def briefings(type: Optional[str] = None):
    return get_briefings(type)


@app.get("/api/actions/summary")
def actions_summary():
    return get_action_summary()


@app.get("/api/actions/{cid}")
def action_status(cid: int):
    return get_action_status(cid)


class ActionUpdate(BaseModel):
    status: str
    note: str = ""


@app.post("/api/actions/{cid}")
def update_action(cid: int, body: ActionUpdate):
    set_action_status(cid, body.status, body.note)
    return get_action_status(cid)


@app.get("/api/agents")
def agents():
    return [
        {
            "name": name,
            "description": AGENT_DESCRIPTIONS.get(name, ""),
            "model_tier": AGENT_MODEL_TIER.get(name, "sonnet"),
        }
        for name in AGENT_REGISTRY
    ]


class AgentRunRequest(BaseModel):
    agent_name: str
    customer_id: Optional[int] = None


@app.post("/api/agents/run")
def run_agent(req: AgentRunRequest):
    agent_name, customer_id = req.agent_name, req.customer_id
    if agent_name not in AGENT_REGISTRY:
        raise HTTPException(status_code=400, detail=f"Unknown agent: {agent_name}")
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
            context["prior_agent"] = prior["agent_name"]
            context["prior_output"] = prior["output_text"]
            context["prior_confidence"] = prior.get("confidence_score", 0.75)
            cid = customer_id
        else:
            if customer_id is None:
                raise HTTPException(status_code=400, detail="customer_id is required for this agent")
            context = build_customer_context(customer_id)
            cid = customer_id

        result = agent.run(context, customer_id=cid)
        run_id = save_agent_run(result)

        if agent_name in ("BriefingAgent", "VPChiefOfStaffAgent"):
            briefing_type = "CEO" if agent_name == "BriefingAgent" else "VP_CX"
            save_briefing(briefing_type, cid, result.output_text, run_id)

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
    except HTTPException:
        raise
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/runs/{run_id}/deck", response_class=HTMLResponse)
def run_deck(run_id: int):
    """Render any saved agent run as a branded slide deck.

    Structured output isn't persisted, so it is re-parsed from the saved
    output_text using the agent's own parser.
    """
    from backend.database import fetchone
    from dataclasses import asdict

    run = fetchone("SELECT * FROM agent_runs WHERE id = ?", (run_id,))
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    agent_name = run["agent_name"]
    if agent_name not in AGENT_REGISTRY:
        raise HTTPException(status_code=400, detail=f"Unknown agent: {agent_name}")

    cid = run.get("customer_id")
    if agent_name == "VPChiefOfStaffAgent" or cid is None:
        context = build_portfolio_context()
    else:
        context = build_customer_context(cid)

    agent = AGENT_REGISTRY[agent_name]()
    structured = agent.parse_structured(run["output_text"] or "", context)
    structured_dict = asdict(structured) if structured else {}

    if agent_name == "KickoffDeckAgent":
        return render_kickoff_deck(structured_dict, context)
    return render_generic_deck(agent_name, structured_dict, context)


@app.get("/api/customers/{customer_id}/kickoff-deck", response_class=HTMLResponse)
def kickoff_deck(customer_id: int, fresh: bool = False):
    """Render the customer's kickoff deck as branded HTML slides.

    Reuses the most recent saved KickoffDeckAgent run so the link opens
    instantly. When no run exists (or ?fresh=1), serves a branded loading
    page that triggers the generation from the browser and reloads when
    done — a live Claude call can take a minute, and a blank page would
    look broken.
    """
    from backend.database import fetchone
    from dataclasses import asdict

    context = build_customer_context(customer_id)
    agent = AGENT_REGISTRY["KickoffDeckAgent"]()

    if not fresh:
        prior = fetchone(
            """SELECT output_text FROM agent_runs
               WHERE agent_name = 'KickoffDeckAgent' AND customer_id = ?
               ORDER BY created_at DESC LIMIT 1""",
            (customer_id,),
        )
        if prior and prior.get("output_text"):
            structured = agent.parse_structured(prior["output_text"], context)
            return render_kickoff_deck(asdict(structured) if structured else {}, context)

    live = bool(os.environ.get("ANTHROPIC_API_KEY"))
    return render_deck_loading(context.get("customer_name", "Customer"), customer_id, live)


@app.get("/api/csm/overview")
def csm_overview():
    """Per-CSM aggregates mirroring the Streamlit CSM Performance page."""
    customers = get_all_customers()
    today = datetime.now().date()
    esc_counts = {row["customer_id"]: row["n"] for row in fetchall(
        "SELECT customer_id, COUNT(*) AS n FROM escalations WHERE status != 'Resolved' GROUP BY customer_id"
    )}
    csm_stats = {}
    for c in customers:
        owner = c.get("csm_owner", "Unassigned")
        s = csm_stats.setdefault(owner, {
            "csm": owner,
            "accounts": 0, "arr": 0, "health_sum": 0, "high": 0, "med": 0, "low": 0,
            "expansion": 0, "renewals_90": 0, "nrr_sum": 0,
            "arr_risk": 0, "qbr_overdue": 0, "champ_gap": 0, "escalations": 0,
            "at_risk_n": 0, "actioned": 0,
        })
        s["accounts"] += 1
        s["arr"] += c["arr"]
        s["health_sum"] += c["health_score"]
        s["nrr_sum"] += c.get("nrr_pct", 0) or 0
        s["expansion"] += c.get("expansion_pipeline_arr", 0) or 0
        s[{"High": "high", "Medium": "med", "Low": "low"}.get(c["risk_level"], "low")] += 1
        s["escalations"] += esc_counts.get(c["id"], 0)
        if c["risk_level"] == "High":
            s["arr_risk"] += c["arr"]
        if c.get("qbr_completion") == "Overdue":
            s["qbr_overdue"] += 1
        if c.get("champion_status") in ("Disengaged", "Left Company"):
            s["champ_gap"] += 1
        if c["risk_level"] in ("High", "Medium"):
            s["at_risk_n"] += 1
            if get_action_status(c["id"]).get("status") in ("In Progress", "Done"):
                s["actioned"] += 1
        try:
            d = (datetime.strptime(c["renewal_date"], "%Y-%m-%d").date() - today).days
            if 0 <= d <= 90:
                s["renewals_90"] += 1
        except Exception:
            pass

    out = []
    for owner, s in csm_stats.items():
        s["avg_health"] = round(s["health_sum"] / s["accounts"], 1) if s["accounts"] else 0
        s["avg_nrr"] = round(s["nrr_sum"] / s["accounts"], 1) if s["accounts"] else 0
        out.append(s)
    out.sort(key=lambda s: -s["avg_health"])
    return {
        "csms": out,
        "team": {
            "managers":      len(out),
            "accounts":      sum(s["accounts"] for s in out),
            "total_arr":     sum(s["arr"] for s in out),
            "arr_risk":      sum(s["arr_risk"] for s in out),
            "at_risk_n":     sum(s["at_risk_n"] for s in out),
            "actioned":      sum(s["actioned"] for s in out),
            "qbr_overdue":   sum(s["qbr_overdue"] for s in out),
        },
    }
