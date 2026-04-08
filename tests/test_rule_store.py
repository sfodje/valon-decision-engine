import pytest

from valon_decision_engine.rule_store import (
    RuleSetNotFoundError,
    get_rule_set,
    save_rule_set,
)

SAMPLE_RULES = [
    {
        "condition": {"all": [{"fact": "has_hardship_flag", "operator": "is_true"}]},
        "actions": [{"method": "waive_late_fee"}],
    }
]


def test_save_rule_set_returns_version(db_path):
    version = save_rule_set(db_path, "late_fee_waiver", SAMPLE_RULES)
    assert version == 1


def test_save_rule_set_increments_version(db_path):
    save_rule_set(db_path, "late_fee_waiver", SAMPLE_RULES)
    version = save_rule_set(db_path, "late_fee_waiver", SAMPLE_RULES)
    assert version == 2


def test_get_rule_set_returns_latest_version(db_path):
    save_rule_set(db_path, "late_fee_waiver", SAMPLE_RULES)
    record = get_rule_set(db_path, "late_fee_waiver")
    assert record.rule_set_id == "late_fee_waiver"
    assert record.version == 1
    assert record.rules == SAMPLE_RULES


def test_get_rule_set_returns_specific_version(db_path):
    save_rule_set(db_path, "late_fee_waiver", SAMPLE_RULES)
    updated = [{"condition": True, "actions": [{"method": "waive_late_fee"}]}]
    save_rule_set(db_path, "late_fee_waiver", updated)
    record = get_rule_set(db_path, "late_fee_waiver", version=1)
    assert record.rules == SAMPLE_RULES


def test_get_rule_set_raises_for_unknown_id(db_path):
    with pytest.raises(RuleSetNotFoundError):
        get_rule_set(db_path, "nonexistent")


def test_get_rule_set_raises_for_unknown_version(db_path):
    save_rule_set(db_path, "late_fee_waiver", SAMPLE_RULES)
    with pytest.raises(RuleSetNotFoundError):
        get_rule_set(db_path, "late_fee_waiver", version=99)
