import pytest

from valon_decision_engine.database import init_db


@pytest.fixture
def db_path(tmp_path):
    """Provide a fresh SQLite database for each test."""
    path = str(tmp_path / "test.db")
    init_db(path)
    return path
