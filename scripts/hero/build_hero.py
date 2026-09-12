"""Header SVG: solo Miguel + tagline. I bottoni clickabili stanno nel README (Portfolio/LinkedIn/Email)."""

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
    chip_stroke = accent

    # Visual button row (decorative — real links are Markdown badges under the SVG)
    def btn(x, label, icon_color):
        return f'''<rect x="{x}" y="168" width="200" height="44" rx="10" fill="{chip}" stroke="{chip_stroke}" stroke-opacity="0.5"/>
<circle cx="{x + 28}" cy="190" r="10" fill="{icon_color}"/>
<text x="{x + 48}" y="196" font-size="14" font-weight="600" fill="{heading}">{label}</text>'''

    buttons = "\n".join([
        btn(56, "PORTFOLIO", accent),
        btn(276, "LINKEDIN", "#0A66C2"),
        btn(496, "EMAIL", "#EA4335"),
    ])

    H = 240
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="{H}" viewBox="0 0 1180 {H}" font-family="ui-sans-serif,system-ui,-apple-system,Segoe UI,sans-serif" role="img" aria-label="Miguel Granados">
<defs>
<linearGradient id="a{s}" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{accent}"/><stop offset="1" stop-color="{soft}"/>
</linearGradient>
<linearGradient id="p{s}" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bot}"/>
</linearGradient>
<clipPath id="w{s}"><rect x="2" y="2" width="1176" height="{H - 4}" rx="16"/></clipPath>
</defs>
<rect x="2" y="2" width="1176" height="{H - 4}" rx="16" fill="{outer}"/>
<g clip-path="url(#w{s})">
<rect x="2" y="2" width="1176" height="{H - 4}" fill="url(#p{s})"/>
<rect x="2" y="2" width="1176" height="40" fill="{bar}"/>
<line x1="2" y1="42" x2="1178" y2="42" stroke="{div}"/>
<circle cx="26" cy="21" r="5" fill="#FF5F56"/>
<circle cx="46" cy="21" r="5" fill="#FFBD2E"/>
<circle cx="66" cy="21" r="5" fill="#27C93F"/>
<text x="590" y="26" text-anchor="middle" font-size="12" font-family="ui-monospace,Menlo,monospace" fill="{body}">miguel@ulamander</text>

<text x="56" y="100" font-size="40" font-weight="700" fill="{heading}">Miguel Granados</text>
<text x="56" y="132" font-size="16" fill="{body}">Tecnico in Sviluppo di Intelligenza Artificiale · Founder @ Ulamander</text>
<text x="56" y="156" font-size="13" fill="{body}">Torino, Italia · Full Stack · AI · Cloud Security</text>
<rect x="56" y="164" width="1068" height="2" rx="1" fill="url(#a{s})"/>
{buttons}
</g>
</svg>
'''


if __name__ == "__main__":
    open("dark.svg", "w").write(build("dark"))
    open("light.svg", "w").write(build("light"))
    print("wrote dark.svg and light.svg")
