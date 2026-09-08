import json
from selabs.evals.metrics import contract_check


def test_contract_check_lte_and_regex_pass():
    pred = json.dumps({"code": "abc123", "value": 7})
    spec = {
        "schema": {
            "required": ["code", "value"],
            "properties": {"code": {"type": "string"}, "value": {"type": "number"}},
        },
        "checks": [
            {"field": "code", "regex": r"^abc\d+$"},
            {"field": "value", "lte": 10},
        ],
    }
    assert contract_check(pred, json.dumps(spec)) == 1.0


def test_contract_check_regex_fail():
    pred = json.dumps({"code": "xyz", "value": 5})
    spec = {
        "schema": {
            "required": ["code", "value"],
            "properties": {"code": {"type": "string"}, "value": {"type": "number"}},
        },
        "checks": [
            {"field": "code", "regex": r"^abc\d+$"},
        ],
    }
    assert contract_check(pred, json.dumps(spec)) == 0.0
