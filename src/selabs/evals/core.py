from __future__ import annotations
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Iterable

from .metrics import REGISTRY as METRICS


@dataclass
class Example:
    id: str
    instruction: str
    expected: str


def exact_match(pred: str, gold: str) -> float:  # backward-compat shim
    return METRICS["exact"](pred, gold)


Metric = Callable[[str, str], float]


def run_eval(
    dataset: Iterable[Example],
    model: Callable[[str], str],
    metric: Metric = exact_match,
    *,
    log_path: Path | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    scores: list[float] = []
    for ex in dataset:
        pred = model(ex.instruction)
        score = metric(pred, ex.expected)
        scores.append(score)
    avg = sum(scores) / len(scores) if scores else 0.0
    report: Dict[str, Any] = {
        "n": len(scores),
        "metric": getattr(metric, "__name__", str(metric)),
        "score": avg,
        "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }
    if metadata:
        report.update(metadata)
    if log_path:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a") as f:
            f.write(json.dumps(report) + "\n")
    return report


def metric_by_name(name: str) -> Metric:
    try:
        return METRICS[name]
    except KeyError:
        raise ValueError(f"unknown metric: {name}")
