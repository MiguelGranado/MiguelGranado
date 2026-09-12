"""Hero SVG compatto: nome + ruolo + core stack. Niente lingue, niente CONTACT."""
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
    h, icon_size = 36, 18
    inner = load_icon_inner(name, ICON_FILES[name])
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="9" '
        f'fill="{box_color}" stroke="{stroke_color}" stroke-opacity="0.45"/>\n'
        f'<g transform="translate({x + 12:.1f},{y + (h - icon_size) / 2:.1f}) '
        f'scale({icon_size / 100:.4f})">{inner}</g>\n'
        f'<text x="{x + 38:.1f}" y="{y + h / 2 + 5:.1f}" font-size="13" fill="{text_color}">{name}</text>'
    )


def stack_row(text_color, box_color, stroke_color, x0=56.0, y=176.0) -> str:
    widths = {"Python": 100, "TypeScript": 128, "React": 94, "PostgreSQL": 136, "Azure": 96}
    x, out = x0, []
    for name in ["Python", "TypeScript", "React", "PostgreSQL", "Azure"]:
        w = widths[name]
        out.append(stack_chip(x, y, w, name, box_color, stroke_color, text_color))
        x += w + 12
    return "\n".join(out)


def build(theme: str) -> str:
    is_dark = theme == "dark"
    s = "D" if is_dark else "L"
    accent = "#fe702d"
    soft = "#ff8a4c" if is_dark else "#e85d1c"
    outer = "#0B1220" if is_dark else "#FFFFFF"
    top = "#111827" if is_dark else "#FFFBF7"
    bot = "#0B1220" if is_dark else "#F8FAFC"
    bar = "#0F172A" if is_dark else "#F1F5F9"
    div = "rgba(148,163,184,0.18)" if is_dark else "rgba(15,23,42,0.10)"
    heading = "#F8FAFC" if is_dark else "#0F172A"
    body = "#94A3B8" if is_dark else "#64748B"
    chip = "#1E293B" if is_dark else "#FFFFFF"

    X, W = 56.0, 1068.0
    PANEL_H = 280
    stack = stack_row(heading, chip, accent, X, 176)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="{PANEL_H}" viewBox="0 0 1180 {PANEL_H}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace" role="img" aria-label="Miguel Granados">
<defs>
<linearGradient id="a{s}" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{accent}"/><stop offset="1" stop-color="{soft}"/>
</linearGradient>
<linearGradient id="p{s}" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bot}"/>
</linearGradient>
<clipPath id="w{s}"><rect x="2" y="2" width="1176" height="{PANEL_H - 4}" rx="16"/></clipPath>
</defs>
<rect x="2" y="2" width="1176" height="{PANEL_H - 4}" rx="16" fill="{outer}"/>
<g clip-path="url(#w{s})">
<rect x="2" y="2" width="1176" height="{PANEL_H - 4}" fill="url(#p{s})"/>
<rect x="2" y="2" width="1176" height="44" fill="{bar}"/>
<line x1="2" y1="46" x2="1178" y2="46" stroke="{div}"/>
<circle cx="28" cy="23" r="5" fill="#FF5F56"/>
<circle cx="48" cy="23" r="5" fill="#FFBD2E"/>
<circle cx="68" cy="23" r="5" fill="#27C93F"/>
<text x="590" y="28" text-anchor="middle" font-size="12" fill="{body}">miguel@ulamander — profile</text>

<text x="{X:.1f}" y="100" font-size="36" font-weight="700" fill="{heading}">Miguel Granados</text>
<text x="{X:.1f}" y="130" font-size="16" fill="{body}">Tecnico in Sviluppo di Intelligenza Artificiale · Founder @ Ulamander</text>
<text x="{X:.1f}" y="154" font-size="13" fill="{body}">Full Stack · AI / LLM · Cloud &amp; DevOps · Automazione · Sicurezza · Torino, Italia</text>
<rect x="{X:.1f}" y="166" width="{W:.1f}" height="2" rx="1" fill="url(#a{s})"/>
{stack}
<text x="{X:.1f}" y="246" font-size="12" fill="{body}">100+ badge &amp; cert · MS Learn Lv.15 · 19 Claude Academy · 11 Google · Fortinet NSE 3 · OCI Foundations</text>
</g>
</svg>
'''


if __name__ == "__main__":
    open("dark.svg", "w").write(build("dark"))
    open("light.svg", "w").write(build("light"))
    print("wrote dark.svg and light.svg")
