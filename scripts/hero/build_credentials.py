"""Credentials panel — ONLY items with a public record (see
datos-fuente/ in the local docs folder for the source of each line):
  Microsoft Learn  -> public profile (level, 59 badges, 8 trophies)
  Claude Academy   -> 19 badges, academy.claude.com/badges/<id> (Aug 2026)
  Google Skillshop -> 10 certifications listed on LinkedIn (May 2026, valid to May 2027)
  Fortinet         -> NSE 3 + Certified Associate Cybersecurity (LinkedIn)
  Oracle           -> OCI 2025 Foundations Associate (Oracle CertView, valid to May 2028)
Anything without a record (AI-900/SC-900 exams, AWS, Shopify...) stays out,
or goes in the roadmap card, clearly marked as not yet earned.
Desktop: assets/credentials-{dark,light}.svg (960). Mobile: assets/credentials-{dark,light}-mobile.svg (480)."""
import os

from design import (ACCENT, DESK_W, DESK_X, MOB_W, MOB_X, MONO, asset, esc, icon, palette,
                    section_label, text_w, window, wrap, write_validated)

PROVIDERS = [
    ("Microsoft Learn", "badge-icons/microsoft.svg", "Level 15", "59 badges · 8 trophies",
     ["Introduction to AI in Azure", "AI Concepts for Developers", "Intro to Microsoft Security Solutions",
      "GitHub Fundamentals — Administration", "Modules across security, Entra, Purview & cloud"]),
    ("Claude Academy · Anthropic", "badge-icons/claude-ai.svg", "19", "badges · Aug 2026",
     ["Building with the Claude API", "Claude Code 101 · Claude Code in Action",
      "Model Context Protocol — Intro & Advanced", "Claude with Amazon Bedrock & Vertex AI",
      "Claude 101 · Platform 101 · Claude Cowork", "AI Fluency track — 9 courses"]),
    ("Google Skillshop", "badge-icons/google.svg", "10", "certifications · valid to May 2027",
     ["Google Ads Search · Display · Video · Apps", "Creative · Measurement",
      "AI-Powered Shopping ads", "Campaign Manager 360 · Google Analytics", "Grow Offline Sales"]),
    ("Fortinet", "badge-icons/fortinet.svg", "NSE 3", "Network Security Associate",
     ["FortiGate Operator 7.6", "Fortinet Certified Associate Cybersecurity", "Issued May 2026"]),
    ("Oracle", "badge-icons/oracle.svg", "OCI", "Oracle Cloud Infrastructure",
     ["OCI 2025 Certified Foundations Associate", "Issued May 2026 · valid until May 2028"]),
]
ROADMAP = ["AI-900", "SC-900", "SC-200", "AZ-500", "AI-102", "Fortinet NSE 4", "GitHub Advanced Security"]
FOCUS = [("Docker", "badge-icons/docker.svg"), ("Linux", "badge-icons/linux.svg"),
         ("Cloudflare Tunnel", "badge-icons/cloudflare.svg"), ("Microsoft Sentinel", "badge-icons/azure.svg"),
         ("Defender XDR", "badge-icons/microsoft.svg"), ("Fortinet", "badge-icons/fortinet.svg"),
         ("GDPR", None), ("EU AI Act", None)]

DESKTOP = dict(W=DESK_W, X=DESK_X, cols=2, gap=20, name=15, big=28, sub=13, item=13.5, item_lh=20, chip=13)
MOBILE = dict(W=MOB_W, X=MOB_X, cols=1, gap=12, name=16, big=26, sub=13.5, item=15, item_lh=22, chip=13.5)


def provider_card(x, y, w, h, prov, p, s) -> str:
    name, ic, big, sub, items = prov
    out = [f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="14" fill="{p["box"]}" stroke="{p["box_stroke"]}" stroke-width="1.2"/>',
           icon(asset(ic), x + 18, y + 18, 20),
           f'<text x="{x + 48:.1f}" y="{y + 33}" font-size="{s["name"]}" font-weight="700" fill="{p["heading"]}">{esc(name)}</text>',
           f'<text x="{x + 18:.1f}" y="{y + 54 + s["big"] * 0.8:.1f}" font-size="{s["big"]}" font-weight="800" fill="{p["accent_tx"]}">{esc(big)}</text>']
    big_w = text_w(big, s["big"], bold=True)
    out.append(f'<text x="{x + 26 + big_w:.1f}" y="{y + 54 + s["big"] * 0.8:.1f}" font-size="{s["sub"]}" fill="{p["body"]}">{esc(sub)}</text>')
    if 26 + big_w + text_w(sub, s["sub"]) > w - 12:
        raise SystemExit(f"{name}: '{big} {sub}' overflows the card")
    iy = y + 54 + s["big"] + 26
    for line in items:
        if 34 + text_w(line, s["item"]) > w - 12:
            raise SystemExit(f"{name}: item '{line}' overflows the card")
        out.append(f'<rect x="{x + 19:.1f}" y="{iy - 7}" width="5" height="5" rx="1" fill="{ACCENT}" transform="rotate(45 {x + 21.5:.1f} {iy - 4.5})"/>')
        out.append(f'<text x="{x + 34:.1f}" y="{iy}" font-size="{s["item"]}" fill="{p["body"]}">{esc(line)}</text>')
        iy += s["item_lh"]
    return "\n".join(out)


def card_height(prov, s, w) -> float:
    return 54 + s["big"] + 26 + len(prov[4]) * s["item_lh"] + 4


def roadmap_card(x, y, w, h, p, s) -> str:
    out = [f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="14" fill="none" stroke="{p["muted"]}" '
           f'stroke-opacity="0.7" stroke-dasharray="6 5" stroke-width="1.2"/>',
           f'<text x="{x + 18:.1f}" y="{y + 33}" font-size="{s["name"]}" font-weight="700" fill="{p["heading"]}">2026 roadmap</text>',
           f'<text x="{x + 18:.1f}" y="{y + 54}" font-size="{s["sub"]}" fill="{p["muted"]}">In preparation — not yet earned</text>']
    cx, cy = x + 18, y + 72
    for item in ROADMAP:
        tw = text_w(item, s["sub"], mono=True) + 20
        if cx + tw > x + w - 14:
            cx, cy = x + 18, cy + 32
        out.append(f'<rect x="{cx:.1f}" y="{cy}" width="{tw:.1f}" height="24" rx="12" fill="none" stroke="{p["cred_stroke"]}"/>')
        out.append(f'<text x="{cx + tw / 2:.1f}" y="{cy + 16.5}" text-anchor="middle" font-size="{s["sub"]}" '
                   f'font-family="{MONO}" fill="{p["body"]}">{esc(item)}</text>')
        cx += tw + 8
    return "\n".join(out)


def roadmap_height(w, s) -> float:
    cx, rows = 18, 1
    for item in ROADMAP:
        tw = text_w(item, s["sub"], mono=True) + 20
        if cx + tw > w - 14:
            cx, rows = 18, rows + 1
        cx += tw + 8
    return 72 + rows * 32 + 6


def focus_chips(x, y, max_w, p, s) -> tuple[str, float]:
    out, cx, cy = [], x, y
    for name, ic in FOCUS:
        tw = text_w(name, s["chip"], bold=True) + (44 if ic else 26)
        if cx + tw > x + max_w:
            cx, cy = x, cy + 44
        out.append(f'<rect x="{cx:.1f}" y="{cy}" width="{tw:.1f}" height="34" rx="10" fill="{p["box"]}" stroke="{p["box_stroke"]}"/>')
        tx = cx + 13
        if ic:
            out.append(icon(asset(ic), cx + 11, cy + 8, 18))
            tx = cx + 36
        out.append(f'<text x="{tx:.1f}" y="{cy + 22}" font-size="{s["chip"]}" font-weight="600" fill="{p["heading"]}">{esc(name)}</text>')
        cx += tw + 10
    return "\n".join(out), cy + 34 - y


def build(theme: str, mobile: bool = False) -> str:
    p, s = palette(theme), (MOBILE if mobile else DESKTOP)
    W, X, cols, gap = s["W"], s["X"], s["cols"], s["gap"]
    CW = W - 2 * X
    cw = (CW - gap * (cols - 1)) / cols
    out = [section_label(X, 80 if mobile else 86, "CERTIFICATIONS & TRAINING", p)]
    head = wrap("Verified credentials, each with a public record", 30 if mobile else 70)
    for i, line in enumerate(head):
        out.append(f'<text x="{X}" y="{(112 if mobile else 120) + i * 28}" font-size="{21 if mobile else 24}" '
                   f'font-weight="800" fill="{p["heading"]}">{esc(line)}</text>')
    y = (112 if mobile else 120) + (len(head) - 1) * 28 + 26
    note = wrap("Microsoft Learn profile · Claude Academy badges · Oracle CertView · LinkedIn — links below.",
                56 if mobile else 110)
    for i, line in enumerate(note):
        out.append(f'<text x="{X}" y="{y + i * 19}" font-size="13" fill="{p["muted"]}">{esc(line)}</text>')
    y += (len(note) - 1) * 19 + 24

    cards = PROVIDERS + [None]                      # last slot = roadmap card
    heights = [card_height(c, s, cw) if c else roadmap_height(cw, s) for c in cards]
    for r in range(0, len(cards), cols):
        row_h = max(heights[r:r + cols])
        for c in range(cols):
            if r + c >= len(cards):
                break
            cx = X + c * (cw + gap)
            prov = cards[r + c]
            h = row_h if cols > 1 else heights[r + c]
            out.append(provider_card(cx, y, cw, h, prov, p, s) if prov else roadmap_card(cx, y, cw, h, p, s))
        y += (row_h if cols > 1 else heights[r]) + gap

    y += 22
    out.append(section_label(X, y, "SECURITY & INFRASTRUCTURE FOCUS", p))
    chips, ch = focus_chips(X, y + 16, CW, p, s)
    out.append(chips)
    y += 16 + ch + 34
    title = "credentials.sh" if mobile else "miguel@ulamander — credentials.sh"
    return window(W, int(y), p, title, "\n".join(out), glow=("88%", "6%"), label="Certifications and training")


if __name__ == "__main__":
    from design import ASSETS
    for theme in ("dark", "light"):
        write_validated(os.path.join(ASSETS, f"credentials-{theme}.svg"), build(theme))
        write_validated(os.path.join(ASSETS, f"credentials-{theme}-mobile.svg"), build(theme, mobile=True))
    print("wrote + validated assets/credentials-{dark,light}(.svg, -mobile.svg)")
