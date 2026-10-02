"""Services + method panel — the 12 professional services and the 4-step
delivery method of miguel.ulamander.com, in the shared design system.
Desktop: assets/services-{dark,light}.svg (960, 3-column grid + method row).
Mobile: assets/services-{dark,light}-mobile.svg (480, 1 column)."""
from __future__ import annotations

import os

from design import (ACCENT, ASSETS, DESK_W, DESK_X, MOB_W, MOB_X, MONO, esc, palette,
                    section_label, text_w, window, wrap, write_validated)

HEADLINE = "From idea to system in production"
INTRO = "End-to-end engineering services for companies that want to automate, scale and secure their operations."
SERVICES = [
    ("Software Development", "Web apps, APIs and scalable backend systems built with modern architectures."),
    ("Business Automation", "Automated workflows with n8n, webhooks and integrations to eliminate repetitive tasks."),
    ("AI Implementation", "AI agents, chatbots, RAG and custom LLMs tailored to your business needs."),
    ("API Integration", "Robust connections between systems, CRMs and external services via REST and webhooks."),
    ("Cloud Infrastructure", "VPS deployment, Docker containers and Oracle Cloud & Azure architecture, production-ready."),
    ("Tech Consulting", "End-to-end tech strategy: what to build, how to secure it and where to apply AI."),
    ("AI Full Stack · E-commerce", "Sites and stores with Claude Code: WordPress, Shopify, high-conversion landing pages."),
    ("Server & NAS Configuration", "Linux, Docker Compose, VPS, UGREEN NAS, nginx, SSL, tunnel and production deploy."),
    ("Cybersecurity & Hardening", "Fortinet, Azure Sentinel, firewall, hardening, backup, audit and data protection."),
    ("Database & Backend", "PostgreSQL, schema design, RLS, REST APIs, JWT/OAuth and multi-tenant SaaS."),
    ("DevOps & Monitoring", "CI/CD, containers, logs, healthchecks, rollback and operational maintenance."),
    ("GDPR · Privacy · EU AI Act", "Data compliance, privacy policy, cookies, client protection and EU AI Act readiness."),
]
METHOD_HEAD = "Full Stack end-to-end: from design to deploy"
METHOD = [
    ("Design & UX", "Brand-first interfaces, clear flows, reusable components."),
    ("Frontend & Backend", "React/Vite, APIs, auth, Postgres/Supabase, SaaS panels."),
    ("AI & Automation", "Local LLMs (Ollama), n8n agent workflows, intent routing."),
    ("Cloud, NAS & Security", "Docker, Cloudflare Tunnel, corporate mail, DNS/SPF, hardening."),
]

DESKTOP = dict(W=DESK_W, X=DESK_X, cols=3, gap=14, title=14, body=12.5, lh=18, chars=34, mcols=2, mchars=52)
MOBILE = dict(W=MOB_W, X=MOB_X, cols=1, gap=10, title=16, body=14.5, lh=21, chars=50, mcols=1, mchars=50)


def text_lines(x, y, lines, size, fill, lh) -> str:
    return "\n".join(f'<text x="{x:.1f}" y="{y + i * lh:.1f}" font-size="{size}" fill="{fill}">{esc(l)}</text>'
                     for i, l in enumerate(lines))


def check(lines, size, max_w, what):
    for line in lines:
        if text_w(line, size) > max_w:
            raise SystemExit(f"{what}: '{line}' overflows")


def build(theme: str, mobile: bool = False) -> str:
    p, s = palette(theme), (MOBILE if mobile else DESKTOP)
    W, X, cols, gap = s["W"], s["X"], s["cols"], s["gap"]
    CW = W - 2 * X
    out = [section_label(X, 80 if mobile else 86, "SERVICES", p)]
    y = 110 if mobile else 120
    for line in wrap(HEADLINE, 30 if mobile else 70):
        out.append(f'<text x="{X}" y="{y}" font-size="{21 if mobile else 24}" font-weight="800" fill="{p["heading"]}">{esc(line)}</text>')
        y += 28
    y -= 2
    for line in wrap(INTRO, 58 if mobile else 110):
        out.append(f'<text x="{X}" y="{y}" font-size="{14 if mobile else 14.5}" fill="{p["body"]}">{esc(line)}</text>')
        y += 20
    y += 12

    cw = (CW - gap * (cols - 1)) / cols
    wrapped = [(t, wrap(d, s["chars"])) for t, d in SERVICES]
    for t, l in wrapped:
        check(l, s["body"], cw - 30, t)
        check([t], s["title"] * 1.08, cw - 52, t)
    card_h = 48 + max(len(l) for _, l in wrapped) * s["lh"]
    for i, (title, lines) in enumerate(wrapped):
        col, row = i % cols, i // cols
        cx, cy = X + col * (cw + gap), y + row * (card_h + gap)
        out.append(f'<rect x="{cx:.1f}" y="{cy:.1f}" width="{cw:.1f}" height="{card_h}" rx="12" fill="{p["box"]}" stroke="{p["box_stroke"]}" stroke-width="1.2"/>')
        out.append(f'<text x="{cx + 16:.1f}" y="{cy + 27}" font-size="11" font-weight="700" font-family="{MONO}" fill="{p["accent_tx"]}">{i + 1:02d}</text>')
        out.append(f'<text x="{cx + 42:.1f}" y="{cy + 28}" font-size="{s["title"]}" font-weight="700" fill="{p["heading"]}">{esc(title)}</text>')
        out.append(text_lines(cx + 16, cy + 52, lines, s["body"], p["body"], s["lh"]))
    rows = -(-len(SERVICES) // cols)
    y += rows * (card_h + gap) - gap + 44

    # Method: four steps connected by the accent rule.
    out.append(section_label(X, y, "METHOD", p))
    y += 26
    for line in wrap(METHOD_HEAD, 34 if mobile else 80):
        out.append(f'<text x="{X}" y="{y}" font-size="{17 if mobile else 18}" font-weight="800" fill="{p["heading"]}">{esc(line)}</text>')
        y += 24
    y += 6
    mcols = s["mcols"]
    mw = (CW - gap * (mcols - 1)) / mcols
    mwrapped = [(t, wrap(d, s["mchars"])) for t, d in METHOD]
    for t, l in mwrapped:
        check(l, s["body"], mw - 30, t)
        check([t], s["title"] * 1.08, mw - 64, t)
    mh = 58 + max(len(l) for _, l in mwrapped) * s["lh"]
    for i, (title, lines) in enumerate(mwrapped):
        mx = X + (i % mcols) * (mw + gap)
        my = y + (i // mcols) * (mh + gap)
        out.append(f'<rect x="{mx:.1f}" y="{my:.1f}" width="{mw:.1f}" height="{mh}" rx="12" fill="{p["box"]}" stroke="{p["box_stroke"]}" stroke-width="1.2"/>')
        out.append(f'<circle cx="{mx + 28:.1f}" cy="{my + 26}" r="14" fill="{ACCENT}"/>')
        out.append(f'<text x="{mx + 28:.1f}" y="{my + 30.5}" text-anchor="middle" font-size="12" font-weight="800" font-family="{MONO}" fill="#FFFFFF">{i + 1:02d}</text>')
        out.append(f'<text x="{mx + 52:.1f}" y="{my + 31}" font-size="{s["title"]}" font-weight="700" fill="{p["heading"]}">{esc(title)}</text>')
        out.append(text_lines(mx + 16, my + 60, lines, s["body"], p["body"], s["lh"]))
    mrows = -(-len(METHOD) // mcols)
    y += mrows * (mh + gap) - gap + 32
    title = "services.sh" if mobile else "miguel@ulamander — services.sh"
    return window(W, int(y), p, title, "\n".join(out), glow=("88%", "5%"), label="Services and method")


if __name__ == "__main__":
    for theme in ("dark", "light"):
        write_validated(os.path.join(ASSETS, f"services-{theme}.svg"), build(theme))
        write_validated(os.path.join(ASSETS, f"services-{theme}-mobile.svg"), build(theme, mobile=True))
    print("wrote + validated assets/services-{dark,light}(.svg, -mobile.svg)")
