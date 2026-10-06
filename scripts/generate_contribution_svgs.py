#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import html
import re
import urllib.request
from pathlib import Path

THEMES = {
    "dark": {
        "bg": "#0D1117",
        "panel": "#161B22",
        "title": "#F0F6FC",
        "subtitle": "#8B949E",
        "border": "#30363D",
        "palette": ["#161B22", "#0E4429", "#006D32", "#26A641", "#39D353"],
        "legend": "#8B949E",
    },
    "light": {
        "bg": "#FFFFFF",
        "panel": "#F6F8FA",
        "title": "#24292F",
        "subtitle": "#57606A",
        "border": "#D0D7DE",
        "palette": ["#EBEDF0", "#9BE9A8", "#40C463", "#30A14E", "#216E39"],
        "legend": "#57606A",
    },
}


def fetch_contributions_html(username: str) -> str:
    url = f"https://github.com/users/{username}/contributions"
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "profile-readme-svg-generator",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def _find_attr(tag: str, name: str) -> str | None:
    match = re.search(fr'{name}="([^"]+)"', tag)
    return match.group(1) if match else None


def extract_cells(html_text: str) -> list[dict]:
    cells = []
    day_tags = re.findall(r"<td[^>]*ContributionCalendar-day[^>]*>", html_text)
    for index, tag in enumerate(day_tags):
        date = _find_attr(tag, "data-date")
        if not date:
            continue
        level = int(_find_attr(tag, "data-level") or 0)
        id_value = _find_attr(tag, "id") or ""
        id_match = re.search(r"contribution-day-component-(\\d+)-(\\d+)", id_value)
        if id_match:
            col = int(id_match.group(1))
            row = int(id_match.group(2))
        else:
            col = index // 7
            row = index % 7
        cells.append(
            {
                "x": float(col * 13),
                "y": float(row * 13),
                "w": 10.0,
                "h": 10.0,
                "count": level,
                "date": date,
            }
        )

    if not cells:
        raise RuntimeError("No contribution cells found in fetched SVG")

    cells.sort(key=lambda item: item["date"])
    return cells


def build_thresholds(counts: list[int]) -> tuple[int, int, int]:
    positives = sorted(count for count in counts if count > 0)
    if not positives:
        return 0, 0, 0

    def at_percentile(p: float) -> int:
        idx = int((len(positives) - 1) * p)
        return positives[idx]

    q1 = at_percentile(0.25)
    q2 = at_percentile(0.50)
    q3 = at_percentile(0.75)
    return q1, q2, q3


def count_to_level(count: int, thresholds: tuple[int, int, int]) -> int:
    if count <= 0:
        return 0
    q1, q2, q3 = thresholds
    if count <= q1:
        return 1
    if count <= q2:
        return 2
    if count <= q3:
        return 3
    return 4


def render_theme(username: str, cells: list[dict], theme_name: str) -> str:
    theme = THEMES[theme_name]
    min_x = min(cell["x"] for cell in cells)
    min_y = min(cell["y"] for cell in cells)
    max_x = max(cell["x"] + cell["w"] for cell in cells)
    max_y = max(cell["y"] + cell["h"] for cell in cells)

    grid_w = int(max_x - min_x)
    grid_h = int(max_y - min_y)

    width = 1060
    height = 260
    grid_x = 36
    grid_y = 86
    title_x = 36

    today = dt.datetime.now(dt.UTC).strftime("%Y-%m-%d")
    first_date = cells[0]["date"]
    last_date = cells[-1]["date"]
    thresholds = build_thresholds([cell["count"] for cell in cells])

    lines: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="Animated GitHub contribution graph for {html.escape(username)}">',
        "  <defs>",
        "    <style>",
        "      .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace; }",
        "    </style>",
        "  </defs>",
        f'  <rect x="0" y="0" width="{width}" height="{height}" rx="14" fill="{theme["bg"]}"/>',
        f'  <rect x="18" y="18" width="{width - 36}" height="{height - 36}" rx="12" fill="{theme["panel"]}" stroke="{theme["border"]}"/>',
        f'  <text x="{title_x}" y="46" class="mono" font-size="16" font-weight="600" fill="{theme["title"]}">$ github contributions --user {html.escape(username)}</text>',
        f'  <text x="{title_x}" y="66" class="mono" font-size="12" fill="{theme["subtitle"]}">range: {first_date} → {last_date} · updated: {today}</text>',
    ]

    for index, cell in enumerate(cells):
        x = int(grid_x + (cell["x"] - min_x))
        y = int(grid_y + (cell["y"] - min_y))
        level = count_to_level(cell["count"], thresholds)
        fill = theme["palette"][level]
        begin = 0.25 + (index * 0.008)
        lines.extend(
            [
                f'  <rect x="{x}" y="{y}" width="{int(cell["w"])}" height="{int(cell["h"])}" rx="2" fill="{fill}" opacity="0">',
                f'    <title>{cell["date"]}: activity level {cell["count"]}</title>',
                f'    <animate attributeName="opacity" values="0;1" begin="{begin:.3f}s" dur="0.1s" fill="freeze"/>',
                "  </rect>",
            ]
        )

    legend_x = grid_x + grid_w + 28
    legend_y = grid_y + 12
    lines.append(
        f'  <text x="{legend_x}" y="{legend_y - 10}" class="mono" font-size="11" fill="{theme["legend"]}">less</text>'
    )
    for i, color in enumerate(theme["palette"]):
        lx = legend_x + i * 18
        lines.append(
            f'  <rect x="{lx}" y="{legend_y}" width="12" height="12" rx="2" fill="{color}" stroke="{theme["border"]}"/>'
        )
    lines.append(
        f'  <text x="{legend_x + (len(theme["palette"]) - 1) * 18 + 24}" y="{legend_y + 10}" class="mono" font-size="11" fill="{theme["legend"]}">more</text>'
    )
    lines.append("</svg>")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate animated contribution graph SVGs.")
    parser.add_argument("--username", required=True, help="GitHub username")
    parser.add_argument("--outdir", default=".", help="Output directory")
    args = parser.parse_args()

    html_text = fetch_contributions_html(args.username)
    cells = extract_cells(html_text)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    dark = render_theme(args.username, cells, "dark")
    light = render_theme(args.username, cells, "light")

    (outdir / "contributions-dark.svg").write_text(dark, encoding="utf-8")
    (outdir / "contributions-light.svg").write_text(light, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
