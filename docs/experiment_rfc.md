# Experiment RFC Template

## Summary
Goal, hypothesis, and target user behavior/experience.

## Metrics & Gates
- Primary metrics: instruction-following success (exact), JSON validity/schema, citation presence, safety (PII-safe).
- Secondary: similarity (token F1, cosine) for qualitative drift.
- Gates: minimum thresholds (e.g., exact ≥ 90%, JSON valid ≥ 98%, PII-safe ≥ 99%).

## Design
- Dataset: JSONL goldens with `id,input,expected`.
- Model adapter: offline stub for reproducibility; real clients only via env vars.
- Logging: JSON summaries with `run_id`, `timestamp`, `latency_ms`, `cost_tokens`.

## Risks & Safeguards
- No secrets; offline-first.
- Policy-as-code for gates; failing gate blocks merges.

## Rollout
- Start with small datasets; expand with observed failures.
- Monitor charts (coverage/results.svg) and adjust thresholds.

