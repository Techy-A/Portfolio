"""Render index.html from the template, injecting the FIGlet name lettering.

Usage: pip install pyfiglet && python src/build.py
"""
import html
from pathlib import Path

import pyfiglet

ROOT = Path(__file__).resolve().parent.parent


def letter(text, font):
    lines = [l.rstrip() for l in pyfiglet.figlet_format(text, font=font, width=300).split("\n")]
    while lines and not lines[-1].strip():
        lines.pop()
    return html.escape("\n".join(lines), quote=False)


page = (ROOT / "src" / "index.template.html").read_text(encoding="utf-8")
for key, text, font in [
    ("ROMAN_A", "ARYAN", "roman"),
    ("ROMAN_W", "AWASTHI", "roman"),
    ("BASIC_A", "ARYAN", "smslant"),
    ("BASIC_W", "AWASTHI", "smslant"),
]:
    page = page.replace("{{" + key + "}}", letter(text, font))
(ROOT / "index.html").write_text(page, encoding="utf-8")
print("wrote index.html")
