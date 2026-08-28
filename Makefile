.PHONY: test lint format cov chart all

test:
	pytest -q

lint:
	ruff check .

format:
	black --line-length 100 .

cov:
	pytest --cov=src --cov-report=term-missing

chart:
	PYTHONPATH=src python scripts/generate_results_chart.py --input results/evals.jsonl --output docs/results.svg

all: lint test cov chart

