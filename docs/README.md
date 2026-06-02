# VP CX Agent OS — Onyx Security

A lightweight executive demo platform showing how AI agents can run a post-sale customer organization.

## Quick Start

```bash
# 1. Install and seed data
bash setup.sh

# 2. Start both servers
bash start.sh

# App: http://localhost:8501
# API: http://localhost:8000/docs
```

## Optional: Live Claude Responses

```bash
export ANTHROPIC_API_KEY=your_key_here
bash start.sh
```

Without a key, the app runs in **mock mode** with realistic pre-written outputs.

## Architecture

```
frontend/app.py          Streamlit UI (5 pages)
backend/main.py          FastAPI REST API
backend/crud.py          Database queries
backend/context_builder  Builds agent input context from DB
agents/agents.py         6 CX agents
agents/base_agent.py     Execution, cost tracking, mock mode
agents/model_router.py   Haiku / Sonnet / Opus routing logic
prompts/templates.py     All agent system + user prompts
data/synthetic_data.py   25-customer dataset generation
data/cx_agent_os.db      SQLite database (auto-created)
```

## The 6 Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| CustomerHealthAgent | Haiku | Scoring, risk signals, recommendations |
| ImplementationAgent | Sonnet | Milestone status, blockers, recovery plan |
| BriefingAgent | Sonnet | CEO-ready executive briefings |
| EscalationCommanderAgent | Opus | Critical escalation battle plans |
| SkeptikQAAgent | Opus | Adversarial QA on prior agent outputs |
| VPChiefOfStaffAgent | Sonnet | Weekly portfolio review |

## Model Routing Logic

- **Haiku** → High-volume extraction, scoring, classification
- **Sonnet** → Synthesis, planning, executive writing  
- **Opus** → Escalations, QA, high-stakes judgment

## Demo Flow

1. Open **Portfolio Dashboard** → see 3 critical, 7 at-risk accounts
2. Click **JetStream Airlines** or **Acme Corp** (high-risk)
3. Open **Customer 360** → review health, tickets, escalations
4. Click **CEO Briefing** → see Sonnet-generated executive brief
5. Click **Escalation Commander** → see Opus battle plan
6. Navigate to **Briefings** → Generate Weekly VP CX Review
7. Open **Audit Trail & Costs** → see full model routing history
