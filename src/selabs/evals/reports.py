from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List


def _scale(value: float, in_min: float, in_max: float, out_min: float, out_max: float) -> float:
    if in_max == in_min:
        return (out_min + out_max) / 2.0
    ratio = (value - in_min) / (in_max - in_min)
    return out_min + ratio * (out_max - out_min)


def build_svg_line_chart(
    scores: Iterable[float], *, width: int = 640, height: int = 220, margin: int = 30,
    latency_ms: Iterable[float] | None = None,
) -> str:
    values: List[float] = list(scores)
    w, h, m = width, height, margin
    plot_w, plot_h = w - 2 * m, h - 2 * m

    if not values:
        return (
            f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}'>"
            f"<rect width='100%' height='100%' fill='#ffffff'/>"
            f"<text x='{w/2:.1f}' y='{h/2:.1f}' font-family='Verdana' font-size='14'"
            f" text-anchor='middle' fill='#666'>No results yet</text></svg>"
        )

    # Clamp to [0,1]
    values = [max(0.0, min(1.0, v)) for v in values]

    xs = [m + (plot_w * (i / (len(values) - 1 or 1))) for i in range(len(values))]
    ys = [m + (plot_h * (1 - v)) for v in values]  # invert so higher scores are higher on chart
    points = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))

    # Simple grid
    grid = []
    for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
        y = m + plot_h * (1 - frac)
        grid.append(f"<line x1='{m}' y1='{y:.1f}' x2='{m+plot_w}' y2='{y:.1f}' stroke='#eee' />")
        grid.append(
            f"<text x='{m-8}' y='{y+4:.1f}' font-family='Verdana' font-size='10' text-anchor='end' fill='#888'>{int(frac*100)}</text>"
        )

    svg = [
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}' role='img' aria-label='Eval results'>",
        "<rect width='100%' height='100%' fill='#ffffff'/>",
        f"<rect x='{m}' y='{m}' width='{plot_w}' height='{plot_h}' fill='none' stroke='#ccc' />",
        *grid,
        f"<polyline fill='none' stroke='#2c7be5' stroke-width='2' points='{points}' />",
        f"<circle cx='{xs[-1]:.1f}' cy='{ys[-1]:.1f}' r='3' fill='#2c7be5' />",
        f"<text x='{xs[-1]+6:.1f}' y='{ys[-1]-6:.1f}' font-family='Verdana' font-size='10' fill='#2c7be5'>{int(values[-1]*100)}</text>",
    ]

    # Optional latency overlay
    if latency_ms:
        lat_vals = list(latency_ms)
        if lat_vals:
            mn, mx = min(lat_vals), max(lat_vals)
            norm = [0.0 if mx == mn else (v - mn) / (mx - mn) for v in lat_vals]
            ys2 = [m + (plot_h * (1 - v)) for v in norm]
            points2 = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs[: len(ys2)], ys2))
            svg += [
                f"<polyline fill='none' stroke='#f6c343' stroke-width='2' points='{points2}' />",
                f"<circle cx='{xs[min(len(xs)-1, len(ys2)-1)]:.1f}' cy='{ys2[-1]:.1f}' r='3' fill='#f6c343' />",
            ]

    svg.append("</svg>")
    
    return "".join(svg)


def write_results_chart(results_path: Path, out_svg: Path) -> None:
    scores: List[float] = []
    lats: List[float] = []
    if results_path.exists():
        for line in results_path.read_text().splitlines():
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            score = obj.get("score")
            if isinstance(score, (int, float)):
                # If JSON score is given as percentage, normalize to 0..1; otherwise assume 0..1 already
                scores.append(score if score <= 1.0 else score / 100.0)
            lat = obj.get("latency_ms")
            if isinstance(lat, (int, float)):
                lats.append(float(lat))
    svg = build_svg_line_chart(scores, latency_ms=lats if lats else None)
    out_svg.parent.mkdir(parents=True, exist_ok=True)
    out_svg.write_text(svg)
