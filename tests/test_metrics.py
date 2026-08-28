from selabs.evals.metrics import (
    char_ngram_similarity,
    exact_match,
    jaccard,
    json_valid,
    regex_match,
)


def test_regex_match_fullmatch():
    assert regex_match("hello", "h.*o") == 1.0
    assert regex_match("hello", "world") == 0.0


def test_json_valid_metric():
    assert json_valid("{}") == 1.0
    assert json_valid("not json") == 0.0


def test_exact_match_trims():
    assert exact_match(" hi ", "hi") == 1.0


def test_jaccard_tokens():
    assert jaccard("a b c", "a c d") > 0
    assert jaccard("", "") == 1.0
    assert jaccard("", "x") == 0.0


def test_char_ngram_similarity():
    assert char_ngram_similarity("hello", "hel") > 0
    assert char_ngram_similarity("", "") == 1.0
    assert char_ngram_similarity("", "x") == 0.0
