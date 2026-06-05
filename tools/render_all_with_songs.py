"""Re-render every qualifying capture-day with a mood-matched song from songs/.

Songs are matched by a keyword substring (robust to exact filenames with spaces /
unicode). Edit MAP to re-assign. Writes a manifest of day → theme → song → output.
Reads the volume read-only; outputs to analysis/volume/.
"""
from __future__ import annotations

import glob
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = os.path.join(ROOT, ".venv", "bin", "python")
SONGS = os.path.join(ROOT, "songs")
INDEX = os.path.join(ROOT, "analysis", "volume", "index.json")

# (capture-day, song keyword, min-worthiness floor, theme) — mood-matched.
MAP = [
    ("2026-01-18", "Midnight City",  0.5,  "waterfall hike"),
    ("2026-03-25", "restless",       0.5,  "sunrise → hike → camp"),
    ("2026-05-23", "Where'd",        0.4,  "overnight camping trip"),
    ("2026-05-22", "Dopamine",       0.45, "stargazing + nature"),
    ("2026-05-02", "Spring Snow",    0.35, "coastal day"),
    ("2026-05-24", "Hang",           0.4,  "hike + friends road trip"),
    ("2026-04-04", "YOUHA",          0.4,  "biking + street food"),
    ("2026-04-02", "Frisky",         0.4,  "biking + photos"),
    ("2026-03-24", "Koi Ni",         0.4,  "brunch + stargazing"),
    ("2026-03-26", "Count On Me",    0.4,  "casual day out"),
    ("2026-05-09", "WENDY",          0.4,  "friends hangout"),
]


def find_song(kw: str) -> str | None:
    for f in sorted(glob.glob(os.path.join(SONGS, "*.mp3"))):
        if kw.lower() in os.path.basename(f).lower():
            return f
    return None


def main() -> int:
    manifest = []
    for day, kw, mw, theme in MAP:
        song = find_song(kw)
        if not song:
            print(f"!! no song matching '{kw}' for {day}"); continue
        out = os.path.join(ROOT, "analysis", "volume", f"{day}_recap.mp4")
        rc = subprocess.run(
            [PY, os.path.join(ROOT, "tools", "compose_recap.py"),
             "--analysis", os.path.join(ROOT, "analysis", "volume", f"{day}_analysis.json"),
             "--from-index", INDEX, "--day", day, "--music", song,
             "--target-seconds", "55", "--beats-per-cut", "4", "--duck",
             "--min-worthiness", str(mw), "--out", out], cwd=ROOT).returncode
        ok = rc == 0 and os.path.exists(out)
        print(f"{'OK  ' if ok else 'FAIL'} {day}  {theme:<26} ← {os.path.basename(song)}")
        manifest.append({"day": day, "theme": theme, "song": os.path.basename(song),
                         "out": f"analysis/volume/{day}_recap.mp4", "ok": ok})
    json.dump(manifest, open(os.path.join(ROOT, "analysis", "volume", "recaps_manifest.json"), "w"), indent=2)
    print(f"\n{sum(m['ok'] for m in manifest)}/{len(manifest)} rendered · manifest → analysis/volume/recaps_manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
