"""Render index.html from the template, injecting the ASCII hands.

Usage: pip install numpy scipy pillow && python src/hands.py && python src/build.py
(hands.py only needs to run again when the drawing changes; src/hands.json is committed.)
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Public address of the site. Link previews need absolute URLs, so change this
# if the site is served from somewhere else (a custom domain, another repo name).
SITE = "https://techy-a.github.io/portfolio/"


def with_spark(art):
    """Escape the drawing and put a spark in the gap between the two fingertips."""
    lines = [list(l) for l in art["lines"]]
    (ar, ac), (gr, gc) = art["adam_tip"], art["god_tip"]
    r, c = round((ar + gr) / 2), round((ac + gc) / 2)
    while len(lines[r]) <= c:
        lines[r].append(" ")
    assert lines[r][c] == " ", "the spark must sit in empty space"
    out = []
    for i, row in enumerate(lines):
        if i == r:
            out.append(html.escape("".join(row[:c]), quote=False) + '<span class="spark">*</span>'
                       + html.escape("".join(row[c + 1:]), quote=False))
        else:
            out.append(html.escape("".join(row), quote=False))
    return "\n".join(out), f"{r},{c}"


hands = json.loads((ROOT / "src" / "hands.json").read_text())
page = (ROOT / "src" / "index.template.html").read_text(encoding="utf-8")
wide, spark_wide = with_spark(hands["wide"])
narrow, spark_narrow = with_spark(hands["narrow"])
count = sum(len(l.replace(" ", "")) for l in hands["wide"]["lines"])
for key, value in {
    "HANDS_WIDE": wide, "HANDS_NARROW": narrow,
    "SPARK_WIDE": spark_wide, "SPARK_NARROW": spark_narrow,
    "HANDS_COUNT": f"{count:,}", "SITE": SITE,
}.items():
    page = page.replace("{{" + key + "}}", value)
assert "{{" not in page
(ROOT / "index.html").write_text(page, encoding="utf-8")
print("wrote index.html,", count, "characters in the hands")
