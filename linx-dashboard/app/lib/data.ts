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
  products: string[];
};

export type Product = {
  id: string;
  name: string;
  short: string;
  description: string;
  accent: string;
};

export const products: Product[] = [
  { id: "iga", name: "Modern IGA", short: "IGA", description: "Risk-centric access reviews, approvals, and governance workflows.", accent: "#f2c94c" },
  { id: "ispm", name: "Identity Security Posture", short: "ISPM", description: "Continuous identity-risk discovery and in-platform remediation.", accent: "#ff7d5f" },
  { id: "jit", name: "Just-in-Time Access", short: "JIT", description: "Time-bound, right-sized privileged access with automatic revocation.", accent: "#48c7a7" },
  { id: "lifecycle", name: "Lifecycle Management", short: "JML", description: "Automated joiner, mover, and leaver access orchestration.", accent: "#5aa7ff" },
  { id: "nhi", name: "Non-Human Identity Governance", short: "NHI", description: "Ownership, purpose, and least privilege for service and agentic identities.", accent: "#b89cff" },
  { id: "ai-access", name: "AI Access Control", short: "AI Access", description: "MCP gateway enforcement and auditability for agent actions.", accent: "#ff9f43" },
  { id: "graph", name: "Identity Graph", short: "Graph", description: "A normalized source of truth for every identity-to-resource relationship.", accent: "#75d7e8" },
  { id: "autopilot", name: "Autopilot", short: "Autopilot", description: "Always-on identity analysis, remediation, and escalation.", accent: "#94d36b" },
];

export const accounts: Account[] = [
  { id: 1, name: "Northstar Financial", industry: "Financial Services", tier: "Strategic", region: "AMER", arr: 1480000, health: 91, risk: "Low", renewalDays: 142, adoption: 88, identities: 126400, integrations: 42, risksResolved: 738, reviewCompletion: 96, expansion: 380000, owner: "Maya Chen", champion: "Strong", riskReason: "No material risk; AI access-control expansion is ready.", nextAction: "Launch MCP gateway design workshop with Security Architecture.", products: ["iga", "ispm", "jit", "lifecycle", "graph", "autopilot"] },
  { id: 2, name: "Aperture Health", industry: "Healthcare", tier: "Enterprise", region: "AMER", arr: 1120000, health: 54, risk: "High", renewalDays: 38, adoption: 61, identities: 84200, integrations: 27, risksResolved: 312, reviewCompletion: 72, expansion: 0, owner: "Jordan Patel", champion: "At risk", riskReason: "Access-review completion slipped and two HRIS connectors remain blocked.", nextAction: "Run a 30-day recovery plan with weekly executive checkpoints.", products: ["iga", "ispm", "graph"] },
  { id: 3, name: "Vertex Commerce", industry: "Digital Commerce", tier: "Enterprise", region: "EMEA", arr: 980000, health: 78, risk: "Medium", renewalDays: 76, adoption: 74, identities: 69300, integrations: 31, risksResolved: 445, reviewCompletion: 89, expansion: 260000, owner: "Maya Chen", champion: "Strong", riskReason: "Privileged-access program is still mostly standing access.", nextAction: "Convert the first five admin roles to JIT access.", products: ["iga", "ispm", "lifecycle", "graph"] },
  { id: 4, name: "Summit Cloud", industry: "SaaS & Cloud", tier: "Strategic", region: "AMER", arr: 1360000, health: 85, risk: "Low", renewalDays: 189, adoption: 92, identities: 101800, integrations: 38, risksResolved: 694, reviewCompletion: 98, expansion: 440000, owner: "Elena Rossi", champion: "Strong", riskReason: "Healthy program with rapid non-human identity growth.", nextAction: "Package NHI governance and Autopilot expansion business case.", products: ["iga", "ispm", "jit", "lifecycle", "nhi", "graph"] },
  { id: 5, name: "Keystone Energy", industry: "Critical Infrastructure", tier: "Enterprise", region: "EMEA", arr: 890000, health: 48, risk: "High", renewalDays: 57, adoption: 58, identities: 47300, integrations: 19, risksResolved: 228, reviewCompletion: 68, expansion: 0, owner: "Jordan Patel", champion: "Developing", riskReason: "On-prem directory coverage and remediation ownership are incomplete.", nextAction: "Escalate connector plan and assign remediation owners by business unit.", products: ["ispm", "graph"] },
  { id: 6, name: "Atlas Logistics", industry: "Transportation", tier: "Enterprise", region: "APAC", arr: 760000, health: 73, risk: "Medium", renewalDays: 94, adoption: 69, identities: 51600, integrations: 24, risksResolved: 351, reviewCompletion: 84, expansion: 210000, owner: "Sam Okafor", champion: "Strong", riskReason: "Lifecycle automation covers employees but not contractors.", nextAction: "Extend mover and offboarding flows to contractor populations.", products: ["iga", "lifecycle", "graph"] },
  { id: 7, name: "Meridian Media", industry: "Media", tier: "Growth", region: "AMER", arr: 540000, health: 82, risk: "Low", renewalDays: 211, adoption: 86, identities: 28900, integrations: 22, risksResolved: 306, reviewCompletion: 93, expansion: 180000, owner: "Elena Rossi", champion: "Strong", riskReason: "Healthy adoption; agentic identity inventory is the next gap.", nextAction: "Discover AI agents and prioritize AI Access Control pilot.", products: ["iga", "ispm", "lifecycle", "graph", "autopilot"] },
  { id: 8, name: "Crescent Bio", industry: "Life Sciences", tier: "Enterprise", region: "EMEA", arr: 830000, health: 66, risk: "Medium", renewalDays: 121, adoption: 71, identities: 44200, integrations: 25, risksResolved: 287, reviewCompletion: 80, expansion: 230000, owner: "Sam Okafor", champion: "Developing", riskReason: "Audit evidence is strong, but JIT adoption remains limited.", nextAction: "Tie JIT rollout to the next SOX evidence cycle.", products: ["iga", "ispm", "graph"] },
  { id: 9, name: "Harbor Retail", industry: "Retail", tier: "Growth", region: "APAC", arr: 460000, health: 76, risk: "Low", renewalDays: 168, adoption: 79, identities: 33400, integrations: 18, risksResolved: 264, reviewCompletion: 91, expansion: 140000, owner: "Sam Okafor", champion: "Strong", riskReason: "Healthy core deployment; lifecycle automation is under-scoped.", nextAction: "Quantify help-desk savings from automated JML workflows.", products: ["ispm", "lifecycle", "graph"] },
  { id: 10, name: "Pioneer Systems", industry: "Technology", tier: "Enterprise", region: "AMER", arr: 1040000, health: 59, risk: "High", renewalDays: 29, adoption: 64, identities: 77600, integrations: 29, risksResolved: 394, reviewCompletion: 75, expansion: 0, owner: "Jordan Patel", champion: "At risk", riskReason: "Executive sponsor changed and remediation backlog is growing.", nextAction: "Rebuild the executive value narrative around measurable risk reduction.", products: ["iga", "ispm", "jit", "graph"] },
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
  { id: "ExpansionArchitect", name: "Expansion Architect", group: "Grow", tier: "Sonnet", description: "Finds peer-evidenced whitespace across the Linx platform." },
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
