from selabs.evals.metrics import bleu, rouge_l


def test_bleu_identical():
    assert bleu("the quick brown fox", "the quick brown fox") > 0.99


def test_bleu_empty_vs_text():
    assert bleu("", "text") == 0.0


def test_rouge_l_identical():
    assert rouge_l("a b c d", "a b c d") == 1.0


def test_rouge_l_partial():
    assert rouge_l("a b c", "a c d") > 0
