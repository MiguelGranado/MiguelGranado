#!/usr/bin/env python3
"""Contribution activity calendar — painted heatmap (no eat-to-empty).

Real calendar.json. Extra header space. Stronger orange so Mar–Sep activity reads clearly.
Subtle Platane-style square trail optional; cells stay colored.
"""
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAL = Path(__file__).resolve().parent / "calendar.json"
SIZE, STEP = 12, 16
VIEW_W = 1180

PAL = {
    "dark": {
        # empty → clearly painted oranges (level 1 already visible, not grey-on-grey)
        "dots": ["#21262d", "#c2410c", "#ea580c", "#fb923c", "#fe702d"],
        "snake": "#fe702d",
        "bg": "#0d1117",
        "text": "#e6edf3",
        "muted": "#8b949e",
        "border": "#30363d",
        "stroke": "#0d1117",
    },
    "light": {
        "dots": ["#ebedf0", "#fdba74", "#fb923c", "#ea580c", "#c2410c"],
        "snake": "#ea580c",
        "bg": "#ffffff",
        "text": "#1f2328",
        "muted": "#656d76",
        "border": "#d0d7de",
        "stroke": "#ffffff",
    },
}
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def sun0(iso: str) -> int:
    return (datetime.fromisoformat(iso).weekday() + 1) % 7


def boost(level: int) -> int:
    """Make real activity read stronger on the heatmap (still based on real days)."""
    if level <= 0:
        return 0
    return min(4, level + 1)  # 1→2, 2→3, 3→4, 4→4


def build(theme: str) -> str:
    p = PAL[theme]
    data = json.loads(CAL.read_text())
    total = int(data["total"])
    days = data["days"]

    cols: list[list[dict | None]] = []
    col: list[dict | None] = [None] * 7
    for day in days:
        r = sun0(day["date"])
        col[r] = day
        if r == 6:
            cols.append(col)
            col = [None] * 7
    if any(x is not None for x in col):
        cols.append(col)

    label_w, header_h, month_gap, legend_h, pad = 28, 48, 18, 28, 16
    n_weeks = len(cols)
    grid_w, grid_h = n_weeks * STEP, 7 * STEP
    ox = pad + label_w
    oy = header_h + month_gap  # months sit in month_gap band; title alone in header_h
    H = oy + grid_h + legend_h + 8

    cells = []
    contrib: list[tuple[int, int]] = []
    for wi, week in enumerate(cols):
        for di in range(7):
            day = week[di]
            x = ox + wi * STEP
            y = oy + di * STEP
            raw = min((day or {}).get("level", 0), 4)
            lvl = boost(raw)
            fill = p["dots"][lvl]
            cells.append(
                f'<rect x="{x}" y="{y}" width="{SIZE}" height="{SIZE}" rx="2" ry="2" fill="{fill}"/>'
            )
            if day and raw > 0:
                contrib.append((x, y))

    # Soft square trail (arifhaxn-like), does NOT clear cell colors
    snakes = []
    if len(contrib) >= 2:
        n = len(contrib)
        dur = max(12000, n * 320)
        kfs = []
        for i, (x, y) in enumerate(contrib):
            pct = 100 * i / max(n - 1, 1)
            kfs.append(f"{pct:.2f}%{{transform:translate({x}px,{y}px)}}")
        kfs.append(f"100%{{transform:translate({contrib[0][0]}px,{contrib[0][1]}px)}}")
        style = (
            f".s{{fill:{p['snake']};opacity:0.95;shape-rendering:geometricPrecision}}"
            f"@keyframes crawl{{{''.join(kfs)}}}"
        )
        for i, (sz, rx, off) in enumerate(
            [(13.5, 4.2, -0.75), (11.5, 3.8, 0.25), (10.0, 3.4, 1.0), (9.0, 3.0, 1.5)]
        ):
            delay = -i * (dur / n) * 1.35
            snakes.append(
                f'<rect class="s" width="{sz}" height="{sz}" rx="{rx}" ry="{rx}" x="{off:.1f}" y="{off:.1f}" '
                f'style="animation:crawl {dur}ms linear {delay:.0f}ms infinite"/>'
            )
    else:
        style = ""

    months = []
    last_m = None
    for wi, week in enumerate(cols):
        day = next((d for d in week if d), None)
        if not day:
            continue
        m = datetime.fromisoformat(day["date"]).month
        if m != last_m:
            last_m = m
            months.append(
                f'<text x="{ox + wi * STEP}" y="{oy - 6}" font-size="10" '
                f'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" '
                f'fill="{p["muted"]}">{MONTHS[m - 1]}</text>'
            )

    day_labs = []
    for label, row in (("Mon", 1), ("Wed", 3), ("Fri", 5)):
        day_labs.append(
            f'<text x="{ox - 6}" y="{oy + row * STEP + SIZE - 1}" text-anchor="end" font-size="9" '
            f'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" '
            f'fill="{p["muted"]}">{label}</text>'
        )

    lx = ox + grid_w - 5 * (SIZE + 3) - 48
    ly = oy + grid_h + 10
    legend = [
        f'<text x="{lx - 24}" y="{ly + SIZE - 2}" font-size="10" '
        f'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" fill="{p["muted"]}">Less</text>'
    ]
    for i, fill in enumerate(p["dots"]):
        legend.append(
            f'<rect x="{lx + i * (SIZE + 3)}" y="{ly}" width="{SIZE}" height="{SIZE}" rx="2" fill="{fill}"/>'
        )
    legend.append(
        f'<text x="{lx + 5 * (SIZE + 3) + 4}" y="{ly + SIZE - 2}" font-size="10" '
        f'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" fill="{p["muted"]}">More</text>'
    )

    total_fmt = f"{total:,}"
    # Title at y=20; months at oy-6 (~60) → clear gap
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{VIEW_W}" height="{H}" viewBox="0 0 {VIEW_W} {H}" role="img" aria-label="{total_fmt} contributions in the last year">
<desc>Contribution activity heatmap · real days · Ulamander</desc>
<style>{style}</style>
<rect width="100%" height="100%" rx="6" fill="{p["bg"]}" stroke="{p["border"]}" stroke-width="1"/>
<text x="{ox}" y="22" font-size="14" font-weight="600" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" fill="{p["text"]}">{total_fmt} contributions in the last year</text>
{"".join(months)}
{"".join(day_labs)}
{"".join(cells)}
{"".join(snakes)}
{"".join(legend)}
</svg>
'''


if __name__ == "__main__":
    from xml.etree import ElementTree as ET

    for theme, name in (("dark", "snake-dark.svg"), ("light", "snake-light.svg")):
        path = ROOT / name
        path.write_text(build(theme))
        ET.parse(path)
        print("ok", name, path.stat().st_size, "H=", build(theme).split('height="')[1][:3])
