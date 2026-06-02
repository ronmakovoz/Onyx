"""
Model routing logic. Selects the right Claude model based on task complexity.
Cost estimates use Anthropic's published per-million-token pricing.
"""

from dataclasses import dataclass
from typing import Literal

ModelTier = Literal["haiku", "sonnet", "opus"]

MODEL_IDS = {
    "haiku": "claude-haiku-4-5-20251001",
    "sonnet": "claude-sonnet-4-6",
    "opus": "claude-opus-4-8",
}

# Cost per million tokens (input / output)
MODEL_COSTS = {
    "haiku":  {"input": 0.80,  "output": 4.00},
    "sonnet": {"input": 3.00,  "output": 15.00},
    "opus":   {"input": 15.00, "output": 75.00},
}

AGENT_ROUTING = {
    "CustomerHealthAgent":     ("haiku",  "High-volume scoring and extraction — Haiku is fast and cost-efficient."),
    "ImplementationAgent":     ("sonnet", "Synthesis of milestone data and planning — Sonnet balances quality and cost."),
    "BriefingAgent":           ("sonnet", "Executive writing requires nuance and polish — Sonnet is optimal."),
    "EscalationCommanderAgent":("opus",   "High-stakes escalation judgment needs Opus's reasoning depth."),
    "SkeptikQAAgent":          ("opus",   "QA critique requires adversarial reasoning — Opus provides the most rigorous review."),
    "VPChiefOfStaffAgent":     ("sonnet", "Portfolio synthesis and executive review — Sonnet handles breadth well."),
}


@dataclass
class RoutingDecision:
    model_tier: ModelTier
    model_id: str
    rationale: str

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        costs = MODEL_COSTS[self.model_tier]
        return (input_tokens / 1_000_000 * costs["input"]) + (output_tokens / 1_000_000 * costs["output"])


def route(agent_name: str) -> RoutingDecision:
    tier, rationale = AGENT_ROUTING.get(agent_name, ("sonnet", "Default to Sonnet for balanced performance."))
    return RoutingDecision(model_tier=tier, model_id=MODEL_IDS[tier], rationale=rationale)
