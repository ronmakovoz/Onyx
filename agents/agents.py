"""
All six CX agents. Each defines its own system/user prompts
and inherits execution, routing, and cost tracking from BaseAgent.
"""

from agents.base_agent import BaseAgent
from prompts.templates import (
    HEALTH_SYSTEM, HEALTH_USER,
    IMPL_SYSTEM, IMPL_USER,
    BRIEFING_SYSTEM, BRIEFING_USER,
    ESCALATION_SYSTEM, ESCALATION_USER,
    SKEPTIK_SYSTEM, SKEPTIK_USER,
    VPCOS_SYSTEM, VPCOS_USER,
)


class CustomerHealthAgent(BaseAgent):
    name = "CustomerHealthAgent"

    def build_prompt(self, ctx):
        return HEALTH_SYSTEM, HEALTH_USER.format(**ctx)


class ImplementationAgent(BaseAgent):
    name = "ImplementationAgent"

    def build_prompt(self, ctx):
        return IMPL_SYSTEM, IMPL_USER.format(**ctx)


class BriefingAgent(BaseAgent):
    name = "BriefingAgent"

    def build_prompt(self, ctx):
        return BRIEFING_SYSTEM, BRIEFING_USER.format(**ctx)


class EscalationCommanderAgent(BaseAgent):
    name = "EscalationCommanderAgent"

    def build_prompt(self, ctx):
        return ESCALATION_SYSTEM, ESCALATION_USER.format(**ctx)


class SkeptikQAAgent(BaseAgent):
    name = "SkeptikQAAgent"

    def build_prompt(self, ctx):
        return SKEPTIK_SYSTEM, SKEPTIK_USER.format(**ctx)


class VPChiefOfStaffAgent(BaseAgent):
    name = "VPChiefOfStaffAgent"

    def build_prompt(self, ctx):
        return VPCOS_SYSTEM, VPCOS_USER.format(**ctx)


AGENT_REGISTRY = {
    "CustomerHealthAgent": CustomerHealthAgent,
    "ImplementationAgent": ImplementationAgent,
    "BriefingAgent": BriefingAgent,
    "EscalationCommanderAgent": EscalationCommanderAgent,
    "SkeptikQAAgent": SkeptikQAAgent,
    "VPChiefOfStaffAgent": VPChiefOfStaffAgent,
}
