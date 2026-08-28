from pathlib import Path
import sys

from selabs.skills import skill_template


def test_skill_template_main(tmp_path: Path, monkeypatch):
    ds = tmp_path / "ds.jsonl"
    ds.write_text(
        "\n".join(
            [
                '{"id": 1, "input": "a", "expected": "a"}',
                '{"id": 2, "input": "b", "expected": "b"}',
            ]
        )
    )

    monkeypatch.setenv("PYTHONPATH", str((Path(__file__).resolve().parents[2] / "src")))
    argv = sys.argv
    try:
        sys.argv = ["skill_template", str(ds)]
        rc = skill_template.main()
        assert rc == 0
    finally:
        sys.argv = argv
