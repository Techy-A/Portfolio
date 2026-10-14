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
SEAM_PCT = 91              # the very strongest, on their dark side, are left open as a shadow seam
EDGE_PCT = 90              # the strongest light-to-dark steps inside the hand (a lit finger over a shaded one) become creases
CELL_ASPECT = 2.0          # a character cell is about twice as tall as it is wide
BINS = 8                   # colour bins for tinting
FADE = 0.05               # share of the width over which the arms fade out
FLOOR = 2                 # lowest ramp step for skin inside the outline (",")
DARK = 0.12               # how much darkness counts toward being skin (the shaded underside of a forearm)
GAP = (0.3792, 0.4538)     # the point between the two fingertips, as fractions of the fresco
WIDE = (0.293, 0.365, 0.472, 0.528)   # both hands, with a short stretch of each forearm
NARROW = (0.345, 0.385, 0.44, 0.52)   # phones: the fingertips about to touch


def strip_halos(lines, tints, fading, faint=" .,:;'`", min_len=3):
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

    # the plaster is pale (brightness above 0.85) and nearly grey (saturation 0.11 to 0.18).
    # Lit skin is more saturated (0.24 and up); shaded skin, like the underside of
    # Adam's forearm, can be as grey as 0.20 but is always darker, so darkness
    # counts toward being skin as well
    hsv = np.asarray(big.convert("HSV"), float) / 255
    s, v = hsv[..., 1], hsv[..., 2]
    score = ndimage.gaussian_filter(np.maximum(s, s + DARK * (0.86 - v)), 1.5)
    # hysteresis: keep regions that are at least faintly skin-coloured AND contain
    # clearly skin-coloured pixels; warm stains in the plaster are only the former
    mask = ndimage.binary_opening(score > sat_cut, iterations=4)
    lab, n = ndimage.label(mask)
    core = ndimage.maximum(score, lab, range(1, n + 1))
    mask = np.isin(lab, [i + 1 for i, m in enumerate(core) if m > sat_cut + 0.12])
    # fill only small holes, so plaster seen between hanging fingers stays open
    holes = ndimage.binary_fill_holes(mask) & ~mask
    hl, hn = ndimage.label(holes)
    hs = ndimage.sum(holes, hl, range(1, hn + 1))
    mask |= np.isin(hl, [i + 1 for i, z in enumerate(hs) if z < 0.0015 * mask.size])
    lab, n = ndimage.label(mask)
    sizes = ndimage.sum(mask, lab, range(1, n + 1))
    mask = np.isin(lab, [i + 1 for i, z in enumerate(sizes) if z > 0.01 * mask.size])
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
        return strength, coh, (-(np.degrees(phi) + 90)) % 180, cell(gx), cell(gy)

    m_str, m_coh, m_ang, m_gx, m_gy = tensor(mask.astype(float), 1.5)   # silhouette
    l_str, l_coh, l_ang, l_gx, l_gy = tensor(lum, 1.2)                  # where a lit finger lies over a shaded one
    # rank creases only among cells inside the hand: the silhouette is always the
    # strongest edge and would otherwise crowd out the finger-over-finger steps
    inside = (cov >= 0.8) & ~fading
    cut = np.percentile(l_str[inside], EDGE_PCT) if inside.any() else 1
    seam = np.percentile(l_str[inside], SEAM_PCT) if inside.any() else 1

    def outline(a, gx, gy):
        """Outline glyph that follows the shape and sits on the skin side of the cell."""
        if a < 22.5 or a >= 157.5:
            return "_" if gy > 0 else "-"
        if 67.5 <= a < 112.5:
            return "(" if gx > 0 else ")"
        return "/" if a < 67.5 else "\\"

    def crease(a):
        if a < 22.5 or a >= 157.5:
            return "_"
        return "/" if a < 67.5 else "|" if a < 112.5 else "\\"

    top = len(RAMP) - 1
    lines, tints = [], []
    for i in range(rows):
        row, tint = [], []
        for j in range(cols):
            # where the arm fades out at the left and right edges it dissolves into
            # a scatter; everywhere else the hand gets a drawn outline
            if fading[i, j]:
                drop = cov[i, j] < 0.3 or (cov[i, j] < 0.9 and grain[i, j] > cov[i, j] ** 1.5)
            else:
                drop = cov[i, j] < 0.3
            if drop:
                row.append(" "), tint.append(-1)
                continue
            if contours and not fading[i, j] and cov[i, j] < 0.8:
                ch = outline(m_ang[i, j], m_gx[i, j], m_gy[i, j])
            elif contours and inside[i, j] and l_str[i, j] > seam and t[i, j] < 0.5:
                # the deepest step, on its dark side, is left open: a shadow seam
                # like the one Michelangelo paints between overlapping fingers
                row.append(" "), tint.append(-1)
                continue
            elif contours and inside[i, j] and l_str[i, j] > cut and l_coh[i, j] > 0.5:
                ch = crease(l_ang[i, j])
            elif fading[i, j]:
                # the arm dissolves into dust: lighter characters as it fades
                ch = RAMP[max(1, int(t[i, j] * min(1.0, cov[i, j]) ** 1.5 * top + 0.5))]
            else:
                ch = RAMP[max(1, min(top, int(FLOOR + t[i, j] * (top - FLOOR) + 0.5)))]
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
    return {"lines": lines, "tints": tints, "cols": cols, "rows": len(lines), "spark": [sr, sc],
            "crop": list(crop), "trim": used[0], "grid_rows": rows}


def main():
    global FADE
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--cols", type=int, default=300)
    ap.add_argument("--narrow-cols", type=int, default=110)
    ap.add_argument("--sat", type=float, default=0.19, help="skin score (saturation, plus darkness) above which a pixel counts as skin")
    ap.add_argument("--gamma", type=float, default=0.85)
    a = ap.parse_args()
    wide = convert(a.image, WIDE, a.cols, a.sat, a.gamma, contours=True, local=1.0)
    FADE = 0.08
    narrow = convert(a.image, NARROW, a.narrow_cols, a.sat, a.gamma, contours=True, local=1.0)
    out = {"wide": wide, "narrow": narrow}
    (ROOT / "src" / "fresco.json").write_text(json.dumps(out))
    for k, v in out.items():
        print(k, v["rows"], "rows x", v["cols"], "cols, spark at", v["spark"],
              "characters", sum(len(l.replace(" ", "")) for l in v["lines"]))


if __name__ == "__main__":
    main()
