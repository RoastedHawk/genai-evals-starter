from selabs.evals.metrics import contract_check


def test_contract_check_pass():
    pred = '{"action":"transfer","amount":12.5,"currency":"USD"}'
    spec = {
        "schema": {
            "required": ["action", "amount", "currency"],
            "properties": {
                "action": {"type": "string"},
                "amount": {"type": "number"},
                "currency": {"type": "string"},
            },
        },
        "checks": [
            {"field": "action", "equals": "transfer"},
            {"field": "currency", "in": ["USD", "EUR"]},
            {"field": "amount", "gte": 0},
        ],
    }
    assert contract_check(pred, __import__('json').dumps(spec)) == 1.0


def test_contract_check_fail():
    pred = '{"action":"transfer","amount":-1,"currency":"CAD"}'
    spec = {
        "schema": {
            "required": ["action", "amount", "currency"],
            "properties": {
                "action": {"type": "string"},
                "amount": {"type": "number"},
                "currency": {"type": "string"},
            },
        },
        "checks": [
            {"field": "currency", "in": ["USD", "EUR"]},
            {"field": "amount", "gte": 0},
        ],
    }
    assert contract_check(pred, __import__('json').dumps(spec)) == 0.0

