"""Portrait as a stippled dot cloud with a staggered per-dot reveal animation,
matching arifhaxn's VISUAL.MAP technique (confirmed by inspecting his live
profile's rendered SVG). Background-invariant: luminance diff from an
estimated background (sampled from the image corners) decides whether a cell
draws a dot at all, and how many/how large. Safety pattern: each dot's base
`opacity` attribute IS its final value — the <animate> only interpolates FROM
0, so the portrait renders correctly even if the animation never executes
(e.g. a rendering context that ignores SMIL)."""
import math
import random
from PIL import Image

MAX_DOTS_PER_CELL = 2
DOT_R_MIN, DOT_R_MAX = 0.55, 1.15
SWEEP_SECONDS = 1.6
FADE_DUR = 0.45


def build(path: str, accent: str, box_w: float, box_h: float, cols: int = 46, seed: int = 7) -> str:
    rng = random.Random(seed)
    rows = round(cols * box_h / box_w)
    im = Image.open(path).convert("L").resize((cols, rows), Image.LANCZOS)
    px = im.load()

    corners = [px[0, 0], px[cols - 1, 0], px[0, rows - 1], px[cols - 1, rows - 1]]
    bg = sum(corners) / len(corners) / 255.0

    cell_w, cell_h = box_w / cols, box_h / rows
    cx0, cy0 = box_w / 2, box_h / 2
    max_dist = math.hypot(cx0, cy0)

    out = []
    for ry in range(rows):
        for rx in range(cols):
            lum = px[rx, ry] / 255.0
            diff = min(1.0, abs(lum - bg) * 2.4)
            if diff < 0.08:
                continue
            n_dots = max(1, round(diff * MAX_DOTS_PER_CELL))
            base_x, base_y = rx * cell_w, ry * cell_h
            for _ in range(n_dots):
                dx = base_x + rng.uniform(0.1, cell_w - 0.1)
                dy = base_y + rng.uniform(0.1, cell_h - 0.1)
                r = DOT_R_MIN + (DOT_R_MAX - DOT_R_MIN) * diff * rng.uniform(0.7, 1.0)
                opacity = 0.45 + diff * 0.55
                dist = math.hypot(dx - cx0, dy - cy0)
                begin = (dist / max_dist) * SWEEP_SECONDS + rng.uniform(0, 0.12)
                out.append(
                    f'<circle cx="{dx:.1f}" cy="{dy:.1f}" r="{r:.2f}" fill="{accent}" opacity="{opacity:.2f}">'
                    f'<animate attributeName="opacity" values="0;{opacity:.2f}" dur="{FADE_DUR}s" '
                    f'begin="{begin:.2f}s" fill="freeze" calcMode="spline" keySplines=".4 0 .2 1"/>'
                    f'</circle>'
                )
    return "\n".join(out)
