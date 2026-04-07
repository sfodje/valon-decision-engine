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

## Design Decisions

**Immutable append-only records over event sourcing.** Every decision is written once and never
modified. Event sourcing would add replay infrastructure and derived-state complexity that isn't
justified here — the DecisionRecord IS the state a regulator needs. Append-only is simpler,
auditable by default, and maps directly to how compliance teams think about records.

**Rules as versioned data, not versioned code.** Encoding rules as JSON stored in the database
means compliance teams can inspect exactly what rules were active at any point in time without
reading a codebase. It also makes rule changes a data operation (deploy a new version, not a new
binary), which is safer in a regulated environment where rule changes need change-management
approval trails.

**Stateless rule evaluation.** `evaluate()` takes all inputs explicitly and produces a
deterministic output. No hidden state, no side effects beyond the audit record. This makes the
evaluation layer horizontally scalable and trivially testable — properties that matter when you're
running millions of decisions per day across a $110B loan portfolio.

**SQLite for the demo.** In production, the `decisions` table is append-only and grows
indefinitely — the right production choice is Postgres with time-based partitioning (by month or
quarter) so audit queries against current data stay fast. The `loan_id` index also becomes
critical at scale; it's intentionally absent here to keep the demo dependency-free.

## At Scale

The evaluation path (rule lookup → fact construction → roolz execution → record write) is
stateless and CPU-bound — it scales horizontally behind a load balancer with no coordination
overhead. The bottleneck at volume is the audit write path: at 1M+ decisions/day, batching
inserts and writing to a partitioned Postgres table with an async worker keeps p99 latency
stable. The audit read path (`GET /decisions?loan_id=X`) is read-heavy and cacheable — a Redis
layer in front of the DB handles burst traffic during regulatory reviews without touching the
primary. Rule sets themselves change rarely and are small; caching the current version in-process
eliminates the DB round-trip on the hot path entirely.

## Connection to production

I developed py-roolz to power the carrier rate engine at Shippo — a system where 50+ carriers each define
different compliance rules that must be evaluated deterministically at high throughput.
The auditable decision layer demonstrated here extends that foundation to meet the stricter
traceability requirements of regulated finance.
