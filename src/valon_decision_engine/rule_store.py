"""Rule store for versioned immutable rule sets."""

import json

from valon_decision_engine.database import get_connection
from valon_decision_engine.models import RuleSetRecord


class RuleSetNotFoundError(Exception):
    """Raised when a rule set or version cannot be found."""

    pass


def save_rule_set(db_path: str, rule_set_id: str, rules: list[dict]) -> int:
    """Persist a new version of a rule set. Returns the new version number.

    Args:
        db_path: Path to the SQLite database.
        rule_set_id: Identifier for the rule set.
        rules: List of rule objects to store.

    Returns:
        The new version number.
    """
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            "SELECT MAX(version) FROM rule_sets WHERE rule_set_id = ?",
            (rule_set_id,),
        )
        row = cursor.fetchone()
        next_version = (row[0] or 0) + 1
        conn.execute(
            "INSERT INTO rule_sets (rule_set_id, version, rules_json) VALUES (?, ?, ?)",
            (rule_set_id, next_version, json.dumps(rules)),
        )
        conn.commit()
        return next_version


def get_rule_set(
    db_path: str, rule_set_id: str, version: int | None = None
) -> RuleSetRecord:
    """Retrieve a rule set by id. Fetches latest version if version is omitted.

    Args:
        db_path: Path to the SQLite database.
        rule_set_id: Identifier for the rule set.
        version: Optional version number. If omitted, returns the latest version.

    Returns:
        A RuleSetRecord containing the rule set data.

    Raises:
        RuleSetNotFoundError: If the rule set or version is not found.
    """
    with get_connection(db_path) as conn:
        if version is None:
            cursor = conn.execute(
                "SELECT rule_set_id, version, rules_json FROM rule_sets "
                "WHERE rule_set_id = ? ORDER BY version DESC LIMIT 1",
                (rule_set_id,),
            )
        else:
            cursor = conn.execute(
                "SELECT rule_set_id, version, rules_json FROM rule_sets "
                "WHERE rule_set_id = ? AND version = ?",
                (rule_set_id, version),
            )
        row = cursor.fetchone()
        if row is None:
            raise RuleSetNotFoundError(
                f"Rule set '{rule_set_id}' version={version} not found."
            )
        return RuleSetRecord(
            rule_set_id=row["rule_set_id"],
            version=row["version"],
            rules=json.loads(row["rules_json"]),
        )
