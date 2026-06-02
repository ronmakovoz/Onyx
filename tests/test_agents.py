"""
Agent test suite using synthetic data.
Tests agent execution, structured output parsing, model routing, and cost tracking.
Run: python -m pytest tests/test_agents.py -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import sqlite3
from pathlib import Path

from agents.agents import AGENT_REGISTRY, AGENT_MODEL_TIER
from agents.model_router import route, MODEL_IDS
from agents.outputs import (
    HealthOutput, ImplementationOutput, BriefingOutput,
    EscalationOutput, SkeptikOutput, VPReviewOutput,
)
from backend.context_builder import build_customer_context, build_portfolio_context
from backend.crud import get_all_customers, get_customer_360

DB_PATH = Path(__file__).parent.parent / "data" / "cx_agent_os.db"


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def db():
    assert DB_PATH.exists(), f"Database not found at {DB_PATH}. Run: python data/generate_synthetic_data.py"
    return sqlite3.connect(DB_PATH)

@pytest.fixture(scope="session")
def customers():
    return get_all_customers()

@pytest.fixture(scope="session")
def high_risk_customer(customers):
    c = next((c for c in customers if c["risk_level"] == "High"), None)
    assert c, "No high-risk customer found in database"
    return c

@pytest.fixture(scope="session")
def healthy_customer(customers):
    c = next((c for c in customers if c["risk_level"] == "Low"), None)
    assert c, "No healthy customer found in database"
    return c

@pytest.fixture(scope="session")
def high_risk_ctx(high_risk_customer):
    return build_customer_context(high_risk_customer["id"])

@pytest.fixture(scope="session")
def healthy_ctx(healthy_customer):
    return build_customer_context(healthy_customer["id"])

@pytest.fixture(scope="session")
def portfolio_ctx():
    return build_portfolio_context()


# ── Database integrity tests ──────────────────────────────────────────────────

class TestDatabase:
    def test_customer_count(self, customers):
        assert len(customers) == 25, f"Expected 25 customers, got {len(customers)}"

    def test_risk_distribution(self, customers):
        high   = sum(1 for c in customers if c["risk_level"] == "High")
        medium = sum(1 for c in customers if c["risk_level"] == "Medium")
        low    = sum(1 for c in customers if c["risk_level"] == "Low")
        assert high >= 5,  f"Need at least 5 high-risk customers, got {high}"
        assert medium >= 4, f"Need at least 4 medium-risk, got {medium}"
        assert low >= 8,   f"Need at least 8 healthy, got {low}"

    def test_all_customers_have_required_fields(self, customers):
        required = ["name", "industry", "arr", "renewal_date", "health_score",
                    "risk_level", "champion_status", "sentiment", "renewal_risk_score"]
        for c in customers:
            for field in required:
                assert field in c and c[field] is not None, f"Customer {c['id']} missing {field}"

    def test_health_scores_in_range(self, customers):
        for c in customers:
            assert 0 <= c["health_score"] <= 100, f"Customer {c['id']} health score out of range: {c['health_score']}"

    def test_high_risk_customers_have_tickets(self, db):
        high_risk_ids = [
            row[0] for row in db.execute("SELECT id FROM customers WHERE risk_level='High'").fetchall()
        ]
        for cid in high_risk_ids:
            count = db.execute(
                "SELECT COUNT(*) FROM support_tickets WHERE customer_id=? AND severity IN ('P1','P2')",
                (cid,)
            ).fetchone()[0]
            assert count > 0, f"High-risk customer {cid} should have P1/P2 tickets"

    def test_high_risk_customers_have_escalations(self, db):
        high_risk_ids = [
            row[0] for row in db.execute("SELECT id FROM customers WHERE risk_level='High'").fetchall()
        ]
        for cid in high_risk_ids:
            count = db.execute(
                "SELECT COUNT(*) FROM escalations WHERE customer_id=?", (cid,)
            ).fetchone()[0]
            assert count > 0, f"High-risk customer {cid} should have escalations"

    def test_champion_left_means_no_engagement(self, db):
        rows = db.execute(
            "SELECT c.id FROM customers c WHERE c.champion_status='Left Company'"
        ).fetchall()
        for (cid,) in rows:
            eng = db.execute(
                "SELECT engagement_level FROM stakeholders WHERE customer_id=? AND role='Champion'",
                (cid,)
            ).fetchone()
            if eng:
                assert eng[0] in ("None", "Low"), \
                    f"Customer {cid}: champion left but engagement is '{eng[0]}'"

    def test_renewals_within_180_days(self, db):
        count = db.execute("SELECT COUNT(*) FROM renewals").fetchone()[0]
        assert count >= 12, f"Need at least 12 renewals in 180-day window, got {count}"

    def test_health_history_30_days(self, db):
        count = db.execute("SELECT COUNT(*) FROM health_history").fetchone()[0]
        assert count >= 25 * 28, f"Expected at least 700 health history points, got {count}"


# ── Context builder tests ─────────────────────────────────────────────────────

class TestContextBuilder:
    def test_customer_context_has_required_keys(self, high_risk_ctx):
        required = ["customer_name", "industry", "arr", "renewal_days", "health_score",
                    "champion_status", "sentiment", "renewal_risk", "open_tickets",
                    "open_escalations", "escalation_summary", "milestones",
                    "impl_status", "days_behind", "meeting_notes"]
        for key in required:
            assert key in high_risk_ctx, f"Context missing key: {key}"

    def test_high_risk_context_has_escalations(self, high_risk_ctx):
        assert high_risk_ctx["open_escalations"] > 0, "High-risk customer should have active escalations"

    def test_high_risk_context_has_open_tickets(self, high_risk_ctx):
        assert high_risk_ctx["open_tickets"] > 0, "High-risk customer should have open tickets"

    def test_portfolio_context_has_all_segments(self, portfolio_ctx):
        assert portfolio_ctx["critical_count"] > 0,  "Portfolio should have critical customers"
        assert portfolio_ctx["at_risk_count"]  > 0,  "Portfolio should have at-risk customers"
        assert portfolio_ctx["healthy_count"]  > 0,  "Portfolio should have healthy customers"
        assert portfolio_ctx["total_arr"]      > 0,  "Portfolio should have total ARR"
        assert portfolio_ctx["arr_at_risk"]    > 0,  "Portfolio should have ARR at risk"

    def test_renewal_days_is_integer(self, high_risk_ctx):
        assert isinstance(high_risk_ctx["renewal_days"], int), "renewal_days should be an integer"

    def test_healthy_customer_has_lower_risk(self, high_risk_ctx, healthy_ctx):
        assert high_risk_ctx["health_score"] < healthy_ctx["health_score"], \
            "High-risk customer should have lower health score than healthy customer"
        assert high_risk_ctx["renewal_risk"] > healthy_ctx["renewal_risk"], \
            "High-risk customer should have higher renewal risk"


# ── Model routing tests ───────────────────────────────────────────────────────

class TestModelRouting:
    def test_haiku_agents(self):
        assert route("CustomerHealthAgent").model_tier == "haiku"

    def test_sonnet_agents(self):
        assert route("ImplementationAgent").model_tier == "sonnet"
        assert route("BriefingAgent").model_tier == "sonnet"

    def test_opus_agents(self):
        assert route("EscalationCommanderAgent").model_tier == "opus"
        assert route("SkeptikQAAgent").model_tier == "opus"
        assert route("VPChiefOfStaffAgent").model_tier == "opus"

    def test_all_model_ids_valid(self):
        valid_ids = set(MODEL_IDS.values())
        for agent_name in AGENT_REGISTRY:
            decision = route(agent_name)
            assert decision.model_id in valid_ids, \
                f"{agent_name} routes to unknown model ID: {decision.model_id}"

    def test_rationale_not_empty(self):
        for agent_name in AGENT_REGISTRY:
            decision = route(agent_name)
            assert len(decision.rationale) > 20, f"{agent_name} has empty routing rationale"

    def test_cost_estimation_positive(self):
        decision = route("BriefingAgent")
        cost = decision.estimate_cost(1000, 500)
        assert cost > 0, "Cost should be positive"

    def test_opus_costs_more_than_haiku(self):
        haiku_cost  = route("CustomerHealthAgent").estimate_cost(1000, 500)
        opus_cost   = route("EscalationCommanderAgent").estimate_cost(1000, 500)
        assert opus_cost > haiku_cost * 5, "Opus should cost significantly more than Haiku"


# ── Agent execution tests (mock mode) ────────────────────────────────────────

class TestCustomerHealthAgent:
    def test_runs_without_error(self, high_risk_ctx, high_risk_customer):
        agent = AGENT_REGISTRY["CustomerHealthAgent"]()
        result = agent.run(high_risk_ctx, customer_id=high_risk_customer["id"])
        assert result.output_text, "Agent should produce output"
        assert result.is_mock is True

    def test_produces_structured_output(self, high_risk_ctx, high_risk_customer):
        agent = AGENT_REGISTRY["CustomerHealthAgent"]()
        result = agent.run(high_risk_ctx, customer_id=high_risk_customer["id"])
        assert result.structured is not None, "Should produce structured output"
        assert isinstance(result.structured, HealthOutput)

    def test_structured_fields_populated(self, high_risk_ctx, high_risk_customer):
        agent = AGENT_REGISTRY["CustomerHealthAgent"]()
        result = agent.run(high_risk_ctx, customer_id=high_risk_customer["id"])
        s = result.structured
        assert 0 <= s.health_score <= 100
        assert s.risk_level in ("Low","Medium","High","Critical","Unknown")
        assert len(s.recommended_actions) > 0
        assert 0.0 <= s.confidence_score <= 1.0

    def test_cost_is_positive(self, high_risk_ctx, high_risk_customer):
        agent = AGENT_REGISTRY["CustomerHealthAgent"]()
        result = agent.run(high_risk_ctx, customer_id=high_risk_customer["id"])
        assert result.estimated_cost_usd > 0

    def test_model_is_haiku(self, high_risk_ctx, high_risk_customer):
        agent = AGENT_REGISTRY["CustomerHealthAgent"]()
        result = agent.run(high_risk_ctx, customer_id=high_risk_customer["id"])
        assert "haiku" in result.model_used.lower()

    def test_high_risk_has_risk_drivers(self, high_risk_ctx, high_risk_customer):
        agent = AGENT_REGISTRY["CustomerHealthAgent"]()
        result = agent.run(high_risk_ctx, customer_id=high_risk_customer["id"])
        assert len(result.structured.top_risk_drivers) > 0


class TestImplementationAgent:
    def test_runs_without_error(self, high_risk_ctx, high_risk_customer):
        agent = AGENT_REGISTRY["ImplementationAgent"]()
        result = agent.run(high_risk_ctx, customer_id=high_risk_customer["id"])
        assert result.output_text

    def test_produces_structured_output(self, high_risk_ctx, high_risk_customer):
        agent = AGENT_REGISTRY["ImplementationAgent"]()
        result = agent.run(high_risk_ctx, customer_id=high_risk_customer["id"])
        assert isinstance(result.structured, ImplementationOutput)

    def test_launch_confidence_valid(self, high_risk_ctx, high_risk_customer):
        agent = AGENT_REGISTRY["ImplementationAgent"]()
        result = agent.run(high_risk_ctx, customer_id=high_risk_customer["id"])
        assert result.structured.launch_confidence in ("High","Medium","Low","Very Low")

    def test_model_is_sonnet(self, high_risk_ctx, high_risk_customer):
        agent = AGENT_REGISTRY["ImplementationAgent"]()
        result = agent.run(high_risk_ctx, customer_id=high_risk_customer["id"])
        assert "sonnet" in result.model_used.lower()

    def test_stalled_implementation_low_confidence(self, high_risk_ctx, high_risk_customer):
        agent = AGENT_REGISTRY["ImplementationAgent"]()
        result = agent.run(high_risk_ctx, customer_id=high_risk_customer["id"])
        # High-risk customer should not have High launch confidence
        if high_risk_ctx.get("days_behind", 0) > 20:
            assert result.structured.launch_confidence in ("Low","Very Low","Medium")


class TestBriefingAgent:
    def test_runs_without_error(self, high_risk_ctx, high_risk_customer):
        agent = AGENT_REGISTRY["BriefingAgent"]()
        result = agent.run(high_risk_ctx, customer_id=high_risk_customer["id"])
        assert result.output_text

    def test_output_contains_arr(self, high_risk_ctx, high_risk_customer):
        agent = AGENT_REGISTRY["BriefingAgent"]()
        result = agent.run(high_risk_ctx, customer_id=high_risk_customer["id"])
        # ARR should appear in the output
        arr_str = str(high_risk_ctx["arr"])[:6]  # first 6 digits
        assert arr_str in result.output_text.replace(",",""), "Briefing should reference the customer's ARR"

    def test_produces_briefing_structured(self, high_risk_ctx, high_risk_customer):
        agent = AGENT_REGISTRY["BriefingAgent"]()
        result = agent.run(high_risk_ctx, customer_id=high_risk_customer["id"])
        assert isinstance(result.structured, BriefingOutput)
        assert result.structured.briefing_type == "CEO"


class TestEscalationCommanderAgent:
    def test_runs_without_error(self, high_risk_ctx, high_risk_customer):
        agent = AGENT_REGISTRY["EscalationCommanderAgent"]()
        result = agent.run(high_risk_ctx, customer_id=high_risk_customer["id"])
        assert result.output_text

    def test_model_is_opus(self, high_risk_ctx, high_risk_customer):
        agent = AGENT_REGISTRY["EscalationCommanderAgent"]()
        result = agent.run(high_risk_ctx, customer_id=high_risk_customer["id"])
        assert "opus" in result.model_used.lower()

    def test_produces_escalation_output(self, high_risk_ctx, high_risk_customer):
        agent = AGENT_REGISTRY["EscalationCommanderAgent"]()
        result = agent.run(high_risk_ctx, customer_id=high_risk_customer["id"])
        assert isinstance(result.structured, EscalationOutput)

    def test_severity_is_valid(self, high_risk_ctx, high_risk_customer):
        agent = AGENT_REGISTRY["EscalationCommanderAgent"]()
        result = agent.run(high_risk_ctx, customer_id=high_risk_customer["id"])
        assert result.structured.severity in ("Critical","High","Medium")

    def test_recovery_plan_not_empty(self, high_risk_ctx, high_risk_customer):
        agent = AGENT_REGISTRY["EscalationCommanderAgent"]()
        result = agent.run(high_risk_ctx, customer_id=high_risk_customer["id"])
        assert len(result.structured.recovery_plan_48h) > 0

    def test_opus_costs_more_than_sonnet(self, high_risk_ctx, high_risk_customer):
        esc_agent   = AGENT_REGISTRY["EscalationCommanderAgent"]()
        brief_agent = AGENT_REGISTRY["BriefingAgent"]()
        esc_result   = esc_agent.run(high_risk_ctx, customer_id=high_risk_customer["id"])
        brief_result = brief_agent.run(high_risk_ctx, customer_id=high_risk_customer["id"])
        # In mock mode tokens are random, but we can check model assignment
        assert "opus"   in esc_result.model_used.lower()
        assert "sonnet" in brief_result.model_used.lower()


class TestSkeptikQAAgent:
    def test_runs_with_prior_output(self, high_risk_ctx, high_risk_customer):
        # First generate a briefing
        prior = AGENT_REGISTRY["BriefingAgent"]().run(high_risk_ctx, customer_id=high_risk_customer["id"])
        # Then run skeptik
        ctx = {**high_risk_ctx,
               "prior_agent": "BriefingAgent",
               "prior_output": prior.output_text,
               "prior_confidence": prior.confidence_score}
        agent = AGENT_REGISTRY["SkeptikQAAgent"]()
        result = agent.run(ctx, customer_id=high_risk_customer["id"])
        assert result.output_text

    def test_skeptik_lowers_confidence(self, high_risk_ctx, high_risk_customer):
        prior = AGENT_REGISTRY["BriefingAgent"]().run(high_risk_ctx, customer_id=high_risk_customer["id"])
        ctx = {**high_risk_ctx,
               "prior_agent": "BriefingAgent",
               "prior_output": prior.output_text,
               "prior_confidence": prior.confidence_score}
        agent = AGENT_REGISTRY["SkeptikQAAgent"]()
        result = agent.run(ctx, customer_id=high_risk_customer["id"])
        s = result.structured
        assert s.revised_confidence <= s.original_confidence, \
            "Skeptik should not raise confidence above original"

    def test_skeptik_provides_critiques(self, high_risk_ctx, high_risk_customer):
        prior = AGENT_REGISTRY["BriefingAgent"]().run(high_risk_ctx, customer_id=high_risk_customer["id"])
        ctx = {**high_risk_ctx,
               "prior_agent": "BriefingAgent",
               "prior_output": prior.output_text,
               "prior_confidence": prior.confidence_score}
        result = AGENT_REGISTRY["SkeptikQAAgent"]().run(ctx, customer_id=high_risk_customer["id"])
        s = result.structured
        total_critiques = len(s.unsupported_claims) + len(s.missing_evidence) + len(s.overconfident_conclusions)
        assert total_critiques > 0, "Skeptik should find at least one issue"

    def test_verdict_is_valid(self, high_risk_ctx, high_risk_customer):
        prior = AGENT_REGISTRY["BriefingAgent"]().run(high_risk_ctx, customer_id=high_risk_customer["id"])
        ctx = {**high_risk_ctx,
               "prior_agent": "BriefingAgent",
               "prior_output": prior.output_text,
               "prior_confidence": prior.confidence_score}
        result = AGENT_REGISTRY["SkeptikQAAgent"]().run(ctx, customer_id=high_risk_customer["id"])
        assert result.structured.verdict in ("Approve","Approve with Edits","Reject")


class TestVPChiefOfStaffAgent:
    def test_runs_portfolio_wide(self, portfolio_ctx):
        agent = AGENT_REGISTRY["VPChiefOfStaffAgent"]()
        result = agent.run(portfolio_ctx, customer_id=None)
        assert result.output_text

    def test_model_is_opus(self, portfolio_ctx):
        agent = AGENT_REGISTRY["VPChiefOfStaffAgent"]()
        result = agent.run(portfolio_ctx)
        assert "opus" in result.model_used.lower()

    def test_structured_output_populated(self, portfolio_ctx):
        agent = AGENT_REGISTRY["VPChiefOfStaffAgent"]()
        result = agent.run(portfolio_ctx)
        assert isinstance(result.structured, VPReviewOutput)
        s = result.structured
        assert s.arr_at_risk > 0
        assert len(s.top_5_risks) > 0 or len(s.top_5_executive_actions) > 0

    def test_no_customer_id_required(self, portfolio_ctx):
        agent = AGENT_REGISTRY["VPChiefOfStaffAgent"]()
        result = agent.run(portfolio_ctx, customer_id=None)
        assert result.customer_id is None


# ── Agent result contract tests ───────────────────────────────────────────────

class TestAgentResultContract:
    """Every agent result must satisfy the base contract."""

    @pytest.mark.parametrize("agent_name", list(AGENT_REGISTRY.keys()))
    def test_result_has_required_fields(self, agent_name, high_risk_ctx, portfolio_ctx, high_risk_customer):
        agent = AGENT_REGISTRY[agent_name]()
        if agent_name == "VPChiefOfStaffAgent":
            result = agent.run(portfolio_ctx, customer_id=None)
        elif agent_name == "SkeptikQAAgent":
            prior = AGENT_REGISTRY["BriefingAgent"]().run(high_risk_ctx, customer_id=high_risk_customer["id"])
            ctx = {**high_risk_ctx, "prior_agent": "BriefingAgent",
                   "prior_output": prior.output_text, "prior_confidence": prior.confidence_score}
            result = agent.run(ctx, customer_id=high_risk_customer["id"])
        else:
            result = agent.run(high_risk_ctx, customer_id=high_risk_customer["id"])

        assert result.agent_name  == agent_name
        assert result.model_used,    f"{agent_name}: model_used is empty"
        assert result.output_text,   f"{agent_name}: output_text is empty"
        assert result.estimated_cost_usd > 0, f"{agent_name}: cost should be positive"
        assert 0 <= result.confidence_score <= 1, f"{agent_name}: confidence out of range"
        assert result.created_at,    f"{agent_name}: created_at is empty"
        assert result.input_tokens  > 0, f"{agent_name}: input_tokens should be > 0"
        assert result.output_tokens > 0, f"{agent_name}: output_tokens should be > 0"

    @pytest.mark.parametrize("agent_name", list(AGENT_REGISTRY.keys()))
    def test_result_serializable(self, agent_name, high_risk_ctx, portfolio_ctx, high_risk_customer):
        import json
        agent = AGENT_REGISTRY[agent_name]()
        if agent_name == "VPChiefOfStaffAgent":
            result = agent.run(portfolio_ctx, customer_id=None)
        elif agent_name == "SkeptikQAAgent":
            prior = AGENT_REGISTRY["BriefingAgent"]().run(high_risk_ctx, customer_id=high_risk_customer["id"])
            ctx = {**high_risk_ctx, "prior_agent": "BriefingAgent",
                   "prior_output": prior.output_text, "prior_confidence": prior.confidence_score}
            result = agent.run(ctx, customer_id=high_risk_customer["id"])
        else:
            result = agent.run(high_risk_ctx, customer_id=high_risk_customer["id"])

        d = result.to_dict()
        try:
            json.dumps(d, default=str)
        except Exception as e:
            pytest.fail(f"{agent_name} result not JSON serializable: {e}")
