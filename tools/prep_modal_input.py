"""Build CutClaw's input for the hybrid: worthiness-selected clips → one 480p concat.

Lore's front end picks the worthy clips; we concat them (time-ordered, normalized to a
uniform 480p 16:9 canvas, small enough to upload) and hand that to CutClaw's spine on
Modal, which does the actual compose (Playwriter/Editor/Reviewer) to the music. Reads
the volume read-only; writes the concat locally.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--day", required=True)
    ap.add_argument("--from-index", dest="from_index", default=os.path.join(ROOT, "analysis/volume/index.json"))
    ap.add_argument("--analysis", default="")
    ap.add_argument("--min-worth", type=float, default=0.5)
    ap.add_argument("--res", type=int, default=480)
    ap.add_argument("--out", default="")
    a = ap.parse_args()

    analysis = a.analysis or os.path.join(ROOT, f"analysis/volume/{a.day}_analysis.json")
    index = json.load(open(a.from_index))
    day = next((d for d in index["days"] if d["day"] == a.day), None)
    keymap = {c["key"]: c["full"] for s in day["sessions"] for c in s["clips"] if c.get("full")}

    data = json.load(open(analysis))
    clips = [c for c in data["clips"]
             if not str(c.get("caption", "")).startswith("[")
             and float(c.get("worthiness", 0)) >= a.min_worth and c.get("timestamp")]
    clips.sort(key=lambda c: c["timestamp"])

    def src(c):
        m = re.search(r"(\d{8})_(\d{6})_(\d+)", c["file"])
        return keymap.get(f"{m.group(1)}_{m.group(2)}_{m.group(3)}") if m else None

    w = (a.res * 16 // 9) // 2 * 2
    out = a.out or os.path.join(ROOT, f"analysis/volume/{a.day}_selected.mp4")
    total = 0.0
    with tempfile.TemporaryDirectory() as tmp:
        segs, boundaries, cum = [], [], 0
        for i, c in enumerate(clips):
            p = src(c)
            if not p or not os.path.exists(p):
                print(f"  skip {c['file']} (no full-res)"); continue
            seg = os.path.join(tmp, f"s{i:03d}.mp4")
            r = subprocess.run(
                ["ffmpeg", "-v", "error", "-i", p,
                 "-vf", f"scale={w}:{a.res}:force_original_aspect_ratio=increase,crop={w}:{a.res},fps=30,setsar=1,format=yuv420p",
                 "-c:v", "libx264", "-preset", "veryfast", "-crf", "26",
                 "-c:a", "aac", "-ar", "48000", "-ac", "2", "-y", seg], capture_output=True, text=True)
            if r.returncode == 0 and os.path.exists(seg):
                n = round(float(c.get("duration_s", 60)) * 30)   # 30 fps concat
                boundaries.append((cum, cum + n)); cum += n
                segs.append(seg)
                total += float(c.get("duration_s", 60))
                print(f"  [{c['worthiness']:.2f}] {c['timestamp'][11:16]} {c.get('activity','')[:22]}")
        if not segs:
            print("no clips selected"); return 1
        lst = os.path.join(tmp, "list.txt")
        open(lst, "w").write("".join(f"file '{s}'\n" for s in segs))
        subprocess.run(["ffmpeg", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst,
                        "-c", "copy", "-y", out], check=True)
    sz = os.path.getsize(out) / 1e6
    shots = out[:-4] + "_shots.txt"   # known cut points → CutClaw skips its (failing) detection
    open(shots, "w").write("\n".join(f"{s} {e}" for s, e in boundaries) + "\n")
    print(f"\n✅ {len(segs)} clips · ~{total/60:.1f} min · {sz:.0f}MB → {out}")
    print(f"   shots → {shots} ({len(boundaries)} boundaries)")
    print(f"   upload: modal volume put lore-data \"{out}\" {a.day}_selected.mp4")
    print(f"           modal volume put lore-data \"{shots}\" {a.day}_selected_shots.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
