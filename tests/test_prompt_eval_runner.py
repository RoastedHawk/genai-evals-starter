import json
from pathlib import Path

from selabs.skills.prompt_eval_runner import main


def test_runner_echo_exact(tmp_path: Path):
    data = tmp_path / "ds.jsonl"
    data.write_text("\n".join([
        '{"id": 1, "input": "a", "expected": "a"}',
        '{"id": 2, "input": "b", "expected": "b"}',
    ]))

    out = tmp_path / "results.jsonl"
    rc = main([str(data), "--metric", "exact", "--model", "echo", "--output", str(out)])
    assert rc == 0
    # file should contain one JSON line
    lines = out.read_text().strip().splitlines()
    assert len(lines) == 1
    obj = json.loads(lines[0])
    assert obj["n"] == 2
    assert obj["score"] == 1.0


def test_runner_regex_and_schema(tmp_path: Path):
    # regex dataset
    ds1 = tmp_path / "digits.jsonl"
    ds1.write_text("\n".join([
        '{"id": 1, "input": "123", "expected": "^[0-9]+$"}',
        '{"id": 2, "input": "456", "expected": "^[0-9]+$"}',
    ]))
    out1 = tmp_path / "r1.jsonl"
    assert main([str(ds1), "--metric", "regex", "--output", str(out1)]) == 0

    # schema dataset
    ds2 = tmp_path / "json.jsonl"
    ds2.write_text("\n".join([
        '{"id": 1, "input": "{\\"name\\":\\"a\\",\\"age\\":1}", "expected": ""}',
    ]))
    schema = tmp_path / "schema.json"
    schema.write_text('{"type":"object","required":["name","age"],"properties":{"name":{"type":"string"},"age":{"type":"integer"}}}')
    out2 = tmp_path / "r2.jsonl"
    assert main([str(ds2), "--metric", "json_schema", "--schema", str(schema), "--output", str(out2)]) == 0
