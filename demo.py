"""
End-to-end demo of the Valon Decision Engine.

Run with: PYTHONPATH=src python demo.py

Demonstrates:
  1. Seeding versioned mortgage rule sets
  2. Evaluating decisions and recording immutable audit trails
  3. Querying the full decision history for a loan
"""
import json
import os
from valon_decision_engine.database import init_db
from valon_decision_engine.demo_rules import seed_demo_rules
from valon_decision_engine.engine import evaluate, get_decisions_for_loan

DB_PATH = "demo.db"


def header(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def run():
    # Clean slate for demo
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db(DB_PATH)
    seed_demo_rules(DB_PATH)

    loan_id = "loan-2026-001"

    header("Scenario 1: Late fee waiver — hardship borrower, 10 days late")
    result = evaluate(
        DB_PATH,
        "late_fee_waiver",
        {"days_late": 10, "has_hardship": True, "days_until_tax_payment": 60},
        loan_id=loan_id,
    )
    print(f"  decision_id:      {result.decision_id}")
    print(f"  rule_set_version: {result.rule_set_version}")
    print(f"  actions_taken:    {result.actions_taken}")
    print(f"  fact_snapshot:    {json.dumps(result.fact_snapshot)}")

    header("Scenario 2: Late fee waiver — no hardship, 10 days late")
    result = evaluate(
        DB_PATH,
        "late_fee_waiver",
        {"days_late": 10, "has_hardship": False, "days_until_tax_payment": 60},
        loan_id=loan_id,
    )
    print(f"  decision_id:      {result.decision_id}")
    print(f"  actions_taken:    {result.actions_taken}  (no waiver — condition not met)")

    header("Scenario 3: Late fee waiver — 45 days late (manual review triggered)")
    result = evaluate(
        DB_PATH,
        "late_fee_waiver",
        {"days_late": 45, "has_hardship": True, "days_until_tax_payment": 60},
        loan_id=loan_id,
    )
    print(f"  decision_id:      {result.decision_id}")
    print(f"  actions_taken:    {result.actions_taken}")

    header("Scenario 4: Payment allocation — tax due in 20 days")
    result = evaluate(
        DB_PATH,
        "payment_allocation",
        {"days_late": 0, "has_hardship": False, "days_until_tax_payment": 20},
        loan_id=loan_id,
    )
    print(f"  decision_id:      {result.decision_id}")
    print(f"  actions_taken:    {result.actions_taken}")

    header(f"Full audit trail for {loan_id}")
    history = get_decisions_for_loan(DB_PATH, loan_id)
    for i, record in enumerate(history, 1):
        print(f"\n  [{i}] {record.timestamp}")
        print(f"      rule_set:    {record.rule_set_id} v{record.rule_set_version}")
        print(f"      actions:     {record.actions_taken}")
        print(f"      decision_id: {record.decision_id}")


if __name__ == "__main__":
    run()
