from __future__ import annotations

import argparse
import json
from pathlib import Path

from selabs.evals.core import Example, run_eval


def trivial_model(prompt: str) -> str:
    # Deterministic placeholder model for offline evals
    # Echo model so simple fixtures (expected == input) pass.
    return prompt


def load_jsonl(path: Path) -> list[Example]:
    items: list[Example] = []
    with path.open() as f:
        for line in f:
            obj = json.loads(line)
            items.append(Example(id=str(obj["id"]), instruction=obj["input"], expected=obj["expected"]))
    return items


def main() -> int:
    ap = argparse.ArgumentParser(description="Skill template: offline eval runner")
    ap.add_argument("dataset", type=Path, help="Path to JSONL with id,input,expected")
    args = ap.parse_args()

    ds = load_jsonl(args.dataset)
    report = run_eval(ds, trivial_model)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
