from pathlib import Path
from selabs.skills.citations_or_silence import main, iter_jsonl, guard_response
import json

def test_iter_jsonl(tmp_path: Path):
    p = tmp_path / "d.jsonl"
    rows = [
        {"id": 1, "input": "x", "expected": "source: foo"},
        {"id": 2, "input": "y", "expected": "no cite"},
    ]
    p.write_text("\n".join(json.dumps(r) for r in rows))
    rows2 = list(iter_jsonl(p))
    assert rows2 and rows2[0]["id"] == 1 and rows2[-1]["id"] == 2

def test_guard_response_and_main(tmp_path: Path):
    ds = tmp_path / "ds.jsonl"
    ds.write_text(json.dumps({"id": 1, "input": "q", "expected": "source: bar"}))
    out = tmp_path / "guarded.jsonl"
    rc = main([str(ds), "--output", str(out)])
    assert rc == 0 and out.exists()
    unsafe = guard_response("no refs here")
    assert "sources" in unsafe.lower()
