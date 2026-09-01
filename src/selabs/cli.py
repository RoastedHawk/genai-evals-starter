from __future__ import annotations

import argparse
from pathlib import Path

from selabs.skills import prompt_eval_runner as runner


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="selabs", description="SE Labs Eval CLI")
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("eval-run", help="Run an eval with a dataset and metric")
    r.add_argument("dataset", type=Path)
    r.add_argument("--metric", default="exact",
                   choices=["exact","regex","json","json_schema","token_f1","semantic_cosine","bleu","rouge_l"],
                   help="Metric name")
    r.add_argument("--schema", type=Path, default=None)
    r.add_argument("--model", default="echo", choices=["echo","reverse"]) 
    r.add_argument("--limit", type=int, default=0)
    r.add_argument("--output", type=Path, default=Path("results")/"evals.jsonl")

    args = ap.parse_args(argv)

    cmd = args.cmd
    if cmd == "eval-run":
        argv2 = [
            str(args.dataset),
            "--metric", args.metric,
            "--model", args.model,
            "--output", str(args.output),
        ]
        if args.limit:
            argv2 += ["--limit", str(args.limit)]
        if args.schema:
            argv2 += ["--schema", str(args.schema)]
        return runner.main(argv2)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

