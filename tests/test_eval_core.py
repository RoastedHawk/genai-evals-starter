from selabs.evals.core import Example, run_eval


def echo_model(prompt: str) -> str:
    return prompt


def test_exact_match_eval():
    dataset = [
        Example(id="1", instruction="hi", expected="hi"),
        Example(id="2", instruction="bye", expected="bye"),
    ]
    report = run_eval(dataset, echo_model)
    assert report["n"] == 2
    assert report["score"] == 1.0
