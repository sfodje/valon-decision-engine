import pytest
from pydantic import ValidationError

from valon_decision_engine.loan_domain import (
    DecisionActor,
    LoanFact,
    loan_fact_from_dict,
)


def test_loan_fact_methods():
    fact = LoanFact(days_late=15, has_hardship=True, days_until_tax_payment=25)
    assert fact.get_days_late() == 15
    assert fact.has_hardship() is True
    assert fact.get_days_until_tax_payment() == 25


def test_loan_fact_from_dict():
    data = {"days_late": 10, "has_hardship": False, "days_until_tax_payment": 45}
    fact = loan_fact_from_dict(data)
    assert fact.get_days_late() == 10
    assert fact.has_hardship() is False


def test_loan_fact_defaults():
    fact = LoanFact()
    assert fact.get_days_late() == 0
    assert fact.has_hardship() is False
    assert fact.get_days_until_tax_payment() is None


def test_loan_fact_rejects_wrong_types():
    with pytest.raises(ValidationError):
        LoanFact(days_late="not-a-number")


def test_loan_fact_from_dict_only_requires_relevant_fields():
    fact = loan_fact_from_dict({"days_late": 5, "has_hardship": True})
    assert fact.get_days_late() == 5
    assert fact.get_days_until_tax_payment() is None


def test_decision_actor_records_actions():
    actor = DecisionActor()
    actor.waive_late_fee()
    actor.allocate_to_escrow_first()
    assert actor.actions_taken == ["waive_late_fee", "allocate_to_escrow_first"]


def test_decision_actor_starts_empty():
    actor = DecisionActor()
    assert actor.actions_taken == []
