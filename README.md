# SE Labs (Python) — Personal GenAI Track

[![CI](https://github.com/RoastedHawk/se-labs-python/actions/workflows/ci.yml/badge.svg)](https://github.com/RoastedHawk/se-labs-python/actions/workflows/ci.yml)
![coverage](docs/coverage.svg)

A clean personal workspace for building software engineering skills focused on GenAI skills and evaluation.

## Why This Repo
- Demonstrates practical GenAI evaluation and product-engineering hygiene (tests, CI, coverage, lint, charts).
- Offline, deterministic, and safe to share (no secrets, no external calls).
- Clean, minimal Python that’s easy to review during interviews.

## Goals
- Practice Python engineering with tests, lint, and CI-ready structure.
- Build reusable "skills" (CLI tools) with clear contracts.
- Design and run offline GenAI evaluations with deterministic fixtures.

## Stack
- Python 3.11+
- Pytest for tests
- Ruff + Black for lint/format (optional)

## Quickstart
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # optional if you add deps
pytest
```

## Layout
- `src/selabs/skills/` — skill CLIs (Typer-friendly shape)
- `src/selabs/evals/` — eval harness + metrics
- `data/evals/` — small offline datasets (JSONL)
- `tests/` — unit tests for metrics and skills
- `.agents/skills/personal-growth-coach` — a Codex skill with personal memory

## VS Code
- Python: use `.venv` interpreter
- Testing: pytest enabled
- Format on save: Black
- Lint on save: Ruff

## Guardrails
This repo lives under `.../personal/` and uses the `github-roastedhawk` alias. The pre-push hook blocks any work identity/email.

See also: `docs/architecture.md`, `docs/how_we_evaluate.md`.

## Examples

Run exact match on digits dataset (echo model):

```bash
python -m selabs.skills.prompt_eval_runner data/evals/regex_digits.jsonl \
  --metric exact --model echo --output results/evals.jsonl
```

Run regex check (echo model still passes because inputs are digits):

```bash
python -m selabs.skills.prompt_eval_runner data/evals/regex_digits.jsonl \
  --metric regex --model echo --output results/evals.jsonl
```

Run JSON validity on a JSON dataset (echo model echoes JSON strings):

```bash
python -m selabs.skills.prompt_eval_runner data/evals/json_user.jsonl \
  --metric json --model echo --output results/evals.jsonl
```

Run JSON schema validation with a simple schema:

```bash
python -m selabs.skills.prompt_eval_runner data/evals/json_user.jsonl \
  --metric json_schema --schema data/evals/schemas/user_schema.json \
  --model echo --run-id demo --notes "schema check" --output results/evals.jsonl
```

## Coverage
CI enforces a minimum 80% coverage using `pytest-cov`. Locally, run:

```bash
pytest --cov=src --cov-report=term-missing
```

## Results Chart
CI also generates a simple SVG trend chart at `docs/results.svg` from `results/evals.jsonl`. To update locally:

```bash
PYTHONPATH=src python scripts/generate_results_chart.py --input results/evals.jsonl --output docs/results.svg
```

## Pre-commit Hooks
Install once locally to get fast feedback:

```bash
pip install pre-commit
pre-commit install
```

This runs Black and Ruff (E,F) on staged files before commit.

## Contributing & Security
- License: MIT (see `LICENSE`).
- Security: see `SECURITY.md`. Do not include credentials in issues.
- Contributions: see `CONTRIBUTING.md`.
Run token-level F1 and semantic cosine:

```bash
python -m selabs.skills.prompt_eval_runner data/evals/instruction_following.jsonl \
  --metric token_f1 --model echo --output results/evals.jsonl

python -m selabs.skills.prompt_eval_runner data/evals/instruction_following.jsonl \
  --metric semantic_cosine --model echo --output results/evals.jsonl
```

Require citation presence with regex:

```bash
python -m selabs.skills.prompt_eval_runner data/evals/citation_required.jsonl \
  --metric regex --model echo --output results/evals.jsonl
```

Validate JSON orders against a schema:

```bash
python -m selabs.skills.prompt_eval_runner data/evals/json_order.jsonl \
  --metric json_schema --schema data/evals/schemas/order_schema.json \
  --model echo --output results/evals.jsonl
```
