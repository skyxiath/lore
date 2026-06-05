"""Lore stage-1 metadata day-arc — the narrative spine, with zero API cost.

Parses VID_YYYYMMDD_HHMMSS_*.mp4 timestamps + ffprobe durations into the capture
timeline, clusters clips into chapters by inter-clip gap (gaps = deliberate
ellipses), and emits a JSON artifact the Playwriter can plan against. This is
Lore's metadata-as-narrative-arc contribution; it needs no LLM and no heavy deps.

Usage: python3 tools/metadata_arc.py --clips "tests/test 1/raw clips" [--chapter-gap-min 25]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from datetime import datetime

TS_RE = re.compile(r"VID_(\d{8})_(\d{6})_(\d+)")


def ffprobe(path: str) -> tuple[float, bool, str]:
    out = subprocess.run(["ffprobe", "-v", "quiet", "-print_format", "json",
                          "-show_format", "-show_streams", path],
                         capture_output=True, text=True).stdout
    try:
        info = json.loads(out)
    except Exception:
        return 0.0, False, "?"
    dur = float(info.get("format", {}).get("duration", 0) or 0)
    streams = info.get("streams", [])
    has_a = any(s.get("codec_type") == "audio" for s in streams)
    v = next((s for s in streams if s.get("codec_type") == "video"), {})
    res = f"{v.get('width', '?')}x{v.get('height', '?')}"
    return dur, has_a, res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--clips", required=True)
    ap.add_argument("--chapter-gap-min", type=float, default=25.0,
                    help="inter-clip gap (min) above which a new chapter/ellipsis begins")
    ap.add_argument("--out", default="")
    a = ap.parse_args()

    files = sorted(f for f in os.listdir(a.clips) if f.lower().endswith(".mp4") and TS_RE.search(f))
    clips = []
    for f in files:
        m = TS_RE.search(f)
        ts = datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S")
        dur, has_a, res = ffprobe(os.path.join(a.clips, f))
        clips.append({"file": f, "timestamp": ts, "duration_s": round(dur, 1),
                      "has_audio": has_a, "resolution": res})
    clips.sort(key=lambda c: c["timestamp"])

    t0 = clips[0]["timestamp"]
    chapters, cur = [], []
    prev = None
    for c in clips:
        gap = (c["timestamp"] - prev).total_seconds() / 60 if prev else 0.0
        c["gap_to_prev_min"] = round(gap, 1)
        c["offset_from_start_s"] = round((c["timestamp"] - t0).total_seconds(), 1)
        if prev and gap > a.chapter_gap_min and cur:
            chapters.append(cur); cur = []
        cur.append(c); prev = c["timestamp"]
    if cur:
        chapters.append(cur)

    total = sum(c["duration_s"] for c in clips)
    span_h = (clips[-1]["timestamp"] - t0).total_seconds() / 3600
    artifact = {
        "n_clips": len(clips), "total_footage_s": round(total, 1),
        "capture_span_hours": round(span_h, 2),
        "start": t0.isoformat(), "end": clips[-1]["timestamp"].isoformat(),
        "chapter_gap_min": a.chapter_gap_min, "n_chapters": len(chapters),
        "all_have_audio": all(c["has_audio"] for c in clips),
        "chapters": [
            {"index": i, "start": ch[0]["timestamp"].isoformat(),
             "end": ch[-1]["timestamp"].isoformat(), "n_clips": len(ch),
             "duration_s": round(sum(c["duration_s"] for c in ch), 1),
             "clips": [{**c, "timestamp": c["timestamp"].isoformat()} for c in ch]}
            for i, ch in enumerate(chapters)],
    }
    out = a.out or os.path.join(a.clips, os.pardir, "lore_out", "metadata_arc.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(artifact, f, indent=2)

    print(f"{len(clips)} clips · {total/60:.1f} min footage · {span_h:.1f} h span · "
          f"{'all' if artifact['all_have_audio'] else 'some'} have audio · "
          f"{len(chapters)} chapters (gap>{a.chapter_gap_min:g}m)\n")
    for ch in artifact["chapters"]:
        s = datetime.fromisoformat(ch["start"]).strftime("%H:%M")
        e = datetime.fromisoformat(ch["end"]).strftime("%H:%M")
        print(f"  ▸ Chapter {ch['index']}: {s}–{e}  ({ch['n_clips']} clips, {ch['duration_s']/60:.1f} min)")
        for c in ch["clips"]:
            t = datetime.fromisoformat(c["timestamp"]).strftime("%H:%M")
            print(f"       {t}  {c['duration_s']:>4.0f}s  {c['resolution']}")
        nxt = ch["index"] + 1
        if nxt < len(artifact["chapters"]):
            gnext = datetime.fromisoformat(artifact["chapters"][nxt]["start"]) - datetime.fromisoformat(ch["end"])
            print(f"       … ellipsis ({gnext.total_seconds()/60:.0f} min gap) …")
    print(f"\nartifact → {os.path.normpath(out)}")
    print("This is the Playwriter's narrative spine: chapters are place/time blocks, "
          "gaps are ellipses absorbed by the music structure.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
