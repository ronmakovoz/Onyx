"""
generate_synthetic_data.py
Generates all synthetic JSON files and seeds the SQLite database.
Run: python data/generate_synthetic_data.py
"""

import json
import sqlite3
import random
import uuid
from datetime import datetime, date, timedelta
from pathlib import Path

random.seed(2024)

# ── Output paths ──────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent
DB_PATH  = DATA_DIR / "cx_agent_os.db"


# ══════════════════════════════════════════════════════════════════════════════
# MASTER CUSTOMER DEFINITIONS
# Each entry drives every downstream data file to stay internally consistent.
# ══════════════════════════════════════════════════════════════════════════════

# fmt: off
# Each entry: id, name, industry, region, employees, arr, contract_start_offset,
#             renewal_offset, stage, health, trend, risk, primary_risk_reason, next_action
MASTER_CUSTOMERS = [
    ( 1, "NovaPay",                 "Financial Services",  "NA",    4200,   980000,  -300,  52, "Mature",     86, "Improving", "Low",    "Fraud detection ROI proven; expansion underway",         "Prep multi-product expansion proposal"),
    ( 2, "Sentinel Commerce",       "Ecommerce",           "NA",    3100,   540000,  -210,  88, "Mature",     79, "Stable",    "Low",    "Strong chargeback reduction; healthy adoption",          "Introduce account-takeover module"),
    ( 3, "Orbit Travel Group",      "Travel",              "EMEA",  6800,   720000,  -180,  34, "At Risk",    41, "Declining", "High",   "Booking-fraud model drift; champion disengaged",         "Model retraining workshop + exec call"),
    ( 4, "Horizon Health Systems",  "Healthcare",          "NA",    9400,  1250000,  -420, 140, "Mature",     91, "Stable",    "Low",    "Reference account; zero churn signal",                   "Multi-year renewal + case study"),
    ( 5, "PrimeCart",               "Ecommerce",           "NA",    5200,   430000,   -90,  21, "At Risk",    38, "Declining", "High",   "Low utilization; no exec sponsor; renewal imminent",     "Rapid value demonstration sprint"),
    ( 6, "SecureLedger",            "Financial Services",  "EMEA",  2600,   860000,  -240,  61, "Mature",     74, "Improving", "Medium", "New CISO conducting platform audit",                     "CISO alignment + ROI briefing"),
    ( 7, "Velocity Marketplace",    "Marketplace",         "NA",    3400,   610000,  -150,  29, "At Risk",    44, "Declining", "High",   "Seller-fraud false positives spiking; trust eroding",    "Tuning war room + daily updates"),
    ( 8, "BluePeak Retail",         "Retail",              "NA",    7600,   380000,  -365, 178, "Mature",     76, "Stable",    "Low",    "Steady usage; light upsell available",                   "Pitch store-level analytics add-on"),
    ( 9, "Apex Interactive",        "Gaming",              "APAC",  1900,   470000,  -120,  47, "Onboarding", 35, "Declining", "High",   "Go-live stalled; anti-cheat integration blocked",        "Engineering escalation on integration"),
    (10, "VitalCore Health",        "Healthcare",          "NA",    3200,   690000,  -200,  72, "Mature",     69, "Stable",    "Medium", "Adoption plateau; PHI workflow friction",                "Workflow optimization session"),
    (11, "Kestrel Defense Systems", "Enterprise Technology","NA",   6800,  1400000,  -730, 203, "Mature",     93, "Stable",    "Low",    "Premier strategic account; net promoter",                "QBR + expansion to 2nd division"),
    (12, "LuminaCare Medical",      "Healthcare",          "EMEA",   890,   360000,   -55,   8, "Onboarding", 27, "Declining", "High",   "PHI concern blocking go-live; CISO disengaged",          "Legal + security review escalation"),
    (13, "ShopSphere",              "Ecommerce",           "APAC",  4100,   520000,  -300, 134, "Mature",     81, "Improving", "Low",    "Payment-fraud savings growing; new champion",            "Schedule platform deep-dive"),
    (14, "NovaTech Systems",        "Enterprise Technology","NA",   2200,   760000,  -280,  61, "Mature",     66, "Stable",    "Medium", "SIEM integration gap; roadmap request pending",          "Engineering roadmap sync"),
    (15, "OmniCloud Infrastructure","Enterprise Technology","NA",   4400,   910000,   -45,  26, "At Risk",    45, "Declining", "High",   "Low feature adoption; exec sponsor gone; renewal soon",  "Executive value realization plan"),
    (16, "Sterling Trust Bank",     "Financial Services",  "NA",    8900,  1600000,  -500, 156, "Mature",     89, "Stable",    "Low",    "AML monitoring expanded; strong governance use",         "Annual exec business review"),
    (17, "QuantumLeap Finance",     "Financial Services",  "EMEA",  2600,   620000,  -195,  72, "Mature",     71, "Improving", "Medium", "Relationship reset after sponsor change",                "Sponsor onboarding briefing"),
    (18, "WanderStay Hotels",       "Travel",              "EMEA",  3100,   410000,  -100,  19, "At Risk",    33, "Declining", "High",   "Loyalty-fraud coverage gap; champion left",              "Identify and engage new champion"),
    (19, "NeonPlay Studios",        "Gaming",              "NA",    1500,   280000,  -500, 180, "Mature",     64, "Stable",    "Low",    "Steady account; minor roadmap asks",                     "Annual check-in + renewal prep"),
    (20, "Harbor Retail Group",     "Retail",              "NA",    2900,   370000,  -130,  41, "Mature",     56, "Declining", "Medium", "Adoption plateau; budget review pending",                "Usage workshop + ROI case"),
    (21, "AssureGuard Insurance",   "Insurance",           "NA",    5200,   930000,  -730, 118, "Mature",     87, "Stable",    "Low",    "Claims-fraud ROI strong; compliance aligned",            "Expand to underwriting division"),
    (22, "VantagePoint Capital",    "Financial Services",  "NA",    1900,   750000,   -75,  52, "At Risk",    54, "Declining", "Medium", "Procurement questioning value; CFO pressure",            "Executive ROI briefing"),
    (23, "Meridian Capital",        "Financial Services",  "EMEA",  3400,   880000,  -320,  83, "Mature",     78, "Improving", "Low",    "Transaction-monitoring expansion live",                  "Plan phase-2 rollout"),
    (24, "Brightwork Software",     "SaaS",                "NA",     600,   190000,   -50,  37, "Onboarding", 46, "Stable",    "Medium", "Small team; low adoption; needs enablement",             "Dedicated onboarding sprint"),
    (25, "IronClad Systems",        "Enterprise Technology","NA",   7200,  1100000,  -600, 156, "Mature",     94, "Improving", "Low",    "Best-in-class deployment; expansion signed",             "Case study + reference call"),
    (26, "CartNova",                "Ecommerce",           "LATAM", 2100,   240000,  -160,  64, "Mature",     70, "Stable",    "Low",    "Reliable mid-market account; promoter",                  "Offer annual prepay incentive"),
    (27, "TradeHub",                "Marketplace",         "EMEA",  2800,   330000,  -110,  24, "At Risk",    42, "Declining", "High",   "Escalation backlog; SLA breaches mounting",              "Support war room; SLA recovery plan"),
    (28, "CloudHarbor SaaS",        "SaaS",                "NA",    1700,   280000,  -220,  95, "Mature",     75, "Stable",    "Low",    "Healthy usage; advocate for product",                    "Invite to advisory board"),
    (29, "Beacon Mutual",           "Insurance",           "NA",    4600,   640000,  -290,  77, "Mature",     68, "Stable",    "Medium", "Modest adoption; QBR overdue",                           "Schedule overdue QBR"),
    (30, "SkyRoute Airlines",       "Travel",              "APAC", 12000,   980000,  -120,  15, "At Risk",    31, "Declining", "High",   "Competitor POC underway; champion left; impl late",      "CEO briefing + SWAT team"),
    (31, "PixelForge Games",        "Gaming",              "EMEA",  2200,   350000,  -260,  88, "Mature",     72, "Improving", "Low",    "Payment-fraud reduction proven; growing usage",          "Upsell chargeback automation"),
    (32, "BioNexus Health",         "Healthcare",          "NA",    2800,   720000,   -87,  87, "Expanding",  80, "Improving", "Low",    "Strong usage; expansion in progress",                    "Prep expansion proposal for QBR"),
    (33, "DataVault Analytics",     "SaaS",                "NA",    3500,   950000,  -300, 112, "Mature",     88, "Stable",    "Low",    "Gold-standard customer; NPS 10",                         "Recruit as reference customer"),
    (34, "GlobalEdge Retail",       "Retail",              "EMEA",  5500,   290000,  -420, 168, "Mature",     73, "Stable",    "Low",    "Renewal secured; light upsell opportunity",              "Introduce threat-intel module"),
    (35, "Cobalt Payments",         "Financial Services",  "NA",    3900,   810000,  -140,  48, "At Risk",    47, "Declining", "High",   "Real-time scoring latency complaints; trust at risk",    "Performance remediation plan"),
    (36, "BazaarOne",               "Marketplace",         "APAC",  4200,   560000,  -340,  98, "Mature",     76, "Improving", "Low",    "Seller-trust score adoption rising",                     "Expand to logistics fraud"),
    (37, "HealthFirst Insurance",   "Insurance",           "NA",    3200,   840000,  -150,  56, "Mature",     51, "Declining", "High",   "P1 open 11 days; sentiment negative",                    "Engineering war room; daily updates"),
    (38, "Evora Energy Partners",   "Enterprise Technology","EMEA", 2100,   560000,  -210,  67, "Mature",     67, "Stable",    "Medium", "Security review blocker delaying expansion",             "Expedite review sign-off"),
    (39, "Quayside Logistics",      "Marketplace",         "NA",    1600,   310000,  -180,  23, "At Risk",    37, "Declining", "High",   "Implementation 9 weeks behind; exec disengaged",         "Escalate to VP immediately"),
    (40, "Auric Bank",              "Financial Services",  "APAC",  6100,  1050000,  -380,  92, "Mature",     85, "Stable",    "Low",    "Cross-border fraud coverage strong",                     "Discuss regional expansion"),
    (41, "FreshCart Markets",       "Retail",              "NA",    3300,   320000,  -240,  74, "Mature",     69, "Stable",    "Medium", "Adoption steady; feature gaps noted",                    "Roadmap review with product"),
    (42, "Lumen Insurance Group",   "Insurance",           "EMEA",  4800,   700000,  -160,  44, "At Risk",    49, "Declining", "High",   "Claims-fraud model underperforming; renewal risk",       "Model performance deep-dive"),
    (43, "PlaySphere",              "Gaming",              "NA",    1100,   210000,  -300, 120, "Mature",     71, "Improving", "Low",    "Account-takeover defense adopted well",                  "Offer expansion discount"),
    (44, "Northwind Travel",        "Travel",              "NA",    2700,   480000,  -190,  68, "Mature",     65, "Stable",    "Medium", "Usage flat; exec engagement light",                      "Re-engage exec sponsor"),
    (45, "Vertex SaaS",             "SaaS",                "APAC",  2000,   360000,  -130,  58, "Onboarding", 50, "Stable",    "Medium", "Onboarding slower than plan; needs enablement",          "Accelerate onboarding milestones"),
    (46, "Crestline Capital",       "Financial Services",  "NA",    2400,   590000,  -270,  90, "Mature",     82, "Improving", "Low",    "AML automation delivering value",                        "Expand to sanctions screening"),
    (47, "ZenMarket",               "Marketplace",         "EMEA",  3600,   440000,  -100,  28, "At Risk",    43, "Declining", "High",   "Trust-and-safety team overwhelmed; false positives high","Tuning engagement + exec review"),
    (48, "Summit Health Plan",      "Insurance",           "NA",    5400,   770000,  -330,  96, "Mature",     79, "Stable",    "Low",    "Fraud-waste-abuse savings documented",                   "Build expansion business case"),
    (49, "Pinnacle Gaming",         "Gaming",              "APAC",  2600,   400000,  -150,  35, "At Risk",    46, "Declining", "Medium", "Bonus-abuse coverage gap; mid-tier risk",                "Coverage gap remediation plan"),
    (50, "Atlas Enterprise Cloud",  "Enterprise Technology","NA",   8200,  1300000,  -640, 170, "Mature",     90, "Stable",    "Low",    "Strategic platform standard; multi-region",              "Multi-year strategic renewal"),
]
# fmt: on

REGIONS = ["NA", "EMEA", "APAC", "LATAM"]

CSM_OWNERS = [
    "Maya Rodriguez", "James Okafor", "Priya Nair", "Tyler Bennett",
    "Simone Dubois", "Hiroshi Tanaka", "Aaliya Patel",
]
IMPL_OWNERS = [
    "Derek Walsh", "Keisha Monroe", "Liam Chen", "Sofia Alvarez",
    "Marcus Williams",
]
EXEC_SPONSORS = [
    "Rachel Kim (VP CX)", "David Park (CRO)", "Natasha Ivanova (VP CS)",
]

FIRST = ["James","Sarah","Michael","Jennifer","Robert","Lisa","David","Emily",
         "Chris","Amanda","Brian","Rachel","Kevin","Megan","Eric","Lauren",
         "Omar","Priya","Carlos","Yuki","Fatima","Derek","Simone","Aaliya","Tyler"]
LAST  = ["Chen","Thompson","Rodriguez","Kim","Patel","Williams","Johnson","Davis",
         "Martinez","Brown","Wilson","Anderson","Taylor","Moore","Jackson","White",
         "Harris","Martin","Garcia","Lee","Okafor","Walsh","Dubois","Tanaka","Nair"]

CHAMPION_TITLES = ["CISO","VP of IT","Head of Security","Director of InfoSec","CTO","VP Engineering","Deputy CISO"]
EXEC_TITLES     = ["CEO","CFO","COO","CTO","CISO","SVP Operations","VP Procurement","VP Finance"]
TECH_TITLES     = ["Director of IT","Principal Engineer","Security Architect","Lead DevOps","Head of Infra"]
BIZ_TITLES      = ["VP Operations","Director of Digital","Head of Compliance","VP Strategy","GM Technology"]


def rname():
    return f"{random.choice(FIRST)} {random.choice(LAST)}"

def days(n, base=None):
    b = base or date.today()
    return (b + timedelta(days=n)).isoformat()

def past(n):
    return (datetime.now() - timedelta(days=n)).strftime("%Y-%m-%dT%H:%M:%S")

def ts_past(max_days=180):
    return past(random.randint(1, max_days))

def pct_complete(risk):
    return {"Low": random.randint(75,100), "Medium": random.randint(45,74), "High": random.randint(10,44)}[risk]

def arr_fmt(arr):
    return f"${arr:,}"


# ══════════════════════════════════════════════════════════════════════════════
# 1. CUSTOMERS
# ══════════════════════════════════════════════════════════════════════════════

# Realistic, measurable security/fraud business outcomes by industry. Strong
# outcomes are reserved for healthier accounts to keep the data internally
# consistent (high adoption -> demonstrable ROI).
ROI_OUTCOMES = {
    "Financial Services": ["Fraud losses reduced {a}%", "Manual review queue cut {b}%", "False positives lowered {c}%", "AML alert triage time down {b}%"],
    "Ecommerce":          ["Chargeback rate reduced {a}%", "Payment-fraud losses down {a}%", "Manual reviews reduced {b}%", "Checkout approval rate up {d}%"],
    "Retail":             ["Return-fraud losses reduced {a}%", "Loss-prevention alerts triaged {b}% faster", "False positives lowered {c}%"],
    "Travel":             ["Booking-fraud losses reduced {a}%", "Loyalty-abuse incidents down {a}%", "Manual reviews reduced {b}%"],
    "Marketplace":        ["Seller-fraud incidents reduced {a}%", "Trust-and-safety review load down {b}%", "False positives lowered {c}%"],
    "Healthcare":         ["Fraud-waste-abuse recoveries up {a}%", "Claims review time reduced {b}%", "Security incidents detected: {e}"],
    "Insurance":          ["Claims-fraud losses reduced {a}%", "Investigator hours saved {b}%", "Detected {e} fraud rings this year"],
    "Gaming":             ["Account-takeover incidents down {a}%", "Bonus-abuse losses reduced {a}%", "Manual reviews reduced {b}%"],
    "SaaS":               ["Security incidents detected: {e}", "Analyst time saved {b}%", "False positive rate lowered {c}%"],
    "Enterprise Technology": ["Security incidents detected: {e}", "Mean-time-to-detect reduced {b}%", "Analyst time saved {b}%"],
}

def _roi_outcome(industry, risk):
    pool = ROI_OUTCOMES.get(industry, ROI_OUTCOMES["SaaS"])
    tmpl = random.choice(pool)
    # Stronger numbers for healthier accounts
    if risk == "Low":
        a, b, c, d, e = random.randint(34, 58), random.randint(40, 62), random.randint(45, 70), random.randint(6, 14), random.randint(9, 24)
    elif risk == "Medium":
        a, b, c, d, e = random.randint(18, 33), random.randint(22, 39), random.randint(25, 44), random.randint(3, 7), random.randint(4, 10)
    else:
        a, b, c, d, e = random.randint(6, 17), random.randint(8, 21), random.randint(10, 24), random.randint(1, 4), random.randint(1, 4)
    return tmpl.format(a=a, b=b, c=c, d=d, e=e)

def _tier(arr):
    if arr >= 1_000_000: return "Strategic"
    if arr >= 150_000:   return "Enterprise"
    return "Mid-Market"

def build_customers():
    customers = []
    for row in MASTER_CUSTOMERS:
        (cid, name, industry, region, employees, arr, contract_offset, renewal_offset,
         stage, health, trend, risk, primary_risk, next_action) = row

        csm   = random.choice(CSM_OWNERS)
        impl  = random.choice(IMPL_OWNERS)
        espon = random.choice(EXEC_SPONSORS)
        champion_name = rname()
        tech_sponsor  = rname()
        biz_sponsor   = rname()

        champion_status = (
            "Left Company" if "champion left" in primary_risk.lower() or "champion departed" in primary_risk.lower()
            else "Disengaged" if risk == "High" and random.random() > 0.5
            else "Active"
        )

        adoption = {
            "Low":    random.randint(18, 39),
            "Medium": random.randint(40, 65),
            "High":   random.randint(66, 95),
        }[{"High": "Low", "Medium": "Medium", "Low": "High"}[risk]]

        sentiment = (
            "Negative" if risk == "High" and health < 40
            else "Neutral" if risk in ("High","Medium") or health < 60
            else "Positive"
        )

        renewal_risk_score = round(
            {"High": random.uniform(0.60, 0.90),
             "Medium": random.uniform(0.30, 0.59),
             "Low": random.uniform(0.05, 0.29)}[risk], 2
        )

        onboarding = (
            "Stalled" if risk == "High" and stage == "Onboarding"
            else "In Progress" if stage == "Onboarding"
            else "Complete"
        )

        sec_review = (
            "Not Started" if risk == "High" and stage == "Onboarding"
            else "Blocked" if "security review blocker" in primary_risk.lower() or "sec review" in primary_risk.lower()
            else "In Progress" if risk in ("High","Medium") and stage != "Mature"
            else "Complete"
        )

        # ── New CS / retention / expansion metrics (internally consistent) ─────
        tier = _tier(arr)

        # NPS: healthy accounts promote, at-risk detract
        nps = {"Low": random.randint(8, 10), "Medium": random.randint(5, 7), "High": random.randint(-10, 4)}[risk]
        nps_trend = {"Improving": "up", "Stable": "flat", "Declining": "down"}[trend]

        # Net & Gross Revenue Retention — strong adoption/exec engagement -> higher NRR
        nrr_pct = {"Low": random.randint(112, 138), "Medium": random.randint(98, 111), "High": random.randint(72, 97)}[risk]
        grr_pct = {"Low": random.randint(96, 100), "Medium": random.randint(89, 96), "High": random.randint(70, 88)}[risk]

        # Expansion pipeline & upsell likelihood
        upsell_likelihood = {"Low": random.uniform(0.45, 0.85), "Medium": random.uniform(0.20, 0.44), "High": random.uniform(0.03, 0.18)}[risk]
        upsell_likelihood = round(upsell_likelihood, 2)
        expansion_pipeline_arr = 0
        if risk == "Low" and random.random() > 0.35:
            expansion_pipeline_arr = random.choice([40000, 60000, 80000, 120000, 180000, 250000])
        elif risk == "Medium" and random.random() > 0.7:
            expansion_pipeline_arr = random.choice([30000, 50000, 75000])

        # Time to value / production (days). Onboarding accounts may not have hit TTV yet.
        if stage == "Onboarding" and onboarding != "Complete":
            ttv_days = None
            ttp_days = None
        else:
            ttv_days = {"Low": random.randint(18, 42), "Medium": random.randint(43, 78), "High": random.randint(80, 150)}[risk]
            ttp_days = ttv_days + random.randint(20, 60)

        utilization_pct = max(5, min(100, adoption + random.randint(-6, 6)))

        exec_engagement = {
            "Low":    random.choice(["High", "High", "Medium"]),
            "Medium": random.choice(["Medium", "Low"]),
            "High":   ("None" if champion_status == "Left Company" else random.choice(["Low", "None"])),
        }[risk]

        # QBR cadence
        last_qbr_days_ago = random.randint(20, 110)
        qbr_completion = (
            "Overdue" if last_qbr_days_ago > 90 or "qbr overdue" in primary_risk.lower()
            else "On Track" if risk == "Low"
            else "Scheduled"
        )

        usage_trend = {"Improving": "Growing", "Stable": "Steady", "Declining": "Declining"}[trend]

        contract_term_months = random.choice([12, 12, 12, 24, 36] if tier != "Mid-Market" else [12, 12, 24])

        # Cost to serve scales with support load (risk) and inversely with tier efficiency
        cost_to_serve = int(arr * {"High": random.uniform(0.16, 0.24), "Medium": random.uniform(0.10, 0.15), "Low": random.uniform(0.05, 0.09)}[risk])

        roi_outcome = _roi_outcome(industry, risk)

        customers.append({
            "id": cid,
            "name": name,
            "industry": industry,
            "region": region,
            "customer_tier": tier,
            "employee_count": employees,
            "arr": arr,
            "contract_start_date": days(contract_offset),
            "renewal_date": days(renewal_offset),
            "contract_term_months": contract_term_months,
            "lifecycle_stage": stage,
            "health_score": health,
            "health_trend": trend,
            "csm_owner": csm,
            "implementation_owner": impl,
            "executive_sponsor_internal": espon,
            "champion_name": champion_name,
            "champion_title": random.choice(CHAMPION_TITLES),
            "champion_status": champion_status,
            "technical_sponsor": tech_sponsor,
            "business_sponsor": biz_sponsor,
            "adoption_score": adoption,
            "utilization_pct": utilization_pct,
            "sentiment": sentiment,
            "nps": nps,
            "nps_trend": nps_trend,
            "risk_level": risk,
            "primary_risk_reason": primary_risk,
            "recommended_next_action": next_action,
            "renewal_risk_score": renewal_risk_score,
            "nrr_pct": nrr_pct,
            "grr_pct": grr_pct,
            "upsell_likelihood": upsell_likelihood,
            "expansion_pipeline_arr": expansion_pipeline_arr,
            "time_to_first_value_days": ttv_days,
            "time_to_production_days": ttp_days,
            "executive_engagement": exec_engagement,
            "qbr_completion": qbr_completion,
            "last_qbr_date": past(last_qbr_days_ago),
            "usage_trend": usage_trend,
            "cost_to_serve": cost_to_serve,
            "roi_outcome": roi_outcome,
            "onboarding_status": onboarding,
            "security_review_status": sec_review,
            "arr_formatted": arr_fmt(arr),
        })
    return customers


# ══════════════════════════════════════════════════════════════════════════════
# 2. SUPPORT TICKETS
# ══════════════════════════════════════════════════════════════════════════════

TICKET_POOL = {
    "P1": [
        "SSO authentication failing for all users",
        "Audit log ingestion stopped — 6-hour gap in coverage",
        "Alert pipeline down — no detections firing",
        "Data export producing corrupted files",
        "API gateway returning 500 errors on all requests",
        "PHI data appearing in unencrypted audit export",
        "MFA enforcement bypassed after platform update",
        "SIEM integration silent for 8+ hours",
    ],
    "P2": [
        "SSO integration failing intermittently (15% failure rate)",
        "API rate limits too restrictive for enterprise workloads",
        "Dashboard reports not loading for non-admin users",
        "User provisioning delays exceeding 24 hours",
        "Webhook delivery failing for Slack integration",
        "Role-based access not propagating after group changes",
        "Custom detection rule not triggering on known threat pattern",
        "Cloud connector losing sync every 48 hours",
        "Compliance report export missing 3 required fields",
        "Alert deduplication creating false negatives",
    ],
    "P3": [
        "Alert noise too high — estimated 60% false positive rate",
        "Unable to export compliance reports in PDF format",
        "Slow query performance on datasets > 1M events",
        "UI session timeout too aggressive (15 minutes)",
        "Missing pagination on threat hunt results",
        "Audit log search returning inconsistent results",
        "Mobile app notification delays > 10 minutes",
        "CSV export truncating fields over 256 characters",
        "Duplicate entries in user activity report",
        "Dashboard widget not refreshing on Safari",
    ],
    "P4": [
        "Feature request: bulk user import via CSV",
        "Documentation missing for advanced YARA rule syntax",
        "Request to add dark mode to analyst console",
        "Typo in onboarding email template",
        "Minor UI misalignment in mobile view",
    ],
}

def build_tickets(customers):
    tickets = []
    tid = 1
    for c in customers:
        risk = c["risk_level"]
        counts = {
            "High":   {"P1": random.randint(2,4), "P2": random.randint(3,6), "P3": random.randint(2,5), "P4": random.randint(0,2)},
            "Medium": {"P1": random.randint(0,1), "P2": random.randint(2,4), "P3": random.randint(2,4), "P4": random.randint(1,3)},
            "Low":    {"P1": 0,                   "P2": random.randint(0,2), "P3": random.randint(1,3), "P4": random.randint(1,2)},
        }[risk]

        for sev, count in counts.items():
            for _ in range(count):
                status = (
                    "Open"        if sev in ("P1","P2") and risk == "High" and random.random() > 0.3
                    else "In Progress" if random.random() > 0.5
                    else "Resolved"
                )
                opened_days_ago = random.randint(1, 90)
                resolved_at = None
                if status == "Resolved":
                    resolved_at = past(random.randint(1, max(1, opened_days_ago - 1)))

                # Escalation reference — high-risk customers get notes
                escalation_ref = None
                if sev == "P1" and risk == "High" and status != "Resolved":
                    escalation_ref = f"Linked to account escalation — {c['name']} executive review"

                tickets.append({
                    "id": tid,
                    "customer_id": c["id"],
                    "customer_name": c["name"],
                    "title": random.choice(TICKET_POOL[sev]),
                    "severity": sev,
                    "status": status,
                    "opened_at": past(opened_days_ago),
                    "resolved_at": resolved_at,
                    "escalation_reference": escalation_ref,
                    "assignee": rname(),
                    "days_open": opened_days_ago if status != "Resolved" else None,
                })
                tid += 1
    return tickets


# ══════════════════════════════════════════════════════════════════════════════
# 3. IMPLEMENTATIONS
# ══════════════════════════════════════════════════════════════════════════════

ALL_MILESTONES = [
    ("Kickoff & Scoping",               7),
    ("Technical Discovery",             14),
    ("Environment Provisioning",        21),
    ("SSO / Identity Provider Integration", 35),
    ("Initial Data Ingestion",          42),
    ("Pilot Group Onboarding (25 users)", 56),
    ("Detection Policy Configuration",  63),
    ("Integration Testing & QA",        77),
    ("Security Review Sign-off",        84),
    ("Full Production Rollout",         98),
    ("Hypercare Period (30 days)",      128),
    ("QBR #1 — 90-Day Review",         180),
]

def build_implementations(customers):
    implementations = []
    iid = 1
    # Only customers in Onboarding stage or with impl-related risk get full records
    impl_customer_ids = set()
    for c in customers:
        if c["lifecycle_stage"] == "Onboarding" or "impl" in c["primary_risk_reason"].lower() or "onboard" in c["primary_risk_reason"].lower():
            impl_customer_ids.add(c["id"])
    # Also include a random sample of mature accounts (for history)
    mature = [c for c in customers if c["id"] not in impl_customer_ids]
    for c in random.sample(mature, min(7, len(mature))):
        impl_customer_ids.add(c["id"])

    for c in customers:
        if c["id"] not in impl_customer_ids:
            continue

        risk  = c["risk_level"]
        stage = c["lifecycle_stage"]
        pct   = pct_complete(risk)

        milestones = []
        total = len(ALL_MILESTONES)
        done_count = int(total * pct / 100)

        overall_status = (
            "Stalled"     if risk == "High" and stage == "Onboarding"
            else "Behind Schedule" if risk == "High"
            else "On Track"        if risk == "Low"
            else "Slight Delay"
        )

        days_behind = (
            random.randint(30, 70) if risk == "High"
            else random.randint(7, 21) if risk == "Medium"
            else 0
        )

        for idx, (mname, planned_days) in enumerate(ALL_MILESTONES):
            if idx < done_count:
                mstatus = "Complete"
                actual_offset = planned_days + (days_behind if risk != "Low" else 0) + random.randint(-3, 5)
                completed_at = past(max(1, 300 - actual_offset))
            elif idx == done_count:
                mstatus = "In Progress"
                completed_at = None
            else:
                mstatus = "Not Started"
                completed_at = None

            blocker = None
            if mstatus == "In Progress" and risk == "High":
                blockers = [
                    "Waiting on customer IT to provision service account",
                    "Security review committee not convened",
                    "Scope change requires SOW amendment",
                    "Key stakeholder unavailable for sign-off",
                    "Customer data classification incomplete",
                ]
                blocker = random.choice(blockers)

            milestones.append({
                "milestone_name": mname,
                "planned_days_from_start": planned_days,
                "status": mstatus,
                "completed_at": completed_at,
                "blocker": blocker,
            })

        implementations.append({
            "id": iid,
            "customer_id": c["id"],
            "customer_name": c["name"],
            "implementation_owner": c["implementation_owner"],
            "overall_status": overall_status,
            "pct_complete": pct,
            "days_behind_schedule": days_behind,
            "go_live_target": days(random.randint(10, 90)),
            "milestones": milestones,
        })
        iid += 1

    return implementations


# ══════════════════════════════════════════════════════════════════════════════
# 4. ESCALATIONS
# ══════════════════════════════════════════════════════════════════════════════

ESCALATION_TEMPLATES = [
    ("Contract SLA breach — 72hr P1 response not met for 3rd consecutive ticket",  "Critical"),
    ("Executive sponsor threatening contract termination",                           "Critical"),
    ("Implementation 6+ weeks behind schedule with no recovery plan",               "Critical"),
    ("Confirmed competitor POC underway — displacement risk",                       "Critical"),
    ("Champion left the company — no identified replacement",                       "High"),
    ("P1 security incident unresolved for 5+ days",                                "Critical"),
    ("Renewal at risk — economic buyer not engaged",                                "High"),
    ("Product gap blocking customer go-live",                                       "High"),
    ("Budget freeze announced — renewal approval not expected",                     "High"),
    ("PHI / regulated data concern raised by customer legal team",                  "Critical"),
    ("New CISO conducting platform audit — potential replacement evaluation",        "High"),
    ("OT / SCADA integration failure blocking production security controls",        "High"),
    ("Customer NPS score dropped to 4 — executive notice required",                 "High"),
    ("Customer threatening to escalate to Onyx board",                              "Critical"),
    ("Adoption < 20% at 90 days — customer questioning product value",              "High"),
]

def build_escalations(customers):
    escalations = []
    eid = 1

    high_risk = [c for c in customers if c["risk_level"] == "High"]
    medium_risk = [c for c in customers if c["risk_level"] == "Medium"]

    # High-risk customers get 2-3 escalations each
    for c in high_risk:
        count = random.randint(2, 3)
        used = set()
        for _ in range(count):
            template = random.choice([t for t in ESCALATION_TEMPLATES if t not in used])
            used.add(template)
            title, sev = template
            escalations.append({
                "id": eid,
                "customer_id": c["id"],
                "customer_name": c["name"],
                "title": title,
                "severity": sev,
                "status": random.choice(["Open", "Open", "In Progress"]),
                "owner": c["csm_owner"],
                "opened_at": ts_past(30),
                "executive_aware": sev == "Critical",
                "arr_at_risk": c["arr"],
                "resolution_plan": None,
                "last_update": ts_past(3),
            })
            eid += 1

    # Medium-risk customers get 0-1 escalation
    for c in medium_risk:
        if random.random() > 0.4:
            template = random.choice(ESCALATION_TEMPLATES[4:])  # only High severity
            title, sev = template
            escalations.append({
                "id": eid,
                "customer_id": c["id"],
                "customer_name": c["name"],
                "title": title,
                "severity": "High",
                "status": "In Progress",
                "owner": c["csm_owner"],
                "opened_at": ts_past(45),
                "executive_aware": False,
                "arr_at_risk": c["arr"],
                "resolution_plan": "CSM monitoring weekly; escalation path prepared.",
                "last_update": ts_past(7),
            })
            eid += 1

    return escalations


# ══════════════════════════════════════════════════════════════════════════════
# 5. RENEWALS
# ══════════════════════════════════════════════════════════════════════════════

def build_renewals(customers):
    renewals = []
    rid = 1
    today = date.today()

    for c in customers:
        renewal_dt = date.fromisoformat(c["renewal_date"])
        days_out   = (renewal_dt - today).days
        if days_out > 180:
            continue  # only next 180 days

        arr = c["arr"]
        risk = c["risk_level"]

        stage_map = {
            "Low":    random.choice(["Expansion Discussion", "Verbal Commit", "Renewal Signed"]),
            "Medium": random.choice(["Renewal Initiated", "Stakeholder Alignment", "Terms Under Review"]),
            "High":   random.choice(["At Risk", "Renewal Initiated", "Executive Escalation Required"]),
        }
        renewal_stage = stage_map[risk]

        # Tie renewal expansion to the customer-level expansion pipeline
        expansion_arr = c.get("expansion_pipeline_arr", 0)

        discount_requested = (
            random.randint(5, 20) if risk in ("High","Medium") else
            random.randint(0, 8)
        )

        commercial_terms = (
            f"{discount_requested}% discount requested by procurement"
            if discount_requested > 0
            else "Flat renewal expected"
        )

        procurement_contact = rname()

        renewals.append({
            "id": rid,
            "customer_id": c["id"],
            "customer_name": c["name"],
            "renewal_date": c["renewal_date"],
            "days_to_renewal": days_out,
            "current_arr": arr,
            "expansion_arr": expansion_arr,
            "projected_arr": arr + expansion_arr,
            "renewal_risk_score": c["renewal_risk_score"],
            "renewal_stage": renewal_stage,
            "commercial_terms_note": commercial_terms,
            "procurement_contact": procurement_contact,
            "csm_owner": c["csm_owner"],
            "requires_exec_involvement": risk == "High" or days_out < 30,
            "forecast_category": (
                "Commit" if risk == "Low" and renewal_stage in ("Renewal Signed","Verbal Commit")
                else "Best Case" if risk == "Low"
                else "At Risk" if risk == "High"
                else "Pipeline"
            ),
        })
        rid += 1

    renewals.sort(key=lambda r: r["days_to_renewal"])
    return renewals


# ══════════════════════════════════════════════════════════════════════════════
# 6. MEETING NOTES
# ══════════════════════════════════════════════════════════════════════════════

MEETING_TYPES = ["QBR", "Weekly Sync", "Executive Briefing", "Implementation Review",
                 "Escalation Call", "Renewal Discussion", "Technical Deep-Dive", "Onboarding Check-in"]

POSITIVE_NOTES = [
    "Customer expressed strong satisfaction with detection accuracy. NPS 9 shared unprompted. Champion confirmed willingness to be a reference.",
    "QBR delivered. Expansion to 2 additional business units discussed. Exec sponsor fully engaged and asked about multi-year pricing.",
    "Platform ROI demonstrated: 40% reduction in false positives, 2 security incidents detected and remediated this quarter. Customer team visibly impressed.",
    "Champion reported team productivity up 30% since rollout. Asked about roadmap for threat intelligence module.",
    "Renewal discussion initiated positively. Customer asked to start paperwork early. No commercial friction.",
    "Customer shared an internal case study they wrote about Onyx — planning to submit to industry conference.",
    "Technical deep-dive on integration architecture. Customer architect called the API design 'best in class.'",
    "New analyst team onboarded. Customer praised quality of training materials and support responsiveness.",
]

NEUTRAL_NOTES = [
    "Routine check-in. Customer mentioned interest in the roadmap update. No blockers raised.",
    "Implementation review. 3 milestones completed on schedule. 1 slightly delayed due to customer IT queue.",
    "Weekly sync. Team acknowledged some configuration complexity but working through it with documentation.",
    "Meeting covered usage review and upcoming feature releases. Customer noted they haven't fully activated threat hunting.",
    "Customer asked about SOC2 report availability. Shared compliance documentation. No concerns raised.",
    "Discussed integration with Splunk. Customer IT team needs 2 weeks to schedule the work. No escalation needed.",
    "Renewal date acknowledged. Customer mentioned internal budget process starts next month. No red flags.",
]

NEGATIVE_NOTES = [
    "Customer expressed frustration with P1 ticket response time. Said 'this level of service is unacceptable for the price we pay.' Escalation path initiated.",
    "Executive sponsor raised concern that platform complexity is slowing down analyst adoption. Considering scaling back deployment.",
    "Champion informed us they are leaving the company next month. No named successor yet. HIGH RISK.",
    "CFO joined unexpectedly and questioned ROI. Asked for detailed cost-benefit analysis before renewal. Timeline unclear.",
    "Customer mentioned they are evaluating a competitor. Said Onyx is 'missing key SIEM integrations they need.' Product gap confirmed.",
    "Implementation review revealed 6-week delay. Customer team visibly frustrated. Project sponsor threatened to involve their CEO.",
    "Sentiment call following P1 incident. Customer's CISO said trust has been damaged. Requires VP-to-VP call to rebuild.",
    "Budget freeze announced mid-call. Procurement contact said renewal approval is not expected until Q4. ARR at risk.",
]

def build_meeting_notes(customers, escalations):
    notes    = []
    nid      = 1
    esc_map  = {}  # customer_id -> list of escalation titles
    for e in escalations:
        esc_map.setdefault(e["customer_id"], []).append(e["title"])

    for c in customers:
        risk = c["risk_level"]
        count = random.randint(2, 4) if risk == "High" else random.randint(2, 3)

        note_pool = (
            NEGATIVE_NOTES if risk == "High"
            else NEUTRAL_NOTES + POSITIVE_NOTES if risk == "Low"
            else NEUTRAL_NOTES
        )

        for i in range(count):
            days_ago  = random.randint(3, 120)
            note_text = random.choice(note_pool)

            # If there's an active escalation, reference it in one note
            if i == 0 and c["id"] in esc_map:
                esc_ref = esc_map[c["id"]][0]
                note_text += f" [Active escalation on file: {esc_ref}]"

            meeting_type = (
                random.choice(["Escalation Call", "Executive Briefing"]) if risk == "High" and i == 0
                else random.choice(MEETING_TYPES)
            )

            notes.append({
                "id": nid,
                "customer_id": c["id"],
                "customer_name": c["name"],
                "meeting_type": meeting_type,
                "date": past(days_ago),
                "attendees_internal": f"{c['csm_owner']}, {random.choice(EXEC_SPONSORS)}",
                "attendees_customer": f"{c['champion_name']}, {c['technical_sponsor']}",
                "summary": note_text,
                "sentiment_signal": (
                    "Negative" if risk == "High" and i < 2
                    else "Positive" if risk == "Low"
                    else "Neutral"
                ),
                "action_items": json.dumps(_gen_action_items(c, risk)),
                "follow_up_due": days(random.randint(3, 14)),
            })
            nid += 1

    return notes

def _gen_action_items(c, risk):
    items = {
        "High":   [
            f"Send daily P1 ticket status update to {c['champion_name']}",
            "Schedule VP-to-VP alignment call within 72 hours",
            "Prepare executive escalation brief",
        ],
        "Medium": [
            "Share updated roadmap timeline",
            "Schedule technical integration review",
            f"Follow up with {c['technical_sponsor']} on open config items",
        ],
        "Low":    [
            "Send expansion proposal draft",
            "Invite to customer advisory board",
            "Share new feature release notes",
        ],
    }[risk]
    return random.sample(items, k=min(2, len(items)))


# ══════════════════════════════════════════════════════════════════════════════
# 7. USAGE METRICS
# ══════════════════════════════════════════════════════════════════════════════

def build_usage_metrics(customers):
    metrics = []
    mid = 1
    today_str = date.today().isoformat()

    for c in customers:
        risk    = c["risk_level"]
        adopt   = c["adoption_score"] / 100
        emp     = c["employee_count"]

        dau              = max(1, int(emp * random.uniform(0.02, 0.12) * adopt))
        mau              = max(dau, int(dau * random.uniform(2.5, 4.5)))
        features_total   = 18
        features_enabled = max(2, int(features_total * adopt + random.uniform(-2, 2)))
        api_calls_30d    = max(100, int(random.randint(2000, 600000) * adopt))
        alerts_30d       = max(10,  int(random.randint(100, 8000)    * adopt))
        fp_rate          = round(random.uniform(0.05, 0.65) * (1.5 - adopt), 2)
        reports_30d      = max(0,   int(random.randint(0, 60)        * adopt))
        integrations     = max(1,   int(random.randint(2, 14)        * adopt))
        logins_7d        = max(1,   int(dau * random.uniform(4, 7)))
        agents_deployed  = max(0,   int(random.randint(0, 50)        * adopt))
        coverage_pct     = min(100, int(adopt * 100 + random.uniform(-10, 10)))

        # Trend: healthy = growing, at-risk = shrinking or flat
        trend_30d = (
            round(random.uniform(0.05, 0.25),  2) if risk == "Low"
            else round(random.uniform(-0.20, 0.05), 2) if risk == "High"
            else round(random.uniform(-0.05, 0.12), 2)
        )

        metrics.append({
            "id": mid,
            "customer_id": c["id"],
            "customer_name": c["name"],
            "recorded_at": today_str,
            "dau": dau,
            "mau": mau,
            "features_enabled": features_enabled,
            "features_total": features_total,
            "api_calls_last_30d": api_calls_30d,
            "alerts_generated_last_30d": alerts_30d,
            "false_positive_rate": fp_rate,
            "reports_exported_last_30d": reports_30d,
            "integrations_active": integrations,
            "unique_logins_last_7d": logins_7d,
            "agents_deployed": agents_deployed,
            "asset_coverage_pct": coverage_pct,
            "dau_trend_30d": trend_30d,
        })
        mid += 1
    return metrics


# ══════════════════════════════════════════════════════════════════════════════
# 8. STAKEHOLDERS
# ══════════════════════════════════════════════════════════════════════════════

def build_stakeholders(customers):
    stakeholders = []
    sid = 1

    for c in customers:
        domain = c["name"].lower().replace(" ", "").replace(",","")[:20] + ".com"
        risk   = c["risk_level"]

        def make_person(name, title, role, engagement):
            nonlocal sid
            s = {
                "id": sid,
                "customer_id": c["id"],
                "customer_name": c["name"],
                "name": name,
                "title": title,
                "email": f"{name.lower().replace(' ','.')}@{domain}",
                "role": role,
                "engagement_level": engagement,
                "last_contacted": past(random.randint(5, 60)),
                "notes": "",
            }
            sid += 1
            return s

        champ_eng = (
            "None" if c["champion_status"] == "Left Company"
            else "Low" if c["champion_status"] == "Disengaged"
            else "High"
        )
        stakeholders.append(make_person(
            c["champion_name"], c["champion_title"], "Champion", champ_eng
        ))
        stakeholders.append(make_person(
            c["technical_sponsor"], random.choice(TECH_TITLES), "Technical Sponsor",
            "Medium" if risk != "High" else "Low"
        ))
        stakeholders.append(make_person(
            c["business_sponsor"], random.choice(BIZ_TITLES), "Business Sponsor",
            "High" if risk == "Low" else "Low" if risk == "High" else "Medium"
        ))
        # Executive contact
        stakeholders.append(make_person(
            rname(), random.choice(EXEC_TITLES), "Executive Sponsor",
            "High" if risk == "Low" else "None" if risk == "High" else "Low"
        ))
        # Optional: economic buyer
        if random.random() > 0.4:
            stakeholders.append(make_person(
                rname(), "CFO" if risk == "High" else "VP Finance", "Economic Buyer",
                "Low" if risk == "High" else "Medium"
            ))

    return stakeholders


# ══════════════════════════════════════════════════════════════════════════════
# 9. HEALTH HISTORY (30-day rolling)
# ══════════════════════════════════════════════════════════════════════════════

def build_health_history(customers):
    history = []
    hid = 1
    today = date.today()

    for c in customers:
        current = c["health_score"]
        trend   = c["health_trend"]

        # Work backwards 30 days
        for offset in range(30, 0, -1):
            day = today - timedelta(days=offset)
            delta = (
                random.uniform(-3, -0.5) if trend == "Declining"
                else random.uniform(0.2, 2.5) if trend == "Improving"
                else random.uniform(-1.5, 1.5)
            )
            # Approximate historical score
            days_back = 30 - offset
            historical = current - (delta * days_back / 30 * 15)
            historical = round(max(10, min(100, historical + random.uniform(-2, 2))), 1)

            history.append({
                "id": hid,
                "customer_id": c["id"],
                "customer_name": c["name"],
                "date": day.isoformat(),
                "health_score": historical,
                "health_trend": trend,
                "notes": None,
            })
            hid += 1

    return history


# ══════════════════════════════════════════════════════════════════════════════
# WRITE JSON FILES
# ══════════════════════════════════════════════════════════════════════════════

def write_json(data, filename):
    path = DATA_DIR / filename
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    print(f"  Wrote {len(data):>4} records → {path.name}")


# ══════════════════════════════════════════════════════════════════════════════
# SEED SQLite
# ══════════════════════════════════════════════════════════════════════════════

SCHEMA = """
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS support_tickets;
DROP TABLE IF EXISTS implementations;
DROP TABLE IF EXISTS implementation_milestones;
DROP TABLE IF EXISTS escalations;
DROP TABLE IF EXISTS renewals;
DROP TABLE IF EXISTS meeting_notes;
DROP TABLE IF EXISTS usage_metrics;
DROP TABLE IF EXISTS stakeholders;
DROP TABLE IF EXISTS health_history;
DROP TABLE IF EXISTS agent_runs;
DROP TABLE IF EXISTS briefings;

CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT, industry TEXT, region TEXT, customer_tier TEXT,
    employee_count INTEGER, arr INTEGER,
    contract_start_date TEXT, renewal_date TEXT, contract_term_months INTEGER,
    lifecycle_stage TEXT, health_score INTEGER, health_trend TEXT,
    csm_owner TEXT, implementation_owner TEXT, executive_sponsor_internal TEXT,
    champion_name TEXT, champion_title TEXT, champion_status TEXT,
    technical_sponsor TEXT, business_sponsor TEXT,
    adoption_score INTEGER, utilization_pct INTEGER, sentiment TEXT,
    nps INTEGER, nps_trend TEXT,
    risk_level TEXT, primary_risk_reason TEXT, recommended_next_action TEXT,
    renewal_risk_score REAL, nrr_pct INTEGER, grr_pct INTEGER,
    upsell_likelihood REAL, expansion_pipeline_arr INTEGER,
    time_to_first_value_days INTEGER, time_to_production_days INTEGER,
    executive_engagement TEXT, qbr_completion TEXT, last_qbr_date TEXT,
    usage_trend TEXT, cost_to_serve INTEGER, roi_outcome TEXT,
    onboarding_status TEXT, security_review_status TEXT,
    arr_formatted TEXT
);

CREATE TABLE support_tickets (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER, customer_name TEXT,
    title TEXT, severity TEXT, status TEXT,
    opened_at TEXT, resolved_at TEXT,
    escalation_reference TEXT, assignee TEXT, days_open INTEGER,
    FOREIGN KEY(customer_id) REFERENCES customers(id)
);

CREATE TABLE implementations (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER, customer_name TEXT,
    implementation_owner TEXT, overall_status TEXT,
    pct_complete INTEGER, days_behind_schedule INTEGER,
    go_live_target TEXT,
    FOREIGN KEY(customer_id) REFERENCES customers(id)
);

CREATE TABLE implementation_milestones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    implementation_id INTEGER, customer_id INTEGER,
    milestone_name TEXT, planned_days_from_start INTEGER,
    status TEXT, completed_at TEXT, blocker TEXT,
    FOREIGN KEY(implementation_id) REFERENCES implementations(id),
    FOREIGN KEY(customer_id) REFERENCES customers(id)
);

CREATE TABLE escalations (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER, customer_name TEXT,
    title TEXT, severity TEXT, status TEXT,
    owner TEXT, opened_at TEXT,
    executive_aware INTEGER, arr_at_risk INTEGER,
    resolution_plan TEXT, last_update TEXT,
    FOREIGN KEY(customer_id) REFERENCES customers(id)
);

CREATE TABLE renewals (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER, customer_name TEXT,
    renewal_date TEXT, days_to_renewal INTEGER,
    current_arr INTEGER, expansion_arr INTEGER, projected_arr INTEGER,
    renewal_risk_score REAL, renewal_stage TEXT,
    commercial_terms_note TEXT, procurement_contact TEXT,
    csm_owner TEXT, requires_exec_involvement INTEGER, forecast_category TEXT,
    FOREIGN KEY(customer_id) REFERENCES customers(id)
);

CREATE TABLE meeting_notes (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER, customer_name TEXT,
    meeting_type TEXT, date TEXT,
    attendees_internal TEXT, attendees_customer TEXT,
    summary TEXT, sentiment_signal TEXT,
    action_items TEXT, follow_up_due TEXT,
    FOREIGN KEY(customer_id) REFERENCES customers(id)
);

CREATE TABLE usage_metrics (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER, customer_name TEXT, recorded_at TEXT,
    dau INTEGER, mau INTEGER,
    features_enabled INTEGER, features_total INTEGER,
    api_calls_last_30d INTEGER, alerts_generated_last_30d INTEGER,
    false_positive_rate REAL, reports_exported_last_30d INTEGER,
    integrations_active INTEGER, unique_logins_last_7d INTEGER,
    agents_deployed INTEGER, asset_coverage_pct INTEGER,
    dau_trend_30d REAL,
    FOREIGN KEY(customer_id) REFERENCES customers(id)
);

CREATE TABLE stakeholders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER, customer_name TEXT,
    name TEXT, title TEXT, email TEXT,
    role TEXT, engagement_level TEXT,
    last_contacted TEXT, notes TEXT,
    FOREIGN KEY(customer_id) REFERENCES customers(id)
);

CREATE TABLE health_history (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER, customer_name TEXT,
    date TEXT, health_score REAL, health_trend TEXT, notes TEXT,
    FOREIGN KEY(customer_id) REFERENCES customers(id)
);

CREATE TABLE agent_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name TEXT, customer_id INTEGER,
    model_used TEXT, model_rationale TEXT,
    input_tokens INTEGER, output_tokens INTEGER,
    estimated_cost_usd REAL, confidence_score REAL,
    output_text TEXT, created_at TEXT,
    FOREIGN KEY(customer_id) REFERENCES customers(id)
);

CREATE TABLE briefings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    briefing_type TEXT, customer_id INTEGER,
    content TEXT, agent_run_id INTEGER,
    created_at TEXT,
    FOREIGN KEY(customer_id) REFERENCES customers(id),
    FOREIGN KEY(agent_run_id) REFERENCES agent_runs(id)
);
"""


def seed_database(customers, tickets, implementations, escalations, renewals,
                  meeting_notes, usage_metrics, stakeholders, health_history):
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)

    def ins(table, rows, cols):
        if not rows:
            return
        placeholders = ",".join(["?"] * len(cols))
        conn.executemany(
            f"INSERT INTO {table} ({','.join(cols)}) VALUES ({placeholders})",
            [[r.get(c) for c in cols] for r in rows]
        )

    ins("customers", customers, [
        "id","name","industry","region","customer_tier","employee_count","arr",
        "contract_start_date","renewal_date","contract_term_months",
        "lifecycle_stage","health_score","health_trend","csm_owner","implementation_owner",
        "executive_sponsor_internal","champion_name","champion_title","champion_status",
        "technical_sponsor","business_sponsor","adoption_score","utilization_pct","sentiment",
        "nps","nps_trend","risk_level","primary_risk_reason","recommended_next_action",
        "renewal_risk_score","nrr_pct","grr_pct","upsell_likelihood","expansion_pipeline_arr",
        "time_to_first_value_days","time_to_production_days","executive_engagement",
        "qbr_completion","last_qbr_date","usage_trend","cost_to_serve","roi_outcome",
        "onboarding_status","security_review_status","arr_formatted"
    ])

    ins("support_tickets", tickets, [
        "id","customer_id","customer_name","title","severity","status",
        "opened_at","resolved_at","escalation_reference","assignee","days_open"
    ])

    impl_rows = []
    milestone_rows = []
    for impl in implementations:
        impl_rows.append(impl)
        for m in impl["milestones"]:
            milestone_rows.append({**m, "implementation_id": impl["id"], "customer_id": impl["customer_id"]})

    ins("implementations", impl_rows, [
        "id","customer_id","customer_name","implementation_owner","overall_status",
        "pct_complete","days_behind_schedule","go_live_target"
    ])
    ins("implementation_milestones", milestone_rows, [
        "implementation_id","customer_id","milestone_name","planned_days_from_start",
        "status","completed_at","blocker"
    ])

    ins("escalations", escalations, [
        "id","customer_id","customer_name","title","severity","status","owner",
        "opened_at","executive_aware","arr_at_risk","resolution_plan","last_update"
    ])

    ins("renewals", renewals, [
        "id","customer_id","customer_name","renewal_date","days_to_renewal",
        "current_arr","expansion_arr","projected_arr","renewal_risk_score",
        "renewal_stage","commercial_terms_note","procurement_contact",
        "csm_owner","requires_exec_involvement","forecast_category"
    ])

    ins("meeting_notes", meeting_notes, [
        "id","customer_id","customer_name","meeting_type","date",
        "attendees_internal","attendees_customer","summary","sentiment_signal",
        "action_items","follow_up_due"
    ])

    ins("usage_metrics", usage_metrics, [
        "id","customer_id","customer_name","recorded_at","dau","mau",
        "features_enabled","features_total","api_calls_last_30d",
        "alerts_generated_last_30d","false_positive_rate","reports_exported_last_30d",
        "integrations_active","unique_logins_last_7d","agents_deployed",
        "asset_coverage_pct","dau_trend_30d"
    ])

    ins("stakeholders", stakeholders, [
        "id","customer_id","customer_name","name","title","email",
        "role","engagement_level","last_contacted","notes"
    ])

    ins("health_history", health_history, [
        "id","customer_id","customer_name","date","health_score","health_trend","notes"
    ])

    conn.commit()
    conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("VP CX Agent OS — Synthetic Data Generator")
    print("=" * 50)

    customers      = build_customers()
    tickets        = build_tickets(customers)
    implementations= build_implementations(customers)
    escalations    = build_escalations(customers)
    renewals       = build_renewals(customers)
    meeting_notes  = build_meeting_notes(customers, escalations)
    usage_metrics  = build_usage_metrics(customers)
    stakeholders   = build_stakeholders(customers)
    health_history = build_health_history(customers)

    print("\nWriting JSON files:")
    write_json(customers,      "customers.json")
    write_json(tickets,        "support_tickets.json")
    write_json(implementations,"implementations.json")
    write_json(escalations,    "escalations.json")
    write_json(renewals,       "renewals.json")
    write_json(meeting_notes,  "meeting_notes.json")
    write_json(usage_metrics,  "usage_metrics.json")
    write_json(stakeholders,   "stakeholders.json")
    write_json(health_history, "health_history.json")

    print("\nSeeding SQLite database:")
    seed_database(customers, tickets, implementations, escalations, renewals,
                  meeting_notes, usage_metrics, stakeholders, health_history)

    # Verification
    conn = sqlite3.connect(DB_PATH)
    tables = ["customers","support_tickets","implementations","implementation_milestones",
              "escalations","renewals","meeting_notes","usage_metrics","stakeholders","health_history"]
    for t in tables:
        n = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t:<30} {n:>4} rows")
    conn.close()

    # Summary stats
    high   = sum(1 for c in customers if c["risk_level"] == "High")
    medium = sum(1 for c in customers if c["risk_level"] == "Medium")
    low    = sum(1 for c in customers if c["risk_level"] == "Low")
    arr_at_risk = sum(c["arr"] for c in customers if c["risk_level"] in ("High","Medium"))

    print(f"\nPortfolio Summary:")
    print(f"  Customers: {len(customers)} total — {high} high / {medium} medium / {low} low risk")
    print(f"  Total ARR: ${sum(c['arr'] for c in customers):,.0f}")
    print(f"  ARR at Risk: ${arr_at_risk:,.0f}")
    print(f"  Escalations: {len(escalations)}")
    print(f"  Renewals (180d): {len(renewals)}")
    print(f"  Support Tickets: {len(tickets)}")
    print(f"\nDone. Database at {DB_PATH}")


if __name__ == "__main__":
    main()
