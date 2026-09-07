from pathlib import Path
from selabs.cli import main

def test_cli_eval_run_echo(tmp_path: Path):
    ds = tmp_path / "ds.jsonl"
    ds.write_text("\n".join([
        {id:
