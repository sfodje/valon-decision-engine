import os
import pytest
from fastapi.testclient import TestClient
from valon_decision_engine.rule_store import save_rule_set


WAIVER_RULES = [
    {
        "condition": {
            "all": [
                {"fact": "has_hardship_flag", "operator": "is_true"},
                {"fact": "get_days_late", "operator": "less_than_or_equal_to", "value": 30},
            ]
        },
        "actions": [{"action": "waive_late_fee"}],
    }
]


@pytest.fixture
def client(db_path):
    os.environ["DB_PATH"] = db_path
    import importlib
    import valon_decision_engine.api as api_module
    importlib.reload(api_module)
    from valon_decision_engine.api import app
    return TestClient(app)


@pytest.fixture
def seeded_client(client, db_path):
    save_rule_set(db_path, "late_fee_waiver", WAIVER_RULES)
    return client


def test_post_decisions_returns_200(seeded_client):
    response = seeded_client.post("/decisions", json={
        "rule_set_id": "late_fee_waiver",
        "fact": {"days_late": 10, "has_hardship": True, "days_until_tax_payment": 60},
        "loan_id": "loan-001",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["rule_set_id"] == "late_fee_waiver"
    assert "waive_late_fee" in data["actions_taken"]


def test_post_decisions_returns_404_for_unknown_rule_set(client):
    response = client.post("/decisions", json={
        "rule_set_id": "nonexistent",
        "fact": {"days_late": 10, "has_hardship": True, "days_until_tax_payment": 60},
    })
    assert response.status_code == 404


def test_get_decision_by_id(seeded_client):
    post_resp = seeded_client.post("/decisions", json={
        "rule_set_id": "late_fee_waiver",
        "fact": {"days_late": 5, "has_hardship": True, "days_until_tax_payment": 60},
        "loan_id": "loan-002",
    })
    decision_id = post_resp.json()["decision_id"]
    get_resp = seeded_client.get(f"/decisions/{decision_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["decision_id"] == decision_id


def test_get_decision_returns_404_for_unknown_id(client):
    response = client.get("/decisions/nonexistent-id")
    assert response.status_code == 404


def test_get_decisions_by_loan_id(seeded_client):
    for _ in range(3):
        seeded_client.post("/decisions", json={
            "rule_set_id": "late_fee_waiver",
            "fact": {"days_late": 5, "has_hardship": True, "days_until_tax_payment": 60},
            "loan_id": "loan-003",
        })
    response = seeded_client.get("/decisions?loan_id=loan-003")
    assert response.status_code == 200
    assert len(response.json()) == 3
