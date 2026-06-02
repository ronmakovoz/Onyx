"""
Base agent class. All agents inherit from this.
Handles Claude API calls, mock mode, cost tracking, and audit logging.
"""

import os
import json
import random
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

from agents.model_router import route, RoutingDecision


@dataclass
class AgentResult:
    agent_name: str
    customer_id: Optional[int]
    model_used: str
    model_rationale: str
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float
    confidence_score: float
    output_text: str
    created_at: str
    is_mock: bool = False


def _call_claude(model_id: str, system: str, user: str) -> tuple[str, int, int]:
    """Returns (text, input_tokens, output_tokens)."""
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    msg = client.messages.create(
        model=model_id,
        max_tokens=2048,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return msg.content[0].text, msg.usage.input_tokens, msg.usage.output_tokens


def _mock_response(agent_name: str, context: dict) -> tuple[str, int, int]:
    """Returns realistic-looking mock output when no API key is set."""
    customer_name = context.get("customer_name", "the customer")
    mock_outputs = {
        "CustomerHealthAgent": f"""## Health Assessment: {customer_name}

**Overall Health Score:** {context.get('health_score', 'N/A')}/100
**Risk Level:** {context.get('risk_label', 'Unknown')}

### Key Risk Signals
- Adoption score trending below industry benchmark (adoption: {context.get('adoption_score', 'N/A')})
- Champion engagement: {context.get('champion_status', 'Unknown')}
- Open escalations require immediate attention
- Renewal in {context.get('renewal_days', '?')} days with current sentiment: {context.get('sentiment', 'Unknown')}

### Recommended Actions
1. Schedule executive sponsor call within 5 business days
2. Assign dedicated CSM for weekly touchpoints
3. Escalate open P1 tickets to engineering leadership
4. Prepare ROI report to justify renewal conversation

**Confidence:** High — based on 90 days of engagement signals""",

        "ImplementationAgent": f"""## Implementation Status: {customer_name}

**Status:** {context.get('onboarding_status', 'Unknown')}
**Completion:** {context.get('impl_progress', '?')}% of milestones complete

### Completed Milestones
- Kickoff & scoping ✓
- Technical discovery ✓
- Environment provisioning ✓

### In Progress
- SSO / IdP integration — blocked on customer IT access
- Policy configuration — 60% complete

### Blockers
1. **IT Access Delay** — Customer IT team hasn't provisioned service account (14 days outstanding)
2. **Scope Creep** — 3 new use cases added post-kickoff, not in original SOW

### Recommended Next Steps
- Escalate IT blocker to {context.get('champion_name', 'champion')} by EOD Friday
- Schedule SOW amendment discussion with account executive
- Project completion re-forecast: +3 weeks from original go-live""",

        "BriefingAgent": f"""# CEO Briefing: {customer_name}
*Prepared by Onyx CX Agent OS — {datetime.now().strftime('%B %d, %Y')}*

---

## Situation
{customer_name} ({context.get('industry', 'Enterprise')}, ${context.get('arr', 0):,} ARR) is approaching renewal in **{context.get('renewal_days', '?')} days** with a health score of **{context.get('health_score', 'N/A')}/100**. The account presents elevated churn risk driven by implementation delays, {context.get('open_tickets', 0)} open support tickets, and a champion who recently {context.get('champion_status', 'changed roles').lower()}.

## Business Risk
The ARR at risk is **${context.get('arr', 0):,}**. Intelligence gathered over the last 90 days indicates declining platform adoption, executive disengagement, and a competitor POC currently underway. If the renewal is lost, this represents a significant reduction in our {context.get('industry', 'sector')} segment revenue and a referenceable customer.

## Recommended Executive Actions
1. **CEO-to-CEO Call** — Request a 30-minute call with their CEO to demonstrate Onyx's executive commitment and hear strategic concerns directly.
2. **Dedicated SWAT Team** — Assign an implementation engineer and senior CSM exclusively to this account for the next 30 days.
3. **Commercial Flexibility** — Authorize the AE to offer a 90-day extension with performance SLAs to de-risk the renewal conversation.

## What Success Looks Like
Within 30 days: all P1 tickets resolved, implementation back on track, executive sponsor re-engaged, renewal signed or extended.""",

        "EscalationCommanderAgent": f"""# Escalation War Room: {customer_name}
*Escalation Commander — {datetime.now().strftime('%B %d, %Y')}*

---

## Threat Assessment
**Severity: CRITICAL** | ARR at Risk: ${context.get('arr', 0):,} | Days to Renewal: {context.get('renewal_days', '?')}

This account is in active churn risk. Multiple converging failure signals demand immediate coordinated response across CS, Engineering, and Executive teams.

## Active Escalations
{context.get('escalation_summary') or '- Implementation 6 weeks behind schedule'}

## Battle Plan

### Hour 0–24: Stabilize
- [ ] VP CS to call economic buyer and acknowledge situation directly
- [ ] Engineering on-call to own all open P1 tickets personally
- [ ] Pause any non-critical communications to avoid noise

### Day 2–7: Demonstrate Progress
- [ ] Daily written status update from Onyx to customer exec team
- [ ] Resolve top 2 open tickets with root-cause documentation
- [ ] Schedule executive alignment call with both CEOs

### Day 7–30: Rebuild Trust
- [ ] Implementation blitz sprint — assign two additional engineers
- [ ] Co-create success plan with customer champion
- [ ] Prepare renewal business case with measured ROI

## Owner Assignments
| Action | Owner | Due |
|--------|-------|-----|
| Executive sponsor call | VP Customer Experience | 24 hours |
| P1 ticket resolution | Engineering Lead | 48 hours |
| Implementation recovery plan | Implementation Manager | 72 hours |
| Commercial terms discussion | Account Executive | 1 week |

## Risk If No Action
Estimated churn probability: **{round(context.get('renewal_risk', 0.7) * 100)}%**
Projected impact: Full ARR loss + negative reference potential""",

        "SkeptikQAAgent": f"""## QA Review — Skeptic Analysis

### What the Previous Agent Got Right
The assessment correctly identifies {customer_name}'s core risk signals: declining adoption, champion instability, and implementation delays. The recommended actions are reasonable and actionable.

### What I'd Push Back On
1. **Confidence may be overstated.** We have only {random.randint(3,8)} data points on sentiment — not enough for high-confidence trend analysis. I'd rate confidence as *Medium*, not High.
2. **Missing competitive context.** The briefing doesn't acknowledge the competitor POC. This is material and the CEO needs to know it explicitly.
3. **Timeline is optimistic.** Resolving P1 tickets in 48 hours assumes Engineering availability. Current sprint is full — this needs explicit resource allocation.
4. **Champion 'left the company' ≠ dead account.** We should identify who replaced them and whether they're warm or cold. The new contact may actually be a better champion.

### Revised Confidence Score: 0.71

### Suggested Additions
- Add competitive displacement risk explicitly
- Clarify engineering resource plan before committing to 48-hour SLA
- Map new stakeholder as potential champion or detractor""",

        "VPChiefOfStaffAgent": f"""# Weekly VP CX Review
*Week of {datetime.now().strftime('%B %d, %Y')} — Onyx Security*

---

## Portfolio Health Summary
| Status | Count | ARR |
|--------|-------|-----|
| 🔴 Critical | {context.get('critical_count', 3)} | ${context.get('critical_arr', 0):,} |
| 🟡 At Risk | {context.get('at_risk_count', 7)} | ${context.get('at_risk_arr', 0):,} |
| 🟢 Healthy | {context.get('healthy_count', 15)} | ${context.get('healthy_arr', 0):,} |

**Total Portfolio ARR:** ${context.get('total_arr', 0):,}
**ARR at Risk (Critical + At Risk):** ${context.get('arr_at_risk', 0):,} ({context.get('risk_pct', '?')}% of portfolio)

---

## This Week's Critical Actions
1. **JetStream Airlines** — CEO call required this week. Implementation 6 weeks behind, competitor POC active. Own it personally.
2. **LuminaCare Medical** — P1 ticket open 7 days. Engineering escalation required. Involves PHI — legal awareness needed.
3. **RedRock Mining** — Champion left. Identify new contact by EOD Friday. Do not let this go dark.

## Renewal Pipeline (Next 90 Days)
{context.get('renewal_pipeline', '5 renewals totaling $2.1M ARR due within 90 days. 3 are at-risk.')}

## What's Working
- ZenithAero Systems: Completed full rollout 2 weeks early. Strong NPS. Expansion conversation started.
- DataVault Analytics: QBR delivered, champion is a net promoter. Reference call agreed.
- WestCoast Pharma: GxP compliance milestone hit — significant customer milestone.

## Risks for VP Awareness
- Engineering backlog: 14 open P1/P2 tickets across the portfolio. Bandwidth constraint emerging.
- Onboarding velocity: 3 new customers stuck in provisioning > 2 weeks. Process review needed.

## Recommended VP Actions This Week
1. Personally call JetStream Airlines VP of IT — today
2. Unblock engineering resources for LuminaCare and Acme
3. Review commercial flexibility options for 3 at-risk renewals with CFO
4. Recognize ZenithAero win with the team publicly

---
*Generated by VP Chief of Staff Agent | Model: Sonnet | Confidence: 0.88*"""
    }

    text = mock_outputs.get(agent_name, f"[Mock output for {agent_name} — set ANTHROPIC_API_KEY for real responses]")
    input_tokens = random.randint(800, 2500)
    output_tokens = random.randint(400, 1200)
    return text, input_tokens, output_tokens


class BaseAgent:
    name: str = "BaseAgent"

    def build_prompt(self, context: dict) -> tuple[str, str]:
        raise NotImplementedError

    def run(self, context: dict, customer_id: Optional[int] = None) -> AgentResult:
        routing: RoutingDecision = route(self.name)
        system_prompt, user_prompt = self.build_prompt(context)

        use_mock = not os.environ.get("ANTHROPIC_API_KEY")

        if use_mock:
            output_text, input_tokens, output_tokens = _mock_response(self.name, context)
        else:
            try:
                output_text, input_tokens, output_tokens = _call_claude(
                    routing.model_id, system_prompt, user_prompt
                )
            except Exception as e:
                output_text = f"[API Error: {e}]\n\n" + _mock_response(self.name, context)[0]
                input_tokens, output_tokens = 1000, 500

        cost = routing.estimate_cost(input_tokens, output_tokens)
        confidence = self._estimate_confidence(context)

        return AgentResult(
            agent_name=self.name,
            customer_id=customer_id,
            model_used=routing.model_id,
            model_rationale=routing.rationale,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            estimated_cost_usd=cost,
            confidence_score=confidence,
            output_text=output_text,
            created_at=datetime.now().isoformat(),
            is_mock=use_mock,
        )

    def _estimate_confidence(self, context: dict) -> float:
        base = 0.85
        if context.get("health_score", 100) < 40:
            base -= 0.10
        if context.get("champion_status") in ("Left Company", "Disengaged"):
            base -= 0.08
        if not context.get("meeting_notes"):
            base -= 0.05
        return round(max(0.50, min(0.98, base + random.uniform(-0.05, 0.05))), 2)
