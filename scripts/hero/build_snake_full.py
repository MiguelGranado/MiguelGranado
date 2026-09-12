#!/usr/bin/env python3
"""Platane/arifhaxn-style contribution snake from real calendar.json.

Visual: empty cells mid-grey, levels 1–4 brighter oranges, snake as linked
rounded squares crawling contribution cells (CSS keyframes like snk).
No 'Gusanito' title — clean SVG only.
"""
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAL = Path(__file__).resolve().parent / "calendar.json"
FRAME_W = 1180
CELL, GAP = 14, 3
PAD_X, PAD_Y = 20, 20
SNAKE_LEN = 4

PALETTES = {
    # Match arifhaxn structure: empty grey → intensity → snake accent
    "dark": {
        "bg": "#0d1117",
        "levels": ["#21262d", "#484f58", "#9a3412", "#ea580c", "#fe702d"],
        "snake": "#fe702d",
        "stroke": "#0d1117",
    },
    "light": {
        "bg": "#ffffff",
        "levels": ["#ebedf0", "#c9d1d9", "#fdba74", "#ea580c", "#c2410c"],
        "snake": "#ea580c",
        "stroke": "#ffffff",
    },
}


def wd_sun0(iso: str) -> int:
    return (datetime.fromisoformat(iso).weekday() + 1) % 7


def load_days():
    data = json.loads(CAL.read_text())
    return data["total"], data["days"]


def build(theme: str) -> str:
    pal = PALETTES[theme]
    total, days = load_days()

    cols: list[list[dict | None]] = []
    col: list[dict | None] = [None] * 7
    for i, day in enumerate(days):
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
    ox = max(PAD_X, (FRAME_W - grid_w) // 2)
    oy = PAD_Y
    H = oy + grid_h + PAD_Y

    cells_svg = []
    path_xy: list[tuple[float, float]] = []
    for wi, week in enumerate(cols):
        for di, day in enumerate(week):
            x = ox + wi * (CELL + GAP)
            y = oy + di * (CELL + GAP)
            lvl = min((day or {}).get("level", 0), 4)
            fill = pal["levels"][lvl]
            cells_svg.append(
                f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" ry="2" fill="{fill}"/>'
            )
            if day and lvl > 0:
                path_xy.append((x + CELL / 2, y + CELL / 2))

    if len(path_xy) < 2:
        path_xy = [(ox + CELL / 2, oy + CELL / 2)]

    n = len(path_xy)
    dur = max(12.0, n * 0.42)

    # Combined crawl keyframes (Platane-style transform animation)
    kframes = []
    for i, (px, py) in enumerate(path_xy):
        pct = 100 * i / max(n - 1, 1)
        kframes.append(f"{pct:.3f}%{{transform:translate({px:.1f}px,{py:.1f}px)}}")
    kframes.append(
        f"100%{{transform:translate({path_xy[0][0]:.1f}px,{path_xy[0][1]:.1f}px)}}"
    )

    style = (
        f".c{{shape-rendering:geometricPrecision;stroke:{pal['stroke']};stroke-width:1px}}"
        f".s{{fill:{pal['snake']};shape-rendering:geometricPrecision}}"
        "@keyframes crawl{" + "".join(kframes) + "}"
    )

    snakes = []
    sizes = [15.5, 13.2, 11.0, 9.2]
    for i in range(SNAKE_LEN):
        s = sizes[i]
        delay = -i * (dur / max(n, 1)) * 1.6
        snakes.append(
            f'<rect class="s s{i}" width="{s:.1f}" height="{s:.1f}" rx="4.5" ry="4.5" '
            f'x="{-s/2:.1f}" y="{-s/2:.1f}" '
            f'style="animation:crawl {dur:.2f}s linear {delay:.2f}s infinite"/>'
        )

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{FRAME_W}" height="{H}" viewBox="0 0 {FRAME_W} {H}" role="img" aria-label="Contribution snake">
<desc>Generated like Platane/snk · real contribution levels · Ulamander palette</desc>
<style>{style}</style>
<rect width="100%" height="100%" rx="8" fill="{pal["bg"]}"/>
{"".join(cells_svg)}
{"".join(snakes)}
</svg>
'''


if __name__ == "__main__":
    from xml.etree import ElementTree as ET

    for theme, name in (("dark", "snake-dark.svg"), ("light", "snake-light.svg")):
        p = ROOT / name
        p.write_text(build(theme))
        ET.parse(p)
        print(f"ok {name} {p.stat().st_size}B path={len(json.loads(CAL.read_text())['days'])}")
