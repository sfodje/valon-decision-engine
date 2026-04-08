"""FastAPI application for the Valon Decision Engine."""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Query

from valon_decision_engine.engine import (
    DecisionNotFoundError,
    evaluate,
    get_decision,
    get_decisions_for_loan,
)
from valon_decision_engine.database import init_db
from valon_decision_engine.models import CreateRuleSetRequest, DecisionResponse, EvaluateRequest
from valon_decision_engine.rule_store import RuleSetNotFoundError, save_rule_set


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    init_db(_db())
    yield


app = FastAPI(title="Valon Decision Engine", lifespan=lifespan)


def _db() -> str:
    return os.environ.get("DB_PATH", "decisions.db")


@app.post("/rule-sets", response_model=dict, status_code=201)
def create_rule_set(request: CreateRuleSetRequest) -> dict:
    """Create a new version of a rule set."""
    version = save_rule_set(_db(), request.rule_set_id, request.rules)
    return {"rule_set_id": request.rule_set_id, "version": version}


@app.post("/decisions", response_model=DecisionResponse)
def post_decision(request: EvaluateRequest) -> DecisionResponse:
    """Evaluate a rule set against a loan fact and record the decision."""
    try:
        record = evaluate(_db(), request.rule_set_id, request.fact, request.loan_id)
    except RuleSetNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return DecisionResponse(
        decision_id=record.decision_id,
        rule_set_id=record.rule_set_id,
        rule_set_version=record.rule_set_version,
        loan_id=record.loan_id,
        actions_taken=record.actions_taken,
        timestamp=record.timestamp,
    )


@app.get("/decisions/{decision_id}", response_model=DecisionResponse)
def fetch_decision(decision_id: str) -> DecisionResponse:
    """Retrieve the full audit record for a single decision."""
    try:
        record = get_decision(_db(), decision_id)
    except DecisionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return DecisionResponse(
        decision_id=record.decision_id,
        rule_set_id=record.rule_set_id,
        rule_set_version=record.rule_set_version,
        loan_id=record.loan_id,
        actions_taken=record.actions_taken,
        timestamp=record.timestamp,
    )


@app.get("/decisions", response_model=list[DecisionResponse])
def list_decisions(
    loan_id: str = Query(..., description="Filter decisions by loan ID"),
) -> list[DecisionResponse]:
    """Retrieve the full decision history for a loan."""
    records = get_decisions_for_loan(_db(), loan_id)
    return [
        DecisionResponse(
            decision_id=r.decision_id,
            rule_set_id=r.rule_set_id,
            rule_set_version=r.rule_set_version,
            loan_id=r.loan_id,
            actions_taken=r.actions_taken,
            timestamp=r.timestamp,
        )
        for r in records
    ]
