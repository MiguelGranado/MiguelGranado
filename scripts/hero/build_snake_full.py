#!/usr/bin/env python3
"""Full-width branded gusanito (1180px). Empty grid + snake travels almost full width."""
from __future__ import annotations

WEEKS = 53
DAYS = 7
CELL = 19
GAP = 3
PAD_X = 12
PAD_Y = 40
SNAKE_LEN = 8
FRAME_W = 1180


def build(theme: str) -> str:
    dark = theme == "dark"
    outer = "#070B14" if dark else "#FFFFFF"
    panel = "#0B1220" if dark else "#F8FAFC"
    cell = "#21262d" if dark else "#E2E8F0"
    stroke = "#161b22" if dark else "#CBD5E1"
    accent = "#fe702d"
    soft = "#fb923c"
    muted = "#64748B"
    label = "#94A3B8" if dark else "#475569"
    title = "#F8FAFC" if dark else "#0F172A"

    grid_w = WEEKS * (CELL + GAP) - GAP
    grid_h = DAYS * (CELL + GAP) - GAP
    ox = max(PAD_X, int((FRAME_W - grid_w) / 2))
    oy = PAD_Y
    H = oy + grid_h + 28

    pts: list[str] = []
    for wi in range(WEEKS):
        xs = ox + wi * (CELL + GAP) + CELL / 2
        rows = range(DAYS) if wi % 2 == 0 else range(DAYS - 1, -1, -1)
        for di in rows:
            ys = oy + di * (CELL + GAP) + CELL / 2
            pts.append(f"{xs:.1f},{ys:.1f}")
    # close loop back to start for seamless repeat
    path_d = "M " + " L ".join(pts) + f" L {pts[0]}"

    cells = []
    for wi in range(WEEKS):
        for di in range(DAYS):
            x = ox + wi * (CELL + GAP)
            y = oy + di * (CELL + GAP)
            cells.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{CELL}" height="{CELL}" rx="3" '
                f'fill="{cell}" stroke="{stroke}" stroke-width="1"/>'
            )

    snakes = []
    for i in range(SNAKE_LEN):
        r = 7.4 - i * 0.42
        op = max(0.35, 1.0 - i * 0.08)
        fill = accent if i < 3 else soft
        # negative begin = trail behind head
        begin = f"-{i * 0.22:.2f}s"
        snakes.append(
            f'<circle r="{r:.2f}" fill="{fill}" fill-opacity="{op:.2f}">'
            f'<animateMotion dur="22s" begin="{begin}" repeatCount="indefinite" path="{path_d}"/>'
            f"</circle>"
        )

    sid = "D" if dark else "L"
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{FRAME_W}" height="{H}" viewBox="0 0 {FRAME_W} {H}" role="img" aria-label="Ulamander gusanito">
<defs>
  <linearGradient id="bar{sid}" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{accent}"/><stop offset="0.5" stop-color="#fbbf24"/><stop offset="1" stop-color="#38BDF8"/>
  </linearGradient>
  <clipPath id="win{sid}"><rect x="2" y="2" width="{FRAME_W - 4}" height="{H - 4}" rx="14"/></clipPath>
</defs>
<rect x="2" y="2" width="{FRAME_W - 4}" height="{H - 4}" rx="14" fill="{outer}"/>
<g clip-path="url(#win{sid})">
  <rect x="2" y="2" width="{FRAME_W - 4}" height="{H - 4}" fill="{panel}"/>
  <text x="{PAD_X}" y="22" font-family="ui-sans-serif,system-ui,sans-serif" font-size="12" font-weight="700" fill="{title}">Gusanito</text>
  <text x="{FRAME_W - PAD_X}" y="22" text-anchor="end" font-family="ui-monospace,Menlo,monospace" font-size="11" fill="{muted}">full width · Ulamander</text>
  <rect x="{PAD_X}" y="28" width="{FRAME_W - PAD_X * 2}" height="2" rx="1" fill="url(#bar{sid})"/>
  {"".join(cells)}
  {"".join(snakes)}
  <text x="{FRAME_W / 2:.0f}" y="{H - 10}" text-anchor="middle" font-family="ui-sans-serif,system-ui,sans-serif" font-size="10" fill="{label}">Branded snake across the full grid · native GitHub activity stays private</text>
</g>
</svg>
'''


if __name__ == "__main__":
    from xml.etree import ElementTree as ET
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    for theme, name in (("dark", "snake-dark.svg"), ("light", "snake-light.svg")):
        p = root / name
        p.write_text(build(theme))
        ET.parse(p)
        print(f"ok {name} {p.stat().st_size}B")
