#!/usr/bin/env python3
"""Build full-width contribution grid from GitHub (authenticated viewer)."""
import json
import subprocess
from datetime import date
from pathlib import Path

q = """
query {
  viewer {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays { contributionCount date }
        }
      }
    }
  }
}
"""
raw = subprocess.check_output(["gh", "api", "graphql", "-f", f"query={q}"], text=True)
cal = json.loads(raw)["data"]["viewer"]["contributionsCollection"]["contributionCalendar"]
weeks = cal["weeks"]
total = cal["totalContributions"]


def cell_color(n: int) -> str:
    if n <= 0:
        return "#30363d"
    if n == 1:
        return "#6e7681"
    if n <= 3:
        return "#fb923c"
    if n <= 6:
        return "#fe702d"
    return "#c2410c"


# Fit to 1180px like the hero
margin_x, margin_y = 24, 28
cols = max(len(weeks), 1)
rows = 7
avail_w = 1180 - 2 * margin_x
cell = min(14, (avail_w - (cols - 1) * 3) / cols)
gap = 3
W, H = 1180, int(margin_y * 2 + rows * (cell + gap) - gap + 24)

rects = []
for wi, week in enumerate(weeks):
    for day in week["contributionDays"]:
        d = date.fromisoformat(day["date"])
        di = (d.weekday() + 1) % 7  # Sun=0
        x = margin_x + wi * (cell + gap)
        y = margin_y + di * (cell + gap)
        n = day["contributionCount"]
        rects.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell:.1f}" height="{cell:.1f}" rx="2" fill="{cell_color(n)}">'
            f'<title>{day["date"]}: {n}</title></rect>'
        )

active = sum(1 for w in weeks for d in w["contributionDays"] if d["contributionCount"] > 0)
svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="GitHub contributions">
<rect width="100%" height="100%" rx="12" fill="#0B1220"/>
<text x="{margin_x}" y="18" font-size="11" font-family="ui-sans-serif,system-ui,sans-serif" fill="#94A3B8">Last 12 months · {total} contributions · {active} active days</text>
{chr(10).join(rects)}
</svg>
'''
out = Path(__file__).resolve().parents[2] / "readme-publicado" / "contrib-grid.svg"
# also write next to script caller cwd if used from clone
Path("contrib-grid.svg").write_text(svg)
print(f"wrote contrib-grid.svg {W}x{H} total={total} active={active} weeks={cols}")
