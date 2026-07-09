# Linx CX Agent OS — FastAPI + Next.js Port

A production-feel port of the Streamlit dashboard (`frontend/app.py`) to a
FastAPI JSON API (`api/`) and a Next.js 14 App Router + Tailwind frontend
(`web/`). The existing `backend/`, `agents/`, `data/` and `frontend/` code is
untouched and used read-only.

## Run it

Two processes, from the repo root:

```bash
# 1. API (port 8000) — auto-seeds data/cx_agent_os.db on first start
pip install -r api/requirements.txt
uvicorn api.main:app --port 8000

# 2. Web (port 3000)
cd web
npm install
npm run dev
```

Open http://localhost:3000. The Next.js dev server rewrites `/api/*` to
`http://localhost:8000/api/*` (see `web/next.config.js`), so there are no CORS
issues in the browser; the API also allows `http://localhost:3000` via CORS.

Agents run in **mock mode** when `ANTHROPIC_API_KEY` is unset — set it in the
environment of the uvicorn process to make live Claude calls.

## Architecture

```
api/main.py            FastAPI app — thin JSON layer over backend/crud.py,
                       backend/context_builder.py and agents/agents.py.
                       Replicates the Streamlit call_agent flow (portfolio
                       context for VPChiefOfStaffAgent, prior-run injection for
                       SkeptikQAAgent, save_agent_run + save_briefing).
                       Adds /api/csm/overview which computes per-CSM aggregates
                       server-side (mirrors the Streamlit CSM Performance page).

web/
  app/layout.tsx       Sidebar shell (Monitor / Deliver / Govern nav), Inter font,
                       Linx brand gradient background.
  app/page.tsx         Executive Dashboard — AI summary band, 5 KPIs, at-risk +
                       expansion columns linking to customer 360s.
  app/customers/       Searchable portfolio table → /customers/[id] 360 view
                       (Overview / AI Agents / Usage & Health / Implementation /
                       Support / People / Renewal tabs, action-status logger,
                       inline-SVG 30-day health chart).
  app/implementation/  KPI strip, weekly priorities, risk-sorted project table,
                       deep-dive + on-demand AI analysis.
  app/csm/             Team KPIs + per-CSM performance cards with coaching insight.
  app/briefings/       CEO briefing (+ Skeptik side-by-side review), VP weekly
                       review, history.
  app/console/         Free-form agent runner with model-routing card.
  app/audit/           Spend KPIs, spend-by-model table, expandable run history.
  components/          Sidebar, AgentReport (react-markdown, executive-document
                       styling with LINX watermark + meta pills), ui.tsx
                       (Card, KpiCard, Pill, ProgressBar, SectionLabel, TabBar…).
  lib/api.ts           fetch helpers, shared types, brand color/format helpers,
                       implementation next-action heuristic.
```

### API endpoints

| Method | Path | Backed by |
| --- | --- | --- |
| GET | `/api/summary` | `get_portfolio_summary()` |
| GET | `/api/customers` | `get_all_customers()` |
| GET | `/api/customers/{cid}/360` | `get_customer_360(cid)` |
| GET | `/api/implementation/overview` | `get_implementation_overview()` |
| GET | `/api/audit?limit=100` | `get_agent_runs(limit)` |
| GET | `/api/costs` | `get_cost_summary()` |
| GET | `/api/briefings?type=CEO\|VP_CX` | `get_briefings(type)` |
| GET | `/api/actions/summary` | `get_action_summary()` |
| GET / POST | `/api/actions/{cid}` | `get_action_status` / `set_action_status` |
| GET | `/api/agents` | `AGENT_REGISTRY` + descriptions + model tiers |
| POST | `/api/agents/run` | full agent execution flow (run, persist, brief) |
| GET | `/api/csm/overview` | per-CSM aggregates (server-side) |
