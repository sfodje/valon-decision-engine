.PHONY: install test format lint typecheck check run demo

PYTHONPATH := src

install:
	pip install -r requirements.txt
	pip install ruff mypy

test:
	PYTHONPATH=$(PYTHONPATH) pytest tests -v

format:
	ruff check --select I --fix .
	ruff format .

lint:
	ruff check .

typecheck:
	PYTHONPATH=$(PYTHONPATH) mypy src --check-untyped-defs

check: format lint typecheck

run:
	PYTHONPATH=$(PYTHONPATH) uvicorn valon_decision_engine.api:app --reload

demo:
	PYTHONPATH=$(PYTHONPATH) python demo.py
