#!/usr/bin/env python3
"""Platane/arifhaxn-style snake + GitHub-like 'N contributions in the last year' header."""
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAL = Path(__file__).resolve().parent / "calendar.json"
FRAME_W = 1180
CELL, GAP = 13, 3
PAD_X = 44
PAD_TOP = 42  # room for title
PAD_BOT = 36  # room for legend
SNAKE_LEN = 4
MONTH_ABBR = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

PALETTES = {
    "dark": {
        "bg": "#0d1117",
        "panel": "#0d1117",
        "border": "#30363d",
        "text": "#e6edf3",
        "muted": "#8b949e",
        "levels": ["#161b22", "#3d2318", "#9a3412", "#ea580c", "#fe702d"],
        "snake": "#fe702d",
        "stroke": "#0d1117",
    },
    "light": {
        "bg": "#ffffff",
        "panel": "#ffffff",
        "border": "#d0d7de",
        "text": "#1f2328",
        "muted": "#656d76",
        "levels": ["#ebedf0", "#fdba74", "#fb923c", "#ea580c", "#c2410c"],
        "snake": "#ea580c",
        "stroke": "#ffffff",
    },
}


def wd_sun0(iso: str) -> int:
    return (datetime.fromisoformat(iso).weekday() + 1) % 7


def build(theme: str) -> str:
    pal = PALETTES[theme]
    data = json.loads(CAL.read_text())
    total = int(data["total"])
    days = data["days"]

    cols: list[list[dict | None]] = []
    col: list[dict | None] = [None] * 7
    for day in days:
        r = wd_sun0(day["date"])
        col[r] = day
        if r == 6:
            cols.append(col)
            col = [None] * 7
    if any(x is not None for x in col):
        cols.append(col)

    n_weeks = len(cols)
    grid_w = n_weeks * (CELL + GAP) - GAP
    grid_h = 7 * (CELL + GAP) - GAP
    ox = PAD_X
    oy = PAD_TOP
    # Center horizontally if space
    if FRAME_W - PAD_X - 16 > grid_w:
        ox = max(PAD_X, (FRAME_W - grid_w) // 2)
    H = oy + grid_h + PAD_BOT

    # Month labels: first week of each month
    month_labels = []
    last_m = None
    for wi, week in enumerate(cols):
        day = next((d for d in week if d), None)
        if not day:
            continue
        dt = datetime.fromisoformat(day["date"])
        if dt.month != last_m:
            last_m = dt.month
            x = ox + wi * (CELL + GAP)
            month_labels.append(
                f'<text x="{x}" y="{oy - 8}" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" '
                f'font-size="11" fill="{pal["muted"]}">{MONTH_ABBR[dt.month - 1]}</text>'
            )

    # Day labels Mon/Wed/Fri (rows 1,3,5 in Sun-start grid)
    day_labels = []
    for label, row in (("Mon", 1), ("Wed", 3), ("Fri", 5)):
        y = oy + row * (CELL + GAP) + CELL - 2
        day_labels.append(
            f'<text x="{ox - 8}" y="{y}" text-anchor="end" '
            f'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" '
            f'font-size="10" fill="{pal["muted"]}">{label}</text>'
        )

    cells_svg = []
    path_xy: list[tuple[float, float]] = []
    for wi, week in enumerate(cols):
        for di, day in enumerate(week):
            x = ox + wi * (CELL + GAP)
            y = oy + di * (CELL + GAP)
            lvl = min((day or {}).get("level", 0), 4)
            fill = pal["levels"][lvl]
            title = f'{day["date"]}: level {lvl}' if day else ""
            cells_svg.append(
                f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" ry="2" fill="{fill}">'
                f"<title>{title}</title></rect>"
            )
            if day and lvl > 0:
                path_xy.append((x + CELL / 2, y + CELL / 2))

    if len(path_xy) < 2:
        path_xy = [(ox + CELL / 2, oy + CELL / 2)]

    n = len(path_xy)
    dur = max(12.0, n * 0.42)
    kframes = []
    for i, (px, py) in enumerate(path_xy):
        pct = 100 * i / max(n - 1, 1)
        kframes.append(f"{pct:.3f}%{{transform:translate({px:.1f}px,{py:.1f}px)}}")
    kframes.append(f"100%{{transform:translate({path_xy[0][0]:.1f}px,{path_xy[0][1]:.1f}px)}}")

    style = (
        f".c{{shape-rendering:geometricPrecision;stroke:{pal['stroke']};stroke-width:1px}}"
        f".s{{fill:{pal['snake']};shape-rendering:geometricPrecision}}"
        "@keyframes crawl{" + "".join(kframes) + "}"
    )

    snakes = []
    sizes = [14.5, 12.5, 10.5, 9.0]
    for i in range(SNAKE_LEN):
        s = sizes[i]
        delay = -i * (dur / max(n, 1)) * 1.6
        snakes.append(
            f'<rect class="s" width="{s:.1f}" height="{s:.1f}" rx="4" ry="4" '
            f'x="{-s/2:.1f}" y="{-s/2:.1f}" '
            f'style="animation:crawl {dur:.2f}s linear {delay:.2f}s infinite"/>'
        )

    # Legend Less → More
    leg_y = oy + grid_h + 18
    leg_x = ox + grid_w - 5 * (CELL + 2) - 40
    legend = [
        f'<text x="{leg_x - 28}" y="{leg_y + CELL - 2}" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="10" fill="{pal["muted"]}">Less</text>'
    ]
    for i, fill in enumerate(pal["levels"]):
        legend.append(
            f'<rect x="{leg_x + i * (CELL + 2)}" y="{leg_y}" width="{CELL}" height="{CELL}" rx="2" fill="{fill}"/>'
        )
    legend.append(
        f'<text x="{leg_x + 5 * (CELL + 2) + 4}" y="{leg_y + CELL - 2}" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="10" fill="{pal["muted"]}">More</text>'
    )

    total_fmt = f"{total:,}"
    title = (
        f'<text x="{ox}" y="24" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" '
        f'font-size="14" font-weight="600" fill="{pal["text"]}">{total_fmt} contributions in the last year</text>'
    )

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{FRAME_W}" height="{H}" viewBox="0 0 {FRAME_W} {H}" role="img" aria-label="{total_fmt} contributions in the last year">
<desc>Contribution calendar + snake · real levels · Ulamander</desc>
<style>{style}</style>
<rect x="1" y="1" width="{FRAME_W - 2}" height="{H - 2}" rx="6" fill="{pal["panel"]}" stroke="{pal["border"]}" stroke-width="1"/>
{title}
{"".join(month_labels)}
{"".join(day_labels)}
{"".join(cells_svg)}
{"".join(snakes)}
{"".join(legend)}
</svg>
'''


if __name__ == "__main__":
    from xml.etree import ElementTree as ET

    for theme, name in (("dark", "snake-dark.svg"), ("light", "snake-light.svg")):
        p = ROOT / name
        p.write_text(build(theme))
        ET.parse(p)
        print(f"ok {name} {p.stat().st_size}B")
