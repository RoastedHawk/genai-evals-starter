from selabs.skills.citations_or_silence import guard_response


def test_guard_allows_with_citation():
    txt = "See details here: https://example.com/paper"
    assert guard_response(txt).startswith("See details")


def test_guard_blocks_without_citation():
    txt = "Answer without any sources"
    out = guard_response(txt)
    assert "sources" in out.lower()

