"""Static checks for the site. No dependencies; runs locally and in CI.

1. index.html is up to date with src/index.template.html (build output committed).
2. Every text file is plain 7-bit ASCII (no em dashes, en dashes or emoji).
3. Every local file the page references exists.
4. No competition rank is claimed anywhere.

Usage: python scripts/check.py   (exit code 1 on any failure)
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEXT = [p for p in ROOT.rglob("*") if p.is_file() and p.suffix in {".html", ".md", ".txt", ".py", ".json", ".yml", ".js", ".css"}
        and not {".git", "node_modules", "test-results", "playwright-report"} & set(p.parts)]
failures = []

# 1. build is current
before = (ROOT / "index.html").read_bytes()
subprocess.run([sys.executable, str(ROOT / "src" / "build.py")], check=True, capture_output=True)
if (ROOT / "index.html").read_bytes() != before:
    failures.append("index.html was out of date with src/index.template.html (now rebuilt: commit it)")

# 2. plain ASCII
for p in TEXT:
    for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        bad = [c for c in line if ord(c) > 127]
        if bad:
            failures.append(f"{p.relative_to(ROOT)}:{n}: non-ASCII {sorted(set(bad))!r}")

# 3. local references resolve
page = (ROOT / "index.html").read_text(encoding="utf-8")
for ref in sorted(set(re.findall(r'(?:src|href|srcset|poster)="([^"#:]+?)(?:\s+\d+w)?"', page))):
    for part in ref.split(","):
        path = part.strip().split(" ")[0]
        if path and not path.startswith(("/", "{")) and not (ROOT / path).exists():
            failures.append(f"index.html references a missing file: {path}")

# 4. no rank claims
for p in TEXT:
    text = p.read_text(encoding="utf-8", errors="replace")
    if p.name != "check.py" and re.search(r"\b(2nd|second) (place|on the (public )?leaderboard)", text, re.I):
        failures.append(f"{p.relative_to(ROOT)}: claims a competition rank")

for f in failures:
    print("FAIL", f)
print(f"{len(TEXT)} text files checked, {len(failures)} failure(s)")
sys.exit(1 if failures else 0)
