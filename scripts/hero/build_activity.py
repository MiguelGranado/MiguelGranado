#!/usr/bin/env python3
"""Contribution activity panel with a Platane-style snake — REAL data only.

Fetches the contribution calendar from GitHub's GraphQL API
(user.contributionsCollection.contributionCalendar). The headline total is
GitHub's own `totalContributions`; cell colours come from GitHub's own
`contributionLevel`. Nothing is edited, boosted or invented. Rebuilt daily by
.github/workflows/activity.yml into the `output` branch.

The snake walks the grid one cell at a time (Manhattan path) and eats every
contribution cell in date order. Safe-animation rule: each cell's base fill is
its real colour and the CSS animation only empties it while the snake passes,
so a paused or unsupported animation still shows the true calendar.

    GITHUB_TOKEN=... python3 scripts/hero/build_activity.py <outdir>
Locally, without GITHUB_TOKEN, it falls back to `gh auth token`.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.request
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from design import (ACCENT, DESK_W, DESK_X, MOB_W, MOB_X, esc, palette,  # noqa: E402
                    section_label, text_w, window, write_validated)

LOGIN = "MiguelGranado"
LEVELS = ["NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
QUERY = """query($login: String!) { user(login: $login) { contributionsCollection {
  contributionCalendar { totalContributions weeks { contributionDays {
    date contributionCount contributionLevel weekday } } } } } }"""
STEP_MS = 110          # time the snake spends per grid cell
SNAKE_LEN = 5          # body segments


def token() -> str:
    t = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if t:
        return t
    return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()


def fetch() -> dict:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"Bearer {token()}", "Content-Type": "application/json",
                 "User-Agent": "profile-activity"})
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if "errors" in body:
        sys.exit(f"GraphQL error: {body['errors']}")
    return body["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def cell_colours(p: dict) -> list[str]:
    if p["dark"]:
        return ["#1E2638", "#7C2D12", "#C2410C", "#EA580C", "#FE702D"]
    return ["#E9EDF3", "#FED7AA", "#FDBA74", "#FB923C", "#EA580C"]


def snake_path(targets: list[tuple[int, int]], start: tuple[int, int]) -> tuple[list[tuple[int, int]], dict]:
    """Grid walk visiting every target in order; returns the cell sequence and
    the step index at which each target is eaten."""
    path, eaten_at = [start], {}
    cx, cy = start
    for tx, ty in targets:
        while (cx, cy) != (tx, ty):
            if cx != tx:
                cx += 1 if tx > cx else -1
            else:
                cy += 1 if ty > cy else -1
            path.append((cx, cy))
        eaten_at[(tx, ty)] = len(path) - 1
    return path, eaten_at


def grid(weeks: list, x0: float, y0: float, size: int, step: int, p: dict, uid: str) -> str:
    cols = cell_colours(p)
    cells, targets, lvl_of = [], [], {}
    for wi, week in enumerate(weeks):
        for d in week["contributionDays"]:
            lvl = LEVELS.index(d["contributionLevel"])
            x, y = x0 + wi * step, y0 + d["weekday"] * step
            if lvl:
                targets.append((wi, d["weekday"]))
                lvl_of[(wi, d["weekday"])] = lvl
                cells.append(f'<rect class="{uid}c{wi}_{d["weekday"]}" x="{x}" y="{y}" width="{size}" height="{size}" rx="3" fill="{cols[lvl]}"/>')
            else:
                cells.append(f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="3" fill="{cols[0]}"/>')
    if not targets:
        return "\n".join(cells)

    path, eaten_at = snake_path(targets, (0, 3))
    path += [(path[-1][0] + 1 + i, path[-1][1]) for i in range(SNAKE_LEN + 1)]   # slide off to the right
    n = len(path)
    dur = n * STEP_MS + 1500                       # + a short pause with the full calendar
    walk = 100 * n * STEP_MS / dur                 # % of the loop spent walking
    css = []
    for (wi, wd), k in eaten_at.items():
        t0 = walk * k / n
        lvl = lvl_of[(wi, wd)]
        css.append(f"@keyframes {uid}k{wi}_{wd}{{0%,{t0:.2f}%{{fill:{cols[lvl]}}}{t0 + 0.3:.2f}%,{walk + 1:.2f}%{{fill:{cols[0]}}}"
                   f"{walk + 4:.2f}%,100%{{fill:{cols[lvl]}}}}}"
                   f".{uid}c{wi}_{wd}{{animation:{uid}k{wi}_{wd} {dur}ms linear infinite}}")
    kf = "".join(f"{walk * i / n:.3f}%{{transform:translate({x0 + cx * step}px,{y0 + cy * step}px)}}"
                 for i, (cx, cy) in enumerate(path))
    css.append(f"@keyframes {uid}crawl{{{kf}100%{{transform:translate({x0 + path[-1][0] * step}px,{y0 + path[-1][1] * step}px)}}}}")
    snake = []
    for i in range(SNAKE_LEN):
        sz = size + 2 - i * 1.6
        off = (size - sz) / 2
        op = 1 - i * 0.15
        snake.append(f'<rect x="{off:.1f}" y="{off:.1f}" width="{sz:.1f}" height="{sz:.1f}" rx="{3 + (1 if i == 0 else 0)}" '
                     f'fill="{ACCENT}" opacity="{op:.2f}" style="transform:translate({x0}px,{y0 + 3 * step}px);'
                     f'animation:{uid}crawl {dur}ms linear {i * STEP_MS}ms infinite"/>')
    return f'<style>{"".join(css)}</style>\n' + "\n".join(cells) + "\n" + "\n".join(snake)


def month_labels(weeks, x0, y, step, p) -> str:
    out, last, last_wi = [], None, -9
    for wi, week in enumerate(weeks):
        m = date.fromisoformat(week["contributionDays"][-1]["date"]).month
        if m != last and wi - last_wi >= 3 and wi < len(weeks) - 2:
            out.append(f'<text x="{x0 + wi * step}" y="{y}" font-size="11" fill="{p["muted"]}">{MONTHS[m - 1]}</text>')
            last_wi = wi
        last = m
    return "\n".join(out)


def legend(x_right, y, size, p) -> str:
    cols = cell_colours(p)
    x = x_right - 5 * (size + 4) - 34
    out = [f'<text x="{x - 8}" y="{y + size - 2}" text-anchor="end" font-size="11" fill="{p["muted"]}">Less</text>']
    for i, c in enumerate(cols):
        out.append(f'<rect x="{x + i * (size + 4)}" y="{y}" width="{size}" height="{size}" rx="3" fill="{c}"/>')
    out.append(f'<text x="{x + 5 * (size + 4) + 4}" y="{y + size - 2}" font-size="11" fill="{p["muted"]}">More</text>')
    return "\n".join(out)


def stats(cal: dict) -> list[tuple[str, str]]:
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    active = [d for d in days if d["contributionCount"] > 0]
    best = max(days, key=lambda d: d["contributionCount"])
    last30 = sum(d["contributionCount"] for d in days[-30:])
    bd = date.fromisoformat(best["date"])
    return [(f'{len(active)}', "active days"),
            (f'{best["contributionCount"]:,}', f'busiest day · {MONTHS[bd.month - 1]} {bd.day}'),
            (f'{last30:,}', "last 30 days")]


def build(cal: dict, theme: str, mobile: bool = False) -> str:
    p = palette(theme)
    total = f'{cal["totalContributions"]:,}'
    if mobile:
        W, X, size, step, weeks = MOB_W, MOB_X, 13, 16, cal["weeks"][-26:]
    else:
        W, X, size, step, weeks = DESK_W, DESK_X, 12, 15, cal["weeks"]
    CW = W - 2 * X
    body = [section_label(X, 80 if mobile else 86, "CONTRIBUTION ACTIVITY", p),
            f'<text x="{X}" y="{112 if mobile else 120}" font-size="{21 if mobile else 24}" font-weight="800" '
            f'fill="{p["heading"]}">{esc(total)} contributions in the last year</text>',
            f'<text x="{X}" y="{136 if mobile else 146}" font-size="13" fill="{p["muted"]}">'
            f'{esc("Live from the GitHub API, refreshed daily" + (" · last 26 weeks shown" if mobile else ""))}</text>']
    # real stats chips
    sx, sy = X, (152 if mobile else 164)
    for num, label in stats(cal):
        w = text_w(num, 15, bold=True) + text_w(label, 12.5) + 34
        body.append(f'<rect x="{sx:.1f}" y="{sy}" width="{w:.1f}" height="30" rx="15" fill="{p["cred_bg"]}" stroke="{p["cred_stroke"]}"/>')
        body.append(f'<text x="{sx + 14:.1f}" y="{sy + 20}" font-size="15" font-weight="800" fill="{p["accent_tx"]}">{esc(num)}'
                    f'<tspan font-size="12.5" font-weight="500" fill="{p["body"]}" dx="6">{esc(label)}</tspan></text>')
        sx += w + 10
        if mobile and sx > X + CW - 120:
            sx, sy = X, sy + 38
    gx = X + (0 if mobile else 34)
    gy = sy + 70
    body.append(month_labels(weeks, gx, gy - 9, step, p))
    if not mobile:
        for label, row in (("Mon", 1), ("Wed", 3), ("Fri", 5)):
            body.append(f'<text x="{gx - 8}" y="{gy + row * step + size - 3}" text-anchor="end" font-size="11" '
                        f'fill="{p["muted"]}">{label}</text>')
    body.append(grid(weeks, gx, gy, size, step, p, "m" if mobile else "d"))
    ly = gy + 7 * step + 14
    body.append(legend(gx + len(weeks) * step - (step - size), ly, size - 2, p))
    H = ly + size + 30
    title = "activity.sh" if mobile else "miguel@ulamander — activity.sh"
    return window(W, H, p, title, "\n".join(body), glow=("8%", "10%"), label=f"{total} contributions in the last year")


if __name__ == "__main__":
    outdir = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(outdir, exist_ok=True)
    cal = fetch()
    for theme in ("dark", "light"):
        write_validated(os.path.join(outdir, f"activity-{theme}.svg"), build(cal, theme))
        write_validated(os.path.join(outdir, f"activity-{theme}-mobile.svg"), build(cal, theme, mobile=True))
    print(f"wrote activity SVGs: {cal['totalContributions']} contributions (GitHub API)")
