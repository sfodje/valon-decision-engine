import pytest
from datetime import datetime, timezone
from valon_decision_engine.models import (
    RuleSetRecord,
    DecisionRecord,
    EvaluateRequest,
    DecisionResponse,
)


def test_rule_set_record_fields():
    record = RuleSetRecord(
        rule_set_id="late_fee_waiver",
        version=1,
        rules=[{"condition": True, "actions": [{"method": "waive_late_fee"}]}],
    )
    assert record.rule_set_id == "late_fee_waiver"
    assert record.version == 1
    assert len(record.rules) == 1


def test_decision_record_fields():
    record = DecisionRecord(
        decision_id="abc-123",
        rule_set_id="late_fee_waiver",
        rule_set_version=1,
        loan_id="loan-456",
        fact_snapshot={"days_late": 10, "has_hardship": True},
        actions_taken=["waive_late_fee"],
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    assert record.decision_id == "abc-123"
    assert record.actions_taken == ["waive_late_fee"]


def test_evaluate_request_loan_id_optional():
    req = EvaluateRequest(
        rule_set_id="late_fee_waiver",
        fact={"days_late": 10, "has_hardship": True, "days_until_tax_payment": 60},
    )
    assert req.loan_id is None


def test_decision_response_fields():
    resp = DecisionResponse(
        decision_id="abc-123",
        rule_set_id="late_fee_waiver",
        rule_set_version=1,
        loan_id=None,
        actions_taken=["waive_late_fee"],
        timestamp="2026-04-07T00:00:00+00:00",
    )
    assert resp.rule_set_version == 1
