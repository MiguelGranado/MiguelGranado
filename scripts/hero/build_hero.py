"""Hero SVG — valid XML only (escape & < > '). No fake buttons."""
import html
import re

ICON_FILES = {
    "Python": ("icons/python.svg", "#3776AB"),
    "TypeScript": ("icons/typescript.svg", "#3178C6"),
    "React": ("icons/reactjs.svg", "#61DAFB"),
    "PostgreSQL": ("icons/postgresql.svg", "#4169E1"),
    "Azure": ("icons/azure.svg", "#0078D4"),
}
_ID_RE = re.compile(r'id="([^"]+)"')


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def load_icon_inner(name: str, path: str) -> str:
    with open(path) as f:
        svg = f.read()
    inner = re.sub(r"^<svg[^>]*>|</svg>\s*$", "", svg.strip())
    for old_id in set(_ID_RE.findall(inner)):
        new_id = f"ic_{name.lower()}_{old_id}"
        inner = inner.replace(f'id="{old_id}"', f'id="{new_id}"')
        inner = inner.replace(f"url(#{old_id})", f"url(#{new_id})")
    return inner


def stack_chip(x, y, w, name, box, text_c) -> str:
    path, brand = ICON_FILES[name]
    h, icon = 36, 18
    inner = load_icon_inner(name, path)
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="10" '
        f'fill="{box}" stroke="{brand}" stroke-opacity="0.55" stroke-width="1.5"/>\n'
        f'<g transform="translate({x + 12:.1f},{y + (h - icon) / 2:.1f}) scale({icon / 100:.4f})">{inner}</g>\n'
        f'<text x="{x + 38:.1f}" y="{y + h / 2 + 5:.1f}" font-size="13" font-weight="600" fill="{text_c}">{esc(name)}</text>'
    )


def pill(x, y, w, label, fill, text_c) -> str:
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="28" rx="14" fill="{fill}"/>'
        f'<text x="{x + w / 2:.1f}" y="{y + 18:.1f}" text-anchor="middle" font-size="11" '
        f'font-weight="600" fill="{text_c}">{esc(label)}</text>'
    )


def build(theme: str) -> str:
    dark = theme == "dark"
    s = "D" if dark else "L"
    accent, soft = "#fe702d", "#fbbf24"
    outer = "#070B14" if dark else "#FFFFFF"
    panel_a = "#121A2B" if dark else "#FFF8F2"
    panel_b = "#0B1220" if dark else "#F1F5F9"
    heading = "#F8FAFC" if dark else "#0F172A"
    body = "#A8B3C7" if dark else "#475569"
    muted = "#64748B"
    chip = "#1A2336" if dark else "#FFFFFF"
    pill_bg = "#243049" if dark else "#FFE8D6"
    pill_tx = "#FDE68A" if dark else "#9A3412"

    widths = {"Python": 102, "TypeScript": 130, "React": 96, "PostgreSQL": 138, "Azure": 98}
    x, chips = 56.0, []
    for name, w in widths.items():
        chips.append(stack_chip(x, 248, w, name, chip, heading))
        x += w + 12
    stack = "\n".join(chips)

    metrics = [
        "100+ Badges & Certs",
        "MS Learn Lv.15",
        "19 Claude Academy",
        "11 Google",
        "Fortinet NSE 3",
        "OCI Foundations",
    ]
    metric_svg, mx = [], 56.0
    for label in metrics:
        w = 18 + len(label) * 7.0
        metric_svg.append(pill(mx, 308, w, label, pill_bg, pill_tx))
        mx += w + 10

    H = 380
    line1 = esc("AI Development Technician · Full Stack · Founder of Ulamander")
    line2 = esc("I turn complex processes into intelligent AI-driven systems · Turin, Italy")
    footer = esc("Real production systems · Web · App · Neural · CRM · Automation · Security-first")

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="{H}" viewBox="0 0 1180 {H}" font-family="ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif" role="img" aria-label="Miguel Granados">
<defs>
<linearGradient id="bg{s}" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="{panel_a}"/><stop offset="1" stop-color="{panel_b}"/>
</linearGradient>
<linearGradient id="name{s}" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{heading}"/><stop offset="0.55" stop-color="{heading}"/><stop offset="1" stop-color="{accent}"/>
</linearGradient>
<linearGradient id="bar{s}" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{accent}"/><stop offset="0.5" stop-color="{soft}"/><stop offset="1" stop-color="#38BDF8"/>
</linearGradient>
<radialGradient id="glow{s}" cx="85%" cy="20%" r="45%">
  <stop offset="0" stop-color="{accent}" stop-opacity="0.28"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/>
</radialGradient>
<radialGradient id="glow2{s}" cx="15%" cy="80%" r="40%">
  <stop offset="0" stop-color="#38BDF8" stop-opacity="0.18"/><stop offset="1" stop-color="#38BDF8" stop-opacity="0"/>
</radialGradient>
<clipPath id="win{s}"><rect x="2" y="2" width="1176" height="{H - 4}" rx="18"/></clipPath>
</defs>
<rect x="2" y="2" width="1176" height="{H - 4}" rx="18" fill="{outer}"/>
<g clip-path="url(#win{s})">
<rect x="2" y="2" width="1176" height="{H - 4}" fill="url(#bg{s})"/>
<rect x="2" y="2" width="1176" height="{H - 4}" fill="url(#glow{s})"/>
<rect x="2" y="2" width="1176" height="{H - 4}" fill="url(#glow2{s})"/>
<rect x="2" y="2" width="1176" height="42" fill="{'#0A1020' if dark else '#EEF2FF'}" fill-opacity="0.85"/>
<circle cx="28" cy="23" r="5" fill="#FF5F56"/>
<circle cx="48" cy="23" r="5" fill="#FFBD2E"/>
<circle cx="68" cy="23" r="5" fill="#27C93F"/>
<text x="590" y="27" text-anchor="middle" font-size="12" font-family="ui-monospace,Menlo,monospace" fill="{muted}">miguel@ulamander — production systems</text>
<rect x="56" y="64" width="188" height="26" rx="13" fill="{pill_bg}"/>
<circle cx="74" cy="77" r="5" fill="#22C55E"/>
<text x="88" y="81" font-size="12" font-weight="600" fill="{pill_tx}">Available for projects</text>
<text x="56" y="128" font-size="42" font-weight="800" fill="url(#name{s})">Miguel Granados</text>
<text x="56" y="160" font-size="16" fill="{body}">{line1}</text>
<text x="56" y="184" font-size="14" fill="{muted}">{line2}</text>
<rect x="56" y="202" width="1068" height="3" rx="1.5" fill="url(#bar{s})"/>
<text x="56" y="232" font-size="11" letter-spacing="2.5" font-weight="700" fill="{accent}">CORE STACK</text>
{stack}
<text x="56" y="300" font-size="11" letter-spacing="2.5" font-weight="700" fill="{accent}">CREDENTIALS</text>
{chr(10).join(metric_svg)}
<text x="56" y="360" font-size="12" fill="{muted}">{footer}</text>
</g>
</svg>
'''


if __name__ == "__main__":
    open("dark.svg", "w").write(build("dark"))
    open("light.svg", "w").write(build("light"))
    from xml.etree import ElementTree as ET
    ET.parse("dark.svg")
    ET.parse("light.svg")
    print("wrote + validated dark.svg and light.svg")
