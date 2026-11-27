"""Render the Manim scenes in src/manim/scenes.py and encode them for the web.

What: for each scene, a Manim render (1280 x 640, 30 fps), then ffmpeg writes media/<name>.mp4 (H.264, plays in every
browser) and media/<name>.webp (the last frame, used as poster and as the reduced-motion still).
Why: the page ships plain video files; nobody needs Manim installed to build or test the site.
Output: media/<name>.mp4 and .webp for each scene in SCENES   (Manim's own cache goes to a temporary folder)
Usage: python src/manim/render.py [name ...]   (no names: all scenes)
"""
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCENES = {"FoldLeak": "folds", "GatePush": "gates", "Rrf": "rrf", "Arena": "arena", "Listen": "listen",
          "Lora": "lora", "Prune": "prune"}
ONLY = set(sys.argv[1:])            # optional: render only these output names, e.g. rrf arena


def run(*cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)


with tempfile.TemporaryDirectory() as tmp:
    for scene, name in SCENES.items():
        if ONLY and name not in ONLY:
            continue
        run(sys.executable, "-m", "manim", "render", "-q", "h", "--fps", "30", "--media_dir", tmp,
            "-o", name, str(ROOT / "src" / "manim" / "scenes.py"), scene)
        raw = next(Path(tmp).rglob(f"{name}.mp4"))
        out = ROOT / "media" / name
        out.parent.mkdir(exist_ok=True)
        run("ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-an", "-c:v", "libx264", "-crf", "27",
            "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", f"{out}.mp4")
        run("ffmpeg", "-y", "-loglevel", "error", "-sseof", "-0.1", "-i", str(raw), "-frames:v", "1",
            "-c:v", "libwebp", "-quality", "85", f"{out}.webp")
        print("wrote", *(f"media/{name}.{ext}" for ext in ("mp4", "webp")))
