from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class Customer(BaseModel):
    id: int
    name: str
    industry: str
    arr: int
    renewal_date: str
    health_score: int
    onboarding_status: str
    adoption_score: int
    champion_name: str
    champion_status: str
    sentiment: str
    renewal_risk: float
    security_review_status: str
    risk_label: str


class SupportTicket(BaseModel):
    id: int
    customer_id: int
    title: str
    severity: str
    status: str
    opened_at: str
    resolved_at: Optional[str] = None


class Escalation(BaseModel):
    id: int
    customer_id: int
    title: str
    severity: str
    owner: str
    status: str
    opened_at: str


class Stakeholder(BaseModel):
    id: int
    customer_id: int
    name: str
    title: str
    email: str
    role: str


class UsageMetric(BaseModel):
    id: int
    customer_id: int
    metric_name: str
    value: float
    recorded_at: str


class ImplementationMilestone(BaseModel):
    id: int
    customer_id: int
    name: str
    status: str
    due_date: str
    completed_at: Optional[str] = None


class MeetingNote(BaseModel):
    id: int
    customer_id: int
    date: str
    summary: str
    attendees: str
    sentiment_signal: str


class AgentRun(BaseModel):
    id: int
    agent_name: str
    customer_id: Optional[int] = None
    model_used: str
    model_rationale: str
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float
    confidence_score: float
    output_text: str
    created_at: str


class Briefing(BaseModel):
    id: int
    briefing_type: str
    customer_id: Optional[int] = None
    content: str
    agent_run_id: int
    created_at: str


class Customer360(BaseModel):
    customer: Customer
    tickets: List[SupportTicket]
    escalations: List[Escalation]
    stakeholders: List[Stakeholder]
    metrics: List[UsageMetric]
    milestones: List[ImplementationMilestone]
    meeting_notes: List[MeetingNote]


class AgentRunRequest(BaseModel):
    agent_name: str
    customer_id: Optional[int] = None


class PortfolioSummary(BaseModel):
    total_customers: int
    total_arr: int
    arr_at_risk: int
    critical_count: int
    at_risk_count: int
    healthy_count: int
    open_escalations: int
    renewals_next_90_days: int
    avg_health_score: float
    top_escalations: List[Escalation]
