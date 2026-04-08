"""Fact and actor objects for mortgage loan rule evaluation."""

from pydantic import BaseModel, ConfigDict, Field


class LoanFact(BaseModel):
    """Fact object for mortgage loan context. Methods are called by roolz rules."""

    model_config = ConfigDict(populate_by_name=True)

    days_late: int = 0
    hardship: bool = Field(default=False, alias="has_hardship")
    days_until_tax_payment: int | None = None

    def get_days_late(self) -> int:
        return self.days_late

    def has_hardship(self) -> bool:
        return self.hardship

    def get_days_until_tax_payment(self) -> int | None:
        return self.days_until_tax_payment


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
    return LoanFact(**data)
