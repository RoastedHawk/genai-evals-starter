#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse

from selabs.evals.reports import write_results_chart


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Generate SVG results chart from JSONL runs")
    ap.add_argument("--input", type=Path, default=Path("results") / "evals.jsonl")
    ap.add_argument("--output", type=Path, default=Path("docs") / "results.svg")
    args = ap.parse_args(argv)

    write_results_chart(args.input, args.output)
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

