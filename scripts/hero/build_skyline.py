#!/usr/bin/env python3
"""Contribution skyline — the real contribution calendar as a flat heat map
that folds up into a 3D skyline, and back down again. REAL data only.

An SVG adaptation of the "Contribution Skyline" React component (21st.dev):
a README image can't run React, canvas or scroll handlers, so the same idea is
done with CSS animations that GitHub does play inside <img>:

  1. flat heat map (GitHub's own calendar and contribution levels)
  2. the whole grid tilts into an isometric floor (one shared transform)
  3. each day rises into a bar, in a wave from the oldest week to the newest
  4. hold, then the bars settle and the floor tilts back flat — and loop
     (10 s; quick eased moves and a small spring on the rise).

Safe-animation rule: every element's base style is the flat heat map, so a
paused or unsupported animation still shows the true calendar. Bar heights
use a log scale so one huge day can't flatten the rest; the busiest day is
always the tallest. Rebuilt by .github/workflows/activity.yml into `output`.

    GITHUB_TOKEN=... python3 scripts/hero/build_skyline.py <outdir>

Also writes contributions.json (every day of the calendar: date, count and
GitHub's level 0-4) for the interactive skyline on miguel.ulamander.com, which
fetches it from raw.githubusercontent.com (CORS *) — same data, same hour.
"""
from __future__ import annotations

import json
import math
import os
import sys
from datetime import date, datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_activity import LEVELS, LOGIN, MONTHS, cell_colours, fetch  # noqa: E402
from design import (DESK_W, DESK_X, MOB_W, MOB_X, MONO, esc, palette,  # noqa: E402
                    section_label, text_w, window, write_validated)

YAW = math.radians(24)          # camera turn: shallow, so the year reads left → right
ELEV = math.radians(36)         # camera height above the floor
CS, SN, SE, CE = math.cos(YAW), math.sin(YAW), math.sin(ELEV), math.cos(ELEV)
MAX_BAR = 5.6                   # tallest bar, in cell units

# Timeline (ms). One loop: flat → tilt → rise → hold → settle → untilt → flat.
# Short holds and quick, eased moves so it reads as one fluid motion.
LOOP = 10000
TILT0, TILT1 = 900, 1700
RISE0, RISE, WAVE, DAY_WAVE = 1600, 600, 900, 100
SETTLE0, SETTLE = 6100, 420
UNTILT0 = SETTLE0 + WAVE + DAY_WAVE + SETTLE
UNTILT1 = UNTILT0 + 800
IN_OUT = "cubic-bezier(.65,0,.35,1)"
OUT = "cubic-bezier(.34,1.4,.64,1)"       # a small overshoot: bars spring up
IN = "cubic-bezier(.5,0,.75,0)"


def pct(ms: float) -> str:
    return f"{100 * ms / LOOP:.2f}%"


def shade(hex_colour: str, k: float) -> str:
    h = hex_colour.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(c * k))) for c in (r, g, b))


def bar_height(count: int, peak: int) -> float:
    if count <= 0 or peak <= 0:
        return 0.0
    return 0.6 + (MAX_BAR - 0.6) * math.log1p(count) / math.log1p(peak)


def streaks(days: list[dict]) -> tuple[tuple, tuple]:
    """(longest, current) as (length, first date, last date); current may end
    yesterday, because today isn't over."""
    longest, run, start = (0, None, None), 0, None
    for d in days:
        if d["contributionCount"] > 0:
            if run == 0:
                start = d["date"]
            run += 1
            if run > longest[0]:
                longest = (run, start, d["date"])
        else:
            run = 0
    j = len(days) - 1
    if j >= 0 and days[j]["contributionCount"] == 0:
        j -= 1
    end = j
    while j >= 0 and days[j]["contributionCount"] > 0:
        j -= 1
    current = (end - j, days[j + 1]["date"], days[end]["date"]) if end - j > 0 else (0, None, None)
    return longest, current


def short(d: str | None) -> str:
    if not d:
        return "—"
    x = date.fromisoformat(d)
    return f"{MONTHS[x.month - 1]} {x.day}"


def stats(cal: dict) -> list[tuple[str, str, str, str]]:
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    best = max(days, key=lambda d: d["contributionCount"])
    (ln, ls, le), (cn, cs_, ce_) = streaks(days)
    first, last = date.fromisoformat(days[0]["date"]), date.fromisoformat(days[-1]["date"])
    def unit(v: int) -> str:
        return "contribution" if v == 1 else "contributions"
    total, top = cal["totalContributions"], best["contributionCount"]
    return [
        ("1 year total", f"{total:,}", unit(total),
         f"{MONTHS[first.month - 1]} {first.year} — {MONTHS[last.month - 1]} {last.year}"),
        ("Busiest day", f"{top:,}", unit(top), short(best["date"]) if top else "—"),
        ("Longest streak", f"{ln}", "day" if ln == 1 else "days", f"{short(ls)} — {short(le)}" if ln else "—"),
        ("Current streak", f"{cn}", "day" if cn == 1 else "days", f"{short(cs_)} — {short(ce_)}" if cn else "no active run"),
    ]


def stat_block(x: float, y: float, s: tuple, p: dict, big: int, anchor: str = "start") -> str:
    """Label, big number + unit, sub-line. `y` is the label baseline."""
    label, value, unit, sub = s
    vw = sum(0.3 if ch in ",." else 0.64 for ch in value) * big     # heavy digits run wider than text_w

    if anchor == "end":
        unit_x = x - text_w(unit, 13)
        vx = unit_x - 6 - vw
        lx, ta = x, "end"
    else:
        vx, unit_x, lx, ta = x, x + vw + 6, x, "start"
    return (f'<text x="{lx:.1f}" y="{y}" text-anchor="{ta}" font-size="12" fill="{p["muted"]}">{esc(label)}</text>'
            f'<text x="{vx:.1f}" y="{y + big + 4}" font-size="{big}" font-weight="800" fill="{p["accent_tx"]}">{esc(value)}</text>'
            f'<text x="{unit_x:.1f}" y="{y + big + 4}" font-size="13" fill="{p["body"]}">{esc(unit)}</text>'
            f'<text x="{lx:.1f}" y="{y + big + 22}" text-anchor="{ta}" font-size="11.5" font-family="{MONO}" '
            f'fill="{p["muted"]}">{esc(sub)}</text>')


def fade(name: str, visible: list[tuple[float, float]], dur: int = 320) -> str:
    """Opacity keyframes: 1 inside each (from, to) window (ms), 0 outside, with
    `dur` ms fades. A window that starts at 0 and/or ends at LOOP wraps."""
    frames = []
    for a, b in visible:
        frames += [(a, 1 if a == 0 else 0), (a + (0 if a == 0 else dur), 1),
                   (b - (0 if b == LOOP else dur), 1), (b, 1 if b == LOOP else 0)]
    frames = sorted({t: v for t, v in frames}.items())
    if frames[0][0] > 0:
        frames.insert(0, (0, 0))
    if frames[-1][0] < LOOP:
        frames.append((LOOP, 0))
    body = "".join(f"{pct(t)}{{opacity:{v}}}" for t, v in frames)
    return f"@keyframes {name}{{{body}}}"


def build(cal: dict, theme: str, mobile: bool = False) -> str:
    p = palette(theme)
    cols = cell_colours(p)
    W, X = (MOB_W, MOB_X) if mobile else (DESK_W, DESK_X)
    CW = W - 2 * X
    weeks = cal["weeks"][-26:] if mobile else cal["weeks"]
    n = len(weeks)
    step, size = (16, 13) if mobile else (15, 12)
    cells = [(wi, d) for wi, w in enumerate(weeks) for d in w["contributionDays"]]
    peak = max((d["contributionCount"] for _, d in cells), default=0)
    st = stats(cal)

    out = [section_label(X, 80 if mobile else 86, "CONTRIBUTION SKYLINE", p),
           f'<text x="{X}" y="{112 if mobile else 120}" font-size="{21 if mobile else 24}" font-weight="800" '
           f'fill="{p["heading"]}">{esc("The last year in 3D" if mobile else "The last year, folded into a skyline")}</text>',
           f'<text x="{X}" y="{136 if mobile else 146}" font-size="13" fill="{p["muted"]}">'
           f'{esc("Live from GitHub · last 26 weeks · refreshed hourly" if mobile else "The real heat map rises into 3D and settles back · live from the GitHub API, refreshed every hour")}</text>']
    Y0 = 160 if mobile else 172

    # ---- flat heat map geometry
    label_w = 0 if mobile else 34
    fx0 = X + label_w + (CW - label_w - n * step) / 2
    fy0 = Y0 + 26

    # ---- isometric geometry: S px per cell, origin (ix, iy) = world (0, 0)
    S = (CW - 16) / (n * CS + 7 * SN)
    hts = {(wi, d["weekday"]): bar_height(d["contributionCount"], peak) for wi, d in cells}

    def iso(x: float, y: float, z: float = 0.0) -> tuple[float, float]:
        return (x * CS - y * SN) * S, (x * SN + y * CS) * SE * S - z * CE * S

    xs, ys = [], []
    for (wi, wd), h in hts.items():
        for cx, cy in ((wi, wd), (wi + 1, wd), (wi, wd + 1), (wi + 1, wd + 1)):
            for z in (0, h):
                sx, sy = iso(cx, cy, z)
                xs.append(sx)
                ys.append(sy)
    ix = X + (CW - (max(xs) - min(xs))) / 2 - min(xs)
    iy = Y0 + 4 - min(ys)
    iso_bottom = iy + max(ys)

    def to_screen(x: float, y: float, z: float = 0.0) -> tuple[float, float]:
        sx, sy = iso(x, y, z)
        return ix + sx, iy + sy

    k = S / step
    flat_tf = f"translate({fx0:.2f}px,{fy0:.2f}px) scale(1,1) rotate(0deg) scale(1) translate({-fx0:.2f}px,{-fy0:.2f}px)"
    iso_tf = (f"translate({ix:.2f}px,{iy:.2f}px) scale(1,{SE:.4f}) rotate({math.degrees(YAW):.2f}deg) "
              f"scale({k:.4f}) translate({-fx0:.2f}px,{-fy0:.2f}px)")
    css = [f"@keyframes tilt{{0%,{pct(TILT0)}{{transform:{flat_tf};animation-timing-function:{IN_OUT}}}"
           f"{pct(TILT1)},{pct(UNTILT0)}{{transform:{iso_tf};animation-timing-function:{IN_OUT}}}"
           f"{pct(UNTILT1)},100%{{transform:{flat_tf}}}}}",
           f".t{{transform-box:view-box;transform-origin:0 0;animation:tilt {LOOP}ms infinite}}",
           f".g{{transform-box:fill-box;transform-origin:50% 100%;transform:scaleY(0)}}",
           fade("flat", [(0, TILT0), (UNTILT1 - 150, LOOP)]),
           fade("isol", [(TILT1 - 250, UNTILT0 + 250)]),
           f".fl{{animation:flat {LOOP}ms infinite}}.il{{opacity:0;animation:isol {LOOP}ms infinite}}"]

    # ---- labels: months + weekdays on the flat map, months along the front edge in 3D
    flat_labels, iso_labels, last_m, last_wi = [], [], None, -9
    for wi, w in enumerate(weeks):
        m = date.fromisoformat(w["contributionDays"][-1]["date"]).month
        if m != last_m and wi - last_wi >= 3 and wi < n - 2:
            flat_labels.append(f'<text x="{fx0 + wi * step:.1f}" y="{fy0 - 9:.1f}" font-size="11" fill="{p["muted"]}">{MONTHS[m - 1]}</text>')
            lx, ly = to_screen(wi + 0.5, 7.4)
            iso_labels.append(f'<text x="{lx:.1f}" y="{ly + 12:.1f}" font-size="11" fill="{p["muted"]}">{MONTHS[m - 1]}</text>')
            last_wi = wi
        last_m = m
    if not mobile:
        for label, row in (("Mon", 1), ("Wed", 3), ("Fri", 5)):
            flat_labels.append(f'<text x="{fx0 - 8:.1f}" y="{fy0 + row * step + size - 3:.1f}" text-anchor="end" '
                               f'font-size="11" fill="{p["muted"]}">{label}</text>')

    # ---- floor: empty days stay flat tiles; drawn first, every bar is in front of or on them
    floor = [f'<rect class="t" x="{fx0 + wi * step:.1f}" y="{fy0 + d["weekday"] * step:.1f}" width="{size}" '
             f'height="{size}" rx="3" fill="{cols[0]}"/>'
             for wi, d in cells if d["contributionCount"] == 0]

    # ---- bars, painter-sorted (far → near). Each: front face, side face, top.
    bars = []
    active = [(wi, d) for wi, d in cells if d["contributionCount"] > 0]
    active.sort(key=lambda c: (c[0] + 0.5) * SN + (c[1]["weekday"] + 0.5) * CS)
    w_frac = size / step
    a_front = math.degrees(math.atan(math.tan(YAW) * SE))
    a_side = -math.degrees(math.atan(SE / math.tan(YAW)))
    for i, (wi, d) in enumerate(active):
        wd = d["weekday"]
        lvl = LEVELS.index(d["contributionLevel"]) or 1
        top = cols[lvl]
        hpx = hts[(wi, wd)] * CE * S
        delay = (wi / max(1, n - 1)) * WAVE + (wd / 6) * DAY_WAVE
        r0, r1 = RISE0 + delay, RISE0 + delay + RISE
        s0, s1 = SETTLE0 + delay, SETTLE0 + delay + SETTLE
        css.append(f"@keyframes l{i}{{0%,{pct(r0)}{{transform:translateY(0);animation-timing-function:{OUT}}}"
                   f"{pct(r1)},{pct(s0)}{{transform:translateY({-hpx:.2f}px);animation-timing-function:{IN}}}"
                   f"{pct(s1)},100%{{transform:translateY(0)}}}}"
                   f"@keyframes g{i}{{0%,{pct(r0)}{{transform:scaleY(0);animation-timing-function:{OUT}}}"
                   f"{pct(r1)},{pct(s0)}{{transform:scaleY(1);animation-timing-function:{IN}}}"
                   f"{pct(s1)},100%{{transform:scaleY(0)}}}}"
                   f".l{i}{{animation:l{i} {LOOP}ms infinite}}.g{i}{{animation:g{i} {LOOP}ms infinite}}")
        x0, y0 = wi, wd                         # the flat cell spans [wi, wi + size/step]
        x1, y1 = x0 + w_frac, y0 + w_frac
        dx_, dy_ = to_screen(x0, y1)            # front face runs D → C
        cx_, cy_ = to_screen(x1, y1)            # side face runs C → B
        front_len = w_frac * CS * S
        side_len = w_frac * SN * S
        bars.append(
            f'<g transform="translate({dx_:.2f},{dy_:.2f}) skewY({a_front:.3f})"><rect class="g g{i}" x="0" y="{-hpx:.2f}" '
            f'width="{front_len:.2f}" height="{hpx:.2f}" fill="{shade(top, 0.80)}"/></g>'
            f'<g transform="translate({cx_:.2f},{cy_:.2f}) skewY({a_side:.3f})"><rect class="g g{i}" x="0" y="{-hpx:.2f}" '
            f'width="{side_len:.2f}" height="{hpx:.2f}" fill="{shade(top, 0.62)}"/></g>'
            f'<g class="l{i}"><rect class="t" x="{fx0 + wi * step:.1f}" y="{fy0 + wd * step:.1f}" width="{size}" '
            f'height="{size}" rx="3" fill="{top}"/></g>')

    # ---- stats: a row under the flat map; in 3D the desktop moves them to the empty corners
    flat_bottom = fy0 + 7 * step
    if mobile:
        sy = max(iso_bottom + 30, flat_bottom + 40)
        stats_svg = []
        for j, s in enumerate(st):
            stats_svg.append(stat_block(X + (j % 2) * (CW / 2), sy + (j // 2) * 74, s, p, 22))
        out_stats = "\n".join(stats_svg)
        H = sy + 74 + 64
    else:
        sy = flat_bottom + 44
        row = "".join(stat_block(X + j * (CW / 4), sy, s, p, 26) for j, s in enumerate(st))
        css.append(fade("crn", [(RISE0 + RISE + 500, SETTLE0 - 100)]))
        css.append(f".cr{{opacity:0;animation:crn {LOOP}ms infinite}}")
        right = X + CW
        corner_tr = (stat_block(right - 250, Y0 + 6, st[1], p, 30, "end")
                     + stat_block(right, Y0 + 6, st[0], p, 30, "end"))
        bl_y = iso_bottom - 70
        corner_bl = (stat_block(X, bl_y, st[2], p, 30) + stat_block(X + 200, bl_y, st[3], p, 30))
        out_stats = (f'<g class="fl">{row}</g>\n<g class="cr">{corner_tr}{corner_bl}</g>')
        H = max(iso_bottom + 22, sy + 58) + 24

    out.append(f"<style>{''.join(css)}</style>")
    out.append(f'<g class="fl">{"".join(flat_labels)}</g>')
    out.append(f'<g class="il">{"".join(iso_labels)}</g>')
    out.append("\n".join(floor))
    out.append("\n".join(bars))
    out.append(out_stats)
    title = "skyline.sh" if mobile else "miguel@ulamander — skyline.sh"
    total = f'{cal["totalContributions"]:,}'
    return window(W, int(H), p, title, "\n".join(out), glow=("70%", "8%"),
                  label=f"{total} contributions in the last year, shown as a heat map that rises into a 3D skyline")


if __name__ == "__main__":
    outdir = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(outdir, exist_ok=True)
    cal = fetch()
    for theme in ("dark", "light"):
        write_validated(os.path.join(outdir, f"skyline-{theme}.svg"), build(cal, theme))
        write_validated(os.path.join(outdir, f"skyline-{theme}-mobile.svg"), build(cal, theme, mobile=True))
    days = [{"date": d["date"], "count": d["contributionCount"], "level": LEVELS.index(d["contributionLevel"])}
            for w in cal["weeks"] for d in w["contributionDays"]]
    with open(os.path.join(outdir, "contributions.json"), "w") as f:
        json.dump({"login": LOGIN, "total": cal["totalContributions"],
                   "updated": datetime.now(timezone.utc).isoformat(timespec="minutes"), "days": days},
                  f, separators=(",", ":"))
    print(f"wrote skyline SVGs + contributions.json: {cal['totalContributions']} contributions (GitHub API)")
