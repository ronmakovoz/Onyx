import sqlite3
from pathlib import Path
from contextlib import contextmanager

DB_PATH = Path(__file__).parent.parent / "data" / "cx_agent_os.db"


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def fetchall(query, params=()):
    with get_conn() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]


def fetchone(query, params=()):
    with get_conn() as conn:
        row = conn.execute(query, params).fetchone()
    return dict(row) if row else None


def execute(query, params=()):
    with get_conn() as conn:
        cur = conn.execute(query, params)
        return cur.lastrowid
