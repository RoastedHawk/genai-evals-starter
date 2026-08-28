from pathlib import Path

from selabs.evals.reports import build_svg_line_chart, write_results_chart


def test_build_svg_line_chart_basic():
    svg = build_svg_line_chart([0.2, 0.5, 1.0])
    assert svg.startswith("<svg") and "polyline" in svg


def test_build_svg_line_chart_empty():
    svg = build_svg_line_chart([])
    assert "No results yet" in svg


def test_write_results_chart(tmp_path: Path):
    results = tmp_path / "evals.jsonl"
    results.write_text("\n".join([
        '{"score": 0.5}',
        '{"score": 1.0}',
    ]))
    out = tmp_path / "chart.svg"
    write_results_chart(results, out)
    assert out.exists() and "<svg" in out.read_text()[:100]

