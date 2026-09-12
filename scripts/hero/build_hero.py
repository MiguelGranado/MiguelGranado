"""Assembles the full theme-aware hero SVG: a single text panel (no photo),
with real tech-logo icons (MIT-licensed, from xandemon/developer-icons) in
the STACK row instead of plain text chips."""
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
    """Return the icon's inner markup (no outer <svg>), with any id=
    definitions namespaced per-icon so multiple icons can share one document."""
    with open(path) as f:
        svg = f.read()
    inner = re.sub(r"^<svg[^>]*>|</svg>\s*$", "", svg.strip())
    ids = set(_ID_RE.findall(inner))
    for old_id in ids:
        new_id = f"ic_{name.lower()}_{old_id}"
        inner = inner.replace(f'id="{old_id}"', f'id="{new_id}"')
        inner = inner.replace(f"url(#{old_id})", f"url(#{new_id})")
    return inner


def stack_chip(x: float, y: float, w: float, name: str, box_color: str, stroke_color: str, text_color: str) -> str:
    h = 30
    icon_size = 18
    icon_x = x + 10
    icon_y = y + (h - icon_size) / 2
    inner = load_icon_inner(name, ICON_FILES[name])
    return f'''<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="8" fill="{box_color}" stroke="{stroke_color}" stroke-opacity="0.5"/>
<g transform="translate({icon_x:.1f},{icon_y:.1f}) scale({icon_size / 100:.4f})">{inner}</g>
<text x="{x + 10 + icon_size + 8:.1f}" y="{y + h / 2 + 5:.1f}" font-size="13" fill="{text_color}">{name}</text>'''


def stack_row(text_color: str, box_color: str, stroke_color: str, x0: float = 500.0) -> str:
    names = ["Python", "TypeScript", "React", "PostgreSQL", "Azure"]
    widths = {"Python": 88, "TypeScript": 118, "React": 82, "PostgreSQL": 128, "Azure": 88}
    x = x0
    y = 212.0
    out = []
    for name in names:
        w = widths[name]
        out.append(stack_chip(x, y, w, name, box_color, stroke_color, text_color))
        x += w + 10
    return "\n".join(out)


# Full tag list from the real portfolio (miguel.ulamander.com, "Certificazioni"
# section) — excludes the 5 already shown with icons above, to avoid duplicates.
EXTRA_STACK_TAGS = [
    "Full Stack", "Node.js", "Docker", "n8n", "Ollama / LLM",
    "Microsoft Sentinel", "Defender XDR", "Fortinet NSE 3", "Oracle Cloud",
    "SC-900", "AI-900", "GDPR", "EU AI Act", "Claude Code", "Shopify",
    "WordPress", "Cloudflare Tunnel",
]


def text_chip_row(tags: list[str], x0: float, y0: float, max_w: float, box_color: str, stroke_color: str, text_color: str) -> tuple[str, float]:
    """Wraps plain-text chips left-to-right within max_w, returns (svg, total_height_used)."""
    h = 28
    pad_x = 13
    gap = 10
    row_gap = 14
    char_w = 6.7
    x, y = x0, y0
    out = []
    for tag in tags:
        w = pad_x * 2 + len(tag) * char_w
        if x + w > x0 + max_w and x > x0:
            x = x0
            y += h + row_gap
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="7" fill="{box_color}" stroke="{stroke_color}" stroke-opacity="0.4"/>')
        out.append(f'<text x="{x + w / 2:.1f}" y="{y + h / 2 + 4.5:.1f}" text-anchor="middle" font-size="12" fill="{text_color}">{tag}</text>')
        x += w + gap
    total_h = (y - y0) + h
    return "\n".join(out), total_h


LANG_STATS = [
    ("Python", 65, "#3776AB"),
    ("TypeScript", 23, "#3178C6"),
    ("JavaScript", 11, "#F7DF1E"),
    ("Other", 1, "#8b8b8b"),
]


def lang_bar(x: float, y: float, w: float, h: float) -> str:
    parts = []
    cx = x
    for _name, pct, color in LANG_STATS:
        seg_w = w * pct / 100
        parts.append(f'<rect x="{cx:.1f}" y="{y:.1f}" width="{seg_w:.1f}" height="{h}" fill="{color}"/>')
        cx += seg_w
    return "\n".join(parts)


def lang_legend(x: float, y: float, text_color: str) -> str:
    parts = []
    cx = x
    for name, pct, color in LANG_STATS:
        parts.append(f'<circle cx="{cx:.1f}" cy="{y - 4:.1f}" r="4" fill="{color}"/>')
        parts.append(f'<text x="{cx + 10:.1f}" y="{y:.1f}" font-size="12" fill="{text_color}">{name} {pct}%</text>')
        cx += 22 + len(f"{name} {pct}%") * 6.6
    return "\n".join(parts)


def build(theme: str) -> str:
    is_dark = theme == "dark"
    suffix = "D" if is_dark else "L"
    accent1 = "#fe702d"
    accent2 = "#fbbf24" if is_dark else "#f59e0b"
    panel_bg_top = "#191410" if is_dark else "#FFFDF9"
    panel_bg_bot = "#0F0B08" if is_dark else "#F5EFE6"
    outer_bg = "#0F0B08" if is_dark else "#FFFFFF"
    topbar_bg = "#231b13" if is_dark else "#F1E9DC"
    divider = "rgba(255,220,180,0.10)" if is_dark else "rgba(50,30,10,0.10)"
    heading_color = "#FBF3E9" if is_dark else "#241a10"
    body_color = "#c9b79b" if is_dark else "#7A6A55"
    label_color = "#e0a066" if is_dark else "#b3651f"
    icon_box_color = "#2A1E12" if is_dark else "#FBF6EF"
    icon_stroke = accent1

    X = 60.0
    PANEL_W = 1080.0
    VAL_X = X + 120

    stack = stack_row(heading_color, icon_box_color, icon_stroke, X)
    extra_stack, extra_h = text_chip_row(EXTRA_STACK_TAGS, X, 250, PANEL_W, icon_box_color, icon_stroke, heading_color)

    # Everything from "NOW BUILDING" down shifts by however tall the wrapped
    # extra-stack block turned out to be, so nothing overlaps. Extra per-
    # section gaps (g1..g4) are added cumulatively so sections breathe
    # instead of feeling stacked on top of each other.
    shift = extra_h + 34
    g1, g2, g3, g4 = 10, 10, 10, 10
    y_now_building = 280 + shift
    y_now_building_1 = 304 + shift
    y_now_building_2 = 324 + shift
    y_contact_label = 365 + shift + g1
    y_contact = [389 + shift + g1, 411 + shift + g1, 433 + shift + g1, 455 + shift + g1, 477 + shift + g1]
    y_credentials_label = 518 + shift + g1 + g2
    y_credentials = 542 + shift + g1 + g2
    y_stats_label = 583 + shift + g1 + g2 + g3
    y_stats = 607 + shift + g1 + g2 + g3
    y_langs_label = 648 + shift + g1 + g2 + g3 + g4
    y_bar = 677 + shift + g1 + g2 + g3 + g4
    y_legend = y_bar + 29

    bar = lang_bar(X, y_bar, PANEL_W, 10)
    legend = lang_legend(X, y_legend, body_color)

    PANEL_H = int(y_legend + 40)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="{PANEL_H}" viewBox="0 0 1180 {PANEL_H}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace" role="img" aria-label="Miguel Granados — profile.sh --live">
<defs>
<linearGradient id="accent{suffix}" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{accent1}"/>
  <stop offset="1" stop-color="{accent2}"/>
</linearGradient>
<linearGradient id="panelGrad{suffix}" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{panel_bg_top}"/>
  <stop offset="1" stop-color="{panel_bg_bot}"/>
</linearGradient>
<filter id="glow{suffix}" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="3"/></filter>
<clipPath id="winClip{suffix}"><rect x="2" y="2" width="1176" height="{PANEL_H - 4}" rx="18"/></clipPath>
<clipPath id="barClip{suffix}"><rect x="{X:.1f}" y="{y_bar:.1f}" width="{PANEL_W:.1f}" height="10" rx="5"/></clipPath>
</defs>
<rect x="2" y="2" width="1176" height="{PANEL_H - 4}" rx="18" fill="{outer_bg}"/>
<g clip-path="url(#winClip{suffix})">
<rect x="2" y="2" width="1176" height="{PANEL_H - 4}" fill="url(#panelGrad{suffix})"/>
<rect x="2" y="2" width="1176" height="46" fill="{topbar_bg}"/>
<line x1="2" y1="48" x2="1178" y2="48" stroke="{divider}"/>
<circle cx="30" cy="25" r="5.5" fill="#ff5f56"/>
<circle cx="50" cy="25" r="5.5" fill="#ffbd2e"/>
<circle cx="70" cy="25" r="5.5" fill="#27c93f"/>
<text x="590" y="29" text-anchor="middle" font-size="12" fill="{body_color}">miguel@ulamander - % ./profile.sh --live</text>

<text x="{X:.1f}" y="110" font-size="34" font-weight="700" fill="{heading_color}">Miguel Granados</text>
<text x="{X:.1f}" y="140" font-size="16" fill="{body_color}">Founder &amp; Engineer @ Ulamander — local-first AI systems</text>

<rect x="{X:.1f}" y="168" width="{PANEL_W:.1f}" height="1.5" fill="url(#accent{suffix})" filter="url(#glow{suffix})"/>

<text x="{X:.1f}" y="200" font-size="13" letter-spacing="2" fill="{label_color}">STACK</text>
<g>
{stack}
</g>
{extra_stack}

<text x="{X:.1f}" y="{y_now_building:.1f}" font-size="13" letter-spacing="2" fill="{label_color}">NOW BUILDING</text>
<text x="{X:.1f}" y="{y_now_building_1:.1f}" font-size="15" fill="{heading_color}">Ulamander-Neural — local AI chat, fine-tuning/</text>
<text x="{X:.1f}" y="{y_now_building_2:.1f}" font-size="15" fill="{heading_color}">distillation panel, multi-board exporter</text>

<text x="{X:.1f}" y="{y_contact_label:.1f}" font-size="13" letter-spacing="2" fill="{label_color}">CONTACT</text>
<text x="{VAL_X:.1f}" y="{y_contact[0]:.1f}" font-size="14" fill="{heading_color}">miguel.ulamander.com</text>
<text x="{VAL_X:.1f}" y="{y_contact[1]:.1f}" font-size="14" fill="{heading_color}">linkedin.com/in/miguel-granados-820b15192</text>
<text x="{VAL_X:.1f}" y="{y_contact[2]:.1f}" font-size="14" fill="{heading_color}">academy.claude.com (Claude Academy)</text>
<text x="{VAL_X:.1f}" y="{y_contact[3]:.1f}" font-size="14" fill="{heading_color}">Google Skillshop — 6x Ads Certified</text>
<text x="{VAL_X:.1f}" y="{y_contact[4]:.1f}" font-size="14" fill="{heading_color}">ulamanderdesing@gmail.com</text>
<text x="{X:.1f}" y="{y_contact[0]:.1f}" font-size="12" fill="{label_color}">Grid.Portfolio</text>
<text x="{X:.1f}" y="{y_contact[1]:.1f}" font-size="12" fill="{label_color}">Grid.LinkedIn</text>
<text x="{X:.1f}" y="{y_contact[2]:.1f}" font-size="12" fill="{label_color}">Grid.Claude</text>
<text x="{X:.1f}" y="{y_contact[3]:.1f}" font-size="12" fill="{label_color}">Grid.Google</text>
<text x="{X:.1f}" y="{y_contact[4]:.1f}" font-size="12" fill="{label_color}">Grid.Mail</text>

<text x="{X:.1f}" y="{y_credentials_label:.1f}" font-size="13" letter-spacing="2" fill="{label_color}">CREDENTIALS</text>
<text x="{X:.1f}" y="{y_credentials:.1f}" font-size="14" fill="{heading_color}">6x Google Ads Certified · 19x Claude Academy · MS Learn Lv.15</text>

<text x="{X:.1f}" y="{y_stats_label:.1f}" font-size="13" letter-spacing="2" fill="{label_color}">GITHUB STATS</text>
<text x="{X:.1f}" y="{y_stats:.1f}" font-size="14" fill="{heading_color}">52 commits · 11 pull requests authored</text>

<text x="{X:.1f}" y="{y_langs_label:.1f}" font-size="13" letter-spacing="2" fill="{label_color}">MOST USED LANGUAGES</text>
<rect x="{X:.1f}" y="{y_bar:.1f}" width="{PANEL_W:.1f}" height="10" rx="5" fill="{icon_box_color}"/>
<g clip-path="url(#barClip{suffix})">
{bar}
</g>
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
