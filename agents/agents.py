"""
All CX agents. Each defines prompts and structured output parsing.
"""

import re
import random
from datetime import datetime
from typing import Optional

from agents.base_agent import BaseAgent
from agents.outputs import (
    HealthOutput, ImplementationOutput, BriefingOutput,
    EscalationOutput, SkeptikOutput, VPReviewOutput,
    ExpansionOutput, QBRPrepOutput, SuccessPlanOutput,
)
from prompts.templates import (
    HEALTH_SYSTEM, HEALTH_USER,
    IMPL_SYSTEM, IMPL_USER,
    BRIEFING_SYSTEM, BRIEFING_USER,
    ESCALATION_SYSTEM, ESCALATION_USER,
    SKEPTIK_SYSTEM, SKEPTIK_USER,
    VPCOS_SYSTEM, VPCOS_USER,
    EXPANSION_SYSTEM, EXPANSION_USER,
    QBR_SYSTEM, QBR_USER,
    SUCCESSPLAN_SYSTEM, SUCCESSPLAN_USER,
)


def _extract_list(text: str, header: str, max_items: int = 5) -> list[str]:
    """Extract a bulleted/numbered list under a markdown header."""
    pattern = rf"###?\s*{re.escape(header)}.*?\n(.*?)(?=\n###|\n##|\Z)"
    m = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if not m:
        return []
    block = m.group(1).strip()
    items = []
    for line in block.splitlines():
        line = line.strip()
        if line and line[0] in "-*•1234567890[":
            clean = re.sub(r"^[\-\*•\[\]✅⚠️🚨\d\.]+\s*", "", line).strip()
            if clean:
                items.append(clean)
        if len(items) >= max_items:
            break
    return items


def _extract_section(text: str, header: str) -> str:
    pattern = rf"###?\s*{re.escape(header)}.*?\n(.*?)(?=\n###|\n##|\Z)"
    m = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else ""


def _extract_confidence(text: str, fallback: float = 0.75) -> float:
    m = re.search(r"[Cc]onfidence[:\s]+(\d+)%", text)
    if m:
        return min(1.0, int(m.group(1)) / 100)
    m = re.search(r"(\d+)%.*confidence", text, re.IGNORECASE)
    if m:
        return min(1.0, int(m.group(1)) / 100)
    return fallback


def _extract_health_score(text: str, fallback: int = 50) -> int:
    m = re.search(r"[Hh]ealth\s+[Ss]core[:\s]+(\d+)/100", text)
    if m:
        return min(100, int(m.group(1)))
    return fallback


def _extract_risk_level(text: str) -> str:
    for level in ("Critical", "High", "Medium", "Low"):
        if re.search(rf"Risk\s+Level[:\s]+{level}", text, re.IGNORECASE):
            return level
    return "Unknown"


# ══════════════════════════════════════════════════════════════════════════════

class CustomerHealthAgent(BaseAgent):
    name = "CustomerHealthAgent"

    def build_prompt(self, ctx: dict) -> tuple[str, str]:
        return HEALTH_SYSTEM, HEALTH_USER.format(**ctx)

    def parse_structured(self, text: str, ctx: dict) -> HealthOutput:
        return HealthOutput(
            health_score=_extract_health_score(text, ctx.get("health_score", 50)),
            risk_level=_extract_risk_level(text) or ctx.get("risk_label", ctx.get("risk_level","Unknown")),
            top_risk_drivers=_extract_list(text, "Top Risk Drivers"),
            positive_signals=_extract_list(text, "Positive Signals"),
            early_warning_signals=_extract_list(text, "Early Warning Signals"),
            recommended_actions=_extract_list(text, "Recommended Next Actions"),
            confidence_score=_extract_confidence(text, ctx.get("_conf", 0.75)),
            confidence_rationale=_extract_section(text, "Confidence Assessment")[:200],
        )

    def _estimate_confidence(self, ctx: dict) -> float:
        base = super()._estimate_confidence(ctx)
        # Health agent has more signal data available — slightly higher floor
        return round(min(0.94, base + 0.03), 2)


class ImplementationAgent(BaseAgent):
    name = "ImplementationAgent"

    def build_prompt(self, ctx: dict) -> tuple[str, str]:
        return IMPL_SYSTEM, IMPL_USER.format(**ctx)

    def parse_structured(self, text: str, ctx: dict) -> ImplementationOutput:
        conf_map = {"High": "High", "Medium": "Medium", "Low": "Low", "Very Low": "Very Low"}
        conf = "Medium"
        for k in conf_map:
            if f"Launch Confidence: {k}" in text or f"**{k}**" in text:
                conf = k
                break

        return ImplementationOutput(
            overall_status=ctx.get("impl_status", "Unknown"),
            pct_complete=ctx.get("impl_progress", 0),
            launch_confidence=conf,
            launch_confidence_rationale=_extract_section(text, f"Launch Confidence")[:300],
            delayed_milestones=_extract_list(text, "In Progress / Stalled"),
            active_blockers=_extract_list(text, "Active Blockers"),
            owner_action_plan=_extract_list(text, "Owner Action Plan"),
            executive_summary=_extract_section(text, "Executive Summary")[:400],
            recommended_intervention=_extract_section(text, "Recommended Intervention")[:300],
        )


class BriefingAgent(BaseAgent):
    name = "BriefingAgent"

    def build_prompt(self, ctx: dict) -> tuple[str, str]:
        return BRIEFING_SYSTEM, BRIEFING_USER.format(**ctx)

    def parse_structured(self, text: str, ctx: dict) -> BriefingOutput:
        return BriefingOutput(
            briefing_type="CEO",
            situation=_extract_section(text, "Situation")[:400],
            business_risk=_extract_section(text, "Business Risk")[:400],
            business_outcomes=_extract_section(text, "Business Outcomes Achieved")[:400],
            key_asks=_extract_list(text, "Key Asks", 3),
            next_30_days=_extract_section(text, "30")[:200],
            next_60_days=_extract_section(text, "60")[:200],
            next_90_days=_extract_section(text, "90")[:200],
            recommended_executive_action=_extract_section(text, "Recommended Executive Action")[:400],
            risk_narrative=_extract_section(text, "Business Risk")[:300],
        )


class EscalationCommanderAgent(BaseAgent):
    name = "EscalationCommanderAgent"

    def build_prompt(self, ctx: dict) -> tuple[str, str]:
        return ESCALATION_SYSTEM, ESCALATION_USER.format(**ctx)

    def parse_structured(self, text: str, ctx: dict) -> EscalationOutput:
        sev = "High"
        for s in ("CRITICAL", "Critical"):
            if s in text[:500]:
                sev = "Critical"
                break

        # Extract exec comms draft between --- markers
        comms_match = re.search(r"---\n(Subject:.*?)\n---", text, re.DOTALL)
        comms_draft = comms_match.group(1).strip() if comms_match else _extract_section(text, "Executive Communication Draft")

        return EscalationOutput(
            severity=sev,
            situation_summary=_extract_section(text, "Situation Summary")[:400],
            likely_root_cause=_extract_section(text, "Likely Root Cause")[:400],
            customer_impact=_extract_section(text, "Customer Impact")[:300],
            internal_owner_map=_extract_list(text, "Internal Owner Map"),
            recovery_plan_48h=_extract_list(text, "Recovery Plan — Next 48 Hours"),
            recovery_plan_2wks=_extract_list(text, "Recovery Plan — Next 2 Weeks"),
            executive_comms_draft=comms_draft[:800],
            recommended_next_step=_extract_section(text, "Recommended Next Step")[:300],
        )

    def _estimate_confidence(self, ctx: dict) -> float:
        # Escalation agent sees the most context — but uncertainty is inherently higher
        base = 0.78
        if ctx.get("open_escalations", 0) > 2:
            base += 0.04
        if ctx.get("champion_status") == "Left Company":
            base -= 0.06
        return round(max(0.52, min(0.88, base + random.uniform(-0.05, 0.05))), 2)


class SkeptikQAAgent(BaseAgent):
    name = "SkeptikQAAgent"

    def build_prompt(self, ctx: dict) -> tuple[str, str]:
        return SKEPTIK_SYSTEM, SKEPTIK_USER.format(**ctx)

    def parse_structured(self, text: str, ctx: dict) -> SkeptikOutput:
        verdict = "Approve with Edits"
        if "🚫 Reject" in text or "Reject" in text[:200]:
            verdict = "Reject"
        elif "✅ Approve" in text and "Edits" not in text[:200]:
            verdict = "Approve"

        orig_conf = ctx.get("prior_confidence", 0.80)
        rev_conf  = _extract_confidence(text, orig_conf - 0.15)
        # Skeptik should lower confidence, not raise it
        rev_conf  = min(rev_conf, orig_conf - 0.05)

        return SkeptikOutput(
            prior_agent=ctx.get("prior_agent", "Unknown"),
            unsupported_claims=_extract_list(text, "Unsupported Claims"),
            missing_evidence=_extract_list(text, "Missing Evidence"),
            overconfident_conclusions=_extract_list(text, "Overconfident Conclusions"),
            alternative_explanations=_extract_list(text, "Alternative Explanations"),
            recommended_edits=_extract_list(text, "Recommended Edits"),
            original_confidence=orig_conf,
            revised_confidence=round(rev_conf, 2),
            revised_confidence_rationale=_extract_section(text, "Skeptik note")[:200],
            verdict=verdict,
        )

    def _estimate_confidence(self, ctx: dict) -> float:
        # Skeptik's "confidence" is in its own critique quality — generally high
        return round(random.uniform(0.80, 0.93), 2)


class VPChiefOfStaffAgent(BaseAgent):
    name = "VPChiefOfStaffAgent"

    def build_prompt(self, ctx: dict) -> tuple[str, str]:
        return VPCOS_SYSTEM, VPCOS_USER.format(**ctx)

    def parse_structured(self, text: str, ctx: dict) -> VPReviewOutput:
        return VPReviewOutput(
            week_ending=datetime.now().strftime("%B %d, %Y"),
            portfolio_health_summary=_extract_section(text, "Portfolio Health Summary")[:600],
            top_5_risks=_extract_list(text, "Top 5 Customer Risks"),
            top_5_executive_actions=_extract_list(text, "Top 5 Executive Actions"),
            arr_at_risk=ctx.get("arr_at_risk", 0),
            renewals_watchlist=_extract_list(text, "Renewals Watchlist"),
            impl_bottlenecks=_extract_list(text, "Implementation Bottlenecks"),
            product_feedback_themes=_extract_list(text, "Product Feedback Themes"),
            support_burden_themes=_extract_list(text, "Support Burden Themes"),
            cross_functional_asks=_extract_list(text, "Cross-Functional Asks"),
            ceo_ready_summary=_extract_section(text, "CEO-Ready Summary")[:400],
        )

    def _estimate_confidence(self, ctx: dict) -> float:
        # Portfolio-wide agent has the most data but inherently more uncertainty
        base = 0.82
        if ctx.get("critical_count", 0) > 5:
            base -= 0.04  # high complexity reduces confidence in synthesis
        return round(max(0.68, min(0.92, base + random.uniform(-0.04, 0.04))), 2)


class ExpansionOpportunityAgent(BaseAgent):
    name = "ExpansionOpportunityAgent"

    def build_prompt(self, ctx: dict) -> tuple[str, str]:
        return EXPANSION_SYSTEM, EXPANSION_USER.format(**ctx)

    def parse_structured(self, text: str, ctx: dict) -> ExpansionOutput:
        upl = ctx.get("expansion_pipeline_arr", 0) or int(ctx.get("arr", 0) * 0.2)
        ul  = ctx.get("upsell_likelihood", 0)
        return ExpansionOutput(
            expansion_thesis=_extract_section(text, "Expansion Thesis")[:400],
            recommended_modules=_extract_list(text, "Recommended Modules"),
            projected_arr_uplift=upl,
            confidence=("High" if ul >= 0.45 else "Medium" if ul >= 0.2 else "Low"),
            proof_points=_extract_list(text, "Proof Points"),
            recommended_play=_extract_list(text, "Recommended Play"),
            best_timing=_extract_section(text, "Best Timing")[:200],
        )


class QBRPreparationAgent(BaseAgent):
    name = "QBRPreparationAgent"

    def build_prompt(self, ctx: dict) -> tuple[str, str]:
        return QBR_SYSTEM, QBR_USER.format(**ctx)

    def parse_structured(self, text: str, ctx: dict) -> QBRPrepOutput:
        return QBRPrepOutput(
            executive_headline=_extract_section(text, "Executive Headline")[:300],
            value_delivered=_extract_list(text, "Value Delivered"),
            adoption_summary=_extract_section(text, "Adoption Summary")[:300],
            open_items=_extract_list(text, "Open Items"),
            proposed_agenda=_extract_list(text, "Proposed Agenda"),
            expansion_talking_points=_extract_list(text, "Expansion Talking Points"),
            success_metrics=_extract_list(text, "Success Metrics"),
        )


class SuccessPlanAgent(BaseAgent):
    name = "SuccessPlanAgent"

    def build_prompt(self, ctx: dict) -> tuple[str, str]:
        return SUCCESSPLAN_SYSTEM, SUCCESSPLAN_USER.format(**ctx)

    def parse_structured(self, text: str, ctx: dict) -> SuccessPlanOutput:
        return SuccessPlanOutput(
            objective=_extract_section(text, "Objective")[:300],
            current_state=_extract_section(text, "Current State")[:300],
            target_state=_extract_section(text, "Target State")[:300],
            workstreams=_extract_list(text, "Workstreams"),
            milestones_30_60_90=_extract_list(text, "Milestones 30 / 60 / 90"),
            success_metrics=_extract_list(text, "Success Metrics"),
            risks_and_mitigations=_extract_list(text, "Risks and Mitigations"),
        )


# ── Registry ──────────────────────────────────────────────────────────────────

AGENT_REGISTRY = {
    "CustomerHealthAgent":      CustomerHealthAgent,
    "ImplementationAgent":      ImplementationAgent,
    "BriefingAgent":            BriefingAgent,
    "EscalationCommanderAgent": EscalationCommanderAgent,
    "SkeptikQAAgent":           SkeptikQAAgent,
    "VPChiefOfStaffAgent":      VPChiefOfStaffAgent,
    "ExpansionOpportunityAgent": ExpansionOpportunityAgent,
    "QBRPreparationAgent":      QBRPreparationAgent,
    "SuccessPlanAgent":         SuccessPlanAgent,
}

AGENT_DESCRIPTIONS = {
    "CustomerHealthAgent":      "Scans customer signals and scores health risk across the portfolio.",
    "ImplementationAgent":      "Diagnoses implementation execution quality and produces recovery plans.",
    "BriefingAgent":            "Generates CEO-grade executive briefings and QBR summaries.",
    "EscalationCommanderAgent": "Manages critical escalations with battle plans and executive comms.",
    "SkeptikQAAgent":           "Adversarially reviews prior agent outputs before executive delivery.",
    "VPChiefOfStaffAgent":      "Produces the weekly VP CX operating review across the full portfolio.",
    "ExpansionOpportunityAgent": "Finds evidence-backed upsell opportunities and quantifies ARR uplift.",
    "QBRPreparationAgent":      "Auto-generates an executive-ready Quarterly Business Review briefing.",
    "SuccessPlanAgent":         "Builds a time-phased 30/60/90 success plan for an account.",
}

AGENT_MODEL_TIER = {
    "CustomerHealthAgent":      "haiku",
    "ImplementationAgent":      "sonnet",
    "BriefingAgent":            "sonnet",
    "EscalationCommanderAgent": "opus",
    "SkeptikQAAgent":           "opus",
    "VPChiefOfStaffAgent":      "opus",
    "ExpansionOpportunityAgent": "sonnet",
    "QBRPreparationAgent":      "sonnet",
    "SuccessPlanAgent":         "sonnet",
}
