from pathlib import Path
from selabs.cli import main
import json

def test_cli_eval_run_echo(tmp_path: Path):
    ds = tmp_path / "ds.jsonl"
    rows = [
        {"id": 1, "input": "a", "expected": "a"},
        {"id": 2, "input": "b", "expected": "b"},
    ]
    ds.write_text("\n".join(json.dumps(r) for r in rows))
    out = tmp_path / "res.jsonl"
    rc = main(["eval-run", str(ds), "--metric", "exact", "--model", "echo", "--output", str(out)])
    assert rc == 0
    assert out.exists()
    text = out.read_text().strip().splitlines()[-1]
    obj = json.loads(text)
    assert "n" in obj and "score" in obj
