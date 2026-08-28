import json
from pathlib import Path

from selabs.evals.core import Example, run_eval


def test_run_eval_logs_and_metadata(tmp_path: Path):
    ds = [
        Example(id="1", instruction="x", expected="x"),
        Example(id="2", instruction="y", expected="y"),
    ]

    def model(s: str) -> str:
        return s

    log = tmp_path / "results.jsonl"
    report = run_eval(ds, model, log_path=log, metadata={"dataset": "tmp", "run_id": "t1"})
    assert report["n"] == 2 and report["score"] == 1.0
    assert log.exists()
    lines = log.read_text().strip().splitlines()
    assert len(lines) == 1
    obj = json.loads(lines[0])
    assert obj["dataset"] == "tmp"
    assert obj["run_id"] == "t1"

