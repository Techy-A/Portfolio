"""Write src/og.html, the 1200 x 627 link preview card. Screenshot it to og.png.

Usage: python src/og.py, then open src/og.html at 1200 x 627 and save a screenshot as og.png.
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(ROOT / "src"))
from build import to_html  # noqa: E402

art = to_html(json.loads((ROOT / "src" / "fresco.json").read_text())["wide"])

page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Link preview card</title>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;1,400;1,500&family=Geist+Mono:wght@400&display=swap" rel="stylesheet">
<style>
html, body {{ margin: 0; }}
body {{ width: 1200px; height: 627px; box-sizing: border-box; padding: 44px 64px 40px; background: #0B0B0B; color: #ECE8E1;
  display: flex; flex-direction: column; justify-content: space-between; overflow: hidden; font-family: "Geist Mono", monospace; }}
.top {{ display: flex; justify-content: space-between; align-items: baseline; }}
.name {{ font-family: "Cormorant Garamond", serif; font-weight: 500; font-size: 92px; line-height: .9; letter-spacing: -.02em; margin: 0; }}
.name i {{ font-weight: 400; color: #ABA59C; }}
.tag {{ font-size: 14px; letter-spacing: .14em; text-transform: uppercase; color: #ABA59C; }}
.tag span {{ color: #D4B06E; }}
pre {{ margin: 0 auto; font-family: "Geist Mono", monospace; font-size: 6.25px; line-height: 1.2; color: #ECE8E1; }}
.t0 {{ color: #7C5A36; }} .t1 {{ color: #98703F; }} .t2 {{ color: #A87E50; }} .t3 {{ color: #C09664; }}
.t4 {{ color: #D4AE80; }} .t5 {{ color: #E4C49C; }} .t6 {{ color: #F0D8B8; }} .t7 {{ color: #F8ECDA; }}
.spark {{ color: #D4B06E; }}
.bottom {{ display: flex; justify-content: space-between; align-items: baseline; border-top: 1px solid #242322; padding-top: 18px; }}
.lead {{ font-family: "Cormorant Garamond", serif; font-weight: 500; font-size: 32px; margin: 0; }}
.lead em {{ color: #D4B06E; }}
.fig {{ font-size: 13px; color: #8A847B; }}
</style></head><body>
<div class="top"><p class="name">Aryan <i>Awasthi</i></p><p class="tag">ML <span>/</span> AI <span>/</span> Data science</p></div>
<pre>{art}</pre>
<div class="bottom"><p class="lead">I try every reasonable answer, then <em>prove</em> which one is better.</p><p class="fig">after Michelangelo, c. 1512, in ASCII</p></div>
</body></html>
"""
(ROOT / "src" / "og.html").write_text(page, encoding="utf-8")
print("wrote src/og.html")
