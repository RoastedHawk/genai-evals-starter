from selabs.evals.reports import build_svg_line_chart, _scale

def test_build_svg_with_latency():
    svg = build_svg_line_chart([0.2, 0.6, 0.8], latency_ms=[50, 60, 70])
    assert "polyline" in svg and "#f6c343" in svg

def test_scale_helper():
    assert abs(_scale(5, 0, 10, 0, 100) - 50.0) < 1e-6
    assert _scale(1, 1, 1, 0, 100) == 50.0
