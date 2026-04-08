from valon_decision_engine.loan_domain import (
    DecisionActor,
    LoanFact,
    loan_fact_from_dict,
)


def test_loan_fact_methods():
    fact = LoanFact(days_late=15, has_hardship=True, days_until_tax_payment=25)
    assert fact.get_days_late() == 15
    assert fact.has_hardship_flag() is True
    assert fact.get_days_until_tax_payment() == 25


def test_loan_fact_from_dict():
    data = {"days_late": 10, "has_hardship": False, "days_until_tax_payment": 45}
    fact = loan_fact_from_dict(data)
    assert fact.get_days_late() == 10
    assert fact.has_hardship_flag() is False


def test_decision_actor_records_actions():
    actor = DecisionActor()
    actor.waive_late_fee()
    actor.allocate_to_escrow_first()
    assert actor.actions_taken == ["waive_late_fee", "allocate_to_escrow_first"]


def test_decision_actor_starts_empty():
    actor = DecisionActor()
    assert actor.actions_taken == []
