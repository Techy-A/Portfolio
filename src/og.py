"""Write src/og.html, the 1200 x 627 link preview card. Screenshot it to og.png.

Usage: python src/og.py, then open src/og.html at 1200 x 627 and save a screenshot as og.png.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

page = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Link preview card</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500&family=Space+Mono&display=swap" rel="stylesheet">
<style>
html, body { margin: 0; }
body { width: 1200px; height: 627px; box-sizing: border-box; padding: 40px 64px 36px; background: #0F1013; color: #ECE9E3;
  display: flex; flex-direction: column; align-items: center; justify-content: space-between; overflow: hidden;
  font-family: "Space Grotesk", sans-serif; text-align: center; }
.tag { margin: 0; font: 14px "Space Mono", monospace; letter-spacing: .08em; text-transform: uppercase; color: #B0ACA4; }
.tag span { color: #D9B26F; }
.name { margin: 6px 0 0; font-size: 84px; line-height: 1; font-weight: 500; letter-spacing: -.045em; }
img { width: 660px; height: auto; display: block; mix-blend-mode: lighten; }
.lead { margin: 0; font-size: 28px; letter-spacing: -.015em; color: #B0ACA4; }
.lead em { font-style: normal; color: #D9B26F; }
</style></head><body>
<div><p class="tag">ML <span>/</span> model evaluation <span>/</span> open to roles</p><p class="name">Aryan Awasthi</p></div>
<img src="../adam.jpg" alt="">
<p class="lead">I try every reasonable answer, then <em>prove</em> which one is better.</p>
</body></html>
"""
(ROOT / "src" / "og.html").write_text(page, encoding="utf-8")
print("wrote src/og.html")
