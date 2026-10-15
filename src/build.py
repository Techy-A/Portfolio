"""Render index.html from the template.

Usage: python src/build.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Public address of the site. Link previews need absolute URLs, so change this
# if the site is served from somewhere else (a custom domain, another repo name).
SITE = "https://techy-a.github.io/portfolio/"


def main():
    page = (ROOT / "src" / "index.template.html").read_text(encoding="utf-8")
    page = page.replace("{{SITE}}", SITE)
    assert "{{" not in page
    (ROOT / "index.html").write_text(page, encoding="utf-8")
    print("wrote index.html")


if __name__ == "__main__":
    main()
