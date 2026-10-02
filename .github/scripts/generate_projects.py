#!/usr/bin/env python3
"""
Generate the projects panel in the profile's shared design system
(scripts/hero/design.py — same palette, fonts and window chrome as the hero).

    python3 .github/scripts/generate_projects.py merged.json out/

Writes four files (the README picks one with <picture><source media>):
  projects.svg / projects-light.svg                 desktop (960), 2-column grid
  projects-mobile.svg / projects-light-mobile.svg   mobile (480), 1 column

One card component for both layouts. The language bar only exists for cards
with "lang_repos"; its numbers are real byte counts written by
refresh_languages.py. Cards without code access show an honest "aside" line.
Everything is static on purpose: an animation that starts from an empty state
renders EMPTY wherever the SMIL/CSS timeline is paused (off-screen images,
link previews, some apps). The blinking cursor starts visible, so it is safe.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts", "hero"))
from design import (ACCENT, DESK_W, DESK_X, GREEN, MOB_W, MOB_X, MONO, SKY, SOFT,  # noqa: E402
                    b64_file, esc, palette, section_label, text_w, window, wrap, write_validated)

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
LANG_COLOURS = [ACCENT, SOFT, SKY, GREEN]
STATUS_COLOURS = {"LIVE": GREEN, "PUBLIC REPO": SKY}
LIGHT_TEXT = {GREEN: "#15803D", SKY: "#0369A1", SOFT: "#B45309"}   # readable on white

HEADLINE = "Systems I've built"
NOTE = "Language split = real byte counts from each project's GitHub repository (private repos included)."

DESKTOP = dict(W=DESK_W, X=DESK_X, cols=2, gap=20, sub=11.5, name=17, desc=13.5, desc_lh=20, icon=20,
               tag=11, legend=12, chip=10)
MOBILE = dict(W=MOB_W, X=MOB_X, cols=1, gap=14, sub=12, name=18, desc=15, desc_lh=22, icon=22,
              tag=12, legend=13, chip=10.5)


def logo_path(name: str, theme: str) -> str | None:
    if not name:
        return None
    p = os.path.join(ROOT, "logos", name.replace("{theme}", theme))
    return p if os.path.exists(p) else None


def img(path: str, x: float, y: float, s: float) -> str:
    uri = b64_file(path)
    return (f'<image href="{uri}" xlink:href="{uri}" x="{x:.1f}" y="{y:.1f}" width="{s}" height="{s}" '
            f'preserveAspectRatio="xMidYMid meet"/>')


def pct(v: float) -> str:
    return f"{v:.1f}%"


def lang_shares(langs: dict) -> list[tuple[str, float]]:
    """Top 3 languages (>= 1%) plus "Other", rounded to one decimal with the
    largest-remainder method so the legend always adds up to exactly 100.0%."""
    total = sum(langs.values()) or 1
    entries = [(k, 1000 * v / total) for k, v in sorted(langs.items(), key=lambda kv: -kv[1])]
    shown = [e for e in entries[:3] if e[1] >= 10]
    rest = 1000 - sum(v for _, v in shown)
    if rest >= 0.5:
        shown.append(("Other", rest))
    floors = [int(v) for _, v in shown]
    short = 1000 - sum(floors)
    for i in sorted(range(len(shown)), key=lambda i: -(shown[i][1] - floors[i]))[:max(short, 0)]:
        floors[i] += 1
    return [(name, f / 10) for (name, _), f in zip(shown, floors) if f > 0]


def status_chip(label: str, right: float, y: float, p: dict, size: float) -> str:
    col = STATUS_COLOURS.get(label, SOFT)
    tx = col if p["dark"] else LIGHT_TEXT[col]
    w = text_w(label, size, bold=True, mono=True) + len(label) * 0.5 + 34
    x, h = right - w, size + 10
    return (f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="{h / 2}" fill="{col}" fill-opacity="0.14" '
            f'stroke="{col}" stroke-opacity="0.5"/>\n'
            f'<circle cx="{x + 12:.1f}" cy="{y + h / 2}" r="3.5" fill="{col}"/>\n'
            f'<text x="{x + 21:.1f}" y="{y + h / 2 + size * 0.38:.1f}" font-size="{size}" font-weight="700" '
            f'font-family="{MONO}" letter-spacing="0.5" fill="{tx}">{esc(label)}</text>')


def lang_bar(langs: dict, x: float, y: float, w: float, p: dict, s: dict, uid: str) -> tuple[str, float]:
    shown = lang_shares(langs)
    out = [f'<clipPath id="{uid}"><rect x="{x}" y="{y}" width="{w:.1f}" height="8" rx="4"/></clipPath>',
           f'<g clip-path="url(#{uid})"><rect x="{x}" y="{y}" width="{w:.1f}" height="8" fill="{p["ring_bg"]}"/>']
    cx = x
    for i, (lang, v) in enumerate(shown):
        col = LANG_COLOURS[i] if lang != "Other" else p["muted"]
        out.append(f'<rect x="{cx:.1f}" y="{y}" width="{w * v / 100:.1f}" height="8" fill="{col}"/>')
        cx += w * v / 100
    out.append("</g>")
    lx, ly = x, y + 28
    for i, (lang, v) in enumerate(shown):
        col = LANG_COLOURS[i] if lang != "Other" else p["muted"]
        label = f"{lang} {pct(v)}"
        lw = 13 + text_w(label, s["legend"], mono=True)
        if lx + lw > x + w:
            lx, ly = x, ly + s["legend"] + 8
        out.append(f'<circle cx="{lx + 4}" cy="{ly - s["legend"] * 0.35:.1f}" r="4" fill="{col}"/>')
        out.append(f'<text x="{lx + 13}" y="{ly}" font-size="{s["legend"]}" font-family="{MONO}" '
                   f'fill="{p["body"]}">{esc(label)}</text>')
        lx += lw + 14
    return "\n".join(out), ly - y + 6


def card(proj: dict, x: float, y: float, w: float, theme: str, p: dict, s: dict, uid: str,
         force_h: float | None = None) -> tuple[str, float]:
    pad = 20
    e = [None,
         f'<text x="{pad}" y="29" font-size="{s["sub"]}" font-family="{MONO}" fill="{p["muted"]}">'
         f'<tspan fill="{ACCENT}">●</tspan> {esc(proj.get("subtitle", ""))}</text>',
         status_chip(proj.get("status", ""), w - 16, 15, p, s["chip"]),
         f'<line x1="1" y1="46" x2="{w - 1:.1f}" y2="46" stroke="{p["box_stroke"]}" stroke-opacity="0.6"/>']
    sub_end = pad + 14 + text_w(proj.get("subtitle", ""), s["sub"], mono=True)
    chip_w = text_w(proj.get("status", ""), s["chip"], bold=True, mono=True) + 40
    if sub_end > w - 16 - chip_w:
        raise SystemExit(f"{proj['name']}: subtitle collides with the status chip")

    logo = logo_path(proj.get("logo"), theme)
    if logo:
        e.append(img(logo, pad, 62, 36))
    e.append(f'<text x="{pad + 50}" y="86" font-size="{s["name"]}" font-weight="700" fill="{p["heading"]}">'
             f'{esc(proj["name"])}<tspan fill="{ACCENT}">_<animate attributeName="opacity" values="1;0;1" '
             f'dur="1.2s" repeatCount="indefinite"/></tspan></text>')
    lines = wrap(proj.get("description", ""), int((w - 2 * pad) / (s["desc"] * 0.54)))
    cy = 122
    for line in lines:
        e.append(f'<text x="{pad}" y="{cy}" font-size="{s["desc"]}" fill="{p["body"]}">{esc(line)}</text>')
        cy += s["desc_lh"]
    cy += 2

    ix = pad
    for name in (proj.get("icon_tags") or [])[:4]:
        path = logo_path(name, theme)
        if path:
            e.append(img(path, ix, cy, s["icon"]))
            ix += s["icon"] + 8
    tx = ix + 4
    th = s["tag"] + 10
    for tag in (proj.get("tags") or [])[:2]:
        tw = text_w(tag, s["tag"], mono=True) + 18
        if tx + tw > w - pad:
            raise SystemExit(f"{proj['name']}: tag '{tag}' does not fit")
        e.append(f'<rect x="{tx:.1f}" y="{cy + (s["icon"] - th) / 2:.1f}" width="{tw:.1f}" height="{th}" rx="{th / 2}" '
                 f'fill="{p["cred_bg"]}" stroke="{p["cred_stroke"]}"/>')
        e.append(f'<text x="{tx + tw / 2:.1f}" y="{cy + s["icon"] / 2 + s["tag"] * 0.36:.1f}" text-anchor="middle" '
                 f'font-size="{s["tag"]}" font-family="{MONO}" fill="{p["tag_tx"]}">{esc(tag)}</text>')
        tx += tw + 6
    cy += s["icon"] + 20

    if proj.get("languages"):
        bar, bh = lang_bar(proj["languages"], pad, cy, w - 2 * pad, p, s, uid)
        e.append(bar)
        cy += bh
    elif proj.get("aside"):
        a = proj["aside"]
        e.append(f'<text x="{pad}" y="{cy + 12}" font-size="{s["legend"] + 2}" fill="{p["body"]}">'
                 f'<tspan font-weight="800" fill="{p["accent_tx"]}">{esc(a["big"])}</tspan> '
                 f'{esc(" ".join(a.get("label", [])))}</text>')
        cy += 22
    h = force_h or cy + 16
    e[0] = (f'<g transform="translate({x:.1f},{y:.1f})">\n'
            f'<rect width="{w:.1f}" height="{h}" rx="14" fill="{p["box"]}" stroke="{p["box_stroke"]}" stroke-width="1.2"/>')
    e.append("</g>")
    return "\n".join(e), h


def build(projects: list, theme: str, mobile: bool = False) -> str:
    p, s = palette(theme), (MOBILE if mobile else DESKTOP)
    W, X, cols, gap = s["W"], s["X"], s["cols"], s["gap"]
    cw = (W - 2 * X - gap * (cols - 1)) / cols
    out = [section_label(X, 80 if mobile else 86, "SELECTED WORK", p)]
    head = wrap(HEADLINE, 28 if mobile else 70)
    for i, line in enumerate(head):
        out.append(f'<text x="{X}" y="{(110 if mobile else 120) + i * 28}" font-size="{21 if mobile else 24}" '
                   f'font-weight="800" fill="{p["heading"]}">{esc(line)}</text>')
    y = (110 if mobile else 120) + (len(head) - 1) * 28 + 26
    note = wrap(NOTE, 56 if mobile else 110)
    for i, line in enumerate(note):
        out.append(f'<text x="{X}" y="{y + i * 19}" font-size="13" fill="{p["muted"]}">{esc(line)}</text>')
    y += (len(note) - 1) * 19 + 22

    for r in range(0, len(projects), cols):
        row = projects[r:r + cols]
        # dry run to size the row, then render every card at the row height
        row_h = max(card(pr, 0, 0, cw, theme, p, s, "tmp")[1] for pr in row)
        for c, pr in enumerate(row):
            svg, _ = card(pr, X + c * (cw + gap), y, cw, theme, p, s, f"lb{p['s']}{W}{r + c}", force_h=row_h)
            out.append(svg)
        y += row_h + gap
    title = "projects.sh" if mobile else "miguel@ulamander — projects.sh"
    return window(W, int(y - gap + 32), p, title, "\n".join(out), glow=("90%", "5%"), label="Projects")


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "merged.json"
    outdir = sys.argv[2] if len(sys.argv) > 2 else "."
    os.makedirs(outdir, exist_ok=True)
    with open(src) as f:
        projects = json.load(f)
    files = {("dark", False): "projects.svg", ("light", False): "projects-light.svg",
             ("dark", True): "projects-mobile.svg", ("light", True): "projects-light-mobile.svg"}
    for (theme, mobile), name in files.items():
        svg = build(projects, theme, mobile)
        write_validated(os.path.join(outdir, name), svg)
        print(f"wrote {name}: {len(svg) // 1024}KB")
