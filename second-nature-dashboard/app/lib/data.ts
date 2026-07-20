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
  doors: number;
  residents: number;
  onboardings: number;
  rbpActivation: number;
  leaseCompletion: number;
  teamHoursSaved: number;
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
  { id: "onboarding", name: "Resident Onboarding", short: "Onboard", description: "Lease Guide and Move Guide take residents from approved to moved with clarity, choice, and accountability.", accent: "#ff7452" },
  { id: "maestro", name: "Maestro™", short: "Maestro", description: "Orchestrate personalized journeys, documents, compliance updates, and when/then workflows at scale.", accent: "#ffc928" },
  { id: "internet", name: "Group Rate Internet", short: "Internet", description: "Fully managed gigabit-speed internet with exclusive portfolio rates and 24/7 support.", accent: "#6c4df6" },
  { id: "insurance", name: "Renters Insurance Program", short: "Insurance", description: "Automatic coverage tracking and enrollment to protect residents, properties, and owners.", accent: "#00a98f" },
  { id: "credit", name: "Credit Building", short: "Credit", description: "Report on-time rent payments to major bureaus to strengthen resident financial health.", accent: "#2c8cff" },
  { id: "filters", name: "Air Filter Delivery", short: "Filters", description: "Deliver filters on schedule to improve lease compliance and reduce costly HVAC work orders.", accent: "#78b84c" },
  { id: "pest", name: "On-Demand Pest Control", short: "Pest", description: "Let residents coordinate treatment directly through geography-specific, fully managed plans.", accent: "#b886ff" },
  { id: "rewards", name: "Resident Rewards", short: "Rewards", description: "Reward on-time payments and other positive behaviors with points, discounts, and prizes.", accent: "#f58bb6" },
  { id: "identity", name: "Identity Protection", short: "Identity", description: "Provide dark-web monitoring, breach-expense coverage, and U.S.-based restoration support.", accent: "#55b7d9" },
  { id: "concierge", name: "Move-In Concierge", short: "Concierge", description: "Help residents set up utilities and services in one guided phone call without adding team workload.", accent: "#ff9c66" },
];

export const accounts: Account[] = [
  { id: 1, name: "Northstar Property Management", industry: "Single-Family", tier: "Strategic", region: "Southeast", arr: 1480000, health: 91, risk: "Low", renewalDays: 142, adoption: 91, doors: 18600, residents: 42100, onboardings: 8740, rbpActivation: 93, leaseCompletion: 98, teamHoursSaved: 4680, integrations: 3, expansion: 380000, owner: "Maya Chen", champion: "Strong", riskReason: "No material risk; Group Rate Internet is the next portfolio-wide value lever.", nextAction: "Model internet activation and vacancy impact for the top five markets.", products: ["onboarding", "maestro", "insurance", "credit", "filters", "pest", "rewards", "identity", "concierge"] },
  { id: 2, name: "Aperture Residential", industry: "Multifamily", tier: "Enterprise", region: "Midwest", arr: 1120000, health: 54, risk: "High", renewalDays: 38, adoption: 61, doors: 12400, residents: 27800, onboardings: 5240, rbpActivation: 58, leaseCompletion: 72, teamHoursSaved: 1840, integrations: 2, expansion: 0, owner: "Jordan Patel", champion: "At risk", riskReason: "Property-accounting mappings remain blocked and RBP activation is below plan.", nextAction: "Run a 30-day recovery plan for AppFolio mapping, addenda, and resident enrollment.", products: ["onboarding", "insurance", "filters", "concierge"] },
  { id: 3, name: "Vertex Property Group", industry: "Build-to-Rent", tier: "Enterprise", region: "Southwest", arr: 980000, health: 78, risk: "Medium", renewalDays: 76, adoption: 76, doors: 9800, residents: 21600, onboardings: 4380, rbpActivation: 81, leaseCompletion: 91, teamHoursSaved: 2630, integrations: 3, expansion: 260000, owner: "Maya Chen", champion: "Strong", riskReason: "Resident Onboarding is healthy, but benefits vary by market without Maestro rules.", nextAction: "Standardize property groups and launch Maestro when/then automation.", products: ["onboarding", "insurance", "credit", "filters", "rewards", "concierge"] },
  { id: 4, name: "Summit Homes", industry: "Single-Family", tier: "Strategic", region: "National", arr: 1360000, health: 85, risk: "Low", renewalDays: 189, adoption: 94, doors: 22400, residents: 49700, onboardings: 10320, rbpActivation: 96, leaseCompletion: 99, teamHoursSaved: 6120, integrations: 4, expansion: 440000, owner: "Elena Rossi", champion: "Strong", riskReason: "Healthy fully managed RBP with demand for internet and portfolio-wide onboarding.", nextAction: "Package Group Rate Internet and Resident Onboarding expansion by market.", products: ["maestro", "insurance", "credit", "filters", "pest", "rewards", "identity", "concierge"] },
  { id: 5, name: "Keystone Rentals", industry: "Single-Family", tier: "Enterprise", region: "Mountain", arr: 890000, health: 48, risk: "High", renewalDays: 57, adoption: 56, doors: 7600, residents: 16800, onboardings: 3150, rbpActivation: 52, leaseCompletion: 67, teamHoursSaved: 1090, integrations: 1, expansion: 0, owner: "Jordan Patel", champion: "Developing", riskReason: "Lease addenda, GL codes, and benefit ownership are incomplete across regions.", nextAction: "Assign regional owners and re-baseline the Build–Integrate–Go Live plan.", products: ["insurance", "filters", "pest", "identity"] },
  { id: 6, name: "Atlas Residential", industry: "Multifamily", tier: "Enterprise", region: "West", arr: 760000, health: 73, risk: "Medium", renewalDays: 94, adoption: 71, doors: 11200, residents: 24600, onboardings: 4670, rbpActivation: 75, leaseCompletion: 86, teamHoursSaved: 2380, integrations: 2, expansion: 210000, owner: "Sam Okafor", champion: "Strong", riskReason: "Core RBP is adopted, while move-in tasks and utility setup remain fragmented.", nextAction: "Extend Resident Onboarding and Move-In Concierge to three pilot regions.", products: ["insurance", "credit", "filters", "pest", "rewards", "identity"] },
  { id: 7, name: "Meridian Property Partners", industry: "Single-Family", tier: "Growth", region: "Southeast", arr: 540000, health: 82, risk: "Low", renewalDays: 211, adoption: 86, doors: 6800, residents: 15100, onboardings: 3080, rbpActivation: 89, leaseCompletion: 95, teamHoursSaved: 1760, integrations: 2, expansion: 180000, owner: "Elena Rossi", champion: "Strong", riskReason: "Healthy benefits adoption; interactive lease transparency is the next gap.", nextAction: "Build a Resident Onboarding business case around three days saved per lease.", products: ["insurance", "credit", "filters", "pest", "rewards", "concierge"] },
  { id: 8, name: "Crescent Communities", industry: "Build-to-Rent", tier: "Enterprise", region: "East", arr: 830000, health: 66, risk: "Medium", renewalDays: 121, adoption: 69, doors: 8900, residents: 19700, onboardings: 3920, rbpActivation: 72, leaseCompletion: 82, teamHoursSaved: 2060, integrations: 3, expansion: 230000, owner: "Sam Okafor", champion: "Developing", riskReason: "Benefits are active, but portfolio compliance updates are still document-heavy.", nextAction: "Pilot Maestro document groups and portfolio-wide compliance updates.", products: ["onboarding", "insurance", "filters", "pest", "identity", "concierge"] },
  { id: 9, name: "Harbor Property Management", industry: "Single-Family", tier: "Growth", region: "Coastal", arr: 460000, health: 76, risk: "Low", renewalDays: 168, adoption: 79, doors: 5400, residents: 12100, onboardings: 2490, rbpActivation: 84, leaseCompletion: 90, teamHoursSaved: 1380, integrations: 2, expansion: 140000, owner: "Sam Okafor", champion: "Strong", riskReason: "Core RBP is healthy; resident financial-health benefits are under-penetrated.", nextAction: "Add Credit Building and Resident Rewards at the next renewal cycle.", products: ["insurance", "filters", "pest", "identity", "concierge"] },
  { id: 10, name: "Pioneer Residential", industry: "Multifamily", tier: "Enterprise", region: "Northeast", arr: 1040000, health: 59, risk: "High", renewalDays: 29, adoption: 63, doors: 10600, residents: 23500, onboardings: 4460, rbpActivation: 65, leaseCompletion: 74, teamHoursSaved: 1920, integrations: 2, expansion: 0, owner: "Jordan Patel", champion: "At risk", riskReason: "Executive sponsor changed and Resident Onboarding rollout is stalled.", nextAction: "Rebuild the value narrative around lease speed, transparency, and ancillary NOI.", products: ["insurance", "credit", "filters", "pest", "identity"] },
];

export const implementations = [
  { account: "Aperture Residential", owner: "Nora Kim", confidence: "Low", progress: 58, target: "Aug 29", delay: 18, phase: "PAS integration & mapping", blocker: "AppFolio custom fields and GL codes", action: "Executive integration workshop with accounting" },
  { account: "Keystone Rentals", owner: "Luis Martin", confidence: "Low", progress: 41, target: "Sep 18", delay: 27, phase: "RBP design & addenda", blocker: "Regional benefit ownership and lease addenda", action: "Finalize package and owners by market" },
  { account: "Pioneer Residential", owner: "Nora Kim", confidence: "Medium", progress: 72, target: "Aug 16", delay: 9, phase: "Resident Onboarding rollout", blocker: "Portfolio compliance approval", action: "Secure sponsor sign-off this week" },
  { account: "Vertex Property Group", owner: "Luis Martin", confidence: "High", progress: 86, target: "Aug 8", delay: 0, phase: "Maestro automation pilot", blocker: "None", action: "Confirm property groups and when/then rules" },
  { account: "Atlas Residential", owner: "Priya Shah", confidence: "High", progress: 79, target: "Sep 2", delay: 0, phase: "Resident Onboarding pilot", blocker: "None", action: "Validate SMS, e-sign, and move-in task flow" },
  { account: "Crescent Communities", owner: "Priya Shah", confidence: "Medium", progress: 64, target: "Sep 12", delay: 5, phase: "Portfolio document migration", blocker: "Property-group hierarchy cleanup", action: "Finalize document groups and compliance owners" },
];

export const agents = [
  { id: "ResidentExperienceHealth", name: "Resident Experience Health", group: "Monitor", tier: "Sonnet", description: "Scores onboarding, RBP activation, lease completion, operational lift, and renewal health." },
  { id: "RenewalPredictor", name: "Renewal Predictor", group: "Monitor", tier: "Sonnet", description: "Explains renewal risk and the evidence required to change the forecast." },
  { id: "PortfolioLaunchNavigator", name: "Portfolio Launch Navigator", group: "Deliver", tier: "Sonnet", description: "Turns integration, package-design, and rollout blockers into a sequenced recovery plan." },
  { id: "ExecutiveBriefing", name: "Executive Briefing", group: "Deliver", tier: "Sonnet", description: "Creates property-management executive briefings grounded in resident, team, and investor outcomes." },
  { id: "RBPExpansionArchitect", name: "RBP Expansion Architect", group: "Grow", tier: "Sonnet", description: "Finds peer-evidenced whitespace across Resident Onboarding and the Resident Benefits Package." },
  { id: "SkeptikQA", name: "Skeptik QA", group: "Govern", tier: "Opus", description: "Stress-tests claims, assumptions, and unsupported recommendations." },
  { id: "VPChiefOfStaff", name: "VP CS Chief of Staff", group: "Lead", tier: "Opus", description: "Synthesizes portfolio risk, capacity, renewals, and expansion priorities." },
  { id: "OperationsPlanner", name: "Resident Operations Planner", group: "Deliver", tier: "Haiku", description: "Drafts concise next actions for onboarding, activation, compliance, and resident-experience gaps." },
];

export const auditRuns = [
  { id: 1128, agent: "Resident Experience Health", account: "Aperture Residential", model: "claude-sonnet-5", tokens: 5128, cost: 0.0384, confidence: 87, time: "Today · 9:42 AM" },
  { id: 1127, agent: "VP CS Chief of Staff", account: "Portfolio", model: "claude-opus-4-6", tokens: 8744, cost: 0.2441, confidence: 92, time: "Today · 8:10 AM" },
  { id: 1126, agent: "RBP Expansion Architect", account: "Summit Homes", model: "claude-sonnet-5", tokens: 4688, cost: 0.0352, confidence: 89, time: "Yesterday · 4:18 PM" },
  { id: 1125, agent: "Portfolio Launch Navigator", account: "Keystone Rentals", model: "claude-sonnet-5", tokens: 6240, cost: 0.0468, confidence: 84, time: "Yesterday · 2:03 PM" },
  { id: 1124, agent: "Skeptik QA", account: "Pioneer Residential", model: "claude-opus-4-6", tokens: 7312, cost: 0.2050, confidence: 94, time: "Yesterday · 11:26 AM" },
];

export const formatMoney = (value: number) =>
  value >= 1_000_000 ? `$${(value / 1_000_000).toFixed(1)}M` : `$${Math.round(value / 1000)}K`;

export const riskColor = (risk: Risk) =>
  ({ High: "#d65745", Medium: "#b97b14", Low: "#2c8f70" })[risk];

export const totalArr = accounts.reduce((sum, account) => sum + account.arr, 0);
export const atRiskArr = accounts.filter((account) => account.risk === "High").reduce((sum, account) => sum + account.arr, 0);
export const expansionArr = accounts.reduce((sum, account) => sum + account.expansion, 0);
