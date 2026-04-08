"""
Mortgage domain rule sets used for the demo.

late_fee_waiver:
    Waive the late fee when the borrower has a hardship flag AND
    the payment is no more than 30 days late.
    Flag for manual review when days_late > 30 regardless of hardship.

payment_allocation:
    When a tax payment is due within 30 days, allocate to escrow first.
"""

from valon_decision_engine.rule_store import save_rule_set

LATE_FEE_WAIVER_RULES = [
    {
        "condition": {
            "all": [
                {"fact": "has_hardship_flag", "operator": "is_true"},
                {
                    "fact": "get_days_late",
                    "operator": "less_than_or_equal_to",
                    "value": 30,
                },
            ]
        },
        "actions": [{"action": "waive_late_fee"}],
    },
    {
        "condition": {"fact": "get_days_late", "operator": "greater_than", "value": 30},
        "actions": [{"action": "flag_for_manual_review"}],
    },
]

PAYMENT_ALLOCATION_RULES = [
    {
        "condition": {
            "fact": "get_days_until_tax_payment",
            "operator": "less_than_or_equal_to",
            "value": 30,
        },
        "actions": [{"action": "allocate_to_escrow_first"}],
    },
]


def seed_demo_rules(db_path: str) -> None:
    """Persist the demo rule sets into the database."""
    save_rule_set(db_path, "late_fee_waiver", LATE_FEE_WAIVER_RULES)
    save_rule_set(db_path, "payment_allocation", PAYMENT_ALLOCATION_RULES)
