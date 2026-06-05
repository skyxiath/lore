"""Read-only index of a camera archive → candidate 'videos' (capture days/sessions).

Insta360 archives store each clip twice (full-res VID_*.mp4 + low-res LRV_*.lrv proxy)
and group by OFFLOAD date, not capture date. This tool dedupes to unique clips, reads
the capture timestamp from the FILENAME (VID/LRV_YYYYMMDD_HHMMSS_NNN), groups into
days→sessions by time gap, and ranks candidate recaps by density. NEVER writes to the
source volume (filename parsing only; no ffprobe needed for the index).

Usage: python3 tools/index_volume.py --root "/Volumes/.../Insta360 Go Ultra" \
         --out analysis/volume/index.json [--session-gap-min 45]
"""
from __future__ import annotations

import argparse
import json
import os
import re
from collections import defaultdict
from datetime import datetime

TS_RE = re.compile(r"(?:VID|LRV|PRO)_?(\d{8})_(\d{6})_(\d+)", re.IGNORECASE)
VID_EXT = {".mp4", ".mov", ".m4v"}
PROXY_EXT = {".lrv"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", default="analysis/volume/index.json")
    ap.add_argument("--session-gap-min", type=float, default=45.0)
    a = ap.parse_args()

    # key = YYYYMMDD_HHMMSS_NNN  → dedupe full-res + proxy under one moment
    moments: dict[str, dict] = {}
    unmatched = 0
    for dirpath, _, files in os.walk(a.root):
        for f in files:
            if f.startswith("."):
                continue
            ext = os.path.splitext(f)[1].lower()
            if ext not in VID_EXT and ext not in PROXY_EXT:
                continue
            m = TS_RE.search(f)
            if not m:
                unmatched += 1
                continue
            key = f"{m.group(1)}_{m.group(2)}_{m.group(3)}"
            try:
                ts = datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S")
            except ValueError:
                unmatched += 1
                continue
            mo = moments.setdefault(key, {"key": key, "ts": ts, "full": None, "proxy": None})
            full = os.path.join(dirpath, f)
            if ext in VID_EXT:
                mo["full"] = full
            else:
                mo["proxy"] = full

    clips = sorted(moments.values(), key=lambda c: c["ts"])
    # group by capture calendar date, then into sessions by gap
    by_day: dict[str, list] = defaultdict(list)
    for c in clips:
        by_day[c["ts"].strftime("%Y-%m-%d")].append(c)

    days_out = []
    for day, cs in sorted(by_day.items()):
        cs.sort(key=lambda c: c["ts"])
        sessions, cur, prev = [], [], None
        for c in cs:
            if prev and (c["ts"] - prev).total_seconds() / 60 > a.session_gap_min and cur:
                sessions.append(cur); cur = []
            cur.append(c); prev = c["ts"]
        if cur:
            sessions.append(cur)
        days_out.append({
            "day": day, "n_clips": len(cs), "n_sessions": len(sessions),
            "start": cs[0]["ts"].strftime("%H:%M"), "end": cs[-1]["ts"].strftime("%H:%M"),
            "span_h": round((cs[-1]["ts"] - cs[0]["ts"]).total_seconds() / 3600, 1),
            "n_with_fullres": sum(1 for c in cs if c["full"]),
            "sessions": [{
                "start": s[0]["ts"].strftime("%H:%M"), "end": s[-1]["ts"].strftime("%H:%M"),
                "n_clips": len(s),
                "clips": [{"key": c["key"], "ts": c["ts"].isoformat(),
                           "full": c["full"], "proxy": c["proxy"]} for c in s],
            } for s in sessions],
        })

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as f:
        json.dump({"root": a.root, "n_unique_clips": len(clips), "n_days": len(days_out),
                   "unmatched": unmatched, "days": days_out}, f, indent=2, default=str)

    print(f"{len(clips)} unique clips · {len(days_out)} capture-days · {unmatched} unmatched names\n")
    print("Candidate videos, ranked by clip count (a dense day = a documented day):")
    print(f"  {'date':<12}{'clips':>6}{'sess':>6}{'span':>7}   day window")
    for d in sorted(days_out, key=lambda d: -d["n_clips"])[:20]:
        print(f"  {d['day']:<12}{d['n_clips']:>6}{d['n_sessions']:>6}{d['span_h']:>6}h   {d['start']}–{d['end']}")
    print(f"\nindex → {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
