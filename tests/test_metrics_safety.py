from selabs.evals.metrics import citation_presence, pii_safe


def test_citation_presence():
    assert citation_presence("Answer... source: docs", "") == 1.0
    assert citation_presence("see https://example.com", "") == 1.0
    assert citation_presence("no citation here", "") == 0.0


def test_pii_safe():
    assert pii_safe("Contact me", "") == 1.0
    assert pii_safe("Email me at a@b.com", "") == 0.0
    assert pii_safe("Call +1 202 555 0101", "") == 0.0

