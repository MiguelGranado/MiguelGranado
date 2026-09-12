#!/usr/bin/env python3
"""Two README insignia cards (replace broken GitHub stats when public metrics are 0)."""
from __future__ import annotations
import html
from pathlib import Path

W, H = 560, 168


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def card(theme: str, kind: str) -> str:
    dark = theme == "dark"
    bg = "#0d1117" if dark else "#FFFFFF"
    panel = "#161b22" if dark else "#F8FAFC"
    bar = "#12171f" if dark else "#F1F5F9"
    accent = "#fe702d" if dark else "#ea580c"
    soft = "#fb923c" if dark else "#c2410c"
    text = "#F8FAFC" if dark else "#0F172A"
    muted = "#94A3B8" if dark else "#475569"
    dim = "#64748B"
    pill = "rgba(254,112,45,0.18)" if dark else "rgba(234,88,12,0.12)"
    stroke = "rgba(254,112,45,0.40)" if dark else "rgba(234,88,12,0.35)"
    sid = ("D" if dark else "L") + kind[0].upper()

    if kind == "credentials":
        title = "CREDENTIALS.INSIGNIAS"
        subtitle = "Verified training · portfolio-aligned"
        pills = [
            ("100+ Badges", 118),
            ("MS Learn Lv.15", 128),
            ("Claude Academy 19", 148),
            ("Google Skillshop 11", 152),
            ("Fortinet NSE 3", 128),
            ("OCI Foundations", 136),
        ]
        footer = "AI-900 · SC-900 · Shopify · AWS foundations"
    else:
        title = "FOCUS.STACK"
        subtitle = "What I ship in production"
        pills = [
            ("Python", 86),
            ("TypeScript", 108),
            ("React", 78),
            ("PostgreSQL", 112),
            ("Azure / Sentinel", 132),
            ("n8n · LLMs", 100),
        ]
        footer = "Full Stack · Cloud Security · AI systems · Turin"

    pill_svg = []
    x, y = 18.0, 62.0
    for label, pw in pills:
        if x + pw > W - 18:
            x = 18.0
            y += 34
        pill_svg.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{pw}" height="26" rx="13" fill="{pill}" stroke="{stroke}" stroke-width="1"/>'
            f'<text x="{x + pw / 2:.1f}" y="{y + 17:.1f}" text-anchor="middle" font-size="11" font-weight="600" fill="{soft}">{esc(label)}</text>'
        )
        x += pw + 8

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(title)}">
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
<text x="18" y="52" font-family="ui-sans-serif,system-ui,sans-serif" font-size="12" fill="{muted}">{esc(subtitle)}</text>
{"".join(pill_svg)}
<text x="18" y="{H - 14}" font-family="ui-sans-serif,system-ui,sans-serif" font-size="11" fill="{dim}">{esc(footer)}</text>
</svg>
'''


if __name__ == "__main__":
    from xml.etree import ElementTree as ET

    root = Path(__file__).resolve().parents[2]
    mapping = {
        ("dark", "credentials"): "insignia-credentials-dark.svg",
        ("light", "credentials"): "insignia-credentials-light.svg",
        ("dark", "focus"): "insignia-focus-dark.svg",
        ("light", "focus"): "insignia-focus-light.svg",
    }
    for (theme, kind), name in mapping.items():
        p = root / name
        p.write_text(card(theme, kind))
        ET.parse(p)
        print(f"ok {name}")
