"""Hero SVG — valid XML only (escape & < > '). No fake buttons.

Single unified card: terminal window chrome (traffic lights + topbar) exists
ONCE, at the very top. Stack and credentials are sections within this same
card (previously two separate "insignia" SVGs with their own window chrome —
merged here so the profile reads as one continuous surface instead of
several stacked windows)."""
import base64
import html
import re

import dot_portrait

ICON_DIR = "icons"
BADGE_ICON_DIR = "badge-icons"
_ID_RE = re.compile(r'id="([^"]+)"')
_VIEWBOX_RE = re.compile(r'viewBox="([-\d.]+)\s+([-\d.]+)\s+([\d.]+)\s+([\d.]+)"')


def ulamander_logo_b64() -> str:
    with open("ulamander-logo.png", "rb") as f:
        return base64.b64encode(f.read()).decode()


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def load_icon(name: str, path: str) -> tuple[str, float, float, float, float]:
    """Returns (inner_markup, min_x, min_y, width, height) from the icon's own
    viewBox — source icons use wildly different viewBoxes (24x24, 100x100,
    228x120, ...), so callers must scale/center against the icon's own
    dimensions rather than assuming a fixed square."""
    with open(path) as f:
        svg = f.read()
    m = _VIEWBOX_RE.search(svg)
    vx, vy, vw, vh = (float(g) for g in m.groups()) if m else (0.0, 0.0, 100.0, 100.0)
    inner = re.sub(r"^<svg[^>]*>|</svg>\s*$", "", svg.strip())
    for old_id in set(_ID_RE.findall(inner)):
        new_id = f"ic_{name}_{old_id}"
        inner = inner.replace(f'id="{old_id}"', f'id="{new_id}"')
        inner = inner.replace(f"url(#{old_id})", f"url(#{new_id})")
    return inner, vx, vy, vw, vh


def icon_group(path: str, key: str, box_x: float, box_y: float, size: float) -> str:
    """Places an icon's own artwork, scaled to fit `size` and centered in a
    `size`x`size` box at (box_x, box_y), regardless of its native viewBox."""
    inner, vx, vy, vw, vh = load_icon(key, path)
    scale = size / max(vw, vh)
    ox = box_x + (size - vw * scale) / 2 - vx * scale
    oy = box_y + (size - vh * scale) / 2 - vy * scale
    return f'<g transform="translate({ox:.2f},{oy:.2f}) scale({scale:.4f})">{inner}</g>'


def stack_chip(x, y, w, name, icon_path, brand, box, text_c) -> str:
    h, icon = 36, 18
    key = re.sub(r"[^a-z0-9]+", "", name.lower())
    icon_svg = icon_group(icon_path, key, x + 12, y + (h - icon) / 2, icon)
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="10" '
        f'fill="{box}" stroke="{brand}" stroke-opacity="0.55" stroke-width="1.5"/>\n'
        f'{icon_svg}\n'
        f'<text x="{x + 38:.1f}" y="{y + h / 2 + 5:.1f}" font-size="13" font-weight="600" fill="{text_c}">{esc(name)}</text>'
    )


def credential_pill(x, y, w, label, icon_path, box, border, text_c) -> str:
    h, icon = 30, 16
    key = re.sub(r"[^a-z0-9]+", "", label.lower())
    icon_svg = icon_group(icon_path, key, x + 11, y + (h - icon) / 2, icon)
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="15" '
        f'fill="{box}" stroke="{border}" stroke-width="1"/>\n'
        f'{icon_svg}\n'
        f'<text x="{x + 33:.1f}" y="{y + h / 2 + 4.5:.1f}" font-size="11.5" font-weight="600" fill="{text_c}">{esc(label)}</text>'
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
    cred_bg = "rgba(254,112,45,0.14)" if dark else "rgba(234,88,12,0.10)"
    cred_stroke = "rgba(254,112,45,0.45)" if dark else "rgba(234,88,12,0.35)"

    # CORE STACK — real languages/frameworks + the automation layer (n8n),
    # which used to live in a separate, now-retired "Focus Stack" card.
    stack_items = [
        ("Python", f"{ICON_DIR}/python.svg", "#3776AB", 102),
        ("TypeScript", f"{ICON_DIR}/typescript.svg", "#3178C6", 130),
        ("React", f"{ICON_DIR}/reactjs.svg", "#61DAFB", 96),
        ("PostgreSQL", f"{ICON_DIR}/postgresql.svg", "#4169E1", 138),
        ("Azure", f"{ICON_DIR}/azure.svg", "#0078D4", 98),
        ("n8n", f"{BADGE_ICON_DIR}/n8n.svg", "#EA4B71", 72),
    ]
    x, chips = 56.0, []
    for name, path, brand, w in stack_items:
        chips.append(stack_chip(x, 248, w, name, path, brand, chip, heading))
        x += w + 12
    stack = "\n".join(chips)

    # CREDENTIALS — real icon pills (previously the separate
    # insignia-credentials-*.svg card); same content, one less window.
    cred_items = [
        ("100+ Badges", f"{BADGE_ICON_DIR}/github-dark.svg", 118),
        ("MS Learn Lv.15", f"{BADGE_ICON_DIR}/microsoft.svg", 138),
        ("Claude Academy 19", f"{BADGE_ICON_DIR}/claude-ai.svg", 158),
        ("Google Skillshop 11", f"{BADGE_ICON_DIR}/google.svg", 168),
        ("Fortinet NSE 3", f"{BADGE_ICON_DIR}/fortinet.svg", 140),
        ("OCI Foundations", f"{BADGE_ICON_DIR}/oracle.svg", 148),
    ]
    cx, cy, cred_svg = 56.0, 308.0, []
    for label, path, w in cred_items:
        if cx + w > 850:
            cx = 56.0
            cy += 40
        cred_svg.append(credential_pill(cx, cy, w, label, path, cred_bg, cred_stroke, pill_tx if dark else "#9A3412"))
        cx += w + 10
    credentials = "\n".join(cred_svg)
    cred_rows = 2 if cy > 308 else 1
    footer_y = cy + 50

    # Portrait: right-aligned column (x=900..1124) spanning most of the card
    # height, clear of every other element (stack/credential rows end around
    # x=850) — a stippled dot cloud with a staggered reveal animation,
    # matching arifhaxn's VISUAL.MAP technique (confirmed by inspecting his
    # live profile's rendered SVG directly).
    PX, PY, PW = 900.0, 50.0, 224.0
    PH = footer_y - PY - 18
    portrait_dots = dot_portrait.build("avatar.png", accent, PW, PH)
    portrait = f'''<clipPath id="pf{s}"><rect x="{PX}" y="{PY}" width="{PW}" height="{PH:.1f}" rx="14"/></clipPath>
<rect x="{PX}" y="{PY}" width="{PW}" height="{PH:.1f}" rx="14" fill="{'#0A1020' if dark else '#F8FAFC'}" stroke="{accent}" stroke-opacity="0.35"/>
<g clip-path="url(#pf{s})">
<g transform="translate({PX},{PY})">
{portrait_dots}
</g>
</g>'''

    H = int(footer_y + 30)
    logo_b64 = ulamander_logo_b64()
    line1 = esc("Founder & CEO, Ulamander · AI Development Technician · Full Stack")
    line2 = esc("I turn complex processes into intelligent AI-driven systems · Turin, Italy")
    footer = esc("Real production systems · Web · App · Neural · CRM · Automation · Security-first")

    # Mobile (<=480 CSS px render width): this banner is always width=100%, so on a
    # phone it renders at ~1/3 of its desktop width — anything below hides the
    # secondary rows (terminal bar, stack chips, credential pills, footer) instead of
    # just shrinking them illegibly, and enlarges + recenters the core identity text
    # (name, role, tagline, availability badge) in the freed vertical space.
    # NOTE: this @media rule only reaches elements when the SVG is rendered as its
    # own document/inline (e.g. opened directly) — most browsers do NOT evaluate it
    # against the display size when the SVG is loaded via <img>, which is how GitHub
    # embeds it. The README's actual mobile fix is a separate, smaller hero-mobile.svg
    # selected via a width-based <picture><source media> at the markdown level (see
    # build_hero_mobile() below) — this in-SVG rule is kept only as a harmless no-op
    # fallback for contexts that do honor it (e.g. the raw file opened directly).
    style = f'''<style>
  .m-hide {{ }}
  .m-shift {{ }}
  @media (max-width: 480px) {{
    .m-hide {{ display: none; }}
    .m-shift {{ transform: translateY(70px); }}
    .m-name {{ font-size: 64px; }}
    .m-line1 {{ font-size: 26px; }}
    .m-line2 {{ font-size: 21px; }}
    .m-badge-text {{ font-size: 18px; }}
    .m-badge-bg {{ width: 280px; height: 38px; }}
    .m-badge-dot {{ r: 7px; }}
  }}
</style>'''

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 1180 {H}" preserveAspectRatio="xMidYMid meet" font-family="ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif" role="img" aria-label="Miguel Granados">
{style}
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
<g class="m-hide">
<rect x="2" y="2" width="1176" height="42" fill="{'#0A1020' if dark else '#EEF2FF'}" fill-opacity="0.85"/>
<circle cx="28" cy="23" r="5" fill="#FF5F56"/>
<circle cx="48" cy="23" r="5" fill="#FFBD2E"/>
<circle cx="68" cy="23" r="5" fill="#27C93F"/>
<text x="590" y="27" text-anchor="middle" font-size="12" font-family="ui-monospace,Menlo,monospace" fill="{muted}">miguel@ulamander — production systems</text>
</g>
<g class="m-shift">
<rect class="m-badge-bg" x="56" y="64" width="188" height="26" rx="13" fill="{pill_bg}"/>
<circle class="m-badge-dot" cx="74" cy="77" r="5" fill="#22C55E"/>
<text class="m-badge-text" x="88" y="81" font-size="12" font-weight="600" fill="{pill_tx}">Available for projects</text>
<image href="data:image/png;base64,{logo_b64}" xlink:href="data:image/png;base64,{logo_b64}" x="264" y="65" width="19" height="22"/>
<text x="291" y="82" font-size="14" font-weight="700" letter-spacing="1.5" fill="{heading}">ULAMANDER</text>
<text class="m-name" x="56" y="128" font-size="42" font-weight="800" fill="url(#name{s})">Miguel Granados</text>
<text class="m-line1" x="56" y="160" font-size="16" fill="{body}">{line1}</text>
<text class="m-line2" x="56" y="184" font-size="14" fill="{muted}">{line2}</text>
</g>
<g class="m-hide">
<rect x="56" y="202" width="1068" height="3" rx="1.5" fill="url(#bar{s})"/>
<text x="56" y="232" font-size="11" letter-spacing="2.5" font-weight="700" fill="{accent}">CORE STACK</text>
{stack}
<text x="56" y="300" font-size="11" letter-spacing="2.5" font-weight="700" fill="{accent}">CREDENTIALS</text>
{credentials}
<text x="56" y="{footer_y:.1f}" font-size="12" fill="{muted}">{footer}</text>
{portrait}
</g>
</g>
</svg>
'''


def build_mobile(theme: str) -> str:
    """Compact vertical card for narrow viewports. The desktop build()'s
    internal @media rule doesn't reliably fire once the SVG is embedded via
    <img> in the README (confirmed on the live GitHub page: content was
    overflowing/cut off on an actual phone-width load) — <picture><source
    media> at the README/markdown level is what browsers DO honor
    reliably, so this is a genuinely separate, smaller rendering instead of
    a CSS-hidden subset of the desktop one."""
    dark = theme == "dark"
    s = "DM" if dark else "LM"
    accent, soft = "#fe702d", "#fbbf24"
    outer = "#070B14" if dark else "#FFFFFF"
    panel_a = "#121A2B" if dark else "#FFF8F2"
    panel_b = "#0B1220" if dark else "#F1F5F9"
    heading = "#F8FAFC" if dark else "#0F172A"
    body = "#A8B3C7" if dark else "#475569"
    muted = "#64748B"
    pill_bg = "#243049" if dark else "#FFE8D6"
    pill_tx = "#FDE68A" if dark else "#9A3412"

    W, H = 600, 280
    line1 = esc("Founder & CEO, Ulamander · AI Development Technician · Full Stack")
    line2 = esc("I turn complex processes into intelligent AI-driven systems · Turin, Italy")
    creds = esc("100+ badges · 19 Claude Academy · MS Learn Lv.15 · Fortinet NSE 3")

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid meet" font-family="ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif" role="img" aria-label="Miguel Granados">
<defs>
<linearGradient id="bg{s}" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="{panel_a}"/><stop offset="1" stop-color="{panel_b}"/>
</linearGradient>
<linearGradient id="name{s}" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{heading}"/><stop offset="0.6" stop-color="{heading}"/><stop offset="1" stop-color="{accent}"/>
</linearGradient>
<linearGradient id="bar{s}" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{accent}"/><stop offset="0.5" stop-color="{soft}"/><stop offset="1" stop-color="#38BDF8"/>
</linearGradient>
<radialGradient id="glow{s}" cx="85%" cy="15%" r="55%">
  <stop offset="0" stop-color="{accent}" stop-opacity="0.26"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/>
</radialGradient>
<clipPath id="win{s}"><rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="18"/></clipPath>
</defs>
<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="18" fill="{outer}"/>
<g clip-path="url(#win{s})">
<rect x="2" y="2" width="{W - 4}" height="{H - 4}" fill="url(#bg{s})"/>
<rect x="2" y="2" width="{W - 4}" height="{H - 4}" fill="url(#glow{s})"/>
<rect x="2" y="2" width="{W - 4}" height="40" fill="{'#0A1020' if dark else '#EEF2FF'}" fill-opacity="0.85"/>
<circle cx="24" cy="21" r="5" fill="#FF5F56"/>
<circle cx="42" cy="21" r="5" fill="#FFBD2E"/>
<circle cx="60" cy="21" r="5" fill="#27C93F"/>
<text x="{W / 2:.0f}" y="25" text-anchor="middle" font-size="11" font-family="ui-monospace,Menlo,monospace" fill="{muted}">miguel@ulamander</text>
<rect x="32" y="64" width="188" height="26" rx="13" fill="{pill_bg}"/>
<circle cx="50" cy="77" r="5" fill="#22C55E"/>
<text x="64" y="81" font-size="12" font-weight="600" fill="{pill_tx}">Available for projects</text>
<text x="32" y="130" font-size="38" font-weight="800" fill="url(#name{s})">Miguel Granados</text>
<text x="32" y="160" font-size="15" fill="{body}">{line1}</text>
<text x="32" y="182" font-size="13" fill="{muted}">{line2}</text>
<rect x="32" y="206" width="{W - 64}" height="2" rx="1" fill="url(#bar{s})"/>
<text x="32" y="236" font-size="12" fill="{muted}">{creds}</text>
<text x="32" y="262" font-size="11" fill="{muted}">Real production systems · Web · App · CRM · Automation</text>
</g>
</svg>
'''


if __name__ == "__main__":
    open("dark.svg", "w").write(build("dark"))
    open("light.svg", "w").write(build("light"))
    open("dark-mobile.svg", "w").write(build_mobile("dark"))
    open("light-mobile.svg", "w").write(build_mobile("light"))
    from xml.etree import ElementTree as ET
    for f in ["dark.svg", "light.svg", "dark-mobile.svg", "light-mobile.svg"]:
        ET.parse(f)
    print("wrote + validated dark.svg, light.svg, dark-mobile.svg, light-mobile.svg")
