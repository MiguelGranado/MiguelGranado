#!/usr/bin/env python3
"""Contribution activity — Platane-style: cells stay painted until snake collects them."""
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
        "dots": ["#21262d", "#c2410c", "#ea580c", "#fb923c", "#fe702d"],
        "snake": "#fe702d",
        "bg": "#0d1117",
        "text": "#e6edf3",
        "muted": "#8b949e",
        "border": "#30363d",
        "stroke": "#1b1f230a",
    },
    "light": {
        "dots": ["#ebedf0", "#fdba74", "#fb923c", "#ea580c", "#c2410c"],
        "snake": "#ea580c",
        "bg": "#ffffff",
        "text": "#1f2328",
        "muted": "#656d76",
        "border": "#d0d7de",
        "stroke": "#1b1f230a",
    },
}
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def sun0(iso: str) -> int:
    return (datetime.fromisoformat(iso).weekday() + 1) % 7


def boost(level: int) -> int:
    if level <= 0:
        return 0
    return min(4, level + 1)


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

    # Generous header so title never sits on Sep/Oct
    label_w, header_h, month_band, legend_h, pad = 28, 56, 22, 30, 18
    n_weeks = len(cols)
    grid_w, grid_h = n_weeks * STEP, 7 * STEP
    ox = pad + label_w
    oy = header_h + month_band
    H = oy + grid_h + legend_h + 10
    c0, c1, c2, c3, c4 = p["dots"]

    contrib: list[tuple[int, int, int, int]] = []  # x, y, lvl, idx
    cells = []
    idx = 0
    for wi, week in enumerate(cols):
        for di in range(7):
            day = week[di]
            x = ox + wi * STEP
            y = oy + di * STEP
            raw = min((day or {}).get("level", 0), 4)
            lvl = boost(raw)
            if day and raw > 0:
                cells.append(
                    f'<rect class="c e{idx}" x="{x}" y="{y}" width="{SIZE}" height="{SIZE}" rx="2" ry="2"/>'
                )
                contrib.append((x, y, lvl, idx))
                idx += 1
            else:
                cells.append(
                    f'<rect class="c" x="{x}" y="{y}" width="{SIZE}" height="{SIZE}" rx="2" ry="2"/>'
                )

    n = max(len(contrib), 1)
    dur = max(14000, n * 340)
    style = [
        f":root{{--cb:{p['stroke']};--cs:{p['snake']};--ce:{c0};--c1:{c1};--c2:{c2};--c3:{c3};--c4:{c4}}}",
        ".c{shape-rendering:geometricPrecision;fill:var(--ce);stroke:var(--cb);stroke-width:1px}",
        ".s{shape-rendering:geometricPrecision;fill:var(--cs)}",
    ]
    # Platane: painted until snake collects (eat) that cell
    for x, y, lvl, i in contrib:
        t0 = 100.0 * i / n
        t1 = min(100.0, t0 + 0.55)
        style.append(
            f"@keyframes e{i}{{0%,{t0:.2f}%{{fill:var(--c{lvl})}}{t1:.2f}%,100%{{fill:var(--ce)}}}}"
            f".e{i}{{animation:e{i} {dur}ms linear infinite}}"
        )

    snakes = []
    if contrib:
        kfs = []
        for i, (x, y, lvl, _) in enumerate(contrib):
            pct = 100 * i / max(len(contrib) - 1, 1)
            kfs.append(f"{pct:.2f}%{{transform:translate({x}px,{y}px)}}")
        kfs.append(f"100%{{transform:translate({contrib[0][0]}px,{contrib[0][1]}px)}}")
        style.append(f"@keyframes crawl{{{''.join(kfs)}}}")
        # head picks up color of current cell (approximate via stepped keyframes)
        color_kfs = []
        for i, (x, y, lvl, _) in enumerate(contrib):
            pct = 100 * i / max(len(contrib) - 1, 1)
            color_kfs.append(f"{pct:.2f}%{{fill:var(--c{lvl})}}")
        color_kfs.append(f"100%{{fill:var(--c{contrib[0][2]})}}")
        style.append(f"@keyframes pick{{{''.join(color_kfs)}}}")
        for i, (sz, rx, off) in enumerate(
            [(14.4, 4.5, -1.2), (12.2, 4.0, -0.1), (10.6, 3.5, 0.7), (9.6, 3.2, 1.2)]
        ):
            delay = -i * (dur / len(contrib)) * 1.45
            # head (i==0) picks cell colors; body stays snake accent
            fill_anim = (
                f"animation:crawl {dur}ms linear {delay:.0f}ms infinite, "
                f"pick {dur}ms linear {delay:.0f}ms infinite"
                if i == 0
                else f"animation:crawl {dur}ms linear {delay:.0f}ms infinite"
            )
            snakes.append(
                f'<rect class="s" width="{sz}" height="{sz}" rx="{rx}" ry="{rx}" x="{off:.1f}" y="{off:.1f}" '
                f'style="{fill_anim}"/>'
            )

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
                f'<text x="{ox + wi * STEP}" y="{oy - 8}" font-size="10" '
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
    ly = oy + grid_h + 12
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
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{VIEW_W}" height="{H}" viewBox="0 0 {VIEW_W} {H}" role="img" aria-label="{total_fmt} contributions in the last year">
<desc>Generated like Platane/snk · collects cell colors</desc>
<style>{"".join(style)}</style>
<rect width="100%" height="100%" rx="6" fill="{p["bg"]}" stroke="{p["border"]}" stroke-width="1"/>
<text x="{ox}" y="24" font-size="14" font-weight="600" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" fill="{p["text"]}">{total_fmt} contributions in the last year</text>
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
        print("ok", name, path.stat().st_size)
