"""Contact bar — three link buttons in the hero's design language (replaces
the generic shields.io badges, whose LinkedIn logo stopped rendering after
simple-icons dropped the brand). Each button is its own small SVG so the
README can wrap it in <a> — links inside an SVG are not clickable via <img>.
Glyphs are drawn here (no third-party brand files) in the accent colour."""
from __future__ import annotations

import os

from design import ACCENT, ASSETS, MONO, esc, palette, write_validated

W, H = 268, 60

BUTTONS = [
    ("portfolio", "Portfolio", "miguel.ulamander.com"),
    ("linkedin", "LinkedIn", "Miguel Granados"),
    ("email", "Email", "info@ulamander.com"),
]


def glyph(kind: str, cx: float, cy: float, p: dict) -> str:
    c = ACCENT
    if kind == "portfolio":  # globe
        return (f'<g fill="none" stroke="{c}" stroke-width="1.8">'
                f'<circle cx="{cx}" cy="{cy}" r="10"/>'
                f'<ellipse cx="{cx}" cy="{cy}" rx="4.4" ry="10"/>'
                f'<line x1="{cx - 10}" y1="{cy}" x2="{cx + 10}" y2="{cy}"/>'
                f'<path d="M{cx - 8.6} {cy - 5} H{cx + 8.6} M{cx - 8.6} {cy + 5} H{cx + 8.6}"/></g>')
    if kind == "linkedin":  # rounded square with "in"
        return (f'<rect x="{cx - 10}" y="{cy - 10}" width="20" height="20" rx="4.5" fill="{c}"/>'
                f'<text x="{cx}" y="{cy + 5}" text-anchor="middle" font-size="13" font-weight="800" '
                f'fill="{p["outer"]}">in</text>')
    return (f'<g fill="none" stroke="{c}" stroke-width="1.8" stroke-linejoin="round">'  # envelope
            f'<rect x="{cx - 11}" y="{cy - 8}" width="22" height="16" rx="3"/>'
            f'<path d="M{cx - 10} {cy - 6.5} L{cx} {cy + 1} L{cx + 10} {cy - 6.5}"/></g>')


def build(kind: str, label: str, sub: str, theme: str) -> str:
    p = palette(theme)
    s = f'{p["s"]}{kind}'
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif" role="img" aria-label="{esc(label)}: {esc(sub)}">
<defs><linearGradient id="bg{s}" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="{p["panel_a"]}"/><stop offset="1" stop-color="{p["panel_b"]}"/></linearGradient></defs>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="url(#bg{s})" stroke="{p["cred_stroke"]}"/>
<circle cx="32" cy="{H / 2}" r="18" fill="{p["cred_bg"]}"/>
{glyph(kind, 32, H / 2, p)}
<text x="62" y="26" font-size="15" font-weight="700" fill="{p["heading"]}">{esc(label)}</text>
<text x="62" y="44" font-size="11.5" font-family="{MONO}" fill="{p["body"]}">{esc(sub)}</text>
<path d="M{W - 30} {H / 2 - 5} l5 5 l-5 5" fill="none" stroke="{p["muted"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
'''


if __name__ == "__main__":
    for kind, label, sub in BUTTONS:
        for theme in ("dark", "light"):
            write_validated(os.path.join(ASSETS, f"contact-{kind}-{theme}.svg"), build(kind, label, sub, theme))
    print("wrote + validated assets/contact-{portfolio,linkedin,email}-{dark,light}.svg")
