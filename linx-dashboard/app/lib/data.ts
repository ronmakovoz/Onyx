export type Risk = "High" | "Medium" | "Low";

export type Account = {
  id: number;
  name: string;
  industry: string;
  tier: string;
  region: string;
  arr: number;
  health: number;
  risk: Risk;
  renewalDays: number;
  adoption: number;
  identities: number;
  integrations: number;
  risksResolved: number;
  reviewCompletion: number;
  expansion: number;
  owner: string;
  champion: string;
  riskReason: string;
  nextAction: string;
  solutions: string[];
};

export type SolutionProduct = {
  id: string;
  name: string;
  short: string;
  description: string;
  outcome: string;
  accent: string;
};

export const solutionProducts: SolutionProduct[] = [
  { id: "iga", name: "Modern IGA", short: "IGA", description: "Access requests, approvals, provisioning, and risk-centric user access reviews.", outcome: "Make governance continuous, contextual, and audit-ready.", accent: "#f2c94c" },
  { id: "ispm", name: "Identity Security Posture Management", short: "ISPM", description: "Continuously find dormant accounts, privilege sprawl, SSO bypass, weak MFA, and hidden access paths.", outcome: "Understand identity risk and remediate it directly in Linx.", accent: "#ff7d5f" },
  { id: "jit", name: "Just-in-Time Access", short: "JIT", description: "Risk-evaluated, time-bound entitlements that revoke automatically when the task ends.", outcome: "Replace standing privilege with right-sized access.", accent: "#48c7a7" },
  { id: "lifecycle", name: "Identity Lifecycle Management", short: "Lifecycle", description: "Event-driven joiner, mover, and leaver orchestration across every connected system.", outcome: "Keep access aligned from first day through final deprovisioning.", accent: "#5aa7ff" },
  { id: "agentic", name: "Non-Human & Agentic Identity Governance", short: "NHI + Agents", description: "Discover service accounts, API keys, bots, and AI agents; map each to an owner, purpose, access, and audit trail.", outcome: "Govern every identity type with the same least-privilege model.", accent: "#b89cff" },
  { id: "ai-access", name: "AI Access Control", short: "AI Control", description: "An inline MCP gateway that evaluates every tool call before execution and attributes it to the full identity chain.", outcome: "Control what agents actually do—not only what servers they can reach.", accent: "#ff9f43" },
];

export const platformCapabilities = [
  { id: "integrations", name: "Flexible integrations", stage: "Connect", description: "Agentlessly ingest identity and entitlement data through out-of-the-box or custom connectors, using scoped APIs and protocol context from systems such as OAuth, SCIM, and SAML." },
  { id: "graph", name: "Identity Graph", stage: "Map", description: "Normalize and correlate humans, non-human identities, AI agents, accounts, roles, entitlements, and resources." },
  { id: "intelligence", name: "Identity intelligence", stage: "Understand", description: "Classify privilege, map blast radius, compare peers and usage, and apply semantic reasoning to access." },
  { id: "copilot", name: "AI Copilot", stage: "Decide", description: "Investigate, explain, recommend, report, and trigger governed action from identity-specific context." },
  { id: "automation", name: "Automation & remediation", stage: "Act", description: "Close the loop with policy enforcement, governance workflows, lifecycle automation, and in-platform remediation." },
  { id: "autopilot", name: "Autopilot", stage: "Operate", description: "Monitor continuously, remediate high-confidence risk autonomously, and escalate ambiguous decisions with full context." },
] as const;

export type ExpansionPlay = {
  productId: string;
  timing: "Now" | "Next" | "Later";
  rationale: string;
  proof: string;
};

export const expansionPlays: Record<number, ExpansionPlay[]> = {
  1: [
    { productId: "ai-access", timing: "Now", rationale: "The account has mature governance and a security-architecture sponsor ready to address agent actions through MCP.", proof: "Define one high-risk MCP workflow, tool-level policy, attribution chain, and blocked-action evidence." },
    { productId: "agentic", timing: "Next", rationale: "AI Access Control is stronger when every agent and underlying NHI has an owner, purpose, and governed lifecycle.", proof: "Inventory agents, map owners and resources, and close unowned or over-privileged access." },
  ],
  2: [],
  3: [
    { productId: "jit", timing: "Now", rationale: "The account still relies on persistent administrator roles despite healthy lifecycle adoption.", proof: "Convert five privileged roles to time-bound access and measure standing privilege removed." },
    { productId: "agentic", timing: "Later", rationale: "Once JIT is proven for humans, extend the same ownership and least-privilege policy to service and agent identities.", proof: "Establish ownership and review coverage for the highest-risk non-human identities." },
  ],
  4: [
    { productId: "ai-access", timing: "Now", rationale: "The core program and NHI governance are mature enough to extend policy into agentic tool calls.", proof: "Pilot inline enforcement for one MCP server with a complete agent-to-human audit trail." },
  ],
  5: [],
  6: [
    { productId: "ispm", timing: "Now", rationale: "Lifecycle automation covers access changes, but the account lacks continuous detection of accumulated privilege and hidden risk.", proof: "Baseline dormant access, privilege outliers, and remediation throughput across contractor populations." },
    { productId: "jit", timing: "Next", rationale: "Contractor workflows create a natural entry point for time-bound privileged access.", proof: "Move one elevated contractor role from standing to automatically expiring access." },
  ],
  7: [
    { productId: "agentic", timing: "Now", rationale: "The account has healthy core adoption and a known gap in AI-agent inventory and ownership.", proof: "Discover all agents, map users and downstream access, and assign accountable owners." },
    { productId: "ai-access", timing: "Next", rationale: "After inventory and ownership, extend the same access profiles to real-time MCP tool-call enforcement.", proof: "Approve and block representative tool calls with attributable audit records." },
  ],
  8: [
    { productId: "jit", timing: "Now", rationale: "Strong audit evidence makes standing privileged access the next measurable risk-reduction target.", proof: "Tie automatic privilege expiry to the next SOX evidence cycle." },
    { productId: "lifecycle", timing: "Next", rationale: "Event-driven lifecycle controls reduce the access drift that otherwise accumulates between certifications.", proof: "Automate role-change and termination events for the highest-risk workforce population." },
  ],
  9: [
    { productId: "iga", timing: "Now", rationale: "The account has posture visibility and lifecycle automation but lacks a unified, risk-centric certification motion.", proof: "Run one contextual access review with automated remediation and an audit-ready evidence package." },
    { productId: "jit", timing: "Next", rationale: "The healthy lifecycle program can support policy-driven, automatically expiring elevated access.", proof: "Convert a high-volume privileged request to self-service JIT." },
  ],
  10: [],
};

export const LINX_PRODUCT_CONTEXT = `Linx is an AI-native identity security and governance platform for human, non-human, and agentic identities.
Foundation: flexible, agentless integrations feed the Identity Graph; the graph normalizes identity, account, entitlement, role, application, and resource relationships. Integration protocols have distinct roles: OAuth authorizes scoped API access for a connector; SCIM standardizes user and group provisioning and deprovisioning; SAML supplies authentication and federation context. Do not present them as interchangeable data transports. Linx correlates those signals with connector APIs, directories, webhooks, and files, then uses SCIM or target APIs for write-back where supported and approved.
Intelligence and action: Identity Intelligence analyzes privilege, blast radius, peers, usage, behavior, and semantic context. Copilot supports investigation, explanation, reporting, and governed actions. Automation & Remediation closes the loop. Autopilot continuously monitors and either remediates policy-aligned risk or escalates ambiguous decisions with context.
Solution modules: Modern IGA; Identity Security Posture Management; Just-in-Time Access; Identity Lifecycle Management; Non-Human & Agentic Identity Governance; AI Access Control.
Important distinction: Agentic Identity Governance discovers agents and governs their ownership, lifecycle, access, and policy. AI Access Control is the inline MCP gateway that evaluates individual tool calls before execution and logs the full agent-to-human or agent-to-NHI identity chain.`;

export const accounts: Account[] = [
  { id: 1, name: "Northstar Financial", industry: "Financial Services", tier: "Strategic", region: "AMER", arr: 1480000, health: 91, risk: "Low", renewalDays: 142, adoption: 88, identities: 126400, integrations: 42, risksResolved: 738, reviewCompletion: 96, expansion: 380000, owner: "Maya Chen", champion: "Strong", riskReason: "No material risk; AI access-control expansion is ready.", nextAction: "Launch an MCP gateway policy workshop with Security Architecture.", solutions: ["iga", "ispm", "jit", "lifecycle"] },
  { id: 2, name: "Aperture Health", industry: "Healthcare", tier: "Enterprise", region: "AMER", arr: 1120000, health: 54, risk: "High", renewalDays: 38, adoption: 61, identities: 84200, integrations: 27, risksResolved: 312, reviewCompletion: 72, expansion: 0, owner: "Jordan Patel", champion: "At risk", riskReason: "Access-review completion slipped and two HRIS connectors remain blocked.", nextAction: "Run a 30-day connector and certification recovery plan with weekly executive checkpoints.", solutions: ["iga", "ispm"] },
  { id: 3, name: "Vertex Commerce", industry: "Digital Commerce", tier: "Enterprise", region: "EMEA", arr: 980000, health: 78, risk: "Medium", renewalDays: 76, adoption: 74, identities: 69300, integrations: 31, risksResolved: 445, reviewCompletion: 89, expansion: 260000, owner: "Maya Chen", champion: "Strong", riskReason: "Privileged-access program is still mostly standing access.", nextAction: "Convert the first five admin roles to JIT access.", solutions: ["iga", "ispm", "lifecycle"] },
  { id: 4, name: "Summit Cloud", industry: "SaaS & Cloud", tier: "Strategic", region: "AMER", arr: 1360000, health: 85, risk: "Low", renewalDays: 189, adoption: 92, identities: 101800, integrations: 38, risksResolved: 694, reviewCompletion: 98, expansion: 440000, owner: "Elena Rossi", champion: "Strong", riskReason: "Healthy program with rapid growth in non-human and agentic identities.", nextAction: "Extend governance into inline MCP tool-call enforcement.", solutions: ["iga", "ispm", "jit", "lifecycle", "agentic"] },
  { id: 5, name: "Keystone Energy", industry: "Critical Infrastructure", tier: "Enterprise", region: "EMEA", arr: 890000, health: 48, risk: "High", renewalDays: 57, adoption: 58, identities: 47300, integrations: 19, risksResolved: 228, reviewCompletion: 68, expansion: 0, owner: "Jordan Patel", champion: "Developing", riskReason: "On-prem directory coverage and remediation ownership are incomplete.", nextAction: "Escalate the connector plan and assign service-account remediation owners by business unit.", solutions: ["ispm"] },
  { id: 6, name: "Atlas Logistics", industry: "Transportation", tier: "Enterprise", region: "APAC", arr: 760000, health: 73, risk: "Medium", renewalDays: 94, adoption: 69, identities: 51600, integrations: 24, risksResolved: 351, reviewCompletion: 84, expansion: 210000, owner: "Sam Okafor", champion: "Strong", riskReason: "Lifecycle automation covers employees but not contractors.", nextAction: "Extend mover and offboarding flows to contractor populations.", solutions: ["iga", "lifecycle"] },
  { id: 7, name: "Meridian Media", industry: "Media", tier: "Growth", region: "AMER", arr: 540000, health: 82, risk: "Low", renewalDays: 211, adoption: 86, identities: 28900, integrations: 22, risksResolved: 306, reviewCompletion: 93, expansion: 180000, owner: "Elena Rossi", champion: "Strong", riskReason: "Healthy adoption; agent inventory and ownership are the next gap.", nextAction: "Discover AI agents, assign owners, then scope AI Access Control.", solutions: ["iga", "ispm", "lifecycle"] },
  { id: 8, name: "Crescent Bio", industry: "Life Sciences", tier: "Enterprise", region: "EMEA", arr: 830000, health: 66, risk: "Medium", renewalDays: 121, adoption: 71, identities: 44200, integrations: 25, risksResolved: 287, reviewCompletion: 80, expansion: 230000, owner: "Sam Okafor", champion: "Developing", riskReason: "Audit evidence is strong, but JIT adoption remains limited.", nextAction: "Tie automatic privilege expiry to the next SOX evidence cycle.", solutions: ["iga", "ispm"] },
  { id: 9, name: "Harbor Retail", industry: "Retail", tier: "Growth", region: "APAC", arr: 460000, health: 76, risk: "Low", renewalDays: 168, adoption: 79, identities: 33400, integrations: 18, risksResolved: 264, reviewCompletion: 91, expansion: 140000, owner: "Sam Okafor", champion: "Strong", riskReason: "Healthy posture and lifecycle adoption; certifications remain fragmented.", nextAction: "Run a contextual access review with automated remediation and packaged audit evidence.", solutions: ["ispm", "lifecycle"] },
  { id: 10, name: "Pioneer Systems", industry: "Technology", tier: "Enterprise", region: "AMER", arr: 1040000, health: 59, risk: "High", renewalDays: 29, adoption: 64, identities: 77600, integrations: 29, risksResolved: 394, reviewCompletion: 75, expansion: 0, owner: "Jordan Patel", champion: "At risk", riskReason: "Executive sponsor changed and the remediation backlog is growing.", nextAction: "Rebuild the executive value narrative around identity-risk reduction and remediation throughput.", solutions: ["iga", "ispm", "jit"] },
];

export const implementations = [
  { account: "Aperture Health", owner: "Nora Kim", confidence: "Low", progress: 58, target: "Aug 29", delay: 18, phase: "Access review launch", blocker: "Workday and legacy HRIS mappings", action: "Executive connector escalation" },
  { account: "Keystone Energy", owner: "Luis Martin", confidence: "Low", progress: 41, target: "Sep 18", delay: 27, phase: "Identity Graph coverage", blocker: "On-prem AD service account ownership", action: "Assign NHI owners by business unit" },
  { account: "Pioneer Systems", owner: "Nora Kim", confidence: "Medium", progress: 72, target: "Aug 16", delay: 9, phase: "Remediation workflows", blocker: "Change-control approval", action: "Secure sponsor sign-off this week" },
  { account: "Vertex Commerce", owner: "Luis Martin", confidence: "High", progress: 86, target: "Aug 8", delay: 0, phase: "JIT pilot", blocker: "None", action: "Confirm privileged-role cutover" },
  { account: "Atlas Logistics", owner: "Priya Shah", confidence: "High", progress: 79, target: "Sep 2", delay: 0, phase: "Lifecycle automation", blocker: "None", action: "Validate contractor mover events" },
  { account: "Crescent Bio", owner: "Priya Shah", confidence: "Medium", progress: 64, target: "Sep 12", delay: 5, phase: "Certification design", blocker: "Reviewer hierarchy cleanup", action: "Finalize reviewer ownership model" },
];

export const agents = [
  { id: "IdentityProgramHealth", name: "Identity Program Health", group: "Monitor", tier: "Sonnet", description: "Scores adoption, risk reduction, governance maturity, and renewal health." },
  { id: "RenewalPredictor", name: "Renewal Predictor", group: "Monitor", tier: "Sonnet", description: "Explains renewal risk and the evidence required to change the forecast." },
  { id: "ImplementationNavigator", name: "Implementation Navigator", group: "Deliver", tier: "Sonnet", description: "Turns rollout blockers into a sequenced identity-program recovery plan." },
  { id: "ExecutiveBriefing", name: "Executive Briefing", group: "Deliver", tier: "Sonnet", description: "Creates CISO-ready account briefings grounded in adoption and outcomes." },
  { id: "ExpansionArchitect", name: "Expansion Architect", group: "Grow", tier: "Sonnet", description: "Finds evidence-backed whitespace across Linx solution modules without mislabeling shared platform capabilities." },
  { id: "SkeptikQA", name: "Skeptik QA", group: "Govern", tier: "Opus", description: "Stress-tests claims, assumptions, and unsupported recommendations." },
  { id: "VPChiefOfStaff", name: "VP CS Chief of Staff", group: "Lead", tier: "Opus", description: "Synthesizes portfolio risk, capacity, renewals, and expansion priorities." },
  { id: "RemediationPlanner", name: "Remediation Planner", group: "Deliver", tier: "Haiku", description: "Drafts concise next actions for identity-risk and governance gaps." },
];

export const auditRuns = [
  { id: 1084, agent: "Identity Program Health", account: "Aperture Health", model: "claude-sonnet-5", tokens: 5128, cost: 0.0384, confidence: 87, time: "Today · 9:42 AM" },
  { id: 1083, agent: "VP CS Chief of Staff", account: "Portfolio", model: "claude-opus-4-6", tokens: 8744, cost: 0.2441, confidence: 92, time: "Today · 8:10 AM" },
  { id: 1082, agent: "Expansion Architect", account: "Summit Cloud", model: "claude-sonnet-5", tokens: 4688, cost: 0.0352, confidence: 89, time: "Yesterday · 4:18 PM" },
  { id: 1081, agent: "Implementation Navigator", account: "Keystone Energy", model: "claude-sonnet-5", tokens: 6240, cost: 0.0468, confidence: 84, time: "Yesterday · 2:03 PM" },
  { id: 1080, agent: "Skeptik QA", account: "Pioneer Systems", model: "claude-opus-4-6", tokens: 7312, cost: 0.2050, confidence: 94, time: "Yesterday · 11:26 AM" },
];

export const formatMoney = (value: number) =>
  value >= 1_000_000 ? `$${(value / 1_000_000).toFixed(1)}M` : `$${Math.round(value / 1000)}K`;

export const riskColor = (risk: Risk) =>
  ({ High: "#d65745", Medium: "#b97b14", Low: "#2c8f70" })[risk];

export const totalArr = accounts.reduce((sum, account) => sum + account.arr, 0);
export const atRiskArr = accounts.filter((account) => account.risk === "High").reduce((sum, account) => sum + account.arr, 0);
export const expansionArr = accounts.reduce((sum, account) => sum + account.expansion, 0);
