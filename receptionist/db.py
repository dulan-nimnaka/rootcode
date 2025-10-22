import os
import sqlite3
from typing import Iterable

DB_FILE = os.path.join(os.path.dirname(__file__), "receptionist.db")

def get_db_path() -> str:
    return DB_FILE

def init_db(force: bool = False) -> None:
    """Create a small SQLite DB with table metadata for the restaurant."""
    if os.path.exists(DB_FILE) and not force:
        return
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tables (
        table_id TEXT PRIMARY KEY,
        capacity INTEGER NOT NULL,
        status TEXT NOT NULL,
        is_combinable INTEGER NOT NULL,
        sync_id TEXT
    )
    """)
    # seed data
    cur.execute("DELETE FROM tables")
    seed = [
        ("T1", 4, "Available", 1, None),
        ("T2", 4, "Available", 1, None),
        ("T3_A", 6, "Available", 0, "S1"),
        ("T3_B", 6, "Available", 0, "S1"),
        ("T4", 2, "Available", 1, None),
    ]
    cur.executemany("INSERT INTO tables(table_id, capacity, status, is_combinable, sync_id) VALUES (?, ?, ?, ?, ?)", seed)
    conn.commit()
    conn.close()

def list_tables() -> Iterable[dict]:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM tables")
    rows = cur.fetchall()
    conn.close()
    for r in rows:
        yield dict(r)

def update_table_status(table_id: str, status: str) -> None:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("UPDATE tables SET status = ? WHERE table_id = ?", (status, table_id))
    conn.commit()
    conn.close()
