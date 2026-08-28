import pytest

from selabs.evals.core import metric_by_name


def test_metric_by_name_known():
    m = metric_by_name("exact")
    assert callable(m)


def test_metric_by_name_unknown():
    with pytest.raises(ValueError):
        metric_by_name("does-not-exist")

