"""Compact theme-aware hero SVG for the GitHub profile.

Hero only: identity + primary icons + credentials + real GitHub stats.
Full tech tags, contact links, and long lists live in README.md (clickable).
"""
import re

ICON_FILES = {
    "Python": "icons/python.svg",
    "TypeScript": "icons/typescript.svg",
    "React": "icons/reactjs.svg",
    "PostgreSQL": "icons/postgresql.svg",
    "Azure": "icons/azure.svg",
}

_ID_RE = re.compile(r'id="([^"]+)"')


def load_icon_inner(name: str, path: str) -> str:
    with open(path) as f:
        svg = f.read()
    inner = re.sub(r"^<svg[^>]*>|</svg>\s*$", "", svg.strip())
    for old_id in set(_ID_RE.findall(inner)):
        new_id = f"ic_{name.lower()}_{old_id}"
        inner = inner.replace(f'id="{old_id}"', f'id="{new_id}"')
        inner = inner.replace(f"url(#{old_id})", f"url(#{new_id})")
    return inner


def stack_chip(x, y, w, name, box_color, stroke_color, text_color) -> str:
    h, icon_size = 34, 18
    inner = load_icon_inner(name, ICON_FILES[name])
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="8" '
        f'fill="{box_color}" stroke="{stroke_color}" stroke-opacity="0.45"/>\n'
        f'<g transform="translate({x + 12:.1f},{y + (h - icon_size) / 2:.1f}) '
        f'scale({icon_size / 100:.4f})">{inner}</g>\n'
        f'<text x="{x + 38:.1f}" y="{y + h / 2 + 5:.1f}" font-size="13" fill="{text_color}">{name}</text>'
    )


def stack_row(text_color, box_color, stroke_color, x0=56.0, y=188.0) -> str:
    widths = {"Python": 98, "TypeScript": 126, "React": 92, "PostgreSQL": 134, "Azure": 94}
    x, out = x0, []
    for name in ["Python", "TypeScript", "React", "PostgreSQL", "Azure"]:
        w = widths[name]
        out.append(stack_chip(x, y, w, name, box_color, stroke_color, text_color))
        x += w + 10
    return "\n".join(out)


# Real language mix from GitHub GraphQL (2026-09-12).
LANG_STATS = [
    ("TypeScript", 76, "#3178C6"),
    ("Python", 12, "#3572A5"),
    ("HTML", 5, "#E34C26"),
    ("Other", 7, "#64748B"),
]


def lang_bar(x, y, w, h=10) -> str:
    parts, cx = [], x
    for _n, pct, color in LANG_STATS:
        sw = w * pct / 100
        parts.append(f'<rect x="{cx:.1f}" y="{y:.1f}" width="{sw:.1f}" height="{h}" fill="{color}"/>')
        cx += sw
    return "\n".join(parts)


def lang_legend(x, y, text_color) -> str:
    parts, cx = [], x
    for name, pct, color in LANG_STATS:
        label = f"{name} {pct}%"
        parts.append(f'<circle cx="{cx:.1f}" cy="{y - 4:.1f}" r="4" fill="{color}"/>')
        parts.append(f'<text x="{cx + 10:.1f}" y="{y:.1f}" font-size="12" fill="{text_color}">{label}</text>')
        cx += 28 + len(label) * 7.2
    return "\n".join(parts)


def build(theme: str) -> str:
    is_dark = theme == "dark"
    s = "D" if is_dark else "L"
    accent = "#fe702d"
    accent_soft = "#ff8a4c" if is_dark else "#e85d1c"
    outer = "#0B1220" if is_dark else "#FFFFFF"
    panel_top = "#111827" if is_dark else "#FFFBF7"
    panel_bot = "#0B1220" if is_dark else "#F8FAFC"
    topbar = "#0F172A" if is_dark else "#F1F5F9"
    divider = "rgba(148,163,184,0.18)" if is_dark else "rgba(15,23,42,0.10)"
    heading = "#F8FAFC" if is_dark else "#0F172A"
    body = "#94A3B8" if is_dark else "#64748B"
    chip_bg = "#1E293B" if is_dark else "#FFFFFF"

    X, PANEL_W = 56.0, 1068.0
    y_stack_label, y_stack = 172.0, 188.0
    y_cred_label, y_cred = 248.0, 272.0
    y_stats_label, y_stats = 312.0, 336.0
    y_langs_label, y_bar = 376.0, 400.0
    y_legend = y_bar + 28
    PANEL_H = int(y_legend + 36)

    stack = stack_row(heading, chip_bg, accent, X, y_stack)
    bar = lang_bar(X, y_bar, PANEL_W)
    legend = lang_legend(X, y_legend, body)

    # Same credential summary as miguel.ulamander.com (About + Certificazioni).
    credentials = "100+ badges &amp; certs · MS Learn Lv.15 · 19 Claude Academy · 11 Google · Fortinet NSE 3 · OCI Foundations"
    github_stats = "73 commits · 21 pull requests authored"

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="{PANEL_H}" viewBox="0 0 1180 {PANEL_H}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace" role="img" aria-label="Miguel Granados — profile">
<defs>
<linearGradient id="accent{s}" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{accent}"/><stop offset="1" stop-color="{accent_soft}"/>
</linearGradient>
<linearGradient id="panel{s}" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{panel_top}"/><stop offset="1" stop-color="{panel_bot}"/>
</linearGradient>
<clipPath id="win{s}"><rect x="2" y="2" width="1176" height="{PANEL_H - 4}" rx="16"/></clipPath>
<clipPath id="bar{s}"><rect x="{X:.1f}" y="{y_bar:.1f}" width="{PANEL_W:.1f}" height="10" rx="5"/></clipPath>
</defs>
<rect x="2" y="2" width="1176" height="{PANEL_H - 4}" rx="16" fill="{outer}"/>
<g clip-path="url(#win{s})">
<rect x="2" y="2" width="1176" height="{PANEL_H - 4}" fill="url(#panel{s})"/>
<rect x="2" y="2" width="1176" height="44" fill="{topbar}"/>
<line x1="2" y1="46" x2="1178" y2="46" stroke="{divider}"/>
<circle cx="28" cy="23" r="5" fill="#FF5F56"/>
<circle cx="48" cy="23" r="5" fill="#FFBD2E"/>
<circle cx="68" cy="23" r="5" fill="#27C93F"/>
<text x="590" y="28" text-anchor="middle" font-size="12" fill="{body}">miguel@ulamander — % ./profile.sh --live</text>

<text x="{X:.1f}" y="98" font-size="32" font-weight="700" fill="{heading}">Miguel Granados</text>
<text x="{X:.1f}" y="126" font-size="15" fill="{body}">Tecnico in Sviluppo di IA · Founder &amp; Engineer @ Ulamander</text>
<text x="{X:.1f}" y="148" font-size="13" fill="{body}">Full Stack · local-first AI · cloud security · Torino, Italy</text>
<rect x="{X:.1f}" y="160" width="{PANEL_W:.1f}" height="2" rx="1" fill="url(#accent{s})"/>

<text x="{X:.1f}" y="{y_stack_label:.1f}" font-size="12" letter-spacing="2.5" fill="{accent}">CORE STACK</text>
{stack}

<text x="{X:.1f}" y="{y_cred_label:.1f}" font-size="12" letter-spacing="2.5" fill="{accent}">CREDENTIALS</text>
<text x="{X:.1f}" y="{y_cred:.1f}" font-size="13" fill="{heading}">{credentials}</text>

<text x="{X:.1f}" y="{y_stats_label:.1f}" font-size="12" letter-spacing="2.5" fill="{accent}">GITHUB STATS</text>
<text x="{X:.1f}" y="{y_stats:.1f}" font-size="13" fill="{heading}">{github_stats}</text>

<text x="{X:.1f}" y="{y_langs_label:.1f}" font-size="12" letter-spacing="2.5" fill="{accent}">MOST USED LANGUAGES</text>
<rect x="{X:.1f}" y="{y_bar:.1f}" width="{PANEL_W:.1f}" height="10" rx="5" fill="{chip_bg}"/>
<g clip-path="url(#bar{s})">{bar}</g>
{legend}
</g>
</svg>
'''


if __name__ == "__main__":
    with open("dark.svg", "w") as f:
        f.write(build("dark"))
    with open("light.svg", "w") as f:
        f.write(build("light"))
    print("wrote dark.svg and light.svg")
