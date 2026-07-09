// Thin fetch helpers + shared types for the Linx CX API.

export async function getJSON<T = any>(path: string): Promise<T> {
  const res = await fetch(path, { cache: "no-store" });
  if (!res.ok) throw new Error(`${path} → ${res.status}`);
  return res.json();
}

export async function postJSON<T = any>(path: string, body: any): Promise<T> {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`${path} → ${res.status}`);
  return res.json();
}

export type Customer = {
  id: number;
  name: string;
  industry: string;
  customer_tier: string;
  region: string;
  arr: number;
  health_score: number;
  health_trend?: string;
  risk_level: "High" | "Medium" | "Low";
  nrr_pct?: number;
  grr_pct?: number;
  adoption_score?: number;
  renewal_date: string;
  renewal_risk_score?: number;
  expansion_pipeline_arr?: number;
  upsell_likelihood?: number;
  primary_risk_reason?: string;
  recommended_next_action?: string;
  roi_outcome?: string;
  champion_status?: string;
  qbr_completion?: string;
  csm_owner?: string;
  employee_count?: number;
  nps?: number;
  utilization_pct?: number;
  executive_engagement?: string;
  security_review_status?: string;
  onboarding_status?: string;
  sentiment?: string;
  forecast_category?: string;
  [k: string]: any;
};

export type AgentResult = {
  error?: string;
  run_id?: number;
  agent_name?: string;
  agent_description?: string;
  customer_id?: number | null;
  model_used?: string;
  model_display?: string;
  model_tier?: string;
  model_rationale?: string;
  input_tokens?: number;
  output_tokens?: number;
  estimated_cost_usd?: number;
  confidence_score?: number;
  output_text?: string;
  structured?: any;
  created_at?: string;
  is_mock?: boolean;
};

export type ImplRow = {
  customer_id: number;
  customer_name: string;
  implementation_owner: string;
  overall_status: string;
  pct_complete: number;
  days_behind_schedule: number;
  kicked_off: boolean;
  kickoff_date: string | null;
  days_post_signature: number | null;
  contract_start_date: string | null;
  go_live_target: string | null;
  days_to_go_live: number | null;
  milestones_total: number;
  milestones_complete: number;
  completed_milestones: string[];
  in_progress_milestones: string[];
  active_blockers: string[];
  launch_confidence: "Very Low" | "Low" | "Medium" | "High";
};

// ── Formatting / color helpers ─────────────────────────────────────────────

export const fmtM = (v: number) => `$${(v / 1e6).toFixed(1)}M`;
export const fmtK = (v: number) => `$${(v / 1e3).toFixed(0)}K`;
export const fmtUSD = (v: number) => `$${v.toLocaleString()}`;

export function healthColor(score: number): string {
  if (score < 40) return "#C43D1B";
  if (score < 60) return "#7A5C1E";
  return "#2D5A3D";
}

export const riskColor: Record<string, string> = {
  High: "#C43D1B",
  Medium: "#7A5C1E",
  Low: "#2D5A3D",
};

export const riskBg: Record<string, string> = {
  High: "#FDF1F2",
  Medium: "#FDF8EE",
  Low: "#EFF6F1",
};

export const confColors: Record<string, string> = {
  "Very Low": "#C43D1B",
  Low: "#C8642A",
  Medium: "#7A5C1E",
  High: "#2D5A3D",
};

export const confBg: Record<string, string> = {
  "Very Low": "#FDF1F2",
  Low: "#FDF3EC",
  Medium: "#FDF8EE",
  High: "#EFF6F1",
};

export function modelTierFromId(modelId: string): string {
  const m = (modelId || "").toLowerCase();
  if (m.includes("haiku")) return "haiku";
  if (m.includes("opus")) return "opus";
  return "sonnet";
}

export function tierColor(tier: string): string {
  return { haiku: "#2D4A7A", sonnet: "#3D3458", opus: "#1B1040" }[tier] || "#1B1040";
}

// Recommended action for an implementation project (mirrors Streamlit logic).
export function implNextAction(r: ImplRow): string {
  if (!r.kicked_off) return "Schedule kickoff this week";
  if (r.active_blockers.length) {
    const blk = r.active_blockers[0];
    return `Clear blocker: ${blk.slice(0, 60)}${blk.length > 60 ? "…" : ""}`;
  }
  if (r.days_behind_schedule > 30) return "Escalate to exec sponsor and re-baseline the plan";
  if (r.days_behind_schedule > 0) return `Run recovery plan to make up ${r.days_behind_schedule}d`;
  if (r.days_to_go_live !== null && r.days_to_go_live < 0) return "Go-live overdue — set a new committed date";
  if (r.days_to_go_live !== null && r.days_to_go_live <= 30) return "Confirm go-live readiness checklist";
  return "On track — maintain weekly cadence";
}

export const AGENT_DISPLAY: Record<string, string> = {
  CustomerHealthAgent: "Health Assessment",
  ImplementationAgent: "Implementation Report",
  BriefingAgent: "Executive Briefing",
  EscalationCommanderAgent: "Escalation Command",
  SkeptikQAAgent: "Skeptik QA Review",
  VPChiefOfStaffAgent: "VP Weekly Review",
  ExpansionOpportunityAgent: "Expansion Opportunity",
  QBRPreparationAgent: "QBR Preparation",
  SuccessPlanAgent: "Success Plan",
  KickoffDeckAgent: "Kickoff Deck",
  BullCaseAgent: "Bull Case",
  BearCaseAgent: "Bear Case",
  SynthesisAgent: "Debate Synthesis",
};

export const AGENT_GROUPS: Record<string, string> = {
  CustomerHealthAgent: "Assess",
  ImplementationAgent: "Assess",
  ExpansionOpportunityAgent: "Grow",
  QBRPreparationAgent: "Grow",
  SuccessPlanAgent: "Grow",
  BriefingAgent: "Communicate",
  KickoffDeckAgent: "Communicate",
  BullCaseAgent: "Verify",
  BearCaseAgent: "Verify",
  SynthesisAgent: "Verify",
  EscalationCommanderAgent: "Respond",
  SkeptikQAAgent: "Verify",
  VPChiefOfStaffAgent: "Portfolio",
};

export function agentDisplayName(name: string): string {
  return AGENT_DISPLAY[name] || name.replace("Agent", "").trim() || name;
}
