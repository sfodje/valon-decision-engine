"""Decision engine: evaluates rule sets and persists immutable audit records."""

import json
import uuid
from datetime import datetime, timezone

from roolz import execute_rules

from valon_decision_engine.database import get_connection
from valon_decision_engine.loan_domain import DecisionActor, loan_fact_from_dict
from valon_decision_engine.models import DecisionRecord
from valon_decision_engine.rule_store import get_rule_set


class DecisionNotFoundError(Exception):
    """Raised when a decision record cannot be found by its ID."""


def evaluate(
    db_path: str,
    rule_set_id: str,
    fact_data: dict,
    loan_id: str | None = None,
) -> DecisionRecord:
    """Evaluate a rule set against fact_data and persist an immutable DecisionRecord.

    Args:
        db_path: Path to the SQLite database.
        rule_set_id: Identifier for the rule set to evaluate.
        fact_data: Dictionary of loan fact values.
        loan_id: Optional loan identifier to associate with the decision.

    Returns:
        The persisted DecisionRecord.
    """
    rule_set = get_rule_set(db_path, rule_set_id)
    fact = loan_fact_from_dict(fact_data)
    actor = DecisionActor()

    for rule in rule_set.rules:
        execute_rules(rule, fact, actor)

    record = DecisionRecord(
        decision_id=str(uuid.uuid4()),
        rule_set_id=rule_set.rule_set_id,
        rule_set_version=rule_set.version,
        loan_id=loan_id,
        fact_snapshot=fact_data,
        actions_taken=actor.actions_taken,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    _persist_decision(db_path, record)
    return record


def get_decision(db_path: str, decision_id: str) -> DecisionRecord:
    """Retrieve a single DecisionRecord by its ID.

    Args:
        db_path: Path to the SQLite database.
        decision_id: The unique decision identifier.

    Returns:
        The matching DecisionRecord.

    Raises:
        DecisionNotFoundError: If no decision with the given ID exists.
    """
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            "SELECT * FROM decisions WHERE decision_id = ?", (decision_id,)
        )
        row = cursor.fetchone()
        if row is None:
            raise DecisionNotFoundError(f"Decision '{decision_id}' not found.")
        return _row_to_record(row)


def get_decisions_for_loan(db_path: str, loan_id: str) -> list[DecisionRecord]:
    """Retrieve all DecisionRecords for a given loan, ordered by timestamp.

    Args:
        db_path: Path to the SQLite database.
        loan_id: The loan identifier.

    Returns:
        List of DecisionRecords ordered by timestamp ascending.
    """
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            "SELECT * FROM decisions WHERE loan_id = ? ORDER BY timestamp ASC",
            (loan_id,),
        )
        return [_row_to_record(row) for row in cursor.fetchall()]


def _persist_decision(db_path: str, record: DecisionRecord) -> None:
    with get_connection(db_path) as conn:
        conn.execute(
            """INSERT INTO decisions
               (decision_id, rule_set_id, rule_set_version, loan_id,
                fact_snapshot, actions_taken, timestamp)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                record.decision_id,
                record.rule_set_id,
                record.rule_set_version,
                record.loan_id,
                json.dumps(record.fact_snapshot),
                json.dumps(record.actions_taken),
                record.timestamp,
            ),
        )
        conn.commit()


def _row_to_record(row) -> DecisionRecord:
    return DecisionRecord(
        decision_id=row["decision_id"],
        rule_set_id=row["rule_set_id"],
        rule_set_version=row["rule_set_version"],
        loan_id=row["loan_id"],
        fact_snapshot=json.loads(row["fact_snapshot"]),
        actions_taken=json.loads(row["actions_taken"]),
        timestamp=row["timestamp"],
    )
