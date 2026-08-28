# Contributing

## Dev setup
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pre-commit install
pytest -q
```

## Running checks locally
```bash
ruff check .
black --check --line-length 100 .
pytest --cov=src --cov-report=term-missing
```

## Commit style
- Write imperative, concise messages: `Fix: handle empty strings in n-gram metric`.
- Small, focused PRs with tests are preferred.

## Scope
This is a personal learning repository; please do not submit features that require secrets or external services.

