"""About card — same design system as the hero (design.py). Copy is taken
from miguel.ulamander.com (EN version) so the two never contradict each other.
Desktop: assets/about-{dark,light}.svg (960 wide, 2x2 card grid).
Mobile: assets/about-{dark,light}-mobile.svg (480 wide, 1 column,
larger type — GitHub's mobile app renders it at ~0.75x)."""
from __future__ import annotations

import os

from design import (ACCENT, DESK_W, DESK_X, MOB_W, MOB_X, SOFT, esc, palette, section_label,
                    window, wrap, write_validated)

HEADLINE = "Founder & CEO of Ulamander — AI Development Technician & Full Stack Engineer."
INTRO = ("IT professional specialised in AI, cloud and cybersecurity — "
         "from secure infrastructure to AI agents and workflow automation.")
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
               card_title=15, card_body=13.5, card_lh=19, footer=13, cols=2)
MOBILE = dict(W=MOB_W, X=MOB_X, head=21, intro=16, quote=16.5, quote_sub=15, big=22, stat=12.5,
              card_title=16.5, card_body=15, card_lh=21, footer=13.5, cols=1)


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
    intro = wrap(INTRO, chars(CW, s["intro"]))
    out.append(text_lines(X, y, intro, s["intro"], p["body"], s["intro"] + 7))
    y += (len(intro) - 1) * (s["intro"] + 7) + 24
    q, qh = quote_block(X, y, CW, p, s)
    out.append(q)
    y += qh + 16
    st, sh = stats_row(X, y, CW, p, s, mobile)
    out.append(st)
    y += sh + 40
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
    y += rows * (card_h + gap) - gap + 38
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
