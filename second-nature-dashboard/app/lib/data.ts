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
  learners: number;
  roleplays: number;
  scenarios: number;
  certification: number;
  scoreLift: number;
  integrations: number;
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
  { id: "roleplay", name: "AI Role Play Scenarios", short: "Role Play", description: "Lifelike 1:1, group, and chat simulations for any customer conversation.", accent: "#ff7452" },
  { id: "courses", name: "Course & Content Builder", short: "Courses", description: "Blend videos, decks, quizzes, and practice into structured learning paths.", accent: "#ffc928" },
  { id: "coaching", name: "AI Coaching & Feedback", short: "Coaching", description: "Objective scoring and personalized, actionable feedback after every session.", accent: "#6c4df6" },
  { id: "insights", name: "Performance Insights", short: "Insights", description: "Manager visibility into progress, trends, strengths, and knowledge gaps.", accent: "#00a98f" },
  { id: "deal-coach", name: "Deal Coach", short: "Deal Coach", description: "Targeted AI coaching for live opportunities, risks, and next steps.", accent: "#2c8cff" },
  { id: "languages", name: "30+ Languages", short: "Global", description: "Localized practice and feedback for globally distributed teams.", accent: "#b886ff" },
  { id: "integrations", name: "Enterprise Integrations", short: "Integrate", description: "Connect LMS, CRM, SAML, and conferencing workflows through SCORM and LTI.", accent: "#55b7d9" },
  { id: "mobile", name: "Mobile Practice", short: "Mobile", description: "Browser-based training on any device with no app download required.", accent: "#f58bb6" },
];

export const accounts: Account[] = [
  { id: 1, name: "Northstar Financial", industry: "Financial Services", tier: "Strategic", region: "AMER", arr: 1480000, health: 91, risk: "Low", renewalDays: 142, adoption: 88, learners: 4260, roleplays: 38740, scenarios: 42, certification: 93, scoreLift: 31, integrations: 5, expansion: 380000, owner: "Maya Chen", champion: "Strong", riskReason: "No material risk; live-deal coaching is the next value frontier.", nextAction: "Launch a Deal Coach design sprint with Revenue Operations.", products: ["roleplay", "courses", "coaching", "insights", "languages", "integrations", "mobile"] },
  { id: 2, name: "Aperture Health", industry: "Healthcare", tier: "Enterprise", region: "AMER", arr: 1120000, health: 54, risk: "High", renewalDays: 38, adoption: 61, learners: 2840, roleplays: 12920, scenarios: 18, certification: 64, scoreLift: 12, integrations: 3, expansion: 0, owner: "Jordan Patel", champion: "At risk", riskReason: "Certification completion slipped and LMS audience sync remains blocked.", nextAction: "Run a 30-day recovery plan with weekly enablement checkpoints.", products: ["roleplay", "courses", "coaching", "insights", "integrations"] },
  { id: 3, name: "Vertex Commerce", industry: "Digital Commerce", tier: "Enterprise", region: "EMEA", arr: 980000, health: 78, risk: "Medium", renewalDays: 76, adoption: 74, learners: 3170, roleplays: 22480, scenarios: 31, certification: 82, scoreLift: 24, integrations: 4, expansion: 260000, owner: "Maya Chen", champion: "Strong", riskReason: "Core role plays are healthy, but coaching is disconnected from live deals.", nextAction: "Pilot Deal Coach with the enterprise new-business team.", products: ["roleplay", "courses", "coaching", "insights", "languages", "mobile"] },
  { id: 4, name: "Summit Cloud", industry: "SaaS & Cloud", tier: "Strategic", region: "AMER", arr: 1360000, health: 85, risk: "Low", renewalDays: 189, adoption: 92, learners: 5120, roleplays: 51690, scenarios: 58, certification: 96, scoreLift: 37, integrations: 6, expansion: 440000, owner: "Elena Rossi", champion: "Strong", riskReason: "Healthy global program with demand from support and partner teams.", nextAction: "Package Support and multilingual expansion with manager insights.", products: ["roleplay", "courses", "coaching", "insights", "deal-coach", "integrations", "mobile"] },
  { id: 5, name: "Keystone Energy", industry: "Energy", tier: "Enterprise", region: "EMEA", arr: 890000, health: 48, risk: "High", renewalDays: 57, adoption: 58, learners: 1980, roleplays: 8640, scenarios: 14, certification: 59, scoreLift: 9, integrations: 2, expansion: 0, owner: "Jordan Patel", champion: "Developing", riskReason: "Multilingual scoring calibration and regional content ownership are incomplete.", nextAction: "Assign content owners and re-baseline the global launch by region.", products: ["roleplay", "courses", "coaching", "languages"] },
  { id: 6, name: "Atlas Logistics", industry: "Transportation", tier: "Enterprise", region: "APAC", arr: 760000, health: 73, risk: "Medium", renewalDays: 94, adoption: 69, learners: 2360, roleplays: 15780, scenarios: 24, certification: 78, scoreLift: 21, integrations: 3, expansion: 210000, owner: "Sam Okafor", champion: "Strong", riskReason: "Sales onboarding is adopted, while support escalation training is still manual.", nextAction: "Extend the scenario library to complex service and escalation calls.", products: ["roleplay", "courses", "coaching", "insights", "mobile"] },
  { id: 7, name: "Meridian Media", industry: "Media", tier: "Growth", region: "AMER", arr: 540000, health: 82, risk: "Low", renewalDays: 211, adoption: 86, learners: 1460, roleplays: 11250, scenarios: 22, certification: 91, scoreLift: 29, integrations: 3, expansion: 180000, owner: "Elena Rossi", champion: "Strong", riskReason: "Healthy adoption; CRM-connected deal coaching is the next gap.", nextAction: "Prioritize a Deal Coach proof of value for strategic opportunities.", products: ["roleplay", "courses", "coaching", "insights", "integrations", "mobile"] },
  { id: 8, name: "Crescent Bio", industry: "Life Sciences", tier: "Enterprise", region: "EMEA", arr: 830000, health: 66, risk: "Medium", renewalDays: 121, adoption: 71, learners: 2120, roleplays: 13870, scenarios: 26, certification: 76, scoreLift: 18, integrations: 4, expansion: 230000, owner: "Sam Okafor", champion: "Developing", riskReason: "Learner activity is rising, but managers lack a consistent coaching cadence.", nextAction: "Launch manager insights reviews tied to certification cohorts.", products: ["roleplay", "courses", "coaching", "languages", "integrations"] },
  { id: 9, name: "Harbor Retail", industry: "Retail", tier: "Growth", region: "APAC", arr: 460000, health: 76, risk: "Low", renewalDays: 168, adoption: 79, learners: 3290, roleplays: 26740, scenarios: 29, certification: 88, scoreLift: 27, integrations: 2, expansion: 140000, owner: "Sam Okafor", champion: "Strong", riskReason: "Core service training is healthy; mobile frontline access is underused.", nextAction: "Roll out QR-linked mobile practice to store teams.", products: ["roleplay", "courses", "coaching", "insights", "languages"] },
  { id: 10, name: "Pioneer Systems", industry: "Technology", tier: "Enterprise", region: "AMER", arr: 1040000, health: 59, risk: "High", renewalDays: 29, adoption: 64, learners: 2780, roleplays: 17420, scenarios: 21, certification: 68, scoreLift: 15, integrations: 4, expansion: 0, owner: "Jordan Patel", champion: "At risk", riskReason: "Executive sponsor changed and the product-certification launch is stalled.", nextAction: "Rebuild the value narrative around ramp time and readiness lift.", products: ["roleplay", "courses", "coaching", "insights", "integrations"] },
];

export const implementations = [
  { account: "Aperture Health", owner: "Nora Kim", confidence: "Low", progress: 58, target: "Aug 29", delay: 18, phase: "Seller onboarding launch", blocker: "LMS audience sync and assignment logic", action: "Executive LMS integration escalation" },
  { account: "Keystone Energy", owner: "Luis Martin", confidence: "Low", progress: 41, target: "Sep 18", delay: 27, phase: "Multilingual service rollout", blocker: "Regional scoring calibration and content owners", action: "Assign owners and certify two priority languages" },
  { account: "Pioneer Systems", owner: "Nora Kim", confidence: "Medium", progress: 72, target: "Aug 16", delay: 9, phase: "Product certification", blocker: "Messaging sign-off from product marketing", action: "Secure sponsor decision this week" },
  { account: "Vertex Commerce", owner: "Luis Martin", confidence: "High", progress: 86, target: "Aug 8", delay: 0, phase: "Deal Coach pilot", blocker: "None", action: "Confirm CRM cohort and success baseline" },
  { account: "Atlas Logistics", owner: "Priya Shah", confidence: "High", progress: 79, target: "Sep 2", delay: 0, phase: "Support escalation library", blocker: "None", action: "Validate three high-volume service scenarios" },
  { account: "Crescent Bio", owner: "Priya Shah", confidence: "Medium", progress: 64, target: "Sep 12", delay: 5, phase: "Manager insights rollout", blocker: "Regional manager hierarchy cleanup", action: "Finalize dashboard audience and coaching cadence" },
];

export const agents = [
  { id: "ReadinessHealth", name: "Readiness Program Health", group: "Monitor", tier: "Sonnet", description: "Scores adoption, readiness lift, certification, coaching activity, and renewal health." },
  { id: "RenewalPredictor", name: "Renewal Predictor", group: "Monitor", tier: "Sonnet", description: "Explains renewal risk and the evidence required to change the forecast." },
  { id: "RolloutNavigator", name: "Rollout Navigator", group: "Deliver", tier: "Sonnet", description: "Turns launch blockers into a sequenced AI role-play program recovery plan." },
  { id: "ExecutiveBriefing", name: "Executive Briefing", group: "Deliver", tier: "Sonnet", description: "Creates enablement-leader briefings grounded in participation, readiness, and business impact." },
  { id: "ExpansionArchitect", name: "Expansion Architect", group: "Grow", tier: "Sonnet", description: "Finds peer-evidenced whitespace across the Second Nature platform." },
  { id: "SkeptikQA", name: "Skeptik QA", group: "Govern", tier: "Opus", description: "Stress-tests claims, assumptions, and unsupported recommendations." },
  { id: "VPChiefOfStaff", name: "VP CS Chief of Staff", group: "Lead", tier: "Opus", description: "Synthesizes portfolio risk, capacity, renewals, and expansion priorities." },
  { id: "CoachingPlanner", name: "Coaching Planner", group: "Deliver", tier: "Haiku", description: "Drafts concise next actions for readiness, certification, and manager coaching gaps." },
];

export const auditRuns = [
  { id: 1084, agent: "Readiness Program Health", account: "Aperture Health", model: "claude-sonnet-5", tokens: 5128, cost: 0.0384, confidence: 87, time: "Today · 9:42 AM" },
  { id: 1083, agent: "VP CS Chief of Staff", account: "Portfolio", model: "claude-opus-4-6", tokens: 8744, cost: 0.2441, confidence: 92, time: "Today · 8:10 AM" },
  { id: 1082, agent: "Expansion Architect", account: "Summit Cloud", model: "claude-sonnet-5", tokens: 4688, cost: 0.0352, confidence: 89, time: "Yesterday · 4:18 PM" },
  { id: 1081, agent: "Rollout Navigator", account: "Keystone Energy", model: "claude-sonnet-5", tokens: 6240, cost: 0.0468, confidence: 84, time: "Yesterday · 2:03 PM" },
  { id: 1080, agent: "Skeptik QA", account: "Pioneer Systems", model: "claude-opus-4-6", tokens: 7312, cost: 0.2050, confidence: 94, time: "Yesterday · 11:26 AM" },
];

export const formatMoney = (value: number) =>
  value >= 1_000_000 ? `$${(value / 1_000_000).toFixed(1)}M` : `$${Math.round(value / 1000)}K`;

export const riskColor = (risk: Risk) =>
  ({ High: "#d65745", Medium: "#b97b14", Low: "#2c8f70" })[risk];

export const totalArr = accounts.reduce((sum, account) => sum + account.arr, 0);
export const atRiskArr = accounts.filter((account) => account.risk === "High").reduce((sum, account) => sum + account.arr, 0);
export const expansionArr = accounts.reduce((sum, account) => sum + account.expansion, 0);
