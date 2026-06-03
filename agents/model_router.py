"""
Model routing logic. Selects the right Claude model based on task type and complexity.
Cost estimates use Anthropic's published per-million-token pricing (2025).
"""

from dataclasses import dataclass
from typing import Literal

ModelTier = Literal["haiku", "sonnet", "opus"]

MODEL_IDS = {
    "haiku":  "claude-haiku-4-5-20251001",
    "sonnet": "claude-sonnet-4-6",
    "opus":   "claude-opus-4-8",
}

MODEL_DISPLAY = {
    "haiku":  "Claude Haiku 4.5",
    "sonnet": "Claude Sonnet 4.6",
    "opus":   "Claude Opus 4.8",
}

# Cost per million tokens (input / output) — USD
MODEL_COSTS = {
    "haiku":  {"input": 0.80,  "output": 4.00},
    "sonnet": {"input": 3.00,  "output": 15.00},
    "opus":   {"input": 15.00, "output": 75.00},
}

AGENT_ROUTING = {
    "CustomerHealthAgent": (
        "haiku",
        "High-volume portfolio scanning and risk scoring. Haiku processes each customer "
        "snapshot efficiently at a fraction of the cost of larger models. Structured "
        "extraction and classification tasks are well within Haiku's capabilities."
    ),
    "ImplementationAgent": (
        "sonnet",
        "Implementation status synthesis requires reading across milestone data, blockers, "
        "and stakeholder engagement to form a coherent narrative. Sonnet balances reasoning "
        "quality with cost for this mid-complexity planning task."
    ),
    "BriefingAgent": (
        "sonnet",
        "Executive briefing and QBR generation demands clear narrative structure, precision "
        "in business language, and evidence-backed claims. Sonnet produces boardroom-quality "
        "output efficiently without requiring Opus-level reasoning depth."
    ),
    "EscalationCommanderAgent": (
        "opus",
        "Critical escalation management requires multi-factor risk assessment, stakeholder "
        "psychology, recovery planning, and executive communication drafting simultaneously. "
        "Opus's extended reasoning and judgment capacity is justified by the ARR at stake."
    ),
    "SkeptikQAAgent": (
        "opus",
        "Adversarial review of agent outputs requires the model to actively resist agreeing "
        "with prior conclusions, identify logical gaps, and surface alternative explanations. "
        "Opus's strongest reasoning layer is required to challenge Sonnet-class outputs effectively."
    ),
    "VPChiefOfStaffAgent": (
        "opus",
        "Portfolio-wide weekly review synthesis requires integrating outputs from five agent "
        "types, forming cross-cutting executive recommendations, and producing C-suite-grade "
        "narrative under uncertainty. Opus is selected for judgment depth and synthesis quality."
    ),
    "ExpansionOpportunityAgent": (
        "sonnet",
        "Expansion analysis weighs adoption, ROI, and relationship signals to build a commercial "
        "thesis and quantify uplift. Sonnet delivers sharp, evidence-grounded recommendations at "
        "the right cost for a high-volume opportunity-scan task."
    ),
    "QBRPreparationAgent": (
        "sonnet",
        "QBR briefing assembly requires structured narrative and clear business framing across "
        "value, adoption, and expansion. Sonnet produces polished, executive-ready documents "
        "without the reasoning depth Opus is reserved for."
    ),
    "SuccessPlanAgent": (
        "sonnet",
        "Success-plan construction is a structured planning task — mapping current vs. target "
        "state into time-phased workstreams with owners. Sonnet balances planning quality and cost."
    ),
}


@dataclass
class RoutingDecision:
    model_tier: ModelTier
    model_id: str
    model_display: str
    rationale: str

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        costs = MODEL_COSTS[self.model_tier]
        return (input_tokens / 1_000_000 * costs["input"]) + (output_tokens / 1_000_000 * costs["output"])


def route(agent_name: str) -> RoutingDecision:
    tier, rationale = AGENT_ROUTING.get(
        agent_name, ("sonnet", "Default to Sonnet for balanced performance and quality.")
    )
    return RoutingDecision(
        model_tier=tier,
        model_id=MODEL_IDS[tier],
        model_display=MODEL_DISPLAY[tier],
        rationale=rationale,
    )
