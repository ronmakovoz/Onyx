"""
reset_demo_db.py
Wipes agent_runs and briefings tables so the demo starts clean,
then re-runs the full synthetic data generator.
Run: python data/reset_demo_db.py
"""

import sqlite3
import subprocess
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent / "cx_agent_os.db"
DATA_DIR = Path(__file__).parent


def reset():
    print("VP CX Agent OS — Demo Reset")
    print("=" * 40)

    # 1. Wipe transactional tables (agent outputs) if DB exists
    if DB_PATH.exists():
        conn = sqlite3.connect(DB_PATH)
        conn.executescript("""
            DELETE FROM agent_runs;
            DELETE FROM briefings;
        """)
        # Reset autoincrement counters
        conn.execute("DELETE FROM sqlite_sequence WHERE name IN ('agent_runs','briefings')")
        conn.commit()
        conn.close()
        print("  Cleared agent_runs and briefings tables.")
    else:
        print("  No existing database found — will create fresh.")

    # 2. Re-run data generator to refresh synthetic data
    print("  Regenerating synthetic data...")
    result = subprocess.run(
        [sys.executable, str(DATA_DIR / "generate_synthetic_data.py")],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print("ERROR:", result.stderr)
        sys.exit(1)

    # 3. Wipe JSON files (optional — regenerated above)
    json_files = [
        "customers.json", "support_tickets.json", "implementations.json",
        "escalations.json", "renewals.json", "meeting_notes.json",
        "usage_metrics.json", "stakeholders.json", "health_history.json",
    ]
    for f in json_files:
        p = DATA_DIR / f
        if p.exists():
            pass  # already overwritten by generator

    print("\nReset complete. Demo database is ready.")
    print(f"  Database: {DB_PATH}")


if __name__ == "__main__":
    reset()
