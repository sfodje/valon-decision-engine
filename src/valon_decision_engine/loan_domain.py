"""Fact and actor objects for mortgage loan rule evaluation."""


class LoanFact:
    """Fact object for mortgage loan context. Methods are called by roolz rules."""

    def __init__(self, days_late: int, has_hardship: bool, days_until_tax_payment: int):
        self._days_late = days_late
        self._has_hardship = has_hardship
        self._days_until_tax_payment = days_until_tax_payment

    def get_days_late(self) -> int:
        return self._days_late

    def has_hardship_flag(self) -> bool:
        return self._has_hardship

    def get_days_until_tax_payment(self) -> int:
        return self._days_until_tax_payment


class DecisionActor:
    """Actor object that records which actions were taken during rule evaluation."""

    def __init__(self):
        self.actions_taken: list[str] = []

    def waive_late_fee(self) -> None:
        self.actions_taken.append("waive_late_fee")

    def allocate_to_escrow_first(self) -> None:
        self.actions_taken.append("allocate_to_escrow_first")

    def flag_for_manual_review(self) -> None:
        self.actions_taken.append("flag_for_manual_review")


def loan_fact_from_dict(data: dict) -> LoanFact:
    """Construct a LoanFact from the raw dict received in an API request."""
    return LoanFact(
        days_late=data["days_late"],
        has_hardship=data["has_hardship"],
        days_until_tax_payment=data["days_until_tax_payment"],
    )
