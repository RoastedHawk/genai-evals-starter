from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

from selabs.evals.metrics import citation_presence


def guard_response(text: str, fallback: str | None = None) -> str:
    """Return text if it contains a simple citation marker, else a safe fallback.

    The check mirrors the "citation_presence" metric: presence of "source:" or an http(s) URL.
    """
    if citation_presence(text, "") >= 1.0:
        return text
    return fallback or "I'm not confident enough to answer without citing sources."


def iter_jsonl(path: Path) -> Iterable[dict]:
    with path.open() as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Citations-or-silence guard skill")
    ap.add_argument("dataset", type=Path, help="JSONL with id,input,expected")
    ap.add_argument("--output", type=Path, default=Path("results") / "guarded.jsonl")
    args = ap.parse_args(argv)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("a") as out:
        for obj in iter_jsonl(args.dataset):
            # For the demo, treat expected as a candidate response
            candidate = obj.get("expected", "")
            guarded = guard_response(candidate)
            out.write(json.dumps({
                "id": obj.get("id"),
                "guarded": guarded,
                "has_citation": bool(citation_presence(candidate, "")),
            }) + "\n")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

