from pathlib import Path
from selabs.skills.citations_or_silence import main, iter_jsonl, guard_response

def test_iter_jsonl(tmp_path: Path):
    p = tmp_path / "d.jsonl"
    p.write_text("\n".join([
        id:1,
        ,
        id:2,
    ]))
    rows = list(iter_jsonl(p))
    assert rows and rows[0]["id"] == 1 and rows[-1]["id"] == 2

def test_guard_response_and_main(tmp_path: Path):
    ds = tmp_path / "ds.jsonl"
    ds.write_text({id:
