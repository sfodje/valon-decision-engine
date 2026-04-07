# valon-decision-engine

A demonstration of auditable, versioned rule evaluation for regulated financial decisions.

Built on [py-roolz](https://github.com/sfodje/py-roolz) — a production rule engine originally
built for carrier compliance at Shippo, where rules from external authorities (carriers) must be
evaluated deterministically with a full audit trail.

ValonOS faces the same pattern at a different scale: mortgage regulations as the rule authority,
AI agents as the actors, and regulators as the auditors. This is the infrastructure layer that
makes AI decisions safe in regulated finance.

## The Problem

Mortgage servicers need to automate decisions — fee waivers, payment allocations, modification
eligibility — but regulators require full traceability: which rule fired, what version, what
inputs, what output. "The AI decided it" is not an acceptable answer.

## What This Demonstrates

- **Versioned rule sets** — rules are immutable once published; every decision references the
  exact version that evaluated it
- **Immutable decision records** — every evaluation persists a full audit trace: inputs, rule
  version, actions taken, timestamp
- **Audit API** — query any decision by ID or retrieve the complete history for a loan

## Tech Stack

Python 3.11, FastAPI, [py-roolz](https://github.com/sfodje/py-roolz), Pydantic v2, SQLite

## Setup

```bash
pip install -r requirements.txt
```

## Run the demo

```bash
PYTHONPATH=src python demo.py
```

Runs four mortgage scenarios (late fee waiver, payment allocation) and prints the full audit trail.

## Run the API

```bash
# Initialize the database and seed demo rule sets
PYTHONPATH=src python -c "
from valon_decision_engine.database import init_db
from valon_decision_engine.demo_rules import seed_demo_rules
init_db('decisions.db')
seed_demo_rules('decisions.db')
"

# Start the server
PYTHONPATH=src uvicorn valon_decision_engine.api:app --reload
```

### API endpoints

**Evaluate a rule set:**
```
POST /decisions
{
  "rule_set_id": "late_fee_waiver",
  "loan_id": "loan-001",
  "fact": {"days_late": 10, "has_hardship": true, "days_until_tax_payment": 60}
}
```

**Retrieve a decision audit record:**
```
GET /decisions/{decision_id}
```

**Full loan decision history:**
```
GET /decisions?loan_id=loan-001
```

## Run tests

```bash
PYTHONPATH=src pytest -v
```

## Connection to production

py-roolz powers Shippo's carrier rate engine — a system where 50+ carriers each define
different compliance rules that must be evaluated deterministically at high throughput.
The auditable decision layer demonstrated here extends that foundation to meet the stricter
traceability requirements of regulated finance.
