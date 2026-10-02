"""Shared design system for every generated profile SVG (hero, contact bar,
about, projects, credentials). One palette, one font stack, one window chrome,
one set of helpers — so the README reads as a single designed surface instead
of a stack of unrelated images.

Rules learned the hard way (see DOCUMENTACION-TECNICA.md):
- Valid XML only: every user-facing string goes through esc().
- No CSS classes on <image> elements: a class that matches a display:none rule
  (even behind an inactive @media) stops the image from decoding at all.
- Animations: base attribute = final value, <animate> only interpolates FROM 0,
  so the SVG is correct even where SMIL never runs.
- Mobile is a separate, narrower SVG selected by <picture><source media> in the
  README — @media inside an SVG loaded via <img> is not reliable.
"""
from __future__ import annotations

import base64
import html
import os
import re

ACCENT, SOFT, SKY, GREEN = "#fe702d", "#fbbf24", "#38BDF8", "#22C55E"

# Canvas sizes. GitHub renders the README at 846 CSS px on desktop (>=1280
# viewport) and ~308 px on a 390 px phone, so a 960-wide desktop canvas shows
# at ~0.88x and the 480-wide mobile canvas at ~0.64-0.75x. The README switches
# to the mobile files below 1100 px viewport (narrow laptops/tablets too).
DESK_W, DESK_X = 960, 48
MOB_W, MOB_X = 480, 24
SANS = "ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.normpath(os.path.join(HERE, "..", "..", "assets"))   # every generated SVG lives here
_ID_RE = re.compile(r'id="([^"]+)"')
_VIEWBOX_RE = re.compile(r'viewBox="([-\d.]+)\s+([-\d.]+)\s+([\d.]+)\s+([\d.]+)"')


def palette(theme: str) -> dict:
    dark = theme == "dark"
    return {
        "dark": dark,
        "s": "D" if dark else "L",
        "outer": "#070B14" if dark else "#FFFFFF",
        "panel_a": "#121A2B" if dark else "#FFF8F2",
        "panel_b": "#0B1220" if dark else "#F1F5F9",
        "bar": "#0A1020" if dark else "#EEF2FF",
        "heading": "#F8FAFC" if dark else "#0F172A",
        "body": "#A8B3C7" if dark else "#475569",
        "muted": "#64748B",
        "box": "#1A2336" if dark else "#FFFFFF",
        "box_stroke": "rgba(254,112,45,0.30)" if dark else "rgba(234,88,12,0.28)",
        "quote_bg": "#17213A" if dark else "#FFF4EC",
        "pill_bg": "#243049" if dark else "#FFE8D6",
        "pill_tx": "#FDE68A" if dark else "#9A3412",
        "cred_bg": "rgba(254,112,45,0.14)" if dark else "rgba(234,88,12,0.10)",
        "cred_stroke": "rgba(254,112,45,0.45)" if dark else "rgba(234,88,12,0.35)",
        "tag_tx": "#FDBA74" if dark else "#9A3412",
        "ring_bg": "rgba(148,163,184,0.18)" if dark else "rgba(100,116,139,0.20)",
        "accent_tx": ACCENT if dark else "#C2410C",
    }


def esc(s) -> str:
    return html.escape(str(s), quote=True)


def text_w(s: str, size: float, bold: bool = False, mono: bool = False) -> float:
    """Rough rendered width for layout (no font metrics available at build
    time). Deliberately a little generous so nothing clips."""
    k = 0.61 if mono else (0.58 if bold else 0.54)
    return len(s) * size * k


def wrap(text: str, max_chars: int) -> list[str]:
    """Word-wrap without truncation — callers size the box to fit the lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if len(trial) > max_chars and cur:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def asset(*parts: str) -> str:
    return os.path.join(HERE, *parts)


def b64_file(path: str) -> str:
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    mime = {"png": "image/png", "svg": "image/svg+xml", "jpg": "image/jpeg"}.get(ext, "image/png")
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode()


def image(path: str, x: float, y: float, w: float, h: float) -> str:
    """Raster/SVG embedded as a data URI. No class attribute, ever (see module doc)."""
    uri = b64_file(path)
    return (f'<image href="{uri}" xlink:href="{uri}" x="{x:.1f}" y="{y:.1f}" '
            f'width="{w:.1f}" height="{h:.1f}" preserveAspectRatio="xMidYMid meet"/>')


def load_icon(name: str, path: str):
    """(inner_markup, min_x, min_y, width, height) from the icon's own viewBox —
    source icons use very different viewBoxes (24x24, 100x100, 228x120...)."""
    with open(path) as f:
        svg = f.read()
    m = _VIEWBOX_RE.search(svg)
    vx, vy, vw, vh = (float(g) for g in m.groups()) if m else (0.0, 0.0, 100.0, 100.0)
    root = re.match(r"\s*<svg[^>]*>", svg)
    # Root presentation attributes (e.g. fill="none") must survive inlining,
    # or stroke-only paths fall back to a solid black fill.
    root_attrs = " ".join(re.findall(r'(?:fill|stroke|stroke-width|stroke-linecap|stroke-linejoin)="[^"]*"',
                                     root.group(0))) if root else ""
    inner = re.sub(r"^<svg[^>]*>|</svg>\s*$", "", svg.strip())
    inner = re.sub(r"<title>.*?</title>", "", inner)
    for old_id in set(_ID_RE.findall(inner)):
        new_id = f"ic_{name}_{old_id}"
        inner = inner.replace(f'id="{old_id}"', f'id="{new_id}"')
        inner = inner.replace(f"url(#{old_id})", f"url(#{new_id})")
    if root_attrs:
        inner = f"<g {root_attrs}>{inner}</g>"
    return inner, vx, vy, vw, vh


def icon(path: str, x: float, y: float, size: float, fill: str | None = None) -> str:
    """Inline vector icon scaled + centered in a size x size box. `fill` tints
    single-colour (simple-icons style) glyphs; multi-colour icons keep theirs.
    Internal ids are keyed by icon + position: unique within one SVG and
    deterministic, so regenerating never produces a spurious diff."""
    key = re.sub(r"[^a-z0-9]+", "", os.path.basename(path).lower())
    inner, vx, vy, vw, vh = load_icon(f"{key}_{x:.0f}_{y:.0f}", path)
    scale = size / max(vw, vh)
    ox = x + (size - vw * scale) / 2 - vx * scale
    oy = y + (size - vh * scale) / 2 - vy * scale
    fill_attr = f' fill="{fill}"' if fill else ""
    return f'<g transform="translate({ox:.2f},{oy:.2f}) scale({scale:.4f})"{fill_attr}>{inner}</g>'


def section_label(x: float, y: float, text: str, p: dict) -> str:
    return (f'<text x="{x}" y="{y}" font-size="11" letter-spacing="2.5" font-weight="700" '
            f'fill="{p["accent_tx"]}">{esc(text)}</text>')


def window(W: int, H: int, p: dict, title: str, body: str, *, chrome: bool = True,
           glow=("85%", "15%"), label: str = "Miguel Granados") -> str:
    """Full SVG document: rounded panel, gradient + glow, optional terminal bar."""
    s = p["s"] + str(W)
    bar = ""
    if chrome:
        bar = f'''<rect x="2" y="2" width="{W - 4}" height="42" fill="{p['bar']}" fill-opacity="0.85"/>
<circle cx="28" cy="23" r="5" fill="#FF5F56"/>
<circle cx="48" cy="23" r="5" fill="#FFBD2E"/>
<circle cx="68" cy="23" r="5" fill="#27C93F"/>
<text x="{W / 2:.0f}" y="27" text-anchor="middle" font-size="12" font-family="{MONO}" fill="{p['muted']}">{esc(title)}</text>'''
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}" preserveAspectRatio="xMidYMid meet" font-family="{SANS}" role="img" aria-label="{esc(label)}">
<defs>
<linearGradient id="bg{s}" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="{p['panel_a']}"/><stop offset="1" stop-color="{p['panel_b']}"/>
</linearGradient>
<radialGradient id="glow{s}" cx="{glow[0]}" cy="{glow[1]}" r="50%">
  <stop offset="0" stop-color="{ACCENT}" stop-opacity="{0.22 if p['dark'] else 0.14}"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/>
</radialGradient>
<linearGradient id="rule{s}" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{ACCENT}"/><stop offset="0.6" stop-color="{SOFT}"/><stop offset="1" stop-color="{SOFT}" stop-opacity="0.15"/>
</linearGradient>
<clipPath id="win{s}"><rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="18"/></clipPath>
</defs>
<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="18" fill="{p['outer']}"/>
<g clip-path="url(#win{s})">
<rect x="2" y="2" width="{W - 4}" height="{H - 4}" fill="url(#bg{s})"/>
<rect x="2" y="2" width="{W - 4}" height="{H - 4}" fill="url(#glow{s})"/>
{bar}
{body}
</g>
<rect x="2.5" y="2.5" width="{W - 5}" height="{H - 5}" rx="17.5" fill="none" stroke="{p['box_stroke']}" stroke-opacity="0.6"/>
</svg>
'''


def rule_id(p: dict, W: int) -> str:
    return f"rule{p['s']}{W}"


def write_validated(path: str, svg: str) -> None:
    """Build the string first, then write (a crash never leaves a truncated
    file), then parse it back so invalid XML fails the build."""
    from xml.etree import ElementTree as ET
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w") as f:
        f.write(svg)
    ET.parse(path)
