#!/usr/bin/env python3
"""Two insignia cards with real brand icons (developer-icons / simple-icons)."""
from __future__ import annotations
import html, re, base64
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ICON_DIR = Path(__file__).resolve().parent / "badge-icons"
W, H = 560, 178


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def load_icon_b64(name: str, size: int = 16) -> str | None:
    path = ICON_DIR / name
    if not path.exists():
        return None
    raw = path.read_text()
    # Ensure viewBox and size; simple-icons are often path-only black
    if "viewBox" not in raw:
        raw = re.sub(r"<svg", '<svg viewBox="0 0 24 24"', raw, count=1)
    # Force fill currentColor -> white/brand handled by tinting via CSS not available;
    # recolor black fills to white for dark pills
    raw = raw.replace('fill="#000"', 'fill="#fff"').replace("fill=\"black\"", 'fill="#fff"')
    if 'fill=' not in raw and "<path" in raw:
        raw = raw.replace("<path", '<path fill="#fff"', 1)
    # Strip xml decls
    raw = re.sub(r"<\?xml[^>]*\?>", "", raw).strip()
    b64 = base64.b64encode(raw.encode()).decode()
    return f"data:image/svg+xml;base64,{b64}"


def pill_with_icon(x, y, w, label, icon_file, soft, pill_bg, stroke) -> str:
    href = load_icon_b64(icon_file) if icon_file else None
    parts = [
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w}" height="28" rx="14" fill="{pill_bg}" stroke="{stroke}" stroke-width="1"/>'
    ]
    tx = x + w / 2
    if href:
        parts.append(
            f'<image href="{href}" x="{x + 10:.1f}" y="{y + 6:.1f}" width="16" height="16"/>'
        )
        tx = x + 18 + (w - 18) / 2
        parts.append(
            f'<text x="{tx:.1f}" y="{y + 18:.1f}" text-anchor="middle" font-size="11" font-weight="600" fill="{soft}">{esc(label)}</text>'
        )
    else:
        parts.append(
            f'<text x="{tx:.1f}" y="{y + 18:.1f}" text-anchor="middle" font-size="11" font-weight="600" fill="{soft}">{esc(label)}</text>'
        )
    return "\n".join(parts)


def card(theme: str, kind: str) -> str:
    dark = theme == "dark"
    bg = "#0d1117" if dark else "#FFFFFF"
    panel = "#161b22" if dark else "#F8FAFC"
    bar = "#12171f" if dark else "#F1F5F9"
    accent = "#fe702d" if dark else "#ea580c"
    soft = "#fb923c" if dark else "#c2410c"
    muted = "#94A3B8" if dark else "#475569"
    dim = "#64748B"
    pill_bg = "rgba(254,112,45,0.14)" if dark else "rgba(234,88,12,0.10)"
    stroke = "rgba(254,112,45,0.45)" if dark else "rgba(234,88,12,0.35)"
    sid = ("D" if dark else "L") + kind[0].upper()

    if kind == "credentials":
        title = "CREDENTIALS"
        subtitle = "Verified training · portfolio-aligned"
        items = [
            ("100+ Badges", 128, "github-dark.svg"),
            ("MS Learn Lv.15", 138, "microsoft.svg"),
            ("Claude Academy 19", 152, "claude-ai.svg"),
            ("Google Skillshop 11", 158, "google.svg"),
            ("Fortinet NSE 3", 136, "fortinet.svg"),
            ("OCI Foundations", 140, "oracle.svg"),
        ]
        footer = "AI-900 · SC-900 · Shopify · AWS foundations"
    else:
        title = "FOCUS STACK"
        subtitle = "What I ship in production"
        items = [
            ("Python", 96, "python.svg"),
            ("TypeScript", 118, "typescript.svg"),
            ("React", 90, "reactjs.svg"),
            ("PostgreSQL", 122, "postgresql.svg"),
            ("Azure / Sentinel", 144, "azure.svg"),
            ("n8n · LLMs", 112, "n8n.svg"),
        ]
        footer = "Full Stack · Cloud Security · AI systems · Turin"

    pills, x, y = [], 16.0, 58.0
    for label, pw, icon in items:
        if x + pw > W - 16:
            x = 16.0
            y += 36
        pills.append(pill_with_icon(x, y, pw, label, icon, soft, pill_bg, stroke))
        x += pw + 8

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(title)}">
<defs>
  <linearGradient id="g{sid}" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{panel}"/><stop offset="1" stop-color="{bg}"/>
  </linearGradient>
</defs>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="12" fill="url(#g{sid})" stroke="{stroke}" stroke-width="1.2"/>
<rect x="1" y="1" width="{W - 2}" height="36" rx="12" fill="{bar}"/>
<rect x="1" y="20" width="{W - 2}" height="17" fill="{bar}"/>
<circle cx="18" cy="18" r="4" fill="#FF5F56"/><circle cx="34" cy="18" r="4" fill="#FFBD2E"/><circle cx="50" cy="18" r="4" fill="#27C93F"/>
<text x="68" y="22" font-family="ui-monospace,Menlo,monospace" font-size="11" font-weight="700" fill="{accent}">{esc(title)}</text>
<text x="16" y="50" font-family="ui-sans-serif,system-ui,sans-serif" font-size="12" fill="{muted}">{esc(subtitle)}</text>
{chr(10).join(pills)}
<text x="16" y="{H - 12}" font-family="ui-sans-serif,system-ui,sans-serif" font-size="11" fill="{dim}">{esc(footer)}</text>
</svg>
'''


if __name__ == "__main__":
    from xml.etree import ElementTree as ET
    mapping = {
        ("dark", "credentials"): "insignia-credentials-dark.svg",
        ("light", "credentials"): "insignia-credentials-light.svg",
        ("dark", "focus"): "insignia-focus-dark.svg",
        ("light", "focus"): "insignia-focus-light.svg",
    }
    for (theme, kind), name in mapping.items():
        p = ROOT / name
        p.write_text(card(theme, kind))
        ET.parse(p)
        print(f"ok {name} {p.stat().st_size}B")
