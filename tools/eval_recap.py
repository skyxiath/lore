"""Evaluation harness for a rendered recap (the metric stage, currently at zero).

Two metrics that need no ground-truth labels:
  • AV-Harmony / beat-alignment — detect the video's cut points (ffmpeg scene
    detection) and the music's beats (librosa), report how tightly cuts land on
    beats (mean offset, % within a perceptual tolerance). Transfers from CutClaw.
  • MLLM-as-judge — sample frames and have a vision model rate coherence / visual
    quality / instruction-following / human-likeness (a cheap automated proxy;
    backstop with a human study later).

Worthiness rank-correlation (Kendall-τ vs human labels) is stubbed — it needs a
labeled set we don't have yet (see open-questions.md / status-vs-plan.md).

Usage:
  ./.venv/bin/python tools/eval_recap.py --recap analysis/volume/2026-01-18_recap.mp4 \
      --music "songs/Midnight City.mp3" --instruction "a waterfall hike" [--judge]
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import tempfile

from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT, ".env"))


def detect_cuts(video: str, thr: float = 0.3) -> list[float]:
    """Scene-change timestamps via ffmpeg's scene detector."""
    r = subprocess.run(
        ["ffmpeg", "-i", video, "-filter:v", f"select='gt(scene,{thr})',showinfo",
         "-f", "null", "-"], capture_output=True, text=True)
    return sorted(float(m) for m in re.findall(r"pts_time:([0-9.]+)", r.stderr))


def beat_times(music: str, until: float) -> list[float]:
    import librosa
    y, sr = librosa.load(music, mono=True)
    _, beats = librosa.beat.beat_track(y=y, sr=sr, units="time")
    return [float(b) for b in beats if b <= until + 0.5]


def av_harmony(cuts: list[float], beats: list[float], tol: float = 0.1) -> dict:
    if not cuts or not beats:
        return {"n_cuts": len(cuts), "note": "no cuts or beats detected"}
    offsets = [min(abs(c - b) for b in beats) for c in cuts]
    within = sum(o <= tol for o in offsets)
    offsets_sorted = sorted(offsets)
    median = offsets_sorted[len(offsets_sorted) // 2]
    return {
        "n_cuts": len(cuts), "n_beats": len(beats),
        "mean_offset_s": round(sum(offsets) / len(offsets), 3),
        "median_offset_s": round(median, 3),
        f"pct_within_{tol}s": round(100 * within / len(cuts), 1),
        "av_harmony_score": round(100 * within / len(cuts), 1),  # CutClaw-style: % on-beat
    }


def mllm_judge(video: str, dur: float, instruction: str, model: str = "gpt-4o") -> dict:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], max_retries=4)
    schema = {
        "type": "object", "additionalProperties": False,
        "required": ["visual_quality", "narrative_coherence", "instruction_following",
                     "human_likeness", "notes"],
        "properties": {
            "visual_quality": {"type": "integer", "description": "1-10 aesthetic/clarity"},
            "narrative_coherence": {"type": "integer", "description": "1-10 does it read as a coherent day/story?"},
            "instruction_following": {"type": "integer", "description": "1-10 fidelity to the instruction (10 if none given)"},
            "human_likeness": {"type": "integer", "description": "1-10 would a good human editor have made this?"},
            "notes": {"type": "string"},
        },
    }
    with tempfile.TemporaryDirectory() as tmp:
        imgs = []
        for i in range(8):
            t = max(0.1, dur * (i + 0.5) / 8)
            p = os.path.join(tmp, f"f{i}.jpg")
            subprocess.run(["ffmpeg", "-v", "quiet", "-ss", f"{t:.2f}", "-i", video,
                            "-frames:v", "1", "-vf", "scale=-2:360", "-q:v", "6", "-y", p], check=False)
            if os.path.exists(p):
                with open(p, "rb") as f:
                    imgs.append("data:image/jpeg;base64," + base64.b64encode(f.read()).decode())
        content = [{"type": "text", "text":
                    f"These are {len(imgs)} frames sampled in order from a short music-synced "
                    f"recap edited from raw POV footage. Instruction: {instruction or '(none)'}. "
                    f"Rate it as an editor would."}]
        content += [{"type": "image_url", "image_url": {"url": u, "detail": "low"}} for u in imgs]
        resp = client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": content}],
            response_format={"type": "json_schema", "json_schema": {"name": "judge", "schema": schema, "strict": True}})
        return json.loads(resp.choices[0].message.content)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--recap", required=True)
    ap.add_argument("--music", default="")
    ap.add_argument("--instruction", default="")
    ap.add_argument("--judge", action="store_true", help="run the MLLM-judge (costs an API call)")
    ap.add_argument("--tol", type=float, default=0.1)
    a = ap.parse_args()

    dur = float(subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                                "-of", "default=nk=1:nw=1", a.recap], capture_output=True, text=True).stdout or 0)
    cuts = detect_cuts(a.recap)
    music = a.music or a.recap   # fall back to the recap's own (music) audio
    beats = beat_times(music, dur)
    report = {"recap": os.path.basename(a.recap), "duration_s": round(dur, 1),
              "av_harmony": av_harmony(cuts, beats, a.tol)}
    print(f"AV-Harmony: {json.dumps(report['av_harmony'])}")
    if a.judge:
        report["mllm_judge"] = mllm_judge(a.recap, dur, a.instruction)
        print(f"MLLM-judge: {json.dumps(report['mllm_judge'])}")
    out = a.recap.rsplit(".", 1)[0] + "_eval.json"
    json.dump(report, open(out, "w"), indent=2)
    print(f"→ {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
