# How We Evaluate

- Datasets: small JSONL fixtures with `id`, `input`, `expected`.
- Metrics:
  - `exact`: strict string equality (for deterministic tasks).
  - `regex`: pattern compliance.
  - `json`: well-formed JSON.
  - `json_schema`: structure and basic type checks.
  - `jaccard`, `char_ngram`: similarity baselines.
- Runs: append a summary JSON to `results/evals.jsonl`.
- CI: gates on lint + tests + 80% coverage; publishes coverage and results charts as SVGs in `docs/`.
- No secrets, no external calls; everything is reproducible locally.

