#!/usr/bin/env python3
"""GitHub achievements panel — read from the live profile, tiers included.

Parses the achievements that GitHub itself shows on
https://github.com/MiguelGranado (sidebar: badge image, name, tier label such
as x2 / x3). GitHub serves a different image per tier (e.g.
pair-extraordinaire-silver, pull-shark-bronze), so the panel shows exactly
what GitHub awarded. Runs daily in .github/workflows/activity.yml: a newly
awarded achievement (e.g. Galaxy Brain) appears automatically, and nothing
that GitHub has not awarded can ever be shown.

    python3 scripts/hero/build_achievements.py <outdir>
Writes achievements-{dark,light}[-mobile].svg.
"""
from __future__ import annotations

import base64
import html
import os
import re
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from design import (DESK_W, DESK_X, MOB_W, MOB_X, MONO, esc, palette,  # noqa: E402
                    section_label, text_w, window, write_validated)

LOGIN = "MiguelGranado"
BADGE_RE = re.compile(
    r'<a href="/%s\?achievement=([a-z0-9-]+)[^"]*" class="position-relative">'
    r'<img src="([^"]+)"[^>]*alt="Achievement: ([^"]+)"[^>]*/>'
    r'(?:<span[^>]*achievement-tier-label--(\w+)[^>]*>(x\d+)</span>)?</a>' % LOGIN)
TIER_COLOURS = {"bronze": "#E8A15A", "silver": "#C9D1D9", "gold": "#F2C94C"}


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 profile-achievements"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def fetch() -> list[dict]:
    page = get(f"https://github.com/{LOGIN}").decode("utf-8", "replace")
    out, seen = [], set()
    for slug, src, name, tier, count in BADGE_RE.findall(page):
        if slug in seen:
            continue
        seen.add(slug)
        out.append({"slug": slug, "name": html.unescape(name), "tier": tier or "", "count": count or "",
                    "img": "data:image/png;base64," + base64.b64encode(get(html.unescape(src))).decode()})
    if not out:
        sys.exit("no achievements parsed — GitHub markup changed? refusing to publish an empty panel")
    return out


def tile(x, y, w, h, a, p, img_size) -> str:
    cx = x + w / 2
    ix, iy = cx - img_size / 2, y + 18
    parts = [f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="14" fill="{p["box"]}" stroke="{p["box_stroke"]}" stroke-width="1.2"/>',
             f'<image href="{a["img"]}" x="{ix:.1f}" y="{iy}" width="{img_size}" height="{img_size}"/>']
    if a["count"]:
        col = TIER_COLOURS.get(a["tier"], "#C9D1D9")
        label = a["count"].replace("x", "×")
        cw = text_w(label, 13, bold=True) + 18
        parts.append(f'<rect x="{ix + img_size - cw + 6:.1f}" y="{iy + img_size - 24}" width="{cw:.1f}" height="24" rx="12" '
                     f'fill="{col}" stroke="{p["outer"]}" stroke-width="2"/>')
        parts.append(f'<text x="{ix + img_size - cw / 2 + 6:.1f}" y="{iy + img_size - 7.5}" text-anchor="middle" font-size="13" '
                     f'font-weight="800" fill="#24292F">{esc(label)}</text>')
    parts.append(f'<text x="{cx:.1f}" y="{iy + img_size + 28}" text-anchor="middle" font-size="15" font-weight="700" '
                 f'fill="{p["heading"]}">{esc(a["name"])}</text>')
    sub = f'{a["tier"].capitalize()} tier · {a["count"].replace("x", "×")}' if a["count"] else "Earned"
    parts.append(f'<text x="{cx:.1f}" y="{iy + img_size + 48}" text-anchor="middle" font-size="12" font-family="{MONO}" '
                 f'fill="{p["muted"]}">{esc(sub)}</text>')
    return "\n".join(parts)


def build(badges: list[dict], theme: str, mobile: bool = False) -> str:
    p = palette(theme)
    W, X = (MOB_W, MOB_X) if mobile else (DESK_W, DESK_X)
    CW = W - 2 * X
    cols = 2 if mobile else min(max(len(badges), 1), 5)
    gap, img = (12, 96) if mobile else (16, 108)
    tw = (CW - gap * (cols - 1)) / cols
    th = img + 82
    out = [section_label(X, 80 if mobile else 86, "GITHUB ACHIEVEMENTS", p),
           f'<text x="{X}" y="{112 if mobile else 120}" font-size="{21 if mobile else 24}" font-weight="800" fill="{p["heading"]}">Earned on GitHub</text>',
           f'<text x="{X}" y="{136 if mobile else 146}" font-size="13" fill="{p["muted"]}">'
           f'{esc("Read daily from the GitHub profile — tiers included" if not mobile else "Read daily from GitHub — tiers included")}</text>']
    y0 = 162 if mobile else 172
    rows = -(-len(badges) // cols)
    for i, a in enumerate(badges):
        r, c = divmod(i, cols)
        in_row = min(cols, len(badges) - r * cols)
        offset = (CW - (in_row * tw + (in_row - 1) * gap)) / 2      # centre a short last row
        out.append(tile(X + offset + c * (tw + gap), y0 + r * (th + gap), tw, th, a, p, img))
    H = y0 + rows * (th + gap) - gap + 30
    title = "achievements.sh" if mobile else "miguel@ulamander — achievements.sh"
    return window(W, int(H), p, title, "\n".join(out), glow=("50%", "0%"), label="GitHub achievements")


if __name__ == "__main__":
    outdir = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(outdir, exist_ok=True)
    badges = fetch()
    for theme in ("dark", "light"):
        write_validated(os.path.join(outdir, f"achievements-{theme}.svg"), build(badges, theme))
        write_validated(os.path.join(outdir, f"achievements-{theme}-mobile.svg"), build(badges, theme, mobile=True))
    print("achievements:", ", ".join(f'{b["name"]} {b["count"]}'.strip() for b in badges))
