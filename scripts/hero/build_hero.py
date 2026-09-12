"""Assembles the theme-aware hero SVG: one text panel (no photo),
with real tech-logo icons (MIT-licensed, from xandemon/developer-icons).

Design rules:
- One accent (Ulamander orange #fe702d) on a cool slate base — no muddy brown + amber clash.
- Chip widths measured from text length so pills stay even.
- Stats and language % are real GitHub numbers (never inflated).
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
    """Return icon inner markup with ids namespaced so icons can share one SVG."""
    with open(path) as f:
        svg = f.read()
    inner = re.sub(r"^<svg[^>]*>|</svg>\s*$", "", svg.strip())
    ids = set(_ID_RE.findall(inner))
    for old_id in ids:
        new_id = f"ic_{name.lower()}_{old_id}"
        inner = inner.replace(f'id="{old_id}"', f'id="{new_id}"')
        inner = inner.replace(f"url(#{old_id})", f"url(#{new_id})")
    return inner


def measure_text(text: str, font_size: float, mono: bool = True) -> float:
    """Approximate monospace / UI text width for chip layout."""
    # SF Mono-ish average; slightly wider for mixed-case UI labels.
    avg = 0.60 if mono else 0.55
    return len(text) * font_size * avg


def stack_chip(x: float, y: float, w: float, name: str, box_color: str, stroke_color: str, text_color: str) -> str:
    h = 32
    icon_size = 18
    icon_x = x + 12
    icon_y = y + (h - icon_size) / 2
    inner = load_icon_inner(name, ICON_FILES[name])
    return f'''<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="8" fill="{box_color}" stroke="{stroke_color}" stroke-opacity="0.45"/>
<g transform="translate({icon_x:.1f},{icon_y:.1f}) scale({icon_size / 100:.4f})">{inner}</g>
<text x="{x + 12 + icon_size + 8:.1f}" y="{y + h / 2 + 5:.1f}" font-size="13" fill="{text_color}">{name}</text>'''


def stack_row(text_color: str, box_color: str, stroke_color: str, x0: float = 56.0) -> str:
    names = ["Python", "TypeScript", "React", "PostgreSQL", "Azure"]
    # Measured chip widths (icon + padding + label) — even visual rhythm.
    widths = {"Python": 96, "TypeScript": 124, "React": 90, "PostgreSQL": 132, "Azure": 92}
    x = x0
    y = 196.0
    out = []
    for name in names:
        w = widths[name]
        out.append(stack_chip(x, y, w, name, box_color, stroke_color, text_color))
        x += w + 10
    return "\n".join(out)


# From miguel.ulamander.com stack chips (excludes the 5 icon chips above).
EXTRA_STACK_TAGS = [
    "Full Stack", "Node.js", "Docker", "n8n", "Ollama / LLM",
    "Microsoft Sentinel", "Defender XDR", "Fortinet NSE 3", "Oracle Cloud",
    "SC-900", "AI-900", "GDPR", "EU AI Act", "Claude Code", "Shopify",
    "WordPress", "Cloudflare Tunnel",
]


def text_chip_row(
    tags: list[str],
    x0: float,
    y0: float,
    max_w: float,
    box_color: str,
    stroke_color: str,
    text_color: str,
) -> tuple[str, float]:
    """Wrap plain-text chips; return (svg, height used)."""
    h = 28
    pad_x = 14
    gap = 8
    row_gap = 10
    font_size = 12
    x, y = x0, y0
    out = []
    for tag in tags:
        w = pad_x * 2 + measure_text(tag, font_size)
        if x + w > x0 + max_w and x > x0:
            x = x0
            y += h + row_gap
        out.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="7" '
            f'fill="{box_color}" stroke="{stroke_color}" stroke-opacity="0.35"/>'
        )
        out.append(
            f'<text x="{x + w / 2:.1f}" y="{y + h / 2 + 4.2:.1f}" text-anchor="middle" '
            f'font-size="{font_size}" fill="{text_color}">{tag}</text>'
        )
        x += w + gap
    total_h = (y - y0) + h
    return "\n".join(out), total_h


# Real language mix from GitHub GraphQL (owner repos, isFork:false) — 2026-09-12.
# TypeScript 76.3% · Python 12.0% · HTML 5.3% · rest grouped as Other.
LANG_STATS = [
    ("TypeScript", 76, "#3178C6"),
    ("Python", 12, "#3572A5"),
    ("HTML", 5, "#E34C26"),
    ("Other", 7, "#64748B"),
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
        label = f"{name} {pct}%"
        parts.append(f'<text x="{cx + 10:.1f}" y="{y:.1f}" font-size="12" fill="{text_color}">{label}</text>')
        cx += 22 + measure_text(label, 12) + 16
    return "\n".join(parts)


def build(theme: str) -> str:
    is_dark = theme == "dark"
    suffix = "D" if is_dark else "L"

    # Cohesive Ulamander palette: cool slate + single orange accent.
    accent = "#fe702d"
    accent_soft = "#ff8a4c" if is_dark else "#e85d1c"
    outer_bg = "#0B1220" if is_dark else "#FFFFFF"
    panel_bg_top = "#111827" if is_dark else "#FFFBF7"
    panel_bg_bot = "#0B1220" if is_dark else "#F8FAFC"
    topbar_bg = "#0F172A" if is_dark else "#F1F5F9"
    divider = "rgba(148,163,184,0.18)" if is_dark else "rgba(15,23,42,0.10)"
    heading_color = "#F8FAFC" if is_dark else "#0F172A"
    body_color = "#94A3B8" if is_dark else "#64748B"
    label_color = accent
    chip_bg = "#1E293B" if is_dark else "#FFFFFF"
    chip_stroke = accent

    X = 56.0
    PANEL_W = 1068.0
    VAL_X = X + 118

    stack = stack_row(heading_color, chip_bg, chip_stroke, X)
    extra_stack, extra_h = text_chip_row(
        EXTRA_STACK_TAGS, X, 240, PANEL_W, chip_bg, chip_stroke, heading_color
    )

    shift = extra_h + 28
    g = 14
    y_now = 268 + shift
    y_now_1 = 292 + shift
    y_now_2 = 312 + shift
    y_contact_label = 348 + shift + g
    y_contact = [
        372 + shift + g,
        394 + shift + g,
        416 + shift + g,
        438 + shift + g,
        460 + shift + g,
    ]
    y_cred_label = 496 + shift + 2 * g
    y_cred = 520 + shift + 2 * g
    y_stats_label = 556 + shift + 3 * g
    y_stats = 580 + shift + 3 * g
    y_langs_label = 616 + shift + 4 * g
    y_bar = 642 + shift + 4 * g
    y_legend = y_bar + 28

    bar = lang_bar(X, y_bar, PANEL_W, 10)
    legend = lang_legend(X, y_legend, body_color)
    PANEL_H = int(y_legend + 36)

    # Real counts from GitHub Search API (2026-09-12): commits=73, PRs authored=21.
    github_stats_line = "73 commits · 21 pull requests authored"

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="{PANEL_H}" viewBox="0 0 1180 {PANEL_H}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace" role="img" aria-label="Miguel Granados — profile.sh --live">
<defs>
<linearGradient id="accent{suffix}" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{accent}"/>
  <stop offset="1" stop-color="{accent_soft}"/>
</linearGradient>
<linearGradient id="panelGrad{suffix}" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{panel_bg_top}"/>
  <stop offset="1" stop-color="{panel_bg_bot}"/>
</linearGradient>
<clipPath id="winClip{suffix}"><rect x="2" y="2" width="1176" height="{PANEL_H - 4}" rx="16"/></clipPath>
<clipPath id="barClip{suffix}"><rect x="{X:.1f}" y="{y_bar:.1f}" width="{PANEL_W:.1f}" height="10" rx="5"/></clipPath>
</defs>
<rect x="2" y="2" width="1176" height="{PANEL_H - 4}" rx="16" fill="{outer_bg}"/>
<g clip-path="url(#winClip{suffix})">
<rect x="2" y="2" width="1176" height="{PANEL_H - 4}" fill="url(#panelGrad{suffix})"/>
<rect x="2" y="2" width="1176" height="44" fill="{topbar_bg}"/>
<line x1="2" y1="46" x2="1178" y2="46" stroke="{divider}"/>
<circle cx="28" cy="23" r="5" fill="#FF5F56"/>
<circle cx="48" cy="23" r="5" fill="#FFBD2E"/>
<circle cx="68" cy="23" r="5" fill="#27C93F"/>
<text x="590" y="28" text-anchor="middle" font-size="12" fill="{body_color}">miguel@ulamander — % ./profile.sh --live</text>

<text x="{X:.1f}" y="98" font-size="32" font-weight="700" fill="{heading_color}">Miguel Granados</text>
<text x="{X:.1f}" y="126" font-size="15" fill="{body_color}">Tecnico in Sviluppo di IA · Founder &amp; Engineer @ Ulamander</text>
<text x="{X:.1f}" y="148" font-size="13" fill="{body_color}">Full Stack · local-first AI · cloud security · Torino, Italy</text>

<rect x="{X:.1f}" y="166" width="{PANEL_W:.1f}" height="2" rx="1" fill="url(#accent{suffix})"/>

<text x="{X:.1f}" y="188" font-size="12" letter-spacing="2.5" fill="{label_color}">STACK</text>
<g>
{stack}
</g>
{extra_stack}

<text x="{X:.1f}" y="{y_now:.1f}" font-size="12" letter-spacing="2.5" fill="{label_color}">NOW BUILDING</text>
<text x="{X:.1f}" y="{y_now_1:.1f}" font-size="14" fill="{heading_color}">Ulamander-Neural — local AI chat, fine-tuning / distillation</text>
<text x="{X:.1f}" y="{y_now_2:.1f}" font-size="14" fill="{heading_color}">panel (QLoRA), multi-board exporter (Pi · ESP32 · Arduino)</text>

<text x="{X:.1f}" y="{y_contact_label:.1f}" font-size="12" letter-spacing="2.5" fill="{label_color}">CONTACT</text>
<text x="{X:.1f}" y="{y_contact[0]:.1f}" font-size="12" fill="{label_color}">Portfolio</text>
<text x="{X:.1f}" y="{y_contact[1]:.1f}" font-size="12" fill="{label_color}">LinkedIn</text>
<text x="{X:.1f}" y="{y_contact[2]:.1f}" font-size="12" fill="{label_color}">Claude</text>
<text x="{X:.1f}" y="{y_contact[3]:.1f}" font-size="12" fill="{label_color}">Google</text>
<text x="{X:.1f}" y="{y_contact[4]:.1f}" font-size="12" fill="{label_color}">Email</text>
<text x="{VAL_X:.1f}" y="{y_contact[0]:.1f}" font-size="13" fill="{heading_color}">miguel.ulamander.com</text>
<text x="{VAL_X:.1f}" y="{y_contact[1]:.1f}" font-size="13" fill="{heading_color}">linkedin.com/in/miguel-granados-820b15192</text>
<text x="{VAL_X:.1f}" y="{y_contact[2]:.1f}" font-size="13" fill="{heading_color}">academy.claude.com — 19 badges</text>
<text x="{VAL_X:.1f}" y="{y_contact[3]:.1f}" font-size="13" fill="{heading_color}">Google Skillshop — 11 certifications</text>
<text x="{VAL_X:.1f}" y="{y_contact[4]:.1f}" font-size="13" fill="{heading_color}">info@ulamander.com</text>

<text x="{X:.1f}" y="{y_cred_label:.1f}" font-size="12" letter-spacing="2.5" fill="{label_color}">CREDENTIALS</text>
<text x="{X:.1f}" y="{y_cred:.1f}" font-size="13" fill="{heading_color}">11× Google · 19× Claude Academy · MS Learn Lv.15 · Fortinet NSE 3 · OCI Foundations</text>

<text x="{X:.1f}" y="{y_stats_label:.1f}" font-size="12" letter-spacing="2.5" fill="{label_color}">GITHUB STATS</text>
<text x="{X:.1f}" y="{y_stats:.1f}" font-size="13" fill="{heading_color}">{github_stats_line}</text>

<text x="{X:.1f}" y="{y_langs_label:.1f}" font-size="12" letter-spacing="2.5" fill="{label_color}">MOST USED LANGUAGES</text>
<rect x="{X:.1f}" y="{y_bar:.1f}" width="{PANEL_W:.1f}" height="10" rx="5" fill="{chip_bg}"/>
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
