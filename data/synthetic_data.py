"""
Generates realistic synthetic data for 25 enterprise customers.
Run directly to seed the database: python data/synthetic_data.py
"""

import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

CUSTOMERS = [
    ("Acme Corp", "Manufacturing", 480000, -45, 42, "At Risk"),
    ("BioNexus Health", "Healthcare", 720000, 87, 71, "Healthy"),
    ("ClearPath Logistics", "Logistics", 310000, 23, 55, "At Risk"),
    ("DataVault Analytics", "Financial Services", 950000, 112, 83, "Healthy"),
    ("Evora Energy", "Energy", 560000, 67, 68, "Healthy"),
    ("Fortress Bank", "Financial Services", 1200000, 34, 44, "At Risk"),
    ("GlobalEdge Retail", "Retail", 290000, 178, 61, "Healthy"),
    ("HealthFirst Insurance", "Insurance", 840000, 56, 52, "At Risk"),
    ("InnovateTech", "Technology", 430000, 91, 79, "Healthy"),
    ("JetStream Airlines", "Transportation", 670000, 15, 38, "Critical"),
    ("Kestrel Defense", "Defense", 1100000, 203, 88, "Healthy"),
    ("LuminaCare Medical", "Healthcare", 380000, 8, 31, "Critical"),
    ("MegaMart Wholesale", "Retail", 520000, 134, 73, "Healthy"),
    ("NovaTech Systems", "Technology", 760000, 61, 66, "Healthy"),
    ("OmniCloud Infra", "Technology", 890000, 29, 48, "At Risk"),
    ("PrecisionMfg Co", "Manufacturing", 340000, 145, 77, "Healthy"),
    ("QuantumLeap Finance", "Financial Services", 620000, 72, 70, "Healthy"),
    ("RedRock Mining", "Energy", 410000, 19, 35, "Critical"),
    ("Silverline Media", "Media", 280000, 95, 62, "Healthy"),
    ("TitanBuild Construction", "Construction", 370000, 41, 57, "At Risk"),
    ("UltraSecure Gov", "Government", 930000, 118, 85, "Healthy"),
    ("VantagePoint Capital", "Financial Services", 750000, 52, 60, "At Risk"),
    ("WestCoast Pharma", "Pharma", 580000, 83, 74, "Healthy"),
    ("XcelOps Consulting", "Professional Services", 320000, 37, 49, "At Risk"),
    ("ZenithAero Systems", "Aerospace", 1050000, 156, 91, "Healthy"),
]

INDUSTRIES = {
    "Manufacturing": ["supply chain visibility", "asset tracking", "compliance audit"],
    "Healthcare": ["PHI data protection", "incident response", "access controls"],
    "Logistics": ["fleet security", "API integrations", "real-time alerting"],
    "Financial Services": ["SOC2 compliance", "threat detection", "pen testing"],
    "Energy": ["OT security", "SCADA protection", "vendor risk"],
    "Insurance": ["claims fraud detection", "data governance", "cloud security"],
    "Technology": ["DevSecOps", "secrets management", "SIEM integration"],
    "Transportation": ["endpoint protection", "network segmentation", "IR planning"],
    "Defense": ["zero trust rollout", "classified data handling", "audit logging"],
    "Retail": ["PCI compliance", "fraud prevention", "mobile security"],
    "Media": ["content protection", "DRM enforcement", "insider threat"],
    "Construction": ["subcontractor access", "remote site security", "IoT protection"],
    "Government": ["FedRAMP alignment", "data residency", "privileged access"],
    "Professional Services": ["client data isolation", "secure collaboration", "DLP"],
    "Aerospace": ["export control compliance", "supply chain integrity", "ITAR"],
    "Pharma": ["IP protection", "clinical trial data security", "GxP compliance"],
}

CHAMPION_TITLES = ["CISO", "VP of IT", "Head of Security", "Director of InfoSec", "CTO", "VP Engineering"]
EXEC_TITLES = ["CEO", "CFO", "COO", "CTO", "CISO", "VP IT", "Director of Procurement"]
FIRST_NAMES = ["James", "Sarah", "Michael", "Jennifer", "Robert", "Lisa", "David", "Emily", "Chris", "Amanda",
               "Brian", "Rachel", "Kevin", "Stephanie", "Mark", "Nicole", "Eric", "Megan", "Jason", "Lauren"]
LAST_NAMES = ["Chen", "Thompson", "Rodriguez", "Kim", "Patel", "Williams", "Johnson", "Davis", "Martinez", "Brown",
              "Wilson", "Anderson", "Taylor", "Moore", "Jackson", "White", "Harris", "Martin", "Garcia", "Lee"]

TICKET_TITLES = [
    "SSO integration failing intermittently",
    "API rate limits too restrictive",
    "Dashboard reports not loading",
    "MFA enrollment errors for new users",
    "Alert noise too high - false positives",
    "Unable to export compliance reports",
    "Integration with Splunk broken after update",
    "User provisioning delays > 24 hours",
    "Slow query performance on large datasets",
    "Webhook delivery failing",
    "Role-based access not propagating correctly",
    "Audit log gaps detected",
    "Cloud connector configuration issue",
    "Password reset flow broken",
    "Custom rule engine not triggering",
]

ESCALATION_TITLES = [
    "Contract SLA breach risk - 72hr response not met",
    "Executive sponsor threatening to pull contract",
    "Implementation 6 weeks behind schedule",
    "Competing vendor POC underway",
    "Champion left the company",
    "P1 incident unresolved for 5+ days",
    "Renewal at risk - CFO not engaged",
    "Product gap blocking go-live",
]

MILESTONE_NAMES = [
    "Kickoff & scoping complete",
    "Technical discovery session",
    "Environment provisioning",
    "SSO / IdP integration",
    "Initial data ingestion",
    "Pilot group onboarding",
    "Policy configuration",
    "Integration testing",
    "Security review signoff",
    "Full production rollout",
    "QBR #1 - 90 day review",
    "Advanced feature enablement",
]

MEETING_SUMMARIES = [
    "Reviewed implementation progress. Customer expressed concern about timeline slippage. Agreed to weekly syncs.",
    "QBR conducted. Positive sentiment on product capabilities. Renewal discussion deferred to next quarter.",
    "Champion raised concern about lack of exec visibility. Agreed to schedule C-suite briefing.",
    "Technical deep-dive on integration architecture. Two blockers identified, escalated to engineering.",
    "Executive sponsor expressed strong satisfaction with ROI. Expansion opportunity surfaced.",
    "Check-in call. Customer reported 40% reduction in false positives. NPS score shared as 9/10.",
    "Discovery session for phase 2. Customer wants to expand to 3 new business units.",
    "Urgent call requested by customer. P1 ticket unresolved, customer frustrated.",
    "Renewal conversation initiated. Procurement wants 15% discount. Legal review underway.",
    "Onboarding review. New security analyst joined, needs platform training.",
]

def random_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

def days_from_now(days):
    return (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

def random_date_past(max_days=180):
    d = random.randint(1, max_days)
    return (datetime.now() - timedelta(days=d)).strftime("%Y-%m-%dT%H:%M:%S")

def build_customers():
    rows = []
    for i, (name, industry, arr, renewal_offset, adoption, risk_label) in enumerate(CUSTOMERS):
        health = {
            "Critical": random.randint(20, 39),
            "At Risk": random.randint(40, 59),
            "Healthy": random.randint(65, 95),
        }[risk_label]
        renewal_risk = {
            "Critical": random.uniform(0.65, 0.90),
            "At Risk": random.uniform(0.35, 0.64),
            "Healthy": random.uniform(0.05, 0.34),
        }[risk_label]
        champion_status = random.choice(["Active", "Active", "Active", "Left Company", "Disengaged"])
        if risk_label == "Critical":
            champion_status = random.choice(["Left Company", "Disengaged"])
        sentiment = {
            "Critical": random.choice(["Negative", "Negative", "Neutral"]),
            "At Risk": random.choice(["Neutral", "Neutral", "Positive", "Negative"]),
            "Healthy": random.choice(["Positive", "Positive", "Neutral"]),
        }[risk_label]
        onboarding = {
            "Critical": random.choice(["Stalled", "Partial"]),
            "At Risk": random.choice(["Partial", "Complete", "Stalled"]),
            "Healthy": "Complete",
        }[risk_label]
        sec_review = {
            "Critical": "Not Started",
            "At Risk": random.choice(["In Progress", "Not Started"]),
            "Healthy": random.choice(["Complete", "In Progress"]),
        }[risk_label]
        rows.append({
            "id": i + 1,
            "name": name,
            "industry": industry,
            "arr": arr,
            "renewal_date": days_from_now(renewal_offset),
            "health_score": health,
            "onboarding_status": onboarding,
            "adoption_score": adoption,
            "champion_name": random_name(),
            "champion_status": champion_status,
            "sentiment": sentiment,
            "renewal_risk": round(renewal_risk, 2),
            "security_review_status": sec_review,
            "risk_label": risk_label,
        })
    return rows

def build_tickets(customers):
    rows = []
    tid = 1
    for c in customers:
        count = {
            "Critical": random.randint(3, 6),
            "At Risk": random.randint(1, 4),
            "Healthy": random.randint(0, 2),
        }[c["risk_label"]]
        for _ in range(count):
            sev = random.choice(["P1", "P1", "P2", "P2", "P3"]) if c["risk_label"] == "Critical" else random.choice(["P2", "P2", "P3", "P3", "P4"])
            status = random.choice(["Open", "Open", "In Progress", "Resolved"])
            opened = random_date_past(90)
            resolved = None
            if status == "Resolved":
                resolved = random_date_past(30)
            rows.append({
                "id": tid,
                "customer_id": c["id"],
                "title": random.choice(TICKET_TITLES),
                "severity": sev,
                "status": status,
                "opened_at": opened,
                "resolved_at": resolved,
            })
            tid += 1
    return rows

def build_escalations(customers):
    rows = []
    eid = 1
    for c in customers:
        if c["risk_label"] == "Critical":
            count = random.randint(1, 3)
        elif c["risk_label"] == "At Risk":
            count = random.randint(0, 2)
        else:
            count = 0
        for _ in range(count):
            rows.append({
                "id": eid,
                "customer_id": c["id"],
                "title": random.choice(ESCALATION_TITLES),
                "severity": random.choice(["Critical", "High"]) if c["risk_label"] == "Critical" else "High",
                "owner": random_name(),
                "status": random.choice(["Open", "In Progress"]),
                "opened_at": random_date_past(30),
            })
            eid += 1
    return rows

def build_stakeholders(customers):
    rows = []
    sid = 1
    for c in customers:
        # Always add champion
        rows.append({
            "id": sid,
            "customer_id": c["id"],
            "name": c["champion_name"],
            "title": random.choice(CHAMPION_TITLES),
            "email": f"{c['champion_name'].lower().replace(' ', '.')}@{c['name'].lower().replace(' ', '')}.com",
            "role": "Champion",
        })
        sid += 1
        # Add 2-3 more stakeholders
        for _ in range(random.randint(2, 3)):
            name = random_name()
            rows.append({
                "id": sid,
                "customer_id": c["id"],
                "name": name,
                "title": random.choice(EXEC_TITLES),
                "email": f"{name.lower().replace(' ', '.')}@{c['name'].lower().replace(' ', '')}.com",
                "role": random.choice(["Executive Sponsor", "Economic Buyer", "End User Lead", "Technical Contact"]),
            })
            sid += 1
    return rows

def build_usage_metrics(customers):
    rows = []
    uid = 1
    for c in customers:
        base = c["adoption_score"] / 100
        metrics = {
            "dau": int(random.randint(10, 500) * base),
            "features_enabled": int(random.randint(3, 20) * base),
            "api_calls_last_30d": int(random.randint(1000, 500000) * base),
            "alerts_generated_last_30d": int(random.randint(50, 5000) * base),
            "reports_exported_last_30d": int(random.randint(0, 50) * base),
            "integrations_active": int(random.randint(1, 12) * base),
            "login_last_7d_unique_users": int(random.randint(5, 200) * base),
        }
        for metric_name, value in metrics.items():
            rows.append({
                "id": uid,
                "customer_id": c["id"],
                "metric_name": metric_name,
                "value": value,
                "recorded_at": days_from_now(0),
            })
            uid += 1
    return rows

def build_milestones(customers):
    rows = []
    mid = 1
    for c in customers:
        milestones = MILESTONE_NAMES[:12] if c["risk_label"] == "Healthy" else MILESTONE_NAMES[:random.randint(4, 9)]
        progress = {
            "Healthy": 0.85,
            "At Risk": 0.55,
            "Critical": 0.30,
        }[c["risk_label"]]
        for i, name in enumerate(milestones):
            complete_threshold = int(len(milestones) * progress)
            if i < complete_threshold:
                status = "Complete"
                completed = random_date_past(random.randint(10, 120))
            elif i == complete_threshold:
                status = "In Progress"
                completed = None
            else:
                status = "Not Started"
                completed = None
            rows.append({
                "id": mid,
                "customer_id": c["id"],
                "name": name,
                "status": status,
                "due_date": days_from_now(random.randint(-30, 60)),
                "completed_at": completed,
            })
            mid += 1
    return rows

def build_meeting_notes(customers):
    rows = []
    nid = 1
    for c in customers:
        count = random.randint(2, 6)
        for i in range(count):
            rows.append({
                "id": nid,
                "customer_id": c["id"],
                "date": random_date_past(random.randint(5, 120)),
                "summary": random.choice(MEETING_SUMMARIES),
                "attendees": f"{random_name()}, {random_name()}, {c['champion_name']}",
                "sentiment_signal": c["sentiment"] if random.random() > 0.3 else random.choice(["Positive", "Neutral", "Negative"]),
            })
            nid += 1
    return rows

def seed_database(db_path="data/cx_agent_os.db"):
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.executescript("""
    DROP TABLE IF EXISTS customers;
    DROP TABLE IF EXISTS support_tickets;
    DROP TABLE IF EXISTS escalations;
    DROP TABLE IF EXISTS stakeholders;
    DROP TABLE IF EXISTS usage_metrics;
    DROP TABLE IF EXISTS implementation_milestones;
    DROP TABLE IF EXISTS meeting_notes;
    DROP TABLE IF EXISTS agent_runs;
    DROP TABLE IF EXISTS briefings;

    CREATE TABLE customers (
        id INTEGER PRIMARY KEY,
        name TEXT, industry TEXT, arr INTEGER,
        renewal_date TEXT, health_score INTEGER,
        onboarding_status TEXT, adoption_score INTEGER,
        champion_name TEXT, champion_status TEXT,
        sentiment TEXT, renewal_risk REAL,
        security_review_status TEXT, risk_label TEXT
    );

    CREATE TABLE support_tickets (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER, title TEXT, severity TEXT,
        status TEXT, opened_at TEXT, resolved_at TEXT,
        FOREIGN KEY(customer_id) REFERENCES customers(id)
    );

    CREATE TABLE escalations (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER, title TEXT, severity TEXT,
        owner TEXT, status TEXT, opened_at TEXT,
        FOREIGN KEY(customer_id) REFERENCES customers(id)
    );

    CREATE TABLE stakeholders (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER, name TEXT, title TEXT,
        email TEXT, role TEXT,
        FOREIGN KEY(customer_id) REFERENCES customers(id)
    );

    CREATE TABLE usage_metrics (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER, metric_name TEXT,
        value REAL, recorded_at TEXT,
        FOREIGN KEY(customer_id) REFERENCES customers(id)
    );

    CREATE TABLE implementation_milestones (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER, name TEXT, status TEXT,
        due_date TEXT, completed_at TEXT,
        FOREIGN KEY(customer_id) REFERENCES customers(id)
    );

    CREATE TABLE meeting_notes (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER, date TEXT, summary TEXT,
        attendees TEXT, sentiment_signal TEXT,
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
    """)

    customers = build_customers()
    tickets = build_tickets(customers)
    escalations = build_escalations(customers)
    stakeholders = build_stakeholders(customers)
    metrics = build_usage_metrics(customers)
    milestones = build_milestones(customers)
    notes = build_meeting_notes(customers)

    c.executemany("INSERT INTO customers VALUES (:id,:name,:industry,:arr,:renewal_date,:health_score,:onboarding_status,:adoption_score,:champion_name,:champion_status,:sentiment,:renewal_risk,:security_review_status,:risk_label)", customers)
    c.executemany("INSERT INTO support_tickets VALUES (:id,:customer_id,:title,:severity,:status,:opened_at,:resolved_at)", tickets)
    c.executemany("INSERT INTO escalations VALUES (:id,:customer_id,:title,:severity,:owner,:status,:opened_at)", escalations)
    c.executemany("INSERT INTO stakeholders VALUES (:id,:customer_id,:name,:title,:email,:role)", stakeholders)
    c.executemany("INSERT INTO usage_metrics VALUES (:id,:customer_id,:metric_name,:value,:recorded_at)", metrics)
    c.executemany("INSERT INTO implementation_milestones VALUES (:id,:customer_id,:name,:status,:due_date,:completed_at)", milestones)
    c.executemany("INSERT INTO meeting_notes VALUES (:id,:customer_id,:date,:summary,:attendees,:sentiment_signal)", notes)

    conn.commit()
    conn.close()
    print(f"Seeded {len(customers)} customers and all related data into {db_path}")

if __name__ == "__main__":
    seed_database()
