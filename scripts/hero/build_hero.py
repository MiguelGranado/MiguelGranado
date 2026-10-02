"""Hero card — identity, core stack and credential summary in ONE window.

Desktop: assets/hero-{dark,light}.svg (960 wide). Mobile:
assets/hero-{dark,light}-mobile.svg (480 wide), selected in the README by <picture><source media>.
All tokens/helpers come from design.py so this matches every other panel."""
from __future__ import annotations

from design import (ACCENT, DESK_W, DESK_X, MOB_W, MOB_X, esc, icon, image, asset, palette,
                    section_label, text_w, window, rule_id, write_validated)

NAME = "Miguel Granados"
ROLE = "Founder & CEO, Ulamander · AI Development Technician · Full Stack"
TAGLINE = "I turn complex processes into intelligent AI-driven systems · Turin, Italy"
FOOTER = "Live in production: company website · SaaS app · real estate CRM · lead funnel · security-first"

# Real languages/frameworks + the automation layer. (name, icon, brand colour)
STACK = [
    ("Python", "icons/python.svg", "#3776AB"),
    ("TypeScript", "icons/typescript.svg", "#3178C6"),
    ("React", "icons/reactjs.svg", "#61DAFB"),
    ("PostgreSQL", "icons/postgresql.svg", "#4169E1"),
    ("Azure", "icons/azure.svg", "#0078D4"),
    ("n8n", "badge-icons/n8n.svg", "#EA4B71"),
]

# Summary only — the detail (every cert, issuer, verify link) lives in the
# credentials panel further down the README. Only items with a public record.
CREDENTIALS = [
    ("MS Learn Level 15", "badge-icons/microsoft.svg"),
    ("Claude Academy 19", "badge-icons/claude-ai.svg"),
    ("Google Skillshop 10", "badge-icons/google.svg"),
    ("Fortinet NSE 3", "badge-icons/fortinet.svg"),
    ("Oracle OCI 2025", "badge-icons/oracle.svg"),
]

LOGO = "ulamander-logo.png"          # small mark next to the wordmark
MARK_HD = "ulamander-mark-hd.png"    # large mark balancing the right side


def availability(x, y, p) -> str:
    return (f'<rect x="{x}" y="{y}" width="188" height="26" rx="13" fill="{p["pill_bg"]}"/>\n'
            f'<circle cx="{x + 18}" cy="{y + 13}" r="5" fill="#22C55E">'
            f'<animate attributeName="opacity" values="1;0.35;1" dur="2.4s" repeatCount="indefinite"/></circle>\n'
            f'<text x="{x + 32}" y="{y + 17}" font-size="12" font-weight="600" fill="{p["pill_tx"]}">Available for projects</text>')


def brand(x, y, p) -> str:
    return (image(asset(LOGO), x, y + 1, 19, 22) + "\n" +
            f'<text x="{x + 27}" y="{y + 18}" font-size="14" font-weight="700" letter-spacing="1.5" '
            f'fill="{p["heading"]}">ULAMANDER</text>')


def stack_chip(x, y, name, path, colour, p) -> tuple[str, float]:
    h, size = 36, 18
    w = 38 + text_w(name, 13, bold=True) + 16
    svg = (f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="10" fill="{p["box"]}" '
           f'stroke="{colour}" stroke-opacity="0.55" stroke-width="1.5"/>\n'
           f'{icon(asset(path), x + 12, y + (h - size) / 2, size)}\n'
           f'<text x="{x + 38:.1f}" y="{y + 23}" font-size="13" font-weight="600" fill="{p["heading"]}">{esc(name)}</text>')
    return svg, w


def credential_pill(x, y, label, path, p) -> tuple[str, float]:
    h, size = 30, 16
    w = 33 + text_w(label, 11.5, bold=True) + 14
    svg = (f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="15" fill="{p["cred_bg"]}" '
           f'stroke="{p["cred_stroke"]}"/>\n'
           f'{icon(asset(path), x + 11, y + (h - size) / 2, size)}\n'
           f'<text x="{x + 33:.1f}" y="{y + 19.5}" font-size="11.5" font-weight="600" fill="{p["pill_tx"]}">{esc(label)}</text>')
    return svg, w


def name_gradient(p, W) -> str:
    return (f'<defs><linearGradient id="name{p["s"]}{W}" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0" stop-color="{p["heading"]}"/><stop offset="0.55" stop-color="{p["heading"]}"/>'
            f'<stop offset="1" stop-color="{ACCENT}"/></linearGradient></defs>')


def build(theme: str) -> str:
    p = palette(theme)
    W, X = DESK_W, DESK_X
    rows = []

    x = X
    for name, path, colour in STACK:
        svg, w = stack_chip(x, 252, name, path, colour, p)
        rows.append(svg)
        x += w + 12

    x, y = X, 334
    for label, path in CREDENTIALS:
        svg, w = credential_pill(x, y, label, path, p)
        if x + w > W - X:
            x, y = X, y + 40
            svg, w = credential_pill(x, y, label, path, p)
        rows.append(svg)
        x += w + 10

    footer_y = y + 62
    H = footer_y + 30
    body = f'''{name_gradient(p, W)}
{availability(X, 64, p)}
{brand(X + 208, 64, p)}
{image(asset(MARK_HD), W - X - 118, 50, 118, 137)}
<text x="{X}" y="130" font-size="44" font-weight="800" fill="url(#name{p["s"]}{W})">{esc(NAME)}</text>
<text x="{X}" y="162" font-size="17" fill="{p["body"]}">{esc(ROLE)}</text>
<text x="{X}" y="186" font-size="15" fill="{p["muted"]}">{esc(TAGLINE)}</text>
<rect x="{X}" y="204" width="{W - 2 * X}" height="3" rx="1.5" fill="url(#{rule_id(p, W)})"/>
{section_label(X, 238, "CORE STACK", p)}
{section_label(X, 320, "CREDENTIALS", p)}
{chr(10).join(rows)}
<text x="{X}" y="{footer_y}" font-size="13" fill="{p["muted"]}">{esc(FOOTER)}</text>'''
    return window(W, H, p, "miguel@ulamander — production systems", body, glow=("85%", "20%"))


def build_mobile(theme: str) -> str:
    """480 wide: GitHub's mobile app renders it at ~0.75x, so type here is
    sized to stay >= ~10 CSS px on a phone."""
    p = palette(theme)
    W, X = MOB_W, MOB_X
    lines = [
        (section_label(X, 252, "CORE STACK", p), None),
        ("Python · TypeScript · React", 276), ("PostgreSQL · Azure · n8n", 298),
        (section_label(X, 334, "CREDENTIALS", p), None),
        ("MS Learn Level 15 · Claude Academy 19 badges", 358),
        ("Google Skillshop 10 · Fortinet NSE 3 · Oracle OCI", 380),
    ]
    rows = "\n".join(t if y is None else
                     f'<text x="{X}" y="{y}" font-size="14" font-weight="600" fill="{p["heading"]}">{esc(t)}</text>'
                     for t, y in lines)
    body = f'''{name_gradient(p, W)}
{availability(X, 62, p)}
{brand(X + 204, 62, p)}
<text x="{X}" y="132" font-size="38" font-weight="800" fill="url(#name{p["s"]}{W})">{esc(NAME)}</text>
<text x="{X}" y="162" font-size="16" fill="{p["body"]}">{esc("Founder & CEO, Ulamander")}</text>
<text x="{X}" y="185" font-size="16" fill="{p["body"]}">{esc("AI Development Technician · Full Stack")}</text>
<text x="{X}" y="208" font-size="14" fill="{p["muted"]}">{esc("Turin, Italy · remote & on-site")}</text>
<rect x="{X}" y="224" width="{W - 2 * X}" height="2" rx="1" fill="url(#{rule_id(p, W)})"/>
{rows}'''
    return window(W, 408, p, "miguel@ulamander", body)


if __name__ == "__main__":
    import os
    from design import ASSETS
    for theme in ("dark", "light"):
        write_validated(os.path.join(ASSETS, f"hero-{theme}.svg"), build(theme))
        write_validated(os.path.join(ASSETS, f"hero-{theme}-mobile.svg"), build_mobile(theme))
    print("wrote + validated assets/hero-{dark,light}(.svg, -mobile.svg)")
