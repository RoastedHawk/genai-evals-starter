# Architecture

```
Data (JSONL) → Model Adapter (echo/reverse stub) → Metrics → Aggregation → Report (JSONL) → Charts (SVG)
```

- `src/selabs/evals/core.py`: dataset structs, run loop, logging.
- `src/selabs/evals/metrics.py`: exact/regex/json/json_schema/jaccard/char_ngram.
- `src/selabs/evals/reports.py`: SVG chart generator.
- `src/selabs/skills/prompt_eval_runner.py`: CLI for running evals.
- `results/evals.jsonl`: append-only summaries.
- `docs/coverage.svg`, `docs/results.svg`: generated artifacts.

## Principles
- Deterministic, offline-first; no secrets; JSONL fixtures.
- Contracts over prompts: metrics validate structure/format.
- CI as a gate: lint + tests + coverage; publish docs artifacts.

