"""Database initialization module."""
import sqlite3
from contextlib import contextmanager


def init_db(db_path: str) -> None:
    """Create tables if they don't exist. Safe to call multiple times.

    Args:
        db_path: Path to the SQLite database file.
    """
    with get_connection(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS rule_sets (
                rule_set_id TEXT NOT NULL,
                version     INTEGER NOT NULL,
                rules_json  TEXT NOT NULL,
                PRIMARY KEY (rule_set_id, version)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS decisions (
                decision_id       TEXT PRIMARY KEY,
                rule_set_id       TEXT NOT NULL,
                rule_set_version  INTEGER NOT NULL,
                loan_id           TEXT,
                fact_snapshot     TEXT NOT NULL,
                actions_taken     TEXT NOT NULL,
                timestamp         TEXT NOT NULL
            )
        """)
        conn.commit()


@contextmanager
def get_connection(db_path: str):
    """Yield a sqlite3 connection with Row factory set.

    Args:
        db_path: Path to the SQLite database file.

    Yields:
        A sqlite3 connection object with row_factory set to sqlite3.Row.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
