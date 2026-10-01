"""About Me card — same visual language as build_hero.py (colors, fonts,
window chrome) so it reads as part of the same design system instead of a
plain markdown section sitting under a polished SVG hero."""
import html

ACCENT, SOFT = "#fe702d", "#fbbf24"

DELIVER = [
    ("Real systems", "Web, App, Neural, CRM and corporate mail already in production"),
    ("Full Stack + AI", "React/TypeScript, Node, Postgres, local LLMs (Ollama) and n8n agents"),
    ("Security-first", "Azure/Sentinel, Fortinet, DNS/SPF/DKIM and operational hardening"),
    ("End-to-end", "From idea to deploy without splitting the project"),
]


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def deliver_card(x, y, w, h, title, desc, accent, box, text_c, body_c) -> str:
    # word-wrap desc at ~34 chars/line for this card width
    words, lines, cur = desc.split(), [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if len(trial) > 34:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    desc_svg = "\n".join(
        f'<text x="{x + 18:.1f}" y="{y + 54 + i * 18:.1f}" font-size="12.5" fill="{body_c}">{esc(line)}</text>'
        for i, line in enumerate(lines)
    )
    return f'''<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="12" fill="{box}" stroke="{accent}" stroke-opacity="0.3" stroke-width="1.2"/>
<rect x="{x + 18:.1f}" y="{y + 20:.1f}" width="8" height="8" rx="2" fill="{accent}" transform="rotate(45 {x + 22:.1f} {y + 24:.1f})"/>
<text x="{x + 36:.1f}" y="{y + 28:.1f}" font-size="14.5" font-weight="700" fill="{text_c}">{esc(title)}</text>
{desc_svg}'''


def build(theme: str) -> str:
    dark = theme == "dark"
    s = "A" + ("D" if dark else "L")
    outer = "#070B14" if dark else "#FFFFFF"
    panel_a = "#121A2B" if dark else "#FFF8F2"
    panel_b = "#0B1220" if dark else "#F1F5F9"
    heading = "#F8FAFC" if dark else "#0F172A"
    body = "#A8B3C7" if dark else "#475569"
    muted = "#64748B"
    box = "#1A2336" if dark else "#FFFFFF"
    quote_bg = "#17213A" if dark else "#FFF4EC"

    W = 1180
    GAP, X0, CONTENT_W = 20.0, 56.0, 1068.0
    CARD_W = (CONTENT_W - GAP) / 2
    cards = []
    for i, (title, desc) in enumerate(DELIVER):
        col, row = i % 2, i // 2
        cx = X0 + col * (CARD_W + GAP)
        cy = 332.0 + row * 116.0
        cards.append(deliver_card(cx, cy, CARD_W, 100.0, title, desc, ACCENT, box, heading, body))
    cards_svg = "\n".join(cards)

    H = 616
    intro1 = esc("Founder of Ulamander — AI Development Technician & Full Stack Engineer.")
    intro2 = esc("Same profile as miguel.ulamander.com.")
    quote1 = esc("I turn complex processes into intelligent AI-driven systems.")
    quote2 = esc("I design and ship frontend, backend, cloud, automations and AI systems to production.")
    footer = esc("Turin, Italy — remote & on-site · reply within 24 hours")

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid meet" font-family="ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif" role="img" aria-label="About Miguel Granados">
<defs>
<linearGradient id="bg{s}" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="{panel_a}"/><stop offset="1" stop-color="{panel_b}"/>
</linearGradient>
<radialGradient id="glow{s}" cx="10%" cy="10%" r="50%">
  <stop offset="0" stop-color="{ACCENT}" stop-opacity="0.18"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/>
</radialGradient>
<clipPath id="win{s}"><rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="18"/></clipPath>
</defs>
<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="18" fill="{outer}"/>
<g clip-path="url(#win{s})">
<rect x="2" y="2" width="{W - 4}" height="{H - 4}" fill="url(#bg{s})"/>
<rect x="2" y="2" width="{W - 4}" height="{H - 4}" fill="url(#glow{s})"/>
<rect x="2" y="2" width="{W - 4}" height="42" fill="{'#0A1020' if dark else '#EEF2FF'}" fill-opacity="0.85"/>
<circle cx="28" cy="23" r="5" fill="#FF5F56"/>
<circle cx="48" cy="23" r="5" fill="#FFBD2E"/>
<circle cx="68" cy="23" r="5" fill="#27C93F"/>
<text x="{W / 2:.0f}" y="27" text-anchor="middle" font-size="12" font-family="ui-monospace,Menlo,monospace" fill="{muted}">miguel@ulamander — about.sh</text>

<text x="56" y="86" font-size="11" letter-spacing="2.5" font-weight="700" fill="{ACCENT}">ABOUT ME</text>
<text x="56" y="118" font-size="24" font-weight="800" fill="{heading}">{intro1}</text>
<text x="56" y="146" font-size="16" fill="{body}">{intro2}</text>

<rect x="56" y="174" width="4" height="86" rx="2" fill="{ACCENT}"/>
<rect x="56" y="174" width="1068" height="86" rx="10" fill="{quote_bg}"/>
<rect x="56" y="174" width="4" height="86" rx="2" fill="{ACCENT}"/>
<text x="84" y="212" font-size="17" font-style="italic" fill="{heading}">{quote1}</text>
<text x="84" y="238" font-size="15" fill="{body}">{quote2}</text>

<text x="56" y="296" font-size="11" letter-spacing="2.5" font-weight="700" fill="{ACCENT}">HOW I DELIVER</text>
{cards_svg}

<circle cx="62" cy="{H - 36}" r="4" fill="{SOFT}"/>
<text x="76" y="{H - 31}" font-size="13" fill="{muted}">{footer}</text>
</g>
</svg>
'''


if __name__ == "__main__":
    open("about-dark.svg", "w").write(build("dark"))
    open("about-light.svg", "w").write(build("light"))
    from xml.etree import ElementTree as ET
    ET.parse("about-dark.svg")
    ET.parse("about-light.svg")
    print("wrote + validated about-dark.svg, about-light.svg")
