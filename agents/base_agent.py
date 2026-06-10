"""
Base agent class. All CX agents inherit from this.
Handles: Claude API calls, mock mode fallback, cost tracking, structured output parsing.
"""

import os
import json
import random
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, Any

from agents.model_router import route, RoutingDecision


@dataclass
class AgentResult:
    agent_name: str
    customer_id: Optional[int]
    model_used: str
    model_display: str
    model_rationale: str
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float
    confidence_score: float
    output_text: str           # full markdown output
    structured: Optional[Any]  # typed output dataclass
    created_at: str
    is_mock: bool = False

    def to_dict(self):
        d = {k: v for k, v in self.__dict__.items() if k != "structured"}
        if self.structured:
            try:
                d["structured"] = asdict(self.structured)
            except Exception:
                d["structured"] = str(self.structured)
        return d


def _call_claude(model_id: str, system: str, user: str) -> tuple[str, int, int]:
    """Returns (response_text, input_tokens, output_tokens)."""
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    msg = client.messages.create(
        model=model_id,
        max_tokens=3000,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return msg.content[0].text, msg.usage.input_tokens, msg.usage.output_tokens


# ── Mock outputs ──────────────────────────────────────────────────────────────

def _mock_health(ctx):
    name = ctx.get("customer_name", "Customer")
    hs   = ctx.get("health_score", 55)
    risk = ctx.get("risk_label", ctx.get("risk_level", "Medium"))
    color = "🔴" if risk == "High" else "🟡" if risk == "Medium" else "🟢"
    return f"""## Customer Health Assessment — {name}
{color} **Risk Level: {risk}** · Health Score: **{hs}/100** · Trend: {ctx.get('health_trend','Unknown')}

---

### Top Risk Drivers
1. **{ctx.get('primary_risk_reason', 'Multiple converging risk signals detected')}**
2. Champion status: **{ctx.get('champion_status','Unknown')}** — relationship continuity at risk
3. Adoption score **{ctx.get('adoption_score',0)}/100** — below threshold for renewal confidence
4. {ctx.get('open_tickets',0)} open support tickets ({ctx.get('open_escalations',0)} escalations active)
5. Renewal in **{ctx.get('renewal_days','?')} days** with current renewal risk score **{ctx.get('renewal_risk',0):.0%}**

### Positive Signals
- Industry: {ctx.get('industry','?')} — strong strategic fit for Onyx's core use case
- Security review status: {ctx.get('security_review_status','?')}
- CSM: {ctx.get('csm_owner','assigned')} is actively engaged

### Early Warning Signals
⚠️ Sentiment trending **{ctx.get('sentiment','Neutral')}** across last 3 meeting notes
⚠️ Adoption score gap: {max(0, 65 - ctx.get('adoption_score',0))} points below renewal-safe threshold
⚠️ Implementation status: **{ctx.get('impl_status','Unknown')}** — {ctx.get('days_behind',0)} days behind

### Recommended Next Actions
1. **[URGENT]** Schedule VP-level alignment call within 5 business days — {ctx.get('recommended_next_action','')}
2. Assign dedicated implementation engineer to unblock {ctx.get('impl_status','stalled')} milestones
3. Prepare evidence-based ROI report for renewal conversation
4. Map new champion candidate — current champion status: {ctx.get('champion_status','?')}
5. Escalate open P1 tickets to engineering leadership with SLA commitment

### Confidence Assessment
**Confidence: {ctx.get('_conf',0.75):.0%}** — Based on {ctx.get('open_tickets',0)} tickets, \
{ctx.get('open_escalations',0)} escalations, and {ctx.get('renewal_days','?')} days to renewal.
Signal quality: {'High' if ctx.get('open_tickets',0) > 2 else 'Medium'} — \
{'multiple corroborating data points' if ctx.get('open_escalations',0) > 0 else 'limited escalation history reduces certainty'}"""


def _mock_implementation(ctx):
    name    = ctx.get("customer_name", "Customer")
    pct     = ctx.get("impl_progress", 50)
    status  = ctx.get("impl_status", "In Progress")
    behind  = ctx.get("days_behind", 0)
    conf    = "Low" if behind > 30 else "Medium" if behind > 7 else "High"
    primary = ctx.get("primary_risk_reason", "No major blockers")
    impl_owner = ctx.get("implementation_owner", "Impl Manager")
    csm     = ctx.get("csm_owner", "CSM")
    sec_rev = ctx.get("security_review_status", "Unknown")
    champ   = ctx.get("champion_status", "Active")
    milestones_txt = ctx.get("milestones", "- Kickoff & Scoping\n- Technical Discovery")

    schedule_note = f"⚠️ {behind} days behind schedule" if behind > 0 else "✅ On schedule"
    conf_note = ("Risk factors present: scope creep, stakeholder availability, and technical blockers are converging."
                 if conf != "High" else "Project is tracking well. No critical blockers identified.")
    blocker_1 = (f"1. **{primary}**" if ctx.get("open_escalations", 0) > 0
                 else "1. Minor configuration items pending customer IT team")
    golive_note = (f"delay of {behind} days." if behind > 0 else "on original schedule.")
    exec_note = ("Immediate executive intervention is recommended to avoid further slippage."
                 if behind > 21 else "Active monitoring and weekly syncs are sufficient.")
    intervention = ("🚨 **Escalate to VP level** — implementation recovery plan required within 72 hours"
                    if behind > 30 else "📋 Weekly status report with milestone owner accountability is sufficient")

    return f"""## Implementation Status — {name}
**Status: {status}** · **{pct}% Complete** · {schedule_note}

---

### Launch Confidence: {conf}
{conf_note}

### Completed Milestones ✅
{milestones_txt}

### Active Blockers
{blocker_1}
2. Security review: **{sec_rev}** — pathway to sign-off needs owner
3. Champion {champ} — stakeholder sign-off may be delayed

### Owner Action Plan
| Action | Owner | Due |
|--------|-------|-----|
| Unblock IT service account | {impl_owner} | 48 hours |
| Security review escalation | {csm} | 72 hours |
| SOW amendment (if scope changed) | Account Executive | 1 week |
| Champion replacement identification | {csm} | 1 week |

### Executive Summary
{name} is currently **{pct}% through implementation** with a projected go-live {golive_note}
The primary blocker is {primary}. {exec_note}

### Recommended Intervention
{intervention}"""


def _mock_briefing(ctx):
    name = ctx.get("customer_name", "Customer")
    arr  = ctx.get("arr", 0)
    days = ctx.get("renewal_days", "?")
    hs   = ctx.get("health_score", 55)
    return f"""# CEO Briefing — {name}
*Prepared by Onyx CX Agent OS · {datetime.now().strftime('%B %d, %Y')} · Confidential*

---

## Situation
{name} ({ctx.get('industry','Enterprise')}, **${arr:,} ARR**) renews in **{days} days**. \
Health score is **{hs}/100** with a **{ctx.get('health_trend','Declining')}** trend. \
The account has **{ctx.get('open_escalations',0)} active escalations** and \
**{ctx.get('open_tickets',0)} open support tickets**. \
Champion is **{ctx.get('champion_status','Unknown')}**. \
Sentiment across recent meetings is **{ctx.get('sentiment','Neutral')}**.

## Business Risk
**ARR at risk: ${arr:,}.** Renewal probability is estimated at \
{100 - int(ctx.get('renewal_risk',0.5)*100)}% based on current signals. \
{ctx.get('primary_risk_reason','Multiple risk factors present.')} \
A lost renewal in {ctx.get('industry','this sector')} reduces our reference base and creates a \
competitive precedent. If {name} churns, expect the competitor who ran a POC to publicize it.

## Business Outcomes Achieved
- Platform deployed across {ctx.get('adoption_score',0)}% of target user base
- Security review status: {ctx.get('security_review_status','In Progress')}
- Implementation: {ctx.get('impl_status','In Progress')} ({ctx.get('impl_progress',0)}% complete)

## Key Asks
1. Authorize 90-day contract extension with performance SLA to de-risk renewal
2. CEO-to-CEO call to demonstrate Onyx's executive commitment
3. Unblock engineering resources for {ctx.get('open_tickets',0)} open P1/P2 tickets

## Recommended Executive Action
**{ctx.get('recommended_next_action','Schedule executive alignment call this week.')}** \
Assign a dedicated SWAT team (1 senior CSM + 1 implementation engineer) to this account for 30 days. \
The cost of retention is a fraction of replacement CAC.

## 30 / 60 / 90 Day Plan
- **30 days:** Resolve all P1 tickets. Re-engage executive sponsor. Deliver ROI report.
- **60 days:** Implementation complete. New champion identified and onboarded. Renewal terms agreed.
- **90 days:** Renewal signed. Expansion conversation initiated. Reference call scheduled.

---
*Evidence base: {ctx.get('open_tickets',0)} tickets · {ctx.get('open_escalations',0)} escalations · \
{days} days to renewal · health score {hs}/100*"""


def _mock_escalation(ctx):
    name = ctx.get("customer_name", "Customer")
    arr  = ctx.get("arr", 0)
    return f"""# Escalation War Room — {name}
*Escalation Commander · {datetime.now().strftime('%B %d, %Y, %H:%M')} · CONFIDENTIAL*

---

## 🚨 Severity: CRITICAL
**ARR at Risk: ${arr:,}** · Days to Renewal: {ctx.get('renewal_days','?')} · Health: {ctx.get('health_score',0)}/100

## Situation Summary
{name} is in active churn risk. {ctx.get('primary_risk_reason','Multiple converging failure signals.')} \
The account shows {ctx.get('open_escalations',0)} active escalations, \
{ctx.get('open_tickets',0)} open support tickets, and a champion who is **{ctx.get('champion_status','Unknown')}**. \
Sentiment is **{ctx.get('sentiment','Negative')}**. Implementation is **{ctx.get('impl_status','Unknown')}**, \
{ctx.get('days_behind',0)} days behind schedule. This is not a single-issue problem — it is a systemic failure.

## Likely Root Cause
Primary: **{ctx.get('primary_risk_reason','Execution gap compounded by relationship breakdown')}**
Contributing: champion departure removed internal advocacy; implementation delays eroded trust; \
P1 ticket backlog demonstrates ongoing product reliability concerns.

## Customer Impact
Customer's AI agent governance and runtime protection are partially dependent on Onyx. Delays and outages are creating \
measurable operational risk for their team. Their CISO is aware and losing patience. \
A competitor has already run a POC, suggesting active evaluation is underway.

## Internal Owner Map
| Role | Owner | Accountability |
|------|-------|---------------|
| Executive Sponsor | VP Customer Experience | Own the relationship — call CEO within 24h |
| Technical Rescue | Engineering Lead | P1 ticket resolution within 48h |
| Commercial | Account Executive | Renewal terms + flexibility authorization |
| Implementation | {ctx.get('implementation_owner','Impl Manager')} | Recovery plan within 72h |
| CSM | {ctx.get('csm_owner','CSM')} | Daily written updates to customer |

## Recovery Plan — Next 48 Hours
- [ ] VP CX calls economic buyer directly — acknowledge the situation, do not minimize
- [ ] Engineering on-call owns every open P1 ticket personally — no handoffs
- [ ] Freeze all non-critical communications to reduce noise
- [ ] Post internal war room Slack channel — #escalation-{name.lower().replace(' ','-')[:12]}
- [ ] Brief CEO and CRO — one paragraph, factual, include ARR figure

## Recovery Plan — Next 2 Weeks
- [ ] Daily written status update from Onyx PM to customer exec team
- [ ] Implementation blitz: assign 2 additional engineers for 2-week sprint
- [ ] Co-create joint success plan with customer — their language, their metrics
- [ ] Prepare renewal business case with measured ROI evidence
- [ ] CEO-to-CEO call — topic: strategic partnership, not incident management

## Executive Communication Draft
---
Subject: Personal note from [VP CX Name] — {name} partnership

[Customer Exec Name],

I'm writing personally because I take your experience with Onyx seriously, and I want to own \
our performance directly. We have not delivered the implementation quality or support responsiveness \
you should expect from us.

I've assigned our best team to your account, effective today. [Engineering Lead] personally owns \
your open issues. [Impl Manager] has a recovery plan ready to share in the next 24 hours.

I'd like 30 minutes with you this week. Not to explain — to listen, and to commit to specific \
outcomes with dates attached.

You have my direct line. I'll follow up within the hour.

[VP CX Name]
---

## Recommended Next Step (Do This First)
**{ctx.get('recommended_next_action','Schedule VP-to-VP call within 24 hours.')}** \
Without executive re-engagement, technical fixes alone will not save this renewal."""


def _mock_skeptik(ctx):
    prior = ctx.get("prior_agent", "Unknown Agent")
    orig_conf = ctx.get("prior_confidence", 0.80)
    revised_conf = max(0.45, orig_conf - random.uniform(0.08, 0.22))
    return f"""## Skeptik QA Review — {prior} Output
*Adversarial review by Skeptik QA Agent · {datetime.now().strftime('%B %d, %Y')}*

---

### Verdict: ⚠️ Approve with Edits
**Original confidence:** {orig_conf:.0%} → **Revised confidence: {revised_conf:.0%}**

---

### Unsupported Claims
1. The output asserts a specific churn probability without disclosing the model or data inputs used. \
Confidence percentages need explicit evidence backing in an executive document.
2. The "business outcomes achieved" section claims value delivery without citing specific metrics \
or comparing against baseline. This is assertion, not evidence.
3. Root cause analysis presents one explanation as definitive. The data supports at least two \
competing hypotheses — this should be flagged to the reader.

### Missing Evidence
- No comparison to cohort benchmarks (what does a healthy {ctx.get('industry','comparable')} customer look like?)
- Champion departure date not specified — material to understanding relationship gap duration
- No mention of competitive intelligence quality (is the POC rumor or confirmed?)
- Implementation delay attribution not established — customer-side vs Onyx-side blocker?

### Overconfident Conclusions
- "Full ARR loss + negative reference potential" is presented as certain. It is one scenario, \
not the only scenario. A partial renewal or pause is equally plausible.
- The 30/60/90-day plan assumes resource availability that has not been verified with Engineering.
- "CEO-to-CEO call" is recommended without knowing whether the customer CEO is engaged or whether \
this would escalate rather than de-escalate tension.

### Alternative Explanations
1. The customer may be using renewal pressure as a negotiating tactic, not genuinely at churn risk
2. Champion departure may have opened a path to a more senior and better-aligned sponsor
3. Low adoption could reflect a scope mismatch rather than product dissatisfaction

### Recommended Edits
1. Replace all confidence percentages with ranges and cite data sources explicitly
2. Add a "What we don't know" section — executives need to see uncertainty acknowledged
3. Reframe 30/60/90 plan as "if resources are allocated" not as fait accompli
4. Add competitive context: is the POC confirmed? What product gap did they name?
5. Remove the phrase "fraction of replacement CAC" — it's unquantified and sounds like sales talk

---
*Skeptik note: This output is usable with edits. The core risk diagnosis is directionally correct \
but the confidence is overstated given data gaps. Do not share the current version with the CEO.*"""


def _mock_vpcos(ctx):
    today = datetime.now().strftime("%B %d, %Y")
    total = ctx.get("total_arr", 0)
    at_risk = ctx.get("arr_at_risk", 0)
    return f"""# Weekly VP CX Operating Review
*Chief of Staff Agent · Week Ending {today} · Onyx Security — INTERNAL*

---

## Portfolio Health Summary
| Segment | Customers | ARR | Trend |
|---------|-----------|-----|-------|
| 🔴 High Risk | {ctx.get('critical_count',0)} | ${ctx.get('critical_arr',0):,} | Declining |
| 🟡 Medium Risk | {ctx.get('at_risk_count',0)} | ${ctx.get('at_risk_arr',0):,} | Mixed |
| 🟢 Healthy | {ctx.get('healthy_count',0)} | ${ctx.get('healthy_arr',0):,} | Stable/Improving |
| **Total** | **{ctx.get('total_customers',0)}** | **${total:,}** | |

**ARR at Risk (High + Medium):** ${at_risk:,} — {ctx.get('risk_pct',0):.1f}% of portfolio

---

## Top 5 Customer Risks (This Week)
{ctx.get('top_at_risk','No data')}

---

## Top 5 Executive Actions Required
1. **[VP CX — TODAY]** Personal call to JetStream Airlines economic buyer. \
Do not delegate. Competitor POC is active. ARR is $670,000.
2. **[VP CX + CRO — 48h]** Authorize commercial flexibility for 3 high-risk renewals. \
Combined ARR: $1.56M. Prepare terms options for CFO review.
3. **[VP Eng — 72h]** Engineering resource allocation for open P1 escalations. \
21 unresolved P1 tickets across portfolio is unsustainable. Name owners by EOD Wednesday.
4. **[VP CX — This week]** Identify champion replacements for 3 customers with departed champions. \
Dark accounts churn silently. This is the highest-probability churn signal in the portfolio.
5. **[VP Product — This week]** CNAPP discovery-source integration gap is now cited in 2 separate accounts as a churn signal. \
This needs a roadmap decision, not another "we're evaluating it" response.

---

## Renewals Watchlist (Next 90 Days)
{ctx.get('renewal_pipeline','No renewal data')}

---

## Implementation Bottlenecks
- 3 implementations stalled on customer-side IT provisioning delays (> 14 days each)
- Security review sign-off process is a recurring blocker — recommend creating a Fast Path for low-risk customers
- Scope creep in 2 active implementations — SOW amendments not initiated — AEs need to act now

## Product Feedback Themes (From Meeting Notes This Week)
1. **Discovery-source integration gaps (CNAPP/SASE)** — mentioned by 2 customers as blocking full value realization
2. **Guardian intervention fatigue** — false positive rate > 40% is being cited in renewal risk conversations
3. **Report export limitations** — 3 customers requested PDF compliance report improvements
4. **Mobile app performance** — 2 enterprise accounts with field security teams flagging this

## Support Burden Themes
- 21 open P1 tickets across the portfolio — concentration in Onboarding-stage customers
- Webhook and API reliability issues appear in 4 separate accounts — potential systemic issue
- Average P1 response time this week: estimated 19 hours against 4-hour SLA — Engineering must address

## Cross-Functional Asks
| Ask | For Team | Owner | Due |
|-----|----------|-------|-----|
| CNAPP discovery-source roadmap decision | Product | VP Product | 1 week |
| P1 ticket SLA enforcement | Engineering | VP Eng | 48 hours |
| Commercial flexibility approval | Finance | CFO | 72 hours |
| Fast Path security review process | Legal/Compliance | General Counsel | 2 weeks |
| Reference customer program launch | Marketing | VP Marketing | 1 month |

---

## CEO-Ready Summary (3 sentences)
**{ctx.get('risk_pct',0):.0f}% of portfolio ARR (${at_risk:,}) is at active risk this week, \
concentrated in {ctx.get('critical_count',0)} high-risk accounts requiring immediate executive attention.** \
The highest-priority actions are a personal VP CX call to JetStream Airlines today and engineering \
resource allocation for 21 open P1 tickets by Wednesday. \
Two product gaps — CNAPP discovery-source integration and Guardian false-positive fatigue — are now appearing in renewal risk conversations \
and require a roadmap decision from Product this week.

---
*Generated by VP Chief of Staff Agent | Model: Claude Opus 4.8 | {today}*"""


def _mock_expansion(ctx):
    name = ctx.get("customer_name", "Customer")
    arr  = ctx.get("arr", 0)
    pipe = ctx.get("expansion_pipeline_arr", 0) or int(arr * 0.2)
    modules = random.sample([
        "AI-SPM", "Runtime Protection", "Guardian Agent Pro",
        "LLM Routing & Cost Optimization", "MCP Supply-Chain Security", "AI ROI Analytics", "Shadow AI Discovery Plus",
    ], 3)
    return f"""# Expansion Opportunity — {name}
*Expansion Opportunity Agent · {datetime.now().strftime('%B %d, %Y')}*

## Expansion Thesis
{name} ({ctx.get('industry','Enterprise')}) is a **{ctx.get('health_trend','Stable')}** account with NRR at \
**{ctx.get('nrr_pct','?')}%** and adoption at **{ctx.get('adoption_score','?')}%**. The proven outcome — \
*{ctx.get('roi_outcome','measurable AI risk reduction')}* — creates a credible basis to expand governance into \
adjacent risk surfaces. Executive engagement is **{ctx.get('executive_engagement','Medium')}**.

## Recommended Modules
- {modules[0]}
- {modules[1]}
- {modules[2]}

## Projected ARR Uplift
**${pipe:,}** incremental ARR over the next two quarters (≈{int(pipe/max(arr,1)*100)}% of current ARR).

## Confidence
**{ 'High' if ctx.get('upsell_likelihood',0) >= 0.45 else 'Medium' if ctx.get('upsell_likelihood',0) >= 0.2 else 'Low' }** — based on upsell likelihood {ctx.get('upsell_likelihood',0)} and current adoption.

## Proof Points
- {ctx.get('roi_outcome','Documented ROI from initial deployment')}
- Adoption {ctx.get('adoption_score','?')}% with {ctx.get('usage_trend','steady')} usage trend
- NPS {ctx.get('nps','?')} — relationship supports a commercial conversation

## Recommended Play
1. Package the proven ROI into a one-page value brief for the economic buyer
2. Run a scoping workshop on {modules[0]} with the technical sponsor
3. Tie the expansion proposal to the upcoming renewal ({ctx.get('renewal_days','?')} days out)

## Best Timing
Initiate now; align the close with the renewal cycle to maximize commercial leverage."""


def _mock_qbr(ctx):
    name = ctx.get("customer_name", "Customer")
    return f"""# QBR Briefing — {name}
*QBR Preparation Agent · {datetime.now().strftime('%B %d, %Y')}*

## Executive Headline
{name} is a **{ctx.get('health_trend','Stable')}** account (health {ctx.get('health_score','?')}/100, NRR {ctx.get('nrr_pct','?')}%) with \
{'strong expansion potential' if ctx.get('expansion_pipeline_arr',0) else 'a focus on value reinforcement'}.

## Value Delivered
- {ctx.get('roi_outcome','Measurable risk reduction since last quarter')}
- Adoption reached {ctx.get('adoption_score','?')}% with {ctx.get('usage_trend','steady')} usage
- {ctx.get('open_escalations',0)} escalation(s) managed; {ctx.get('open_tickets',0)} open support items

## Adoption Summary
Utilization is **{ctx.get('utilization_pct','?')}%** across the deployed footprint. Usage trend is **{ctx.get('usage_trend','Steady')}**.

## Open Items
- Champion status: {ctx.get('champion_status','Active')} ({ctx.get('champion_name','?')}, {ctx.get('champion_title','?')})
- Executive engagement: {ctx.get('executive_engagement','Medium')}
- {ctx.get('primary_risk_reason','No major risks flagged')}

## Proposed Agenda
1. Business outcomes & ROI review
2. Adoption and usage deep-dive
3. Roadmap alignment and open items
4. Expansion opportunities
5. Renewal & commercial planning ({ctx.get('renewal_days','?')} days out)

## Expansion Talking Points
- Build on proven ROI to extend coverage to adjacent risk surfaces
- ${ctx.get('expansion_pipeline_arr',0):,} pipeline identified for this account

## Success Metrics
- NRR {ctx.get('nrr_pct','?')}% · NPS {ctx.get('nps','?')} · Adoption {ctx.get('adoption_score','?')}%"""


def _mock_successplan(ctx):
    name = ctx.get("customer_name", "Customer")
    csm  = ctx.get("csm_owner", "CSM")
    return f"""# Success Plan — {name}
*Success Plan Agent · {datetime.now().strftime('%B %d, %Y')}*

## Objective
Move {name} from **{ctx.get('risk_label','Medium')} risk** to a healthy, expanding account ahead of renewal in {ctx.get('renewal_days','?')} days.

## Current State
Health {ctx.get('health_score','?')}/100 ({ctx.get('health_trend','?')}), adoption {ctx.get('adoption_score','?')}%, NRR {ctx.get('nrr_pct','?')}%. \
Primary risk: {ctx.get('primary_risk_reason','adoption and engagement gaps')}.

## Target State
Health 70+, adoption above 65%, champion re-engaged, renewal secured with expansion attached.

## Workstreams
- **Relationship** (owner: {csm}): re-engage executive sponsor and confirm champion
- **Adoption** (owner: CSM + SE): drive feature activation and usage cadence
- **Support** (owner: Support Lead): clear {ctx.get('open_tickets',0)} open tickets and {ctx.get('open_escalations',0)} escalation(s)
- **Commercial** (owner: {csm}): align renewal and expansion proposal

## Milestones 30 / 60 / 90
- **30 days:** escalations resolved; executive alignment call held; ROI brief delivered
- **60 days:** adoption +15 pts; champion confirmed; renewal terms drafted
- **90 days:** renewal signed; expansion conversation initiated

## Success Metrics
- Health score, adoption %, NRR, open escalation count, renewal status

## Risks and Mitigations
- {ctx.get('primary_risk_reason','Engagement risk')} → weekly cadence with exec sponsor
- Champion change → identify and onboard a backup champion early"""


def _mock_kickoffdeck(ctx):
    name     = ctx.get("customer_name", "Customer")
    industry = ctx.get("industry", "Enterprise")
    champ    = ctx.get("champion_name", "Customer Champion")
    champ_t  = ctx.get("champion_title", "Security Lead")
    tech     = ctx.get("technical_sponsor", "Technical Sponsor")
    biz      = ctx.get("business_sponsor", "Business Sponsor")
    csm      = ctx.get("csm_owner", "Onyx CSM")
    impl     = ctx.get("implementation_owner", "Onyx Implementation Manager")
    golive   = ctx.get("go_live_target", "Not set")
    emp      = ctx.get("employee_count", "?")
    sec_rev  = ctx.get("security_review_status", "Not started")

    from datetime import timedelta
    start = datetime.now().date()
    def d(days): return (start + timedelta(days=days)).strftime("%b %d, %Y")

    track = [
        ("Foundation",  "Kickoff & Scoping",                       7,  impl),
        ("Foundation",  "Technical Discovery",                     14, tech),
        ("Foundation",  "Environment Provisioning",                21, f"{name} IT"),
        ("Integration", "SSO / Identity Provider Integration",     35, tech),
        ("Integration", "Initial Data Ingestion",                  42, impl),
        ("Pilot",       "Pilot Group Onboarding (25 users)",       56, champ),
        ("Pilot",       "Detection Policy Configuration",          63, impl),
        ("Validation",  "Integration Testing & QA",                77, impl),
        ("Validation",  "Security Review Sign-off",                84, tech),
        ("Launch",      "Full Production Rollout",                 98, impl),
        ("Launch",      "Hypercare Period (30 days)",              128, csm),
        ("Value",       "QBR #1 — 90-Day Review",                  180, csm),
    ]
    timeline_rows = "\n".join(
        f"| {phase} | {m} | {d(days)} | {owner} |" for phase, m, days, owner in track
    )

    return f"""# Implementation Kickoff — {name}
*Prepared by Onyx Security · {datetime.now().strftime('%B %d, %Y')} · Client-Facing*

---

## Welcome & Partnership Vision
Welcome to the Onyx Security partnership. Over the next 90–180 days we will give {name} full
visibility and control over AI activity across your {industry.lower()} environment ({emp} employees) —
from discovery of shadow AI to runtime protection in production. Success means your security team
sees every AI agent, governs every action, and proves measurable risk reduction by your first QBR.

## Engagement Team
| Role | Name | Responsibility |
|------|------|----------------|
| Onyx Implementation Manager | {impl} | Owns delivery plan, milestones, and weekly status |
| Onyx Customer Success Manager | {csm} | Owns long-term outcomes, adoption, and executive cadence |
| Onyx Solutions Engineer | Assigned at kickoff | Technical integration and policy configuration |
| Customer Champion | {champ} ({champ_t}) | Internal advocacy, pilot group coordination |
| Customer Technical Sponsor | {tech} | IT access, SSO/IdP admin, environment readiness |
| Customer Business Sponsor | {biz} | Executive checkpoints, success metric sign-off |

## Scope & Objectives
- Deploy the Onyx Secure AI Control Plane across {name}'s environment with full discovery coverage
- Establish a complete inventory of AI agents, models, and shadow AI applications
- Enable runtime protection (prompt injection, jailbreak, and data exfiltration blocking) for the pilot group, then production
- Configure detection policies aligned to {industry} compliance and risk requirements
- Reach Full Production Rollout {'by ' + str(golive) if golive not in (None, 'Not set') else 'within 98 days of kickoff'}

## Implementation Timeline
| Phase | Milestone | Target Date | Owner |
|-------|-----------|-------------|-------|
{timeline_rows}

## Success Metrics
- 100% of discovery sources connected and reporting by Day 42
- Shadow AI inventory baseline established with zero unknown agents at production rollout
- Pilot group (25 users) live with < 5% false-positive policy rate before production
- Security review signed off by Day 84 (current status: {sec_rev})
- Measurable risk findings presented at the 90-day QBR

## First 30 Days
1. **Day 1–7:** Kickoff session held; scope confirmed; weekly sync scheduled — Owner: {impl}
2. **Day 7–14:** Technical discovery complete; environment access granted — Owner: {tech}
3. **Day 14–21:** Onyx environment provisioned; service accounts created — Owner: {name} IT + Onyx SE
4. **Day 21–30:** SSO/IdP integration underway; pilot group of 25 users nominated — Owner: {champ}

## Communication & Governance
Weekly 30-minute delivery sync ({impl} + {tech}), biweekly executive checkpoint ({csm} + {biz}),
and a shared status dashboard updated every Friday. Escalation path: Implementation Manager →
CSM → Onyx VP Customer Experience, with a 24-hour response commitment on blockers.

## What We Need From You
- Named IT contact with admin access for environment provisioning (by Day 14)
- IdP administrator availability for SSO integration (Days 21–35)
- Pilot group of 25 users nominated by {champ} (by Day 30)
- Security review requirements and approver identified (by Day 45)
- Executive sponsor availability for biweekly checkpoints"""


def _mock_bull(ctx):
    name = ctx.get("customer_name", "Customer")
    arr  = ctx.get("arr", 0)
    hs   = ctx.get("health_score", 60)
    adp  = ctx.get("adoption_score", 55)
    nrr  = ctx.get("nrr_pct", 102)
    bull_prob = min(90, max(45, hs + 10))
    return f"""## Bull Case — {name}
**Renewal Probability (Bull): {bull_prob}%** · Confidence: **Medium**

---

### Why This Account Will Renew
1. **Health score {hs}/100** — while below ideal, the trend is stabilizing; the account has not broken below the 40-point critical threshold
2. **Adoption at {adp}%** — meaningful footprint deployed; switching costs are real and quantifiable
3. **NRR at {nrr}%** — the customer has expanded spending, signaling business value realized
4. **ARR of ${arr:,}** — the account is strategically significant to the customer's security program; rip-and-replace is operationally disruptive
5. **ROI outcome confirmed**: {ctx.get('roi_outcome','documented security value delivery')} — this is the strongest renewal anchor available

### Underappreciated Positive Signals
- Implementation completion creates switching-cost lock-in that bears ignore
- Industry: {ctx.get('industry','Enterprise')} — Onyx has deep reference customers in this vertical; peer validation matters
- Champion {ctx.get('champion_name','?')} has institutional knowledge; replacement cost for the customer is high
- Expansion pipeline of ${ctx.get('expansion_pipeline_arr',0):,} signals the customer is thinking forward, not exit

### Counter to Bear Risks
1. Open tickets ({ctx.get('open_tickets',0)}) are a service quality issue, not a platform rejection — resolvable pre-renewal
2. Health score decline is recoverable; every at-risk account Onyx has saved showed a dip followed by a recovery inflection
3. Champion status ({ctx.get('champion_status','Active')}) — even if strained, the operational dependency on the platform persists
4. Renewal risk score of {ctx.get('renewal_risk',0.4):.0%} incorporates noise; the underlying contract data says {100-int(ctx.get('renewal_risk',0.4)*100)}% probability of renewal

### Upside Scenario
If the {ctx.get('open_tickets',0)} open tickets are resolved in the next 30 days and a VP-level alignment call is held, confidence shifts to High. The expansion pipeline of ${ctx.get('expansion_pipeline_arr',0):,} becomes achievable in Q2 — pushing NRR to 115%+ for this account.

### Bull Case Confidence Rationale
**Confidence: {bull_prob}%** — Confidence is Medium rather than High because {ctx.get('renewal_days','?')} days to renewal leaves limited time for recovery. The positive signals are real but require active execution to convert."""


def _mock_bear(ctx):
    name = ctx.get("customer_name", "Customer")
    arr  = ctx.get("arr", 0)
    hs   = ctx.get("health_score", 60)
    adp  = ctx.get("adoption_score", 55)
    bear_prob = max(15, min(60, hs - 20))
    return f"""## Bear Case — {name}
**Renewal Probability (Bear): {bear_prob}%** · Confidence: **Medium**

---

### Why This Account Is At Risk
1. **Health score {hs}/100 with {ctx.get('health_trend','Declining')} trend** — the trajectory, not just the number, is the signal; a declining account with {ctx.get('renewal_days','?')} days to renewal rarely recovers without a forcing function
2. **{ctx.get('open_tickets',0)} open support tickets and {ctx.get('open_escalations',0)} active escalations** — unresolved technical debt erodes trust faster than any relationship effort can rebuild it
3. **Champion {ctx.get('champion_name','?')} status: {ctx.get('champion_status','Active')}** — internal advocacy is either compromised or absent; the deal has no internal owner pulling it forward
4. **Adoption at {adp}%** — below the 65% threshold historically associated with renewal; the customer has not achieved full platform dependency
5. **Renewal risk score {ctx.get('renewal_risk',0.4):.0%}** — Onyx's own scoring model flags this as elevated risk; that signal deserves weight

### Hidden or Underweighted Risks
- Sentiment is **{ctx.get('sentiment','Neutral')}** — neutral sentiment this close to renewal is effectively negative; enthusiastic customers don't churn, ambivalent ones do
- Executive engagement is **{ctx.get('executive_engagement','Medium')}** — without exec-level buy-in, the renewal is a procurement exercise vulnerable to competitive disruption
- Primary risk: **{ctx.get('primary_risk_reason','undefined')}** — this is systemic, not tactical
- No meeting notes or thin meeting notes signal CSM relationship has gone dark — dark accounts churn silently

### Counter to Bull Signals
1. NRR {ctx.get('nrr_pct',102)}% expansion happened before the current risk signals; historical spend doesn't predict future renewal under duress
2. Switching costs are real but overweighted by bulls — when trust breaks, procurement will absorb the switching cost rather than the reputational risk of renewing a failing vendor
3. ROI outcome ({ctx.get('roi_outcome','?')}) is unverified by the customer's economic buyer — if they don't believe it, it doesn't protect the renewal
4. Industry vertical strength is a portfolio argument, not an account-specific argument; this specific customer's experience is what matters

### Downside Scenario
If the open escalations are not resolved within 30 days and no executive re-engagement occurs, the customer initiates a formal evaluation. A competitor who has already run a POC converts within 90 days. Onyx loses ${arr:,} ARR and a reference customer in a key vertical.

### Bear Case Confidence Rationale
**Confidence: {bear_prob}%** — Confidence is Medium because {ctx.get('renewal_days','?')} days still provides a window for recovery. The bear case probability is not higher because the customer has not yet issued a formal cancellation notice or initiated a competitor POC that we know of."""


def _mock_synthesis(ctx):
    name = ctx.get("customer_name", "Customer")
    arr  = ctx.get("arr", 0)
    hs   = ctx.get("health_score", 60)
    risk = ctx.get("renewal_risk", 0.4)
    lo   = max(25, min(60, hs - 15))
    hi   = min(85, lo + 30)
    verdict = "Lean Renew" if hs >= 65 else "Lean Churn" if hs < 45 else "Toss-Up"
    return f"""## Synthesis — {name}
**Calibrated Renewal Probability: {lo}–{hi}%** (range reflects genuine uncertainty)
**Verdict: {verdict}**

---

### Strongest Bull Arguments (accepted)
1. **Switching cost lock-in** — adoption at {ctx.get('adoption_score',55)}% creates real operational dependency; evidence quality: Medium (adoption data is direct)
2. **Documented ROI** — {ctx.get('roi_outcome','security value delivered')} is an anchor the customer's economic buyer has seen; evidence quality: Medium (assumed but not externally verified)
3. **NRR expansion history** — prior expansion to {ctx.get('nrr_pct',102)}% signals the customer has placed value on the platform; evidence quality: High (financial record)

### Strongest Bear Arguments (accepted)
1. **{ctx.get('health_trend','Declining')} health trend into renewal window** — trajectory matters more than point-in-time score; evidence quality: High (objective metric)
2. **Champion status: {ctx.get('champion_status','Active')}** — eroded internal advocacy is the highest-correlation churn predictor in the portfolio; evidence quality: Medium-High
3. **{ctx.get('open_tickets',0)} unresolved support tickets** — operational frustration with no clear resolution ETA; evidence quality: High (ticket data)

### Arguments Rejected (from both sides)
- Bull: "Switching costs will deter exit" — overweighted; procurement absorbs switching cost when trust breaks
- Bull: "Industry vertical strength protects this account" — portfolio argument, not account-specific
- Bear: "NRR expansion is irrelevant" — prior expansion IS signal; it's a data point, not noise
- Bear: "Sentiment = negative" — neutral sentiment interpretation is speculative without meeting note detail

### Swing Factors
1. **Executive re-engagement in the next 21 days** — a VP-to-VP call that acknowledges the service quality gap changes the trajectory more than any technical fix
2. **Resolution of the {ctx.get('open_tickets',0)} open support tickets before renewal** — customers who renew with open tickets have a 3x higher churn rate in year 2
3. **Champion replacement or re-activation** — if the current champion ({ctx.get('champion_status','Active')}) cannot be the internal owner of the renewal, a new one must be identified and activated within 30 days

### Calibrated Probability Rationale
The {lo}–{hi}% range reflects two genuine scenarios: the high end assumes executive re-engagement and ticket resolution occur (achievable); the low end assumes the account continues to drift with no forcing function (equally plausible given current trajectory). A single point estimate would imply false precision given the data gaps.

### Recommended Play
**VP CX calls the economic buyer personally within 5 business days** — not to close the renewal, but to acknowledge the service quality gap, commit to a specific resolution timeline on the open tickets, and reframe the relationship as strategic. This single action is the highest-probability lever available."""



MOCK_DISPATCH = {
    "CustomerHealthAgent":     _mock_health,
    "ImplementationAgent":     _mock_implementation,
    "BriefingAgent":           _mock_briefing,
    "EscalationCommanderAgent":_mock_escalation,
    "SkeptikQAAgent":          _mock_skeptik,
    "VPChiefOfStaffAgent":     _mock_vpcos,
    "ExpansionOpportunityAgent": _mock_expansion,
    "QBRPreparationAgent":     _mock_qbr,
    "SuccessPlanAgent":        _mock_successplan,
    "KickoffDeckAgent":        _mock_kickoffdeck,
    "BullCaseAgent":           _mock_bull,
    "BearCaseAgent":           _mock_bear,
    "SynthesisAgent":          _mock_synthesis,
}


def _mock_response(agent_name: str, context: dict) -> tuple[str, int, int]:
    fn = MOCK_DISPATCH.get(agent_name, lambda ctx: f"[Mock output for {agent_name}]")
    text = fn(context)
    # Realistic token estimates by model tier
    from agents.model_router import AGENT_ROUTING
    tier = AGENT_ROUTING.get(agent_name, ("sonnet",))[0]
    input_tokens  = {"haiku": random.randint(600,1800), "sonnet": random.randint(900,2500), "opus": random.randint(1200,3500)}[tier]
    output_tokens = {"haiku": random.randint(300,700),  "sonnet": random.randint(500,1200), "opus": random.randint(800,2000)}[tier]
    return text, input_tokens, output_tokens


class BaseAgent:
    name: str = "BaseAgent"

    def build_prompt(self, context: dict) -> tuple[str, str]:
        raise NotImplementedError

    def parse_structured(self, text: str, context: dict):
        """Override in subclass to parse structured output from response text."""
        return None

    def run(self, context: dict, customer_id: Optional[int] = None) -> AgentResult:
        routing: RoutingDecision = route(self.name)
        system_prompt, user_prompt = self.build_prompt(context)

        use_mock = not os.environ.get("ANTHROPIC_API_KEY")

        if use_mock:
            context["_conf"] = self._estimate_confidence(context)
            output_text, input_tokens, output_tokens = _mock_response(self.name, context)
        else:
            try:
                output_text, input_tokens, output_tokens = _call_claude(
                    routing.model_id, system_prompt, user_prompt
                )
            except Exception as e:
                output_text = f"[API Error: {e}]\n\n"
                output_text += _mock_response(self.name, context)[0]
                input_tokens, output_tokens = 1000, 500

        cost       = routing.estimate_cost(input_tokens, output_tokens)
        confidence = self._estimate_confidence(context)
        structured = self.parse_structured(output_text, context)

        return AgentResult(
            agent_name=self.name,
            customer_id=customer_id,
            model_used=routing.model_id,
            model_display=routing.model_display,
            model_rationale=routing.rationale,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            estimated_cost_usd=round(cost, 6),
            confidence_score=confidence,
            output_text=output_text,
            structured=structured,
            created_at=datetime.now().isoformat(),
            is_mock=use_mock,
        )

    def _estimate_confidence(self, context: dict) -> float:
        score = 0.87
        if context.get("health_score", 100) < 35:
            score -= 0.10
        if context.get("champion_status") in ("Left Company", "Disengaged"):
            score -= 0.08
        if not context.get("meeting_notes") or context.get("meeting_notes") == "No recent meeting notes":
            score -= 0.06
        if context.get("open_escalations", 0) > 2:
            score -= 0.04
        if context.get("open_tickets", 0) == 0:
            score -= 0.03  # low data volume
        return round(max(0.42, min(0.97, score + random.uniform(-0.04, 0.04))), 2)
