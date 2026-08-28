from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List

from selabs.evals.core import Example, metric_by_name, run_eval
from selabs.evals.metrics import make_json_schema_metric


def model_echo(prompt: str) -> str:
    return prompt


def model_reverse(prompt: str) -> str:
    return prompt[::-1]


def load_jsonl(path: Path) -> List[Example]:
    items: List[Example] = []
    with path.open() as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            items.append(
                Example(id=str(obj["id"]), instruction=obj["input"], expected=obj.get("expected", ""))
            )
    return items


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Prompt Eval Runner")
    ap.add_argument("dataset", type=Path, help="JSONL with fields: id,input,expected")
    ap.add_argument(
        "--metric",
        choices=["exact", "regex", "json", "json_schema"],
        default="exact",
        help="Metric to use",
    )
    ap.add_argument(
        "--model",
        choices=["echo", "reverse"],
        default="echo",
        help="Toy model for offline eval",
    )
    ap.add_argument("--limit", type=int, default=0, help="Limit number of examples")
    ap.add_argument("--run-id", type=str, default=None, help="Optional run id tag")
    ap.add_argument("--notes", type=str, default=None, help="Optional freeform notes")
    ap.add_argument("--schema", type=Path, default=None, help="Path to JSON schema (for json_schema)")
    ap.add_argument(
        "--output",
        type=Path,
        default=Path("results") / "evals.jsonl",
        help="Append summary JSON to this file",
    )
    args = ap.parse_args(argv)

    ds = load_jsonl(args.dataset)
    if args.limit and args.limit > 0:
        ds = ds[: args.limit]

    model = model_echo if args.model == "echo" else model_reverse
    if args.metric == "json_schema":
        if not args.schema:
            ap.error("--schema is required when --metric json_schema")
        schema = json.loads(Path(args.schema).read_text())
        metric = make_json_schema_metric(schema)
    else:
        metric = metric_by_name(args.metric)

    # ensure output dir exists
    args.output.parent.mkdir(parents=True, exist_ok=True)
    report = run_eval(
        ds,
        model,
        metric,
        log_path=args.output,
        metadata={
            "dataset": str(args.dataset),
            "run_id": args.run_id,
            "notes": args.notes,
        },
    )
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
