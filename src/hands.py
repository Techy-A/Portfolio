"""Draw the two hands from The Creation of Adam as ASCII line art.

The hands are modelled here as tubes and palms (no image is traced). Each part
is drawn in front-to-back order as an outline that hides the outlines behind
it, then every character cell is matched against rendered ASCII glyphs and the
closest glyph wins.

Usage: pip install numpy scipy pillow && python src/hands.py
Writes src/hands.json, which build.py reads.
"""
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
CW, CH = 10, 20
COLS = ROWS = W = H = S = 0


def setup(cols, rows):
    global COLS, ROWS, W, H, S
    COLS, ROWS = cols, rows
    W, H = COLS * CW, ROWS * CH
    S = W / (1105 - X0)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
GLYPHS = " .,'`-_/\\|()"
SHADES = " "                      # interior left empty: line art reads best on black
# The scene is described on a 1320-wide sketch and mapped into the grid.
X0, Y0 = 215, 330
DY = 35

PARTS = [
    # name, kind, points, widths. Listed back to front.
    ("adam", "stroke", [(-80, 560), (150, 520), (330, 470)], [150, 135, 115]),                       # forearm
    ("adam", "stroke", [(360, 500), (420, 520), (470, 530), (505, 528)], [46, 40, 34, 28]),          # thumb
    ("adam", "poly", [(320, 410), (400, 395), (480, 410), (488, 470), (420, 500), (330, 525)], None),  # back of hand
    ("adam", "stroke", [(470, 478), (510, 515), (530, 550), (532, 570)], [32, 30, 26, 22]),          # little
    ("adam", "stroke", [(478, 460), (530, 495), (560, 535), (566, 560)], [37, 34, 30, 25]),          # ring
    ("adam", "stroke", [(478, 440), (540, 468), (580, 505), (594, 532)], [40, 37, 33, 28]),          # middle
    ("adam", "stroke", [(470, 418), (530, 425), (570, 440), (596, 458), (606, 474)], [40, 38, 34, 30, 26]),  # index
    ("god", "stroke", [(1200, 380 + DY), (1040, 392 + DY), (900, 400 + DY)], [140, 128, 112]),        # forearm
    ("god", "stroke", [(880, 445 + DY), (835, 465 + DY), (790, 473 + DY), (760, 470 + DY)], [46, 40, 34, 28]),  # thumb
    ("god", "poly", [(910, 345 + DY), (850, 342 + DY), (790, 360 + DY), (782, 420 + DY), (820, 450 + DY), (900, 452 + DY), (920, 445 + DY)], None),
    ("god", "stroke", [(808, 436 + DY), (780, 452 + DY), (768, 468 + DY), (774, 480 + DY)], [32, 30, 26, 22]),  # little, curled
    ("god", "stroke", [(800, 418 + DY), (762, 434 + DY), (744, 454 + DY), (750, 470 + DY)], [37, 34, 30, 25]),  # ring, curled
    ("god", "stroke", [(794, 398 + DY), (748, 410 + DY), (722, 428 + DY), (722, 448 + DY)], [40, 37, 33, 28]),  # middle, half curled
    ("god", "stroke", [(796, 374 + DY), (744, 378 + DY), (700, 383 + DY), (668, 388 + DY)], [41, 38, 34, 29]),  # index, straight
]
SLEEVE_FOLDS = []
# parts merged into one outline per hand: forearm and back of hand
BASES = {"adam": [0, 2], "god": [7, 9]}


def tx(p):
    return ((p[0] - X0) * S, (p[1] - Y0) * S)


def tube_mask(points, widths):
    img = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    pts = [tx(p) for p in points]
    for (x0, y0), (x1, y1), w0, w1 in zip(pts, pts[1:], widths, widths[1:]):
        steps = max(2, int(math.hypot(x1 - x0, y1 - y0) / 2))
        for i in range(steps + 1):
            t = i / steps
            x, y, r = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, S * (w0 + (w1 - w0) * t) / 2
            d.ellipse([x - r, y - r, x + r, y + r], fill=255)
    return np.array(img) > 127


def poly_mask(points):
    img = Image.new("L", (W, H), 0)
    ImageDraw.Draw(img).polygon([tx(p) for p in points], fill=255)
    return ndimage.binary_opening(np.array(img) > 127, iterations=8)


def shade(mask, radius):
    """Height from distance to the edge, then Lambert light from the upper left."""
    dist = ndimage.distance_transform_edt(mask)
    h = np.clip(dist / radius, 0, 1) ** 0.6
    gy, gx = np.gradient(ndimage.gaussian_filter(h, 3))
    nx, ny, nz = -gx * 14, -gy * 14, np.ones_like(h)
    norm = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
    lam = np.clip((nx * -0.55 + ny * -0.65 + nz * 0.52) / norm, 0, 1)
    return np.where(mask, lam * (0.45 + 0.55 * h), 0)


def glyph_tiles():
    font = ImageFont.truetype(FONT, 16.6)
    tiles = []
    for g in GLYPHS:
        img = Image.new("L", (CW, CH), 0)
        ImageDraw.Draw(img).text((0, 1), g, font=font, fill=255)
        tiles.append(ndimage.gaussian_filter(np.array(img, float) / 255, 1.2))
    return tiles


def draw(cols, rows):
    setup(cols, rows)
    lines = np.zeros((H, W))
    who = np.full((H, W), "", dtype=object)
    # forearm, thumb root and back of hand are one surface: merge them so no wrist line is drawn
    masks = []
    for name, kind, pts, widths in PARTS:
        masks.append((name, tube_mask(pts, widths) if kind == "stroke" else poly_mask(pts)))
    merged = []
    for i, (name, m) in enumerate(masks):
        if i in BASES[name][:-1]:
            continue
        if i == BASES[name][-1]:
            m = np.logical_or.reduce([masks[j][1] for j in BASES[name]])
        merged.append((name, m))
    light = np.zeros((H, W))
    inside = np.zeros((H, W), bool)
    for name, m in merged:
        light[m] = shade(m, 26 * S)[m]
        inside |= m
        lines[m] = 0                                  # this part hides what is behind it
        rim = m & ~ndimage.binary_erosion(m, iterations=3, border_value=1)
        lines[rim] = 1
        who[m] = name
    img = Image.fromarray((lines * 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    for f in SLEEVE_FOLDS:
        d.line([tx(p) for p in f], fill=255, width=2)
    lines = np.array(img, float) / 255
    # arms dissolve toward the left and right edges, as in the usual crop of the fresco
    xs = np.linspace(0, 1, W)
    fade = np.clip(np.minimum(xs, 1 - xs) / 0.16, 0, 1) ** 1.5
    lines = lines * fade[None, :]
    light = light * fade[None, :]
    blur = ndimage.gaussian_filter(lines, 1.2)

    tiles = glyph_tiles()
    text, classes = [], []
    for r in range(ROWS):
        row, cls = [], []
        for c in range(COLS):
            cell = blur[r * CH:(r + 1) * CH, c * CW:(c + 1) * CW]
            names = who[r * CH:(r + 1) * CH, c * CW:(c + 1) * CW]
            filled = names[names != ""]
            cls.append(max(set(filled), key=list(filled).count) if len(filled) else "")
            if cell.max() < 0.12:
                block = (slice(r * CH, (r + 1) * CH), slice(c * CW, (c + 1) * CW))
                cov = inside[block].mean()
                v = light[block][inside[block]].mean() if cov > 0.6 else 0
                row.append(SHADES[min(len(SHADES) - 1, int(v * len(SHADES)))] if cov > 0.6 else " ")
                continue
            best = min(range(len(GLYPHS)), key=lambda i: ((tiles[i] - cell) ** 2).sum())
            row.append(GLYPHS[best])
        text.append("".join(row).rstrip())
        classes.append(cls)

    used = [i for i, t in enumerate(text) if t.strip()]
    text, classes = text[used[0]:used[-1] + 1], classes[used[0]:used[-1] + 1]
    runs = []
    for r, cls in enumerate(classes):
        c = 0
        while c < len(cls):
            if cls[c] == "sleeve":
                s = c
                while c < len(cls) and cls[c] == "sleeve":
                    c += 1
                runs.append([r, s, c])
            else:
                c += 1
    adam = [(r, c) for r, cls in enumerate(classes) for c, n in enumerate(cls) if n == "adam"]
    god = [(r, c) for r, cls in enumerate(classes) for c, n in enumerate(cls) if n == "god"]
    a_tip = max(adam, key=lambda p: p[1])
    g_tip = min(god, key=lambda p: p[1])
    return {"lines": text, "sleeve": runs, "cols": COLS, "rows": len(text),
            "adam_tip": list(a_tip), "god_tip": list(g_tip)}


def main():
    out = {"wide": draw(150, 30), "narrow": draw(92, 20)}
    (ROOT / "src" / "hands.json").write_text(json.dumps(out))
    for k, v in out.items():
        print("\n".join(v["lines"]))
        print(k, "rows", v["rows"], "adam tip", v["adam_tip"], "god tip", v["god_tip"],
              "characters", sum(len(l.replace(" ", "")) for l in v["lines"]))


if __name__ == "__main__":
    main()
