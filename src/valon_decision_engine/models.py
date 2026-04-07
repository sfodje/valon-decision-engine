"""Data models for rule sets and decision records."""

from pydantic import BaseModel


class RuleSetRecord(BaseModel):
    """Represents a versioned rule set."""

    rule_set_id: str
    version: int
    rules: list[dict]


class DecisionRecord(BaseModel):
    """Immutable record of a decision made by the rule engine."""

    decision_id: str
    rule_set_id: str
    rule_set_version: int
    loan_id: str | None
    fact_snapshot: dict
    actions_taken: list[str]
    timestamp: str


class EvaluateRequest(BaseModel):
    """Request to evaluate a rule set against a fact set."""

    rule_set_id: str
    fact: dict
    loan_id: str | None = None


class DecisionResponse(BaseModel):
    """Response from a rule evaluation."""

    decision_id: str
    rule_set_id: str
    rule_set_version: int
    loan_id: str | None
    actions_taken: list[str]
    timestamp: str
