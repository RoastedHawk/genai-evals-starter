from selabs.evals.metrics import token_f1, semantic_cosine


def test_token_f1_basic():
    assert token_f1("hello world", "hello") > 0
    assert token_f1("", "") == 1.0
    assert token_f1("only", "different") == 0.0


def test_semantic_cosine_basic():
    assert semantic_cosine("a b c", "a c d") > 0
    assert semantic_cosine("", "") == 1.0
    assert semantic_cosine("", "x") == 0.0

