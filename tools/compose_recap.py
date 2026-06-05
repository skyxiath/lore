"""Lore minimal composer — a real beat-synced day-recap, locally (librosa + ffmpeg).

A lightweight stand-in for CutClaw's agent spine: it takes the worthiness analysis
(tools/day_recap_probe.py) + the music, selects the top moments, ORDERS them by
capture time (the day arc), lands every cut on a musical beat, and renders. Good
enough to see Lore end-to-end today; CutClaw-on-Modal is the sophisticated upgrade.

Usage:
  ./.venv/bin/python tools/compose_recap.py \
      --analysis "tests/test 1/lore_out/day_recap_analysis.json" \
      --clips "tests/test 1/raw clips" --music "tests/test 1/Frisky.mp3" \
      --out "tests/test 1/lore_out/recap.mp4" --target-seconds 60 --beats-per-cut 4
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import tempfile

import numpy as np


def beat_grid(music: str, target_s: float, beats_per_cut: int) -> list[float]:
    import librosa
    y, sr = librosa.load(music, mono=True)
    _, beats = librosa.beat.beat_track(y=y, sr=sr, units="time")
    beats = [float(b) for b in beats]
    if target_s and target_s > 0:
        beats = [b for b in beats if b <= target_s]
    # slot boundaries every `beats_per_cut` beats
    bounds = beats[::beats_per_cut]
    if bounds[0] > 0.05:
        bounds = [0.0] + bounds
    return bounds


def pick_clips(clips: list[dict], k: int, max_per_activity: int = 4) -> list[dict]:
    """Diversity-aware: take high-worthiness clips but skip near-duplicates (same
    activity+place) and cap any single activity, then order by capture time (the arc)."""
    def similar(a, b):
        return (a.get("activity", "").lower() == b.get("activity", "").lower()
                and a.get("place", "").lower() == b.get("place", "").lower())
    ana = [c for c in clips if c.get("timestamp") and not str(c.get("caption", "")).startswith("[")]
    ranked = sorted(ana, key=lambda c: -float(c.get("worthiness", 0)))
    picked, act = [], {}
    for c in ranked:
        if len(picked) >= k:
            break
        if float(c.get("worthiness", 0)) <= 0 and picked:
            break
        a_key = c.get("activity", "").lower()
        if any(similar(c, p) for p in picked) or act.get(a_key, 0) >= max_per_activity:
            continue
        picked.append(c); act[a_key] = act.get(a_key, 0) + 1
    return sorted(picked, key=lambda c: c["timestamp"])


def cut_segment(clip_path: str, clip_dur: float, seg_dur: float, res: int, fps: int,
                out: str) -> bool:
    # Center sub-segment of the source clip, scaled + normalized for clean concat.
    # Keep the clip's own (diegetic) audio so it can sit under the music bed.
    off = max(0.0, (clip_dur - seg_dur) / 2.0)
    w = (res * 16 // 9) // 2 * 2   # fixed 16:9 canvas — sources have mixed aspect ratios
    r = subprocess.run(
        ["ffmpeg", "-v", "error", "-ss", f"{off:.2f}", "-i", clip_path, "-t", f"{seg_dur:.3f}",
         "-vf", (f"scale={w}:{res}:force_original_aspect_ratio=increase,"
                 f"crop={w}:{res},fps={fps},setsar=1,format=yuv420p"),
         "-af", "aresample=async=1:first_pts=0",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
         "-c:a", "aac", "-ar", "48000", "-ac", "2", "-y", out],
        capture_output=True, text=True)
    return r.returncode == 0 and os.path.exists(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--analysis", required=True)
    ap.add_argument("--clips", default="", help="flat dir of clips (interval/test mode)")
    ap.add_argument("--from-index", dest="from_index", default="",
                    help="index.json — resolve full-res .mp4 paths for a volume day")
    ap.add_argument("--day", default="", help="capture day YYYY-MM-DD (with --from-index)")
    ap.add_argument("--music", required=True)
    ap.add_argument("--out", default="")
    ap.add_argument("--target-seconds", type=float, default=60.0, help="0 = full song")
    ap.add_argument("--beats-per-cut", type=int, default=4)
    ap.add_argument("--res", type=int, default=1080)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--min-worthiness", type=float, default=0.0)
    ap.add_argument("--music-gain", dest="music_gain", type=float, default=0.5)
    ap.add_argument("--diegetic-gain", dest="diegetic_gain", type=float, default=1.0)
    ap.add_argument("--duck", action="store_true",
                    help="duck the music under loud diegetic audio (sidechain)")
    a = ap.parse_args()

    data = json.load(open(a.analysis))
    clips = [c for c in data["clips"] if float(c.get("worthiness", 0)) >= a.min_worthiness]

    # resolve each analyzed clip -> source video. Volume mode (--from-index) maps the
    # proxy basename to the FULL-RES .mp4 via the index; else a flat --clips dir.
    keymap = {}
    if a.from_index:
        index = json.load(open(a.from_index))
        day = next((d for d in index.get("days", []) if d["day"] == a.day), None)
        if not day:
            print(f"day {a.day!r} not in {a.from_index}"); return 2
        for s in day["sessions"]:
            for c in s["clips"]:
                if c.get("full"):
                    keymap[c["key"]] = c["full"]

    def src_path(c):
        if a.from_index:
            m = re.search(r"(\d{8})_(\d{6})_(\d+)", c.get("file", ""))
            return keymap.get(f"{m.group(1)}_{m.group(2)}_{m.group(3)}") if m else None
        return os.path.join(a.clips, c["file"])

    full_bounds = beat_grid(a.music, a.target_seconds, a.beats_per_cut)
    chosen = pick_clips(clips, len(full_bounds) - 1)
    k = len(chosen)
    if k < 1:
        print("no clips selected"); return 1
    sel = np.linspace(0, len(full_bounds) - 1, k + 1)
    bounds = [full_bounds[int(round(i))] for i in sel]
    slots = [(bounds[i], bounds[i + 1]) for i in range(k)]

    print(f"music beat grid → {k} cuts (beats_per_cut={a.beats_per_cut}, "
          f"target {a.target_seconds or 'full'}s). Edit decision list:")
    out = a.out or os.path.join(os.path.dirname(a.analysis), "recap.mp4")
    segs = []
    with tempfile.TemporaryDirectory() as tmp:
        for j, (c, (t0, t1)) in enumerate(zip(chosen, slots)):
            dur = round(t1 - t0, 3)
            src = src_path(c)
            if not src or not os.path.exists(src):
                print(f"  {j:02d} skip — no source for {c.get('file')}"); continue
            seg = os.path.join(tmp, f"s{j:03d}.mp4")
            ok = cut_segment(src, float(c.get("duration_s", 60)), dur, a.res, a.fps, seg)
            tt = c["timestamp"][11:16]
            print(f"  {j:02d} @beat {t0:6.2f}s ({dur:4.2f}s) ← {tt} w{c['worthiness']:.2f} "
                  f"{c.get('activity','')[:24]:<24} {'OK' if ok else 'FAIL'}")
            if ok:
                segs.append(seg)
        if not segs:
            print("no segments rendered"); return 1
        # concat (uniform params -> stream copy) then mux music
        lst = os.path.join(tmp, "list.txt")
        with open(lst, "w") as f:
            for s in segs:
                f.write(f"file '{s}'\n")
        av = os.path.join(tmp, "av.mp4")   # concatenated video WITH diegetic audio
        subprocess.run(["ffmpeg", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst,
                        "-c", "copy", "-y", av], check=True)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        mg, dg = a.music_gain, a.diegetic_gain
        # Normalize both audio streams to a common rate+layout FIRST — sidechaincompress
        # and amix error out (exit 234) when sample-rate/channel-layout differ between
        # the diegetic track and the music. Then try duck → plain mix → music-only.
        nd = f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={dg}"
        nm = f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={mg}"
        duck_fc = (f"{nd},asplit=2[d][dk];{nm}[m];"
                   f"[m][dk]sidechaincompress=threshold=0.05:ratio=6:attack=20:release=400[mq];"
                   f"[mq][d]amix=inputs=2:duration=first:normalize=0[a]")
        mix_fc = (f"{nd}[d];{nm}[m];"
                  f"[d][m]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[a]")
        attempts = ([("duck", duck_fc)] if a.duck else []) + [("mix", mix_fc)]
        muxed = False
        for name, fc in attempts:
            r = subprocess.run(["ffmpeg", "-v", "error", "-i", av, "-i", a.music,
                                "-filter_complex", fc, "-map", "0:v", "-map", "[a]",
                                "-c:v", "copy", "-c:a", "aac", "-shortest", "-y", out],
                               capture_output=True, text=True)
            if r.returncode == 0 and os.path.exists(out):
                if name != attempts[0][0]:
                    print(f"  (audio: '{attempts[0][0]}' failed → used '{name}')")
                muxed = True
                break
            print(f"  audio mux '{name}' failed: {r.stderr.strip()[:140]}")
        if not muxed:   # last resort: music only, never lose the video
            subprocess.run(["ffmpeg", "-v", "error", "-i", av, "-i", a.music,
                            "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac",
                            "-shortest", "-y", out], check=True)
            print("  (audio: fell back to music-only)")
    dur = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                          "-of", "default=nk=1:nw=1", out], capture_output=True, text=True).stdout.strip()
    print(f"\n✅ rendered {len(segs)} cuts → {out}  ({float(dur):.1f}s, {a.res}p)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
