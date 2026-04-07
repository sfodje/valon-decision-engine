import sqlite3
import pytest
from valon_decision_engine.database import init_db, get_connection


def test_init_db_creates_rule_sets_table(tmp_path):
    path = str(tmp_path / "test.db")
    init_db(path)
    with get_connection(path) as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='rule_sets'"
        )
        assert cursor.fetchone() is not None


def test_init_db_creates_decisions_table(tmp_path):
    path = str(tmp_path / "test.db")
    init_db(path)
    with get_connection(path) as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='decisions'"
        )
        assert cursor.fetchone() is not None


def test_init_db_is_idempotent(tmp_path):
    path = str(tmp_path / "test.db")
    init_db(path)
    init_db(path)  # second call must not raise


def test_get_connection_returns_row_factory(tmp_path):
    path = str(tmp_path / "test.db")
    init_db(path)
    with get_connection(path) as conn:
        assert conn.row_factory == sqlite3.Row
