"""Render index.html from the template, injecting the ASCII hands.

Usage: python src/build.py
(src/fresco.json is committed; regenerate it with src/fresco.py only if the rendering changes.)
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Public address of the site. Link previews need absolute URLs, so change this
# if the site is served from somewhere else (a custom domain, another repo name).
SITE = "https://techy-a.github.io/portfolio/"


def to_html(art):
    """Escape the drawing, group characters by tint into spans, and set the spark."""
    sr, sc = art["spark"]
    out = []
    for r, (line, tints) in enumerate(zip(art["lines"], art["tints"])):
        if r == sr:
            line = line.ljust(sc + 1)
            tints = tints + [-1] * (len(line) - len(tints))
            assert line[sc] == " ", "the spark must sit in the gap between the fingertips"
        row, c = [], 0
        while c < len(line):
            if r == sr and c == sc:
                row.append('<span class="spark">*</span>')
                c += 1
                continue
            tint, s = tints[c], c
            while c < len(line) and tints[c] == tint and not (r == sr and c == sc):
                c += 1
            chunk = html.escape(line[s:c], quote=False)
            row.append(chunk if tint < 0 or not chunk.strip() else f'<span class="t{tint}">{chunk}</span>')
        out.append("".join(row))
    return "\n".join(out)


def main():
    art = json.loads((ROOT / "src" / "fresco.json").read_text())
    page = (ROOT / "src" / "index.template.html").read_text(encoding="utf-8")
    count = sum(len(l.replace(" ", "")) for l in art["wide"]["lines"])
    for key, value in {
        "HANDS_WIDE": to_html(art["wide"]), "HANDS_NARROW": to_html(art["narrow"]),
        "HANDS_COUNT": f"{count:,}", "SITE": SITE,
    }.items():
        page = page.replace("{{" + key + "}}", value)
    assert "{{" not in page
    (ROOT / "index.html").write_text(page, encoding="utf-8")
    print("wrote index.html,", count, "characters in the hands")


if __name__ == "__main__":
    main()
