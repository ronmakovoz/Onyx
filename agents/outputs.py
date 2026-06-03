"""
Structured output models for all agents.
Each agent returns a typed dataclass alongside the raw markdown text.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class HealthOutput:
    health_score: int                    # 0–100
    risk_level: str                      # Low / Medium / High / Critical
    top_risk_drivers: List[str]          # up to 5 items
    positive_signals: List[str]          # up to 4 items
    early_warning_signals: List[str]     # up to 4 items
    recommended_actions: List[str]       # prioritised, up to 5
    confidence_score: float              # 0.0–1.0
    confidence_rationale: str


@dataclass
class ImplementationOutput:
    overall_status: str                  # On Track / Slight Delay / Behind Schedule / Stalled / At Risk
    pct_complete: int                    # 0–100
    launch_confidence: str              # High / Medium / Low / Very Low
    launch_confidence_rationale: str
    delayed_milestones: List[str]
    active_blockers: List[str]
    owner_action_plan: List[str]         # "Owner: action by date"
    executive_summary: str              # 2–3 sentence boardroom summary
    recommended_intervention: str       # single highest-impact action


@dataclass
class BriefingOutput:
    briefing_type: str                   # CEO / QBR
    situation: str
    business_risk: str
    business_outcomes: str
    key_asks: List[str]
    next_30_days: str
    next_60_days: str
    next_90_days: str
    recommended_executive_action: str
    risk_narrative: str


@dataclass
class EscalationOutput:
    severity: str                        # Critical / High / Medium
    situation_summary: str
    likely_root_cause: str
    customer_impact: str
    internal_owner_map: List[str]        # "Role: Name — action"
    recovery_plan_48h: List[str]
    recovery_plan_2wks: List[str]
    executive_comms_draft: str           # draft email / message for CEO/CRO
    recommended_next_step: str


@dataclass
class SkeptikOutput:
    prior_agent: str
    unsupported_claims: List[str]
    missing_evidence: List[str]
    overconfident_conclusions: List[str]
    alternative_explanations: List[str]
    recommended_edits: List[str]
    original_confidence: float
    revised_confidence: float
    revised_confidence_rationale: str
    verdict: str                         # Approve / Approve with Edits / Reject


@dataclass
class VPReviewOutput:
    week_ending: str
    portfolio_health_summary: str
    top_5_risks: List[str]               # "Customer: reason"
    top_5_executive_actions: List[str]   # concrete, owned actions
    arr_at_risk: int
    renewals_watchlist: List[str]        # "Customer: days out, stage, risk"
    impl_bottlenecks: List[str]
    product_feedback_themes: List[str]
    support_burden_themes: List[str]
    cross_functional_asks: List[str]     # asks of Eng / Product / Finance / Legal
    ceo_ready_summary: str              # 3 sentences max, zero fluff


@dataclass
class ExpansionOutput:
    expansion_thesis: str                # why this account can grow
    recommended_modules: List[str]       # products / modules to upsell
    projected_arr_uplift: int            # $ uplift estimate
    confidence: str                      # High / Medium / Low likelihood
    proof_points: List[str]              # ROI / adoption evidence supporting the play
    recommended_play: List[str]          # concrete steps to land expansion
    best_timing: str                     # when to make the move


@dataclass
class QBRPrepOutput:
    executive_headline: str              # one-line state of the relationship
    value_delivered: List[str]           # outcomes since last QBR
    adoption_summary: str
    open_items: List[str]                # risks / asks to cover
    proposed_agenda: List[str]           # QBR agenda items
    expansion_talking_points: List[str]
    success_metrics: List[str]           # metrics to review


@dataclass
class SuccessPlanOutput:
    objective: str                       # the north-star outcome for the account
    current_state: str
    target_state: str
    workstreams: List[str]               # major workstreams with owners
    milestones_30_60_90: List[str]       # time-phased milestones
    success_metrics: List[str]           # how success is measured
    risks_and_mitigations: List[str]
