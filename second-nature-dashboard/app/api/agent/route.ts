import { NextResponse } from "next/server";
import { env } from "cloudflare:workers";
import { accounts, agents, formatMoney } from "../../lib/data";

export const dynamic = "force-dynamic";

type Payload = { agentId?: unknown; accountId?: unknown };

function mockReport(agentId: string, accountId: number | null) {
  const account = accounts.find((item) => item.id === accountId) ?? accounts[0];
  if (agentId === "VPChiefOfStaff") return `VP CUSTOMER SUCCESS WEEKLY REVIEW\n\nPORTFOLIO POSITION\nThe portfolio is stable, but $3.1M in near-term renewals requires focused execution. Three high-risk accounts share a consistent pattern: incomplete property-accounting integration, weak resident activation, or sponsor change.\n\nTOP PRIORITIES\n1. Recover Aperture Residential with an executive-backed AppFolio mapping plan and weekly RBP activation checkpoints.\n2. Rebuild Pioneer Residential's value narrative around lease speed, transparency, ancillary NOI, and operational time saved.\n3. Finalize Keystone Rentals' benefit package, lease addenda, GL codes, and regional owners.\n\nGROWTH\nPrioritize Group Rate Internet at Northstar Property Management, Resident Onboarding at Summit Homes, and Maestro automation at Vertex Property Group. Combined modeled whitespace is $1.0M.\n\nOPERATING DECISION\nMove launch specialists toward the three renewal-critical portfolios for the next two weeks; protect expansion work only where resident activation is already healthy.`;
  if (agentId === "SkeptikQA") return `SKEPTIK QA REVIEW — ${account.name}\n\nCLAIMS TO CHALLENGE\n• Resident activation alone does not prove durable value; confirm lease completion, team time saved, renewal behavior, and operational outcomes.\n• The expansion recommendation assumes executive and property-level ownership remain active. Validate the decision maker, rollout capacity, and measurable success criterion.\n• Peer adoption is directional evidence, not proof of fit. Confirm the portfolio mix, resident needs, existing benefits, and property-accounting workflow.\n\nMISSING EVIDENCE\n1. Baseline-to-current change in lease cycle time, work orders, calls, or ancillary NOI.\n2. Named owners for package design, integration, accounting, and resident communications.\n3. Renewal decision process and owner/investor value narrative.\n\nCONFIDENCE\n84% — sound direction, but the business case should include harder resident, property-manager, and investor outcomes.`;
  return `${agents.find((item) => item.id === agentId)?.name?.toUpperCase() || "ACCOUNT INTELLIGENCE"} — ${account.name}\n\nEXECUTIVE READOUT\n${account.name} is a ${account.risk.toLowerCase()}-risk ${account.tier.toLowerCase()} account with ${formatMoney(account.arr)} ARR, health ${account.health}/100, and ${account.adoption}% platform adoption. ${account.riskReason}\n\nRESIDENT EXPERIENCE SIGNALS\n• ${account.doors.toLocaleString()} doors and ${account.residents.toLocaleString()} residents across ${account.integrations} connected systems.\n• ${account.onboardings.toLocaleString()} annual onboardings, ${account.leaseCompletion}% lease completion, and ${account.rbpActivation}% RBP activation.\n• ${account.teamHoursSaved.toLocaleString()} modeled team hours saved with ${account.products.length} active Second Nature capabilities.\n\nRECOMMENDED MOVE\n${account.nextAction}\n\nSUCCESS CRITERIA\n1. Name the executive sponsor and property-operations owner.\n2. Establish a 30-day baseline for onboarding, activation, lease completion, and operational workload.\n3. Close the highest-impact PAS, addenda, resident-education, or benefit gap.\n4. Document the measurable resident, property-manager, and investor outcome.\n\nCOMMERCIAL POSITION\n${account.expansion > 0 ? `There is ${formatMoney(account.expansion)} in modeled whitespace, but expansion should follow proof of durable resident activation and operational value.` : "Stabilize the core resident experience before introducing expansion."}`;
}

export async function POST(request: Request) {
  let body: Payload;
  try { body = await request.json() as Payload; } catch { return NextResponse.json({ error: "Invalid request." }, { status: 400 }); }
  const agentId = typeof body.agentId === "string" ? body.agentId : "ResidentExperienceHealth";
  const accountId = Number.isFinite(Number(body.accountId)) ? Number(body.accountId) : null;
  const agent = agents.find((item) => item.id === agentId);
  if (!agent) return NextResponse.json({ error: "Unknown agent." }, { status: 400 });

  const bindings = env as unknown as { ANTHROPIC_API_KEY?: string; ANTHROPIC_MODEL?: string };
  const apiKey = bindings.ANTHROPIC_API_KEY || process.env.ANTHROPIC_API_KEY;
  const model = bindings.ANTHROPIC_MODEL || process.env.ANTHROPIC_MODEL || "claude-sonnet-5";
  if (!apiKey) return NextResponse.json({ report: mockReport(agentId, accountId), model: `${agent.tier} demo`, confidence: 88, live: false });

  const account = accounts.find((item) => item.id === accountId);
  const context = account ? JSON.stringify(account) : JSON.stringify(accounts);
  const prompt = `You are the ${agent.name} for a Second Nature Customer Success executive. Second Nature is the property-management Resident Experience Platform at secondnature.com, not the unrelated AI role-play company. ${agent.description}\nUse only the supplied synthetic data. Produce a concise executive document with uppercase section headings, quantified evidence, clear risks, and 3-5 specific next actions. Never claim the data is production data. Frame outcomes around Resident Onboarding, Maestro, Resident Benefits Package activation, lease clarity, resident financial health, property-team workload, investor asset protection, renewal, and expansion.\n\nCONTEXT:\n${context}`;

  try {
    const response = await fetch("https://api.anthropic.com/v1/messages", { method: "POST", headers: { "Content-Type": "application/json", "x-api-key": apiKey, "anthropic-version": "2023-06-01" }, body: JSON.stringify({ model, max_tokens: 1400, messages: [{ role: "user", content: prompt }] }) });
    if (!response.ok) throw new Error(`Anthropic returned ${response.status}`);
    const data = await response.json() as { content?: Array<{ type: string; text?: string }> };
    const report = data.content?.find((item) => item.type === "text")?.text;
    if (!report) throw new Error("Anthropic returned no text");
    return NextResponse.json({ report, model, confidence: 91, live: true });
  } catch (error) {
    console.error("Anthropic agent run failed", error);
    return NextResponse.json({ report: mockReport(agentId, accountId), model: `${agent.tier} fallback`, confidence: 84, live: false });
  }
}
