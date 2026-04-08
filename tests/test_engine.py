import pytest

from valon_decision_engine.engine import DecisionNotFoundError, evaluate, get_decision
from valon_decision_engine.rule_store import save_rule_set

WAIVER_RULES = [
    {
        "condition": {
            "all": [
                {"fact": "has_hardship", "operator": "is_true"},
                {
                    "fact": "get_days_late",
                    "operator": "less_than_or_equal_to",
                    "value": 30,
                },
            ]
        },
        "actions": [{"action": "waive_late_fee"}],
    }
]


def test_evaluate_returns_decision_id(db_path):
    save_rule_set(db_path, "late_fee_waiver", WAIVER_RULES)
    fact = {"days_late": 10, "has_hardship": True, "days_until_tax_payment": 60}
    result = evaluate(db_path, "late_fee_waiver", fact)
    assert result.decision_id is not None
    assert result.rule_set_id == "late_fee_waiver"
    assert result.rule_set_version == 1


def test_evaluate_records_correct_actions(db_path):
    save_rule_set(db_path, "late_fee_waiver", WAIVER_RULES)
    fact = {"days_late": 10, "has_hardship": True, "days_until_tax_payment": 60}
    result = evaluate(db_path, "late_fee_waiver", fact)
    assert "waive_late_fee" in result.actions_taken


def test_evaluate_no_actions_when_condition_false(db_path):
    save_rule_set(db_path, "late_fee_waiver", WAIVER_RULES)
    fact = {"days_late": 10, "has_hardship": False, "days_until_tax_payment": 60}
    result = evaluate(db_path, "late_fee_waiver", fact)
    assert result.actions_taken == []


def test_evaluate_persists_fact_snapshot(db_path):
    save_rule_set(db_path, "late_fee_waiver", WAIVER_RULES)
    fact = {"days_late": 5, "has_hardship": True, "days_until_tax_payment": 60}
    result = evaluate(db_path, "late_fee_waiver", fact)
    stored = get_decision(db_path, result.decision_id)
    assert stored.fact_snapshot == fact


def test_evaluate_stores_loan_id(db_path):
    save_rule_set(db_path, "late_fee_waiver", WAIVER_RULES)
    fact = {"days_late": 5, "has_hardship": True, "days_until_tax_payment": 60}
    result = evaluate(db_path, "late_fee_waiver", fact, loan_id="loan-789")
    assert result.loan_id == "loan-789"


def test_get_decision_raises_for_unknown_id(db_path):
    with pytest.raises(DecisionNotFoundError):
        get_decision(db_path, "nonexistent-id")
