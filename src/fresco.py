"""Render the hands from Michelangelo's Creation of Adam (public domain) as tonal ASCII.

The plaster behind the hands is pale and nearly grey while skin is saturated, so
the hands are separated from the wall by saturation, then every character cell gets a glyph from a fine
70-step density ramp by brightness, with edges sharpened first so the contours
of the fingers survive. Each cell also keeps the fresco's colour, binned to a
small warm palette, so the page can tint the characters.

The source is the public-domain scan on Wikimedia Commons:
  https://upload.wikimedia.org/wikipedia/commons/5/5b/Michelangelo_-_Creation_of_Adam_%28cropped%29.jpg

Usage:
  pip install numpy scipy pillow
  curl -L -o adam.jpg "<the URL above>"
  python src/fresco.py adam.jpg
Writes src/fresco.json, which build.py reads.
"""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageOps
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
RAMP = " .,:;-=+*#%@"        # symbols only, so no stray words appear
EDGE_PCT = 78              # cells above this edge-strength percentile get a contour glyph
CELL_ASPECT = 2.0          # a character cell is about twice as tall as it is wide
BINS = 8                   # colour bins for tinting
FADE = 0.14               # share of the width over which the arms fade out
FLOOR = 3                 # lowest ramp step for skin inside the outline (":")
EDGE_COV = 0.62           # an outline cell must be at least this much skin to be drawn
EDGE_MIN = 6              # and at least this dense ("="), so no faint ; - trails hug the fingers
GAP = (0.3792, 0.4538)     # the point between the two fingertips, as fractions of the fresco
WIDE = (0.315, 0.37, 0.465, 0.528)    # both hands, wrist to fingertip
NARROW = (0.345, 0.385, 0.44, 0.52)   # phones: the fingertips about to touch


def strip_halos(lines, tints, fading, faint=" .,:;-", min_len=3):
    """Remove one-row runs made only of the faintest characters that have nothing on
    one side of them: the soft cast shadow a finger leaves on the plaster."""
    rows = len(lines)
    grid = [list(l) for l in lines]
    blank = lambda r, a, b: r < 0 or r >= rows or not lines[r][a:b].strip()
    for r in range(rows):
        line, c = lines[r], 0
        while c < len(line):
            if line[c] == " ":
                c += 1
                continue
            s = c
            while c < len(line) and line[c] != " ":
                c += 1
            run = line[s:c]
            in_fade = fading[r, s:c].any() if r < fading.shape[0] else False
            if (len(run) >= min_len and all(ch in faint for ch in run) and not in_fade
                    and (blank(r - 1, s, c) or blank(r + 1, s, c))):
                for k in range(s, c):
                    grid[r][k] = " "
    out_l, out_t = [], []
    for row, tn in zip(grid, tints):
        s = "".join(row).rstrip()
        out_l.append(s)
        out_t.append([x if row[i] != " " else -1 for i, x in enumerate(tn[:len(s)])])
    return out_l, out_t


def despeckle(lines, tints, fading, min_cells=8):
    """Remove small clusters of characters that are not part of a hand (specks of
    plaster or stray outline), except in the fade zones where the scatter is wanted."""
    rows, cols = len(lines), max(len(l) for l in lines)
    ink = np.zeros((rows, cols), bool)
    for i, l in enumerate(lines):
        ink[i, :len(l)] = [ch != " " for ch in l]
    keep_fade = np.zeros_like(ink)
    keep_fade[:, :fading.shape[1]] = fading[:rows, :cols]
    # characters with at most one neighbour are loose flecks
    for _ in range(2):
        nb = ndimage.convolve(ink.astype(int), np.ones((3, 3), int), mode="constant") - ink
        ink &= (nb >= 2) | keep_fade
    lab, n = ndimage.label(ink, structure=np.ones((3, 3)))
    sizes = ndimage.sum(ink, lab, range(1, n + 1))
    small = ~ink | np.isin(lab, [k + 1 for k, s in enumerate(sizes) if s < min_cells]) & ~keep_fade
    out_l, out_t = [], []
    for i, (l, tn) in enumerate(zip(lines, tints)):
        chars, tt = list(l), list(tn)
        for j in range(len(chars)):
            if small[i, j]:
                chars[j], tt[j] = " ", -1
        s = "".join(chars).rstrip()
        out_l.append(s)
        out_t.append(tt[:len(s)])
    return out_l, out_t


def convert(path, crop, cols, sat_cut, gamma, contours=True, local=0.8):
    img = Image.open(path).convert("RGB")
    w, h = img.size
    x0, y0, x1, y1 = crop
    img = img.crop((int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h)))
    rows = max(1, round(cols * img.size[1] / img.size[0] / CELL_ASPECT))

    # work at 4 x 8 pixels per cell, then average
    big = img.resize((cols * 4, rows * 8), Image.LANCZOS)
    rgb = np.asarray(big, float) / 255

    # the plaster behind the hands is pale and nearly grey (saturation about 0.13);
    # skin, lit or shaded, is clearly more saturated (0.24 and up)
    hsv = np.asarray(big.convert("HSV"), float) / 255
    sat = ndimage.gaussian_filter(hsv[..., 1], 1.5)
    mask = sat > sat_cut
    mask = ndimage.binary_opening(mask, iterations=2)
    mask = ndimage.binary_fill_holes(mask)
    lab, n = ndimage.label(mask)
    sizes = ndimage.sum(mask, lab, range(1, n + 1))
    mask = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s > 0.01 * mask.size])
    soft = ndimage.gaussian_filter(mask.astype(float), 1.2)

    # tone: luminance stretched over the skin only, then local contrast so the
    # shaded fingers keep their form instead of sinking into the dark
    lum = np.asarray(big.convert("L"), float) / 255
    lo, hi = np.percentile(lum[mask], [2, 98])
    lum = np.clip((lum - lo) / max(hi - lo, 1e-6), 0, 1)
    detail = lum - ndimage.gaussian_filter(lum, 10)
    lum = np.clip(0.18 + 0.82 * lum + local * detail, 0, 1)
    tone = lum ** gamma

    # the forearms dissolve toward the left and right edges
    xs = np.linspace(0, 1, cols * 4)
    fade = np.clip(np.minimum(xs, 1 - xs) / FADE, 0, 1) ** 1.2 if FADE > 0 else np.ones_like(xs)
    soft = soft * fade[None, :]

    cell = lambda a: a.reshape(rows, 8, cols, 4).mean(axis=(1, 3))
    t = cell(tone * soft) / np.maximum(cell(soft), 1e-6)
    cov = cell(soft)
    rng = np.random.default_rng(7)
    grain = rng.random(cov.shape)
    fading = cell(np.broadcast_to(fade[None, :], soft.shape)) < 0.999   # only the arm ends dissolve
    col = np.stack([cell(rgb[..., i] * soft) / np.maximum(cov, 1e-6) for i in range(3)], -1)

    def tensor(src, sigma):
        gy, gx = np.gradient(ndimage.gaussian_filter(src, sigma))
        jxx, jyy, jxy = cell(gx * gx), cell(gy * gy), cell(gx * gy)
        strength = np.sqrt(jxx + jyy)
        coh = np.sqrt((jxx - jyy) ** 2 + 4 * jxy ** 2) / np.maximum(jxx + jyy, 1e-12)
        phi = 0.5 * np.arctan2(2 * jxy, jxx - jyy)       # gradient angle on screen, y down
        return strength, coh, (-(np.degrees(phi) + 90)) % 180, cell(gy)

    m_str, m_coh, m_ang, m_gy = tensor(mask.astype(float), 1.0)   # silhouette
    l_str, l_coh, l_ang, l_gy = tensor(lum * mask, 1.2)           # creases and finger gaps
    inside = cov >= 0.3
    cut = np.percentile(l_str[inside], EDGE_PCT) if inside.any() else 1

    def glyph(a, gy):
        if a < 22.5 or a >= 157.5:
            return "_" if gy < 0 else "-"
        return "/" if a < 67.5 else "|" if a < 112.5 else "\\"

    lines, tints = [], []
    for i in range(rows):
        row, tint = [], []
        for j in range(cols):
            # a clean outline everywhere, except where the arm fades out at the
            # left and right edges, which keeps a scatter instead of a hard cut
            if fading[i, j]:
                drop = cov[i, j] < 0.3 or (cov[i, j] < 0.9 and grain[i, j] > cov[i, j] ** 1.5)
            else:
                drop = cov[i, j] < EDGE_COV
            if drop:
                row.append(" "), tint.append(-1)
                continue
            edge_of_hand = cov[i, j] < 0.85 and m_str[i, j] > 0
            if contours and edge_of_hand:
                ch = glyph(m_ang[i, j], -m_gy[i, j])
            elif contours and l_str[i, j] > cut and l_coh[i, j] > 0.5:
                ch = glyph(l_ang[i, j], l_gy[i, j])
            else:
                # shaded skin keeps a minimum density so the underside of a finger reads
                # as form, not as a trail of dots; the outline drops its faintest cells
                top = len(RAMP) - 1
                if fading[i, j]:
                    # the arm dissolves into dust: lighter characters as it fades
                    k = max(1, int(t[i, j] * min(1.0, cov[i, j]) ** 1.5 * top + 0.5))
                elif cov[i, j] >= 0.85:
                    k = int(FLOOR + t[i, j] * (top - FLOOR) + 0.5)
                else:
                    k = int(t[i, j] * top + 0.5)
                    if k < EDGE_MIN:
                        row.append(" "), tint.append(-1)
                        continue
                ch = RAMP[max(1, min(top, k))]
            row.append(ch)
            # colour follows the light: 0 = deep ochre shadow ... BINS-1 = plaster highlight
            tint.append(int(min(BINS - 1, max(0, t[i, j] * BINS))))
        lines.append("".join(row).rstrip())
        tints.append(tint[:len(lines[-1])])
    lines, tints = strip_halos(lines, tints, fading)
    lines, tints = despeckle(lines, tints, fading)
    used = [i for i, l in enumerate(lines) if l.strip()]
    lines, tints = lines[used[0]:used[-1] + 1], tints[used[0]:used[-1] + 1]
    # the spark sits midway between the two index fingertips: start from the known
    # point on the fresco, then centre it in the empty run of that row
    sr = int((GAP[1] - y0) / (y1 - y0) * rows) - used[0]
    sc = int((GAP[0] - x0) / (x1 - x0) * cols)
    row = lines[sr].ljust(cols)
    left = max((c for c in range(sc) if row[c] != " "), default=sc)
    right = min((c for c in range(sc + 1, cols) if row[c] != " "), default=sc)
    sc = (left + right) // 2
    return {"lines": lines, "tints": tints, "cols": cols, "rows": len(lines), "spark": [sr, sc]}


def main():
    global FADE
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--cols", type=int, default=280)
    ap.add_argument("--narrow-cols", type=int, default=110)
    ap.add_argument("--sat", type=float, default=0.19, help="saturation above which a pixel counts as skin")
    ap.add_argument("--gamma", type=float, default=0.85)
    a = ap.parse_args()
    wide = convert(a.image, WIDE, a.cols, a.sat, a.gamma, contours=False, local=1.0)
    FADE = 0.10
    narrow = convert(a.image, NARROW, a.narrow_cols, a.sat, a.gamma, contours=False, local=1.0)
    out = {"wide": wide, "narrow": narrow}
    (ROOT / "src" / "fresco.json").write_text(json.dumps(out))
    for k, v in out.items():
        print(k, v["rows"], "rows x", v["cols"], "cols, spark at", v["spark"],
              "characters", sum(len(l.replace(" ", "")) for l in v["lines"]))


if __name__ == "__main__":
    main()
