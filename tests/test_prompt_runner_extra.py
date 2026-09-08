import json
from pathlib import Path
import pytest

from selabs.skills import prompt_eval_runner as runner


def test_runner_reverse_limit_and_skip_blank(tmp_path: Path):
    ds = tmp_path / "ds.jsonl"
    rows = [
        {"id": 1, "input": "ab", "expected": "ba"},
        {},  # will be filtered because it will serialize to {} but ensure blank by writing empty line
        {"id": 2, "input": "cd", "expected": "dc"},
    ]
    # Write with an empty line between to exercise skip-blank branch
    ds.write_text("\n".join([
        json.dumps(rows[0]),
        "",  # blank line
        json.dumps(rows[2]),
    ]))
    out = tmp_path / "out.jsonl"
    rc = runner.main([str(ds), "--metric", "exact", "--model", "reverse", "--limit", "1", "--output", str(out)])
    assert rc == 0 and out.exists()
    last = json.loads(out.read_text().strip().splitlines()[-1])
    assert last.get("n") == 1
    assert 0.0 <= last.get("score", 0) <= 1.0


def test_json_schema_requires_schema(tmp_path: Path):
    ds = tmp_path / "d.jsonl"
    ds.write_text(json.dumps({"id": 1, "input": "{}", "expected": ""}))
    with pytest.raises(SystemExit):
        runner.main([str(ds), "--metric", "json_schema"])  # missing --schema should error
