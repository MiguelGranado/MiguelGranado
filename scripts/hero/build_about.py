"""About card — same design system as the hero (design.py). Copy is taken
from miguel.ulamander.com (EN version) so the two never contradict each other.
Desktop: assets/about-{dark,light}.svg (960 wide, 2x2 card grid).
Mobile: assets/about-{dark,light}-mobile.svg (480 wide, 1 column,
larger type — GitHub's mobile app renders it at ~0.75x)."""
from __future__ import annotations

import os

from design import (ACCENT, DESK_W, DESK_X, MOB_W, MOB_X, SOFT, esc, palette, section_label,
                    text_w, window, wrap, write_validated)

HEADLINE = "Founder & CEO of Ulamander — AI Development Technician & Full Stack Engineer."
INTRO = ("I'm Miguel Granados, an IT professional specialised in artificial intelligence, cloud and "
         "cybersecurity. As founder of Ulamander Corporation, I help companies and professionals turn "
         "complex processes into concrete digital solutions: from secure cloud infrastructure to AI agents "
         "and workflow automation.")
INTRO2 = ("I combine continuously updated technical expertise with a results-driven mindset to build real, "
          "scalable, production-ready systems — designed to grow your business.")
COMPETENCIES = ["AI Architecture", "Production Full Stack", "Business automation", "Cloud Computing",
                "API integrations", "DevOps · Docker · NAS", "Cybersecurity", "GDPR · EU AI Act",
                "Shopify · WordPress"]
ROLES = [
    ("Full Stack & AI Engineer", "Frontend, backend, LLMs, agents and RAG in production"),
    ("Automation Architect", "n8n workflows, webhooks and integrations"),
    ("Cloud Specialist", "Azure · Oracle Cloud · Docker"),
    ("Cybersecurity Mindset", "Sentinel · Defender XDR · Fortinet"),
    ("GDPR · Privacy & EU AI Act", "Data compliance and EU AI Act readiness"),
    ("Full Stack · Claude Code & AI", "AI-assisted development, WordPress, Shopify"),
    ("English · Professional communication", "International clients, multilingual delivery"),
    ("Founder & CEO — ULAMANDER", "AI-driven solutions and digital products"),
]
QUOTE = "I turn complex processes into intelligent AI-driven systems."
QUOTE_SUB = "I design and ship frontend, backend, cloud, automations and AI systems to production."
# Countable figures only. (number, desktop label, mobile label)
#  15 = Microsoft Learn public profile level
#  99 = 67 MS Learn achievements (59 module badges + 8 trophies) + 19 Claude
#       Academy badges + 10 Google Skillshop + 2 Fortinet + 1 Oracle.
#       Not labelled "verified": MS Learn flags 9 of its module badges as
#       unverified, and Claude/Google/Fortinet records need a sign-in to view.
#   4 = app.ulamander.com, ulamander.com, inmobiliaria.ulamander.com,
#       crm-davidevicenzi.ulamander.com (all answering HTTP 200)
STATS = [("15", "Microsoft Learn level", "MS Learn level"),
         ("99", "badges & certifications", "badges & certs"),
         ("4", "live products & sites", "live products")]
DELIVER = [
    ("I ship real systems", "Not just prototypes: website, SaaS app, real estate CRM and corporate mail running live."),
    ("Full Stack + AI", "React/TypeScript, Node, Postgres, local LLMs (Ollama) and n8n agents in one delivery flow."),
    ("Security-first mindset", "Azure/Sentinel, Fortinet, DNS/SPF/DKIM and operational hardening on the stack."),
    ("One end-to-end owner", "From idea to deploy (UI, API, cloud, mail, tunnel) without splitting the project."),
]
FOOTER = "Turin, Italy — remote & on-site · reply within 24 hours"

# Type scale per layout. Mobile is rendered at ~0.75x, so its sizes are larger.
DESKTOP = dict(W=DESK_W, X=DESK_X, head=24, intro=15.5, quote=17, quote_sub=15, big=26, stat=13,
               card_title=15, card_body=13.5, card_lh=19, footer=13, cols=2, chip=12.5, role_step=56)
MOBILE = dict(W=MOB_W, X=MOB_X, head=21, intro=16, quote=16.5, quote_sub=15, big=22, stat=12.5,
              card_title=15.5, card_body=13.5, card_lh=20, footer=13.5, cols=1, chip=13, role_step=58)


def chars(width: float, size: float, k: float = 0.54) -> int:
    return int(width / (size * k))


def text_lines(x, y, lines, size, fill, lh, **kw) -> str:
    extra = "".join(f' {k.replace("_", "-")}="{v}"' for k, v in kw.items())
    return "\n".join(f'<text x="{x}" y="{y + i * lh:.1f}" font-size="{size}" fill="{fill}"{extra}>{esc(l)}</text>'
                     for i, l in enumerate(lines))


def quote_block(x, y, w, p, s) -> tuple[str, float]:
    q = wrap(QUOTE, chars(w - 52, s["quote"], 0.56))
    sub = wrap(QUOTE_SUB, chars(w - 52, s["quote_sub"]))
    qlh, slh = s["quote"] + 8, s["quote_sub"] + 8
    h = 22 + len(q) * qlh + len(sub) * slh + 8
    y_sub = y + 18 + s["quote"] + len(q) * qlh
    svg = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{p["quote_bg"]}"/>\n'
           f'<rect x="{x}" y="{y}" width="4" height="{h}" rx="2" fill="{ACCENT}"/>\n'
           + text_lines(x + 26, y + 18 + s["quote"], q, s["quote"], p["heading"], qlh, font_style="italic") + "\n"
           + text_lines(x + 26, y_sub, sub, s["quote_sub"], p["body"], slh))
    return svg, h


def stats_row(x, y, w, p, s, mobile) -> tuple[str, float]:
    gap, h = 14, s["big"] + 46
    bw = (w - gap * (len(STATS) - 1)) / len(STATS)
    out = []
    for i, (num, label, short) in enumerate(STATS):
        bx = x + i * (bw + gap)
        out.append(f'<rect x="{bx:.1f}" y="{y}" width="{bw:.1f}" height="{h}" rx="12" fill="{p["box"]}" stroke="{p["box_stroke"]}"/>')
        out.append(f'<text x="{bx + 16:.1f}" y="{y + s["big"] + 12}" font-size="{s["big"]}" font-weight="800" '
                   f'fill="{p["accent_tx"]}">{esc(num)}</text>')
        out.append(f'<text x="{bx + 16:.1f}" y="{y + h - 14}" font-size="{s["stat"]}" fill="{p["body"]}">'
                   f'{esc(short if mobile else label)}</text>')
    return "\n".join(out), h


def chips(x, y, max_w, items, p, size) -> tuple[str, float]:
    out, cx, cy, h = [], x, y, size + 16
    for item in items:
        w = text_w(item, size, bold=True) + 26
        if cx + w > x + max_w:
            cx, cy = x, cy + h + 10
        out.append(f'<rect x="{cx:.1f}" y="{cy}" width="{w:.1f}" height="{h}" rx="{h / 2}" fill="{p["cred_bg"]}" stroke="{p["cred_stroke"]}"/>')
        out.append(f'<text x="{cx + w / 2:.1f}" y="{cy + h / 2 + size * 0.36:.1f}" text-anchor="middle" font-size="{size}" '
                   f'font-weight="600" fill="{p["pill_tx"]}">{esc(item)}</text>')
        cx += w + 10
    return "\n".join(out), cy + h - y


def deliver_card(x, y, w, h, title, lines, p, s) -> str:
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="12" fill="{p["box"]}" stroke="{p["box_stroke"]}" stroke-width="1.2"/>\n'
            f'<rect x="{x + 18:.1f}" y="{y + 20:.1f}" width="8" height="8" rx="2" fill="{ACCENT}" transform="rotate(45 {x + 22:.1f} {y + 24:.1f})"/>\n'
            f'<text x="{x + 36:.1f}" y="{y + 29:.1f}" font-size="{s["card_title"]}" font-weight="700" fill="{p["heading"]}">{esc(title)}</text>\n'
            + text_lines(round(x + 18, 1), y + 54, lines, s["card_body"], p["body"], s["card_lh"]))


def build(theme: str, mobile: bool = False) -> str:
    p, s = palette(theme), (MOBILE if mobile else DESKTOP)
    W, X = s["W"], s["X"]
    CW = W - 2 * X
    out = [section_label(X, 80 if mobile else 86, "ABOUT ME", p)]
    y = 110 if mobile else 120
    head = wrap(HEADLINE, chars(CW, s["head"], 0.58))
    out.append(text_lines(X, y, head, s["head"], p["heading"], s["head"] + 7, font_weight="800"))
    y += (len(head) - 1) * (s["head"] + 7) + 28
    for para in (INTRO, INTRO2):
        lines = wrap(para, chars(CW, s["intro"]))
        out.append(text_lines(X, y, lines, s["intro"], p["body"], s["intro"] + 7))
        y += len(lines) * (s["intro"] + 7) + 8
    y += 10
    q, qh = quote_block(X, y, CW, p, s)
    out.append(q)
    y += qh + 16
    st, sh = stats_row(X, y, CW, p, s, mobile)
    out.append(st)
    y += sh + 40
    out.append(section_label(X, y, "CORE COMPETENCIES", p))
    ch, chh = chips(X, y + 16, CW, COMPETENCIES, p, s["chip"])
    out.append(ch)
    y += 16 + chh + 40
    out.append(section_label(X, y, "HOW I DELIVER", p))
    y += 16

    cols, gap = s["cols"], 20 if not mobile else 12
    cw = (CW - gap * (cols - 1)) / cols
    wrapped = [(t, wrap(d, chars(cw - 36, s["card_body"]))) for t, d in DELIVER]
    card_h = 50 + max(len(l) for _, l in wrapped) * s["card_lh"]
    for i, (title, lines) in enumerate(wrapped):
        col, row = i % cols, i // cols
        out.append(deliver_card(X + col * (cw + gap), y + row * (card_h + gap), cw, card_h, title, lines, p, s))
    rows = -(-len(DELIVER) // cols)
    y += rows * (card_h + gap) - gap + 40

    # Professional profile: roles, two columns on desktop.
    out.append(section_label(X, y, "PROFESSIONAL PROFILE", p))
    y += 30
    rw = (CW - gap * (cols - 1)) / cols
    for i, (role, desc) in enumerate(ROLES):
        rx, ry = X + (i % cols) * (rw + gap), y + (i // cols) * s["role_step"]
        out.append(f'<rect x="{rx:.1f}" y="{ry - 13}" width="3" height="{s["role_step"] - 12}" rx="1.5" fill="{ACCENT}"/>')
        out.append(f'<text x="{rx + 14:.1f}" y="{ry}" font-size="{s["card_title"]}" font-weight="700" fill="{p["heading"]}">{esc(role)}</text>')
        out.append(f'<text x="{rx + 14:.1f}" y="{ry + s["card_lh"] + 1}" font-size="{s["card_body"]}" fill="{p["body"]}">{esc(desc)}</text>')
        if 14 + max(text_w(role, s["card_title"], bold=True), text_w(desc, s["card_body"])) > rw:
            raise SystemExit(f"role '{role}' overflows")
    y += -(-len(ROLES) // cols) * s["role_step"] + 18
    footer = wrap(FOOTER, chars(CW - 20, s["footer"]))
    out.append(f'<circle cx="{X + 6}" cy="{y - 5}" r="4" fill="{SOFT}"/>')
    out.append(text_lines(X + 20, y, footer, s["footer"], p["muted"], s["footer"] + 6))
    y += (len(footer) - 1) * (s["footer"] + 6)
    title = "about.sh" if mobile else "miguel@ulamander — about.sh"
    return window(W, int(y + 28), p, title, "\n".join(out), glow=("10%", "8%"), label="About Miguel Granados")


if __name__ == "__main__":
    from design import ASSETS
    for theme in ("dark", "light"):
        write_validated(os.path.join(ASSETS, f"about-{theme}.svg"), build(theme))
        write_validated(os.path.join(ASSETS, f"about-{theme}-mobile.svg"), build(theme, mobile=True))
    print("wrote + validated assets/about-{dark,light}(.svg, -mobile.svg)")
