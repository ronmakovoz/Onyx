import { NextResponse } from "next/server";
import { env } from "cloudflare:workers";
import { accounts, agents, formatMoney, LINX_PRODUCT_CONTEXT, solutionProducts } from "../../lib/data";

export const dynamic = "force-dynamic";

type Payload = { agentId?: unknown; accountId?: unknown };

function mockReport(agentId: string, accountId: number | null) {
  const account = accounts.find((item) => item.id === accountId) ?? accounts[0];
  const solutionNames = account.solutions.map((id) => solutionProducts.find((product) => product.id === id)?.name).filter(Boolean);
  if (agentId === "VPChiefOfStaff") return `VP CUSTOMER SUCCESS WEEKLY REVIEW\n\nPORTFOLIO POSITION\nThe portfolio is stable, but $3.1M in near-term renewals requires focused execution. Three high-risk accounts share a consistent pattern: incomplete source coverage, weak remediation ownership, or sponsor change.\n\nTOP PRIORITIES\n1. Recover Aperture Health with an executive-backed connector plan and weekly access-review checkpoints.\n2. Rebuild Pioneer Systems' value narrative around risk reduction and remediation throughput before renewal.\n3. Assign owners for Keystone Energy's service-account population and re-baseline the Identity Graph rollout.\n\nPLATFORM FOUNDATION\nIdentity Graph, intelligence, automation, and Autopilot support every solution motion; they should be positioned as the shared operating layer, not sold as separate customer use cases.\n\nSOLUTION GROWTH\nPrioritize AI Access Control at Northstar Financial, Agentic Identity Governance at Meridian Media, and JIT Access at Vertex Commerce. Combined modeled whitespace is $1.0M.\n\nOPERATING DECISION\nMove implementation specialists toward the three renewal-critical programs for the next two weeks; protect expansion work only where the core identity program is already healthy.`;
  if (agentId === "SkeptikQA") return `SKEPTIK QA REVIEW — ${account.name}\n\nCLAIMS TO CHALLENGE\n• Adoption alone does not prove durable value; confirm that review completion and remediation throughput remain high.\n• The expansion recommendation assumes executive sponsorship remains active. Validate budget owner, urgency, and a measurable success criterion.\n• Peer adoption is directional evidence, not proof of fit. Confirm the customer's identity architecture and operating maturity.\n\nMISSING EVIDENCE\n1. Baseline-to-current reduction in excessive privilege.\n2. Named owner for the next capability.\n3. Renewal decision process and economic buyer validation.\n\nCONFIDENCE\n84% — sound direction, but the business case should include harder before/after evidence.`;
  return `${agents.find((item) => item.id === agentId)?.name?.toUpperCase() || "ACCOUNT INTELLIGENCE"} — ${account.name}\n\nEXECUTIVE READOUT\n${account.name} is a ${account.risk.toLowerCase()}-risk ${account.tier.toLowerCase()} account with ${formatMoney(account.arr)} ARR, health ${account.health}/100, and ${account.adoption}% program adoption. ${account.riskReason}\n\nPLATFORM FOUNDATION\nThe account's connected identity data is modeled in the Linx Identity Graph, where identity intelligence and automation support the active program.\n\nCURRENT SOLUTION FOOTPRINT\n${solutionNames.map((name) => `• ${name}`).join("\n")}\n\nIDENTITY PROGRAM SIGNALS\n• ${account.identities.toLocaleString()} identities governed across ${account.integrations} connected systems.\n• ${account.risksResolved} identity risks remediated and ${account.reviewCompletion}% access-review completion.\n\nRECOMMENDED MOVE\n${account.nextAction}\n\nSUCCESS CRITERIA\n1. Name the executive owner and technical operator.\n2. Establish a 30-day baseline and target metric.\n3. Close the highest-risk identity workflow in-platform.\n4. Document the measurable security, productivity, and audit outcome.\n\nCOMMERCIAL POSITION\n${account.expansion > 0 ? `There is ${formatMoney(account.expansion)} in modeled whitespace, but expansion should follow proof of durable adoption.` : "Stabilize the core program before introducing expansion."}`;
}

export async function POST(request: Request) {
  let body: Payload;
  try { body = await request.json() as Payload; } catch { return NextResponse.json({ error: "Invalid request." }, { status: 400 }); }
  const agentId = typeof body.agentId === "string" ? body.agentId : "IdentityProgramHealth";
  const accountId = Number.isFinite(Number(body.accountId)) ? Number(body.accountId) : null;
  const agent = agents.find((item) => item.id === agentId);
  if (!agent) return NextResponse.json({ error: "Unknown agent." }, { status: 400 });

  const bindings = env as unknown as { ANTHROPIC_API_KEY?: string; ANTHROPIC_MODEL?: string };
  const apiKey = bindings.ANTHROPIC_API_KEY || process.env.ANTHROPIC_API_KEY;
  const model = bindings.ANTHROPIC_MODEL || process.env.ANTHROPIC_MODEL || "claude-sonnet-5";
  if (!apiKey) return NextResponse.json({ report: mockReport(agentId, accountId), model: `${agent.tier} demo`, confidence: 88, live: false });

  const account = accounts.find((item) => item.id === accountId);
  const context = account ? JSON.stringify(account) : JSON.stringify(accounts);
  const prompt = `You are the ${agent.name} for a Linx Security Customer Success executive. ${agent.description}

PRODUCT REFERENCE — treat this as authoritative:
${LINX_PRODUCT_CONTEXT}

Use only the supplied synthetic customer data and the product reference above. Produce a concise executive document with uppercase section headings, quantified evidence, clear risks, and 3-5 specific next actions. Separate PLATFORM FOUNDATION from CURRENT SOLUTION FOOTPRINT and RECOMMENDED SOLUTION. Do not describe the Identity Graph, analytics, Copilot, automation, or Autopilot as customer solution modules. When discussing agents, distinguish Agentic Identity Governance (inventory, ownership, lifecycle, access policy) from AI Access Control (inline MCP tool-call enforcement and attribution). Never claim the customer data is production data.\n\nCONTEXT:\n${context}`;

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
