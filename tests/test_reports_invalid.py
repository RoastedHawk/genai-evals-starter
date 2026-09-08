from pathlib import Path
from selabs.evals.reports import write_results_chart

def test_write_results_chart_ignores_bad_lines(tmp_path: Path):
    p = tmp_path / "evals.jsonl"
    p.write_text("\n".join([
        "not json",
        "{\"score\": 0.5}",
        " ",
    ]))
    out = tmp_path / "chart.svg"
    write_results_chart(p, out)
    assert out.exists() and out.read_text().startswith("<svg")
