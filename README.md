# GenAI Evals Starter (Python)

[![CI](https://github.com/RoastedHawk/genai-evals-starter/actions/workflows/ci.yml/badge.svg)](https://github.com/RoastedHawk/genai-evals-starter/actions/workflows/ci.yml)
![coverage](docs/coverage.svg)

Starter kit for building and demonstrating GenAI evaluation workflows in Python.

## Why This Repo
- Demonstrates practical GenAI evaluation and product-engineering hygiene (tests, CI, coverage, lint, charts).
- Offline, deterministic, and safe to share (no secrets, no external calls).
- Clean, minimal Python that’s easy to review during interviews.

## Case Study (Portfolio)
- **Problem**: Ensure an assistant follows exact instructions and returns valid, structured outputs (JSON), while providing a simple reliability signal.
- **Approach**: Curate small JSONL goldens; run an offline model stub; gate with metrics (exact, regex, JSON validity, JSON Schema) and semantic baselines (token F1, cosine).
- **Metrics**: Exact match for instruction-following; regex for required tokens (e.g., `source:`); JSON + Schema for structure; token F1 and cosine for similarity.
- **Safety & Tradeoffs**: No secrets; deterministic runs; explicit JSON contracts; CI gates (lint, tests, coverage, typecheck) prevent regressions.
- **Outcome**: A reproducible eval harness with charts and badges that demonstrates engineering hygiene and product-minded evaluation—ready to extend to real adapters later without changing tests.

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
- `src/selabs/skills/` — CLI tools for running evals
- `src/selabs/evals/` — eval harness + metrics
- `data/evals/` — small offline datasets (JSONL) and schemas
- `tests/` — unit tests for metrics and tools

## VS Code
- Python: use `.venv` interpreter
- Testing: pytest enabled
- Format on save: Black
- Lint on save: Ruff

## Safety
- Offline and deterministic; no external calls or secrets.
- See also: `docs/architecture.md`, `docs/how_we_evaluate.md`.

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
