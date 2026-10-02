"""Expertise panel — the six skill pillars of miguel.ulamander.com
("A stack that connects AI, cloud and code"), in the shared design system.
Desktop: assets/expertise-{dark,light}.svg (960, 3x2 grid).
Mobile: assets/expertise-{dark,light}-mobile.svg (480, 1 column)."""
from __future__ import annotations

import os

from design import (ACCENT, ASSETS, DESK_W, DESK_X, MOB_W, MOB_X, MONO, esc, palette,
                    section_label, text_w, window, wrap, write_validated)

HEADLINE = "A stack that connects AI, cloud and code"
INTRO = ("End-to-end IT profile: development, server configuration, cloud, security and AI agents "
         "— ready for real production.")
# Same pillars and items as the portfolio's "Full Stack · Skills" section.
PILLARS = [
    ("01", "Programming", ["Python · JavaScript · TypeScript", "React / Vite · Node.js / Fastify",
                           "PHP · WordPress", "SQL · PostgreSQL", "HTML · CSS · API design"]),
    ("02", "AI & Machine Learning", ["OpenAI / Claude · LLMs", "Prompting · RAG · embeddings",
                                     "AI agents · tool calling · MCP", "Claude API · Bedrock · Vertex AI",
                                     "Gemini · chatbots · AI SDKs"]),
    ("03", "Automation", ["n8n workflows", "Webhooks · cron · code", "REST API · GraphQL",
                          "CRM / ERP integrations", "Email · SMTP · notifications"]),
    ("04", "Server & DevOps", ["Linux · Docker · Compose", "VPS · NAS (UGREEN) setup",
                               "Nginx · reverse proxy · SSL/TLS", "Cloudflare Tunnel · DNS · CDN",
                               "Deploy · backup · monitoring"]),
    ("05", "Cloud & Networks", ["Microsoft Azure", "Oracle Cloud · AWS", "Networking · firewall · VPN",
                                "SMTP · SPF · DKIM · DMARC", "Multi-tenant architectures"]),
    ("06", "Security & Compliance", ["Fortinet NSE 3", "Microsoft Sentinel · Defender XDR",
                                     "GDPR · EU AI Act", "Privacy by design · hardening",
                                     "Audit · backup · RLS · encryption"]),
]

DESKTOP = dict(W=DESK_W, X=DESK_X, cols=3, gap=16, title=15, item=12.5, lh=20)
MOBILE = dict(W=MOB_W, X=MOB_X, cols=1, gap=12, title=16.5, item=14.5, lh=22)


def pillar(x, y, w, h, num, title, items, p, s) -> str:
    out = [f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="14" fill="{p["box"]}" stroke="{p["box_stroke"]}" stroke-width="1.2"/>',
           f'<text x="{x + 18:.1f}" y="{y + 30}" font-size="12" font-weight="700" font-family="{MONO}" fill="{p["accent_tx"]}">{num}</text>',
           f'<text x="{x + 44:.1f}" y="{y + 31}" font-size="{s["title"]}" font-weight="700" fill="{p["heading"]}">{esc(title)}</text>',
           f'<line x1="{x + 18:.1f}" y1="{y + 46}" x2="{x + w - 18:.1f}" y2="{y + 46}" stroke="{p["box_stroke"]}"/>']
    iy = y + 70
    for item in items:
        if 30 + text_w(item, s["item"]) > w - 10:
            raise SystemExit(f"{title}: '{item}' overflows")
        out.append(f'<circle cx="{x + 21:.1f}" cy="{iy - s["item"] * 0.33:.1f}" r="2.6" fill="{ACCENT}"/>')
        out.append(f'<text x="{x + 32:.1f}" y="{iy}" font-size="{s["item"]}" fill="{p["body"]}">{esc(item)}</text>')
        iy += s["lh"]
    return "\n".join(out)


def build(theme: str, mobile: bool = False) -> str:
    p, s = palette(theme), (MOBILE if mobile else DESKTOP)
    W, X, cols, gap = s["W"], s["X"], s["cols"], s["gap"]
    CW = W - 2 * X
    cw = (CW - gap * (cols - 1)) / cols
    out = [section_label(X, 80 if mobile else 86, "EXPERTISE", p)]
    y = 110 if mobile else 120
    for line in wrap(HEADLINE, 30 if mobile else 70):
        out.append(f'<text x="{X}" y="{y}" font-size="{21 if mobile else 24}" font-weight="800" fill="{p["heading"]}">{esc(line)}</text>')
        y += 28
    y -= 2
    for line in wrap(INTRO, 58 if mobile else 110):
        out.append(f'<text x="{X}" y="{y}" font-size="{14 if mobile else 14.5}" fill="{p["body"]}">{esc(line)}</text>')
        y += 20
    y += 12
    card_h = 70 + max(len(it) for _, _, it in PILLARS) * s["lh"] - 4
    for i, (num, title, items) in enumerate(PILLARS):
        col, row = i % cols, i // cols
        out.append(pillar(X + col * (cw + gap), y + row * (card_h + gap), cw, card_h, num, title, items, p, s))
    rows = -(-len(PILLARS) // cols)
    y += rows * (card_h + gap) - gap + 30
    title = "expertise.sh" if mobile else "miguel@ulamander — expertise.sh"
    return window(W, int(y), p, title, "\n".join(out), glow=("12%", "6%"), label="Expertise")


if __name__ == "__main__":
    for theme in ("dark", "light"):
        write_validated(os.path.join(ASSETS, f"expertise-{theme}.svg"), build(theme))
        write_validated(os.path.join(ASSETS, f"expertise-{theme}-mobile.svg"), build(theme, mobile=True))
    print("wrote + validated assets/expertise-{dark,light}(.svg, -mobile.svg)")
