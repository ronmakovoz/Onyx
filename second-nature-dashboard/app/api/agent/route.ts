import { NextResponse } from "next/server";
import { env } from "cloudflare:workers";
import { accounts, agents, formatMoney } from "../../lib/data";

export const dynamic = "force-dynamic";

type Payload = { agentId?: unknown; accountId?: unknown };

function mockReport(agentId: string, accountId: number | null) {
  const account = accounts.find((item) => item.id === accountId) ?? accounts[0];
  if (agentId === "VPChiefOfStaff") return `VP CUSTOMER SUCCESS WEEKLY REVIEW\n\nPORTFOLIO POSITION\nThe portfolio is stable, but $3.1M in near-term renewals requires focused execution. Three high-risk accounts share a consistent pattern: incomplete rollout ownership, weak certification evidence, or sponsor change.\n\nTOP PRIORITIES\n1. Recover Aperture Health with an executive-backed LMS sync plan and weekly certification checkpoints.\n2. Rebuild Pioneer Systems' value narrative around ramp time, readiness lift, and role-play participation before renewal.\n3. Assign regional content owners for Keystone Energy and re-baseline multilingual scoring calibration.\n\nGROWTH\nPrioritize Deal Coach at Northstar Financial, Support and multilingual expansion at Summit Cloud, and live-opportunity coaching at Vertex Commerce. Combined modeled whitespace is $1.0M.\n\nOPERATING DECISION\nMove rollout specialists toward the three renewal-critical programs for the next two weeks; protect expansion work only where the core role-play program is already healthy.`;
  if (agentId === "SkeptikQA") return `SKEPTIK QA REVIEW — ${account.name}\n\nCLAIMS TO CHALLENGE\n• Participation alone does not prove durable value; confirm that certification and objective readiness scores are improving.\n• The expansion recommendation assumes executive sponsorship remains active. Validate budget owner, urgency, and a measurable success criterion.\n• Peer adoption is directional evidence, not proof of fit. Confirm the customer's enablement workflow, audience, and manager operating cadence.\n\nMISSING EVIDENCE\n1. Baseline-to-current improvement in role-play scores and real-world outcomes.\n2. Named owner for the next capability or cohort.\n3. Renewal decision process and economic buyer validation.\n\nCONFIDENCE\n84% — sound direction, but the business case should include harder before-and-after evidence.`;
  return `${agents.find((item) => item.id === agentId)?.name?.toUpperCase() || "ACCOUNT INTELLIGENCE"} — ${account.name}\n\nEXECUTIVE READOUT\n${account.name} is a ${account.risk.toLowerCase()}-risk ${account.tier.toLowerCase()} account with ${formatMoney(account.arr)} ARR, health ${account.health}/100, and ${account.adoption}% learner adoption. ${account.riskReason}\n\nREADINESS PROGRAM SIGNALS\n• ${account.learners.toLocaleString()} learners completed ${account.roleplays.toLocaleString()} role plays across ${account.scenarios} active scenarios.\n• Certification is ${account.certification}% with a ${account.scoreLift}% objective readiness-score lift.\n• Current footprint covers ${account.products.length} Second Nature capabilities and ${account.integrations} connected systems.\n\nRECOMMENDED MOVE\n${account.nextAction}\n\nSUCCESS CRITERIA\n1. Name the executive sponsor and program operator.\n2. Establish a 30-day participation, certification, and readiness baseline.\n3. Close the highest-impact knowledge or behavior gap with assigned practice.\n4. Document the measurable ramp, performance, or manager-capacity outcome.\n\nCOMMERCIAL POSITION\n${account.expansion > 0 ? `There is ${formatMoney(account.expansion)} in modeled whitespace, but expansion should follow proof of durable learner and manager adoption.` : "Stabilize the core program before introducing expansion."}`;
}

export async function POST(request: Request) {
  let body: Payload;
  try { body = await request.json() as Payload; } catch { return NextResponse.json({ error: "Invalid request." }, { status: 400 }); }
  const agentId = typeof body.agentId === "string" ? body.agentId : "ReadinessHealth";
  const accountId = Number.isFinite(Number(body.accountId)) ? Number(body.accountId) : null;
  const agent = agents.find((item) => item.id === agentId);
  if (!agent) return NextResponse.json({ error: "Unknown agent." }, { status: 400 });

  const bindings = env as unknown as { ANTHROPIC_API_KEY?: string; ANTHROPIC_MODEL?: string };
  const apiKey = bindings.ANTHROPIC_API_KEY || process.env.ANTHROPIC_API_KEY;
  const model = bindings.ANTHROPIC_MODEL || process.env.ANTHROPIC_MODEL || "claude-sonnet-5";
  if (!apiKey) return NextResponse.json({ report: mockReport(agentId, accountId), model: `${agent.tier} demo`, confidence: 88, live: false });

  const account = accounts.find((item) => item.id === accountId);
  const context = account ? JSON.stringify(account) : JSON.stringify(accounts);
  const prompt = `You are the ${agent.name} for a Second Nature Customer Success executive. ${agent.description}\nUse only the supplied synthetic data. Produce a concise executive document with uppercase section headings, quantified evidence, clear risks, and 3-5 specific next actions. Never claim the data is production data. Frame outcomes around AI role-play adoption, certification, readiness, manager leverage, renewal, and expansion.\n\nCONTEXT:\n${context}`;

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
