"""Lore front-end probe (stages 1-3) on real interval footage, via OpenAI.

A keys-only, no-heavy-deps prototype of Lore's novel front end:
  1. metadata day-arc   — parse VID_YYYYMMDD_HHMMSS_*.mp4 timestamps -> timeline + gaps
  2. event semantics     — keyframes -> vision model -> activity/place/caption
  3. worthiness gate      — vision + transcript -> worthiness score (what to keep)
     + dialogue channel    — per-clip transcription (the "what was said" signal)

This stands in for Qwen3-VL / the full CutClaw stack (which needs torch/madmom/decord)
so we can see Lore's selection front end working on the actual data today. Output is a
JSON artifact a later composer (CutClaw spine) can consume. See plan/architecture.md.

Usage:
  ./.venv/bin/python tools/day_recap_probe.py --clips "tests/test 1/raw clips" \
      --music "tests/test 1/Frisky.mp3" --subset 6 --model gpt-4o
  (add --all to process every clip; --no-audio to skip transcription)
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import random
import re
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI, APIConnectionError, APIError, RateLimitError

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
load_dotenv(os.path.join(ROOT, ".env"))
# We own retry/backoff explicitly (see _call_with_retry) so --max-retries is meaningful,
# waits are logged, and Retry-After / rate-limit-reset headers are honored. Hence the
# SDK's built-in retry is turned OFF here (max_retries=0) to avoid compounding backoffs.
CLIENT = OpenAI(api_key=os.environ["OPENAI_API_KEY"], max_retries=0, timeout=90)

# Backoff envelope for 429 (rate limit) / transient 5xx / connection errors. These are
# only a *floor*: when the server tells us how long to wait via a header, we honor that.
RETRYABLE_STATUS = {429, 500, 502, 503, 504}
BASE_DELAY = 2.0   # seconds; doubles each attempt
MAX_DELAY = 60.0   # cap on a single wait
JITTER = 1.0       # + U(0, JITTER) so concurrent workers don't retry in lockstep

TS_RE = re.compile(r"(?:VID|LRV|PRO)_?(\d{8})_(\d{6})_(\d+)", re.IGNORECASE)

WORTHINESS_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["activity", "place", "caption", "worthiness", "worthiness_reason",
                 "has_meaningful_speech", "notable_audio"],
    "properties": {
        "activity": {"type": "string", "description": "what the wearer is doing (1-4 words)"},
        "place": {"type": "string", "description": "where this is (1-4 words)"},
        "caption": {"type": "string", "description": "one vivid sentence describing the moment"},
        "worthiness": {"type": "number", "description": "0..1: how worth keeping in a short, music-synced day-recap. Dead time/blurry/repetitive=low; vivid/peak/social/scenic moments=high"},
        "worthiness_reason": {"type": "string"},
        "has_meaningful_speech": {"type": "boolean", "description": "is there dialogue that matters to the story (not filler)?"},
        "notable_audio": {"type": "string", "description": "salient diegetic sound if any (laughter, cheering, music, impact, waves...) else empty"},
    },
}


def _parse_duration(s: str) -> float | None:
    """Parse an OpenAI rate-limit reset hint ('1s', '6m0s', '880ms', '0.5') to seconds."""
    s = s.strip().lower()
    try:
        return float(s)  # a bare number means seconds
    except ValueError:
        pass
    if s.endswith("ms"):
        try:
            return float(s[:-2]) / 1000.0
        except ValueError:
            return None
    units, total, num, matched = {"h": 3600, "m": 60, "s": 1}, 0.0, "", False
    for ch in s:
        if ch.isdigit() or ch == ".":
            num += ch
        elif ch in units and num:
            total += float(num) * units[ch]; num = ""; matched = True
        else:
            return None
    return total if matched and not num else None


def _retry_after_seconds(exc: Exception) -> float | None:
    """Server-suggested wait from a 429/5xx response, if any header carries one."""
    headers = getattr(getattr(exc, "response", None), "headers", None)
    if not headers:
        return None
    for key, scale in (("retry-after-ms", 0.001), ("retry-after", 1.0)):
        v = headers.get(key)
        if v:
            try:
                return float(v) * scale
            except ValueError:
                pass
    for key in ("x-ratelimit-reset-requests", "x-ratelimit-reset-tokens"):
        v = headers.get(key)
        if v and (secs := _parse_duration(v)) is not None:
            return secs
    return None


def _error_kind(exc: Exception) -> str:
    """Short, machine-readable label for the 'error' field on a failed clip."""
    if isinstance(exc, RateLimitError):
        return "rate_limit"
    if isinstance(exc, APIConnectionError):
        return "connection"
    status = getattr(exc, "status_code", None)
    return f"http_{status}" if status else type(exc).__name__


def _call_with_retry(fn, *, max_retries: int, label: str = ""):
    """Run an OpenAI call, retrying 429 / transient 5xx / connection errors with
    header-aware exponential backoff. Honors Retry-After / retry-after-ms /
    x-ratelimit-reset-* when the server sends them, else falls back to capped
    exponential backoff with jitter. Re-raises the last error once retries are
    exhausted so the caller can flag the clip as failed (not silently score it 0)."""
    for attempt in range(max_retries + 1):
        try:
            return fn()
        except APIError as e:
            status = getattr(e, "status_code", None)
            retryable = isinstance(e, APIConnectionError) or status in RETRYABLE_STATUS
            if not retryable or attempt >= max_retries:
                raise
            backoff = min(BASE_DELAY * (2 ** attempt), MAX_DELAY)
            wait = max(_retry_after_seconds(e) or 0.0, backoff) + random.uniform(0, JITTER)
            tag = f"{label} " if label else ""
            print(f"  ⟳ {tag}{type(e).__name__} "
                  f"(retry {attempt + 1}/{max_retries}, waiting {wait:.1f}s)", file=sys.stderr)
            time.sleep(wait)


def probe_duration(path: str) -> float:
    out = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                          "-of", "default=nk=1:nw=1", path], capture_output=True, text=True).stdout.strip()
    try:
        return float(out)
    except ValueError:
        return 0.0


def parse_ts(fname: str) -> datetime | None:
    m = TS_RE.search(fname)
    return datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S") if m else None


def extract_frames(clip: str, dur: float, n: int, tmp: str) -> list[str]:
    """Grab n evenly-spread keyframes, downscaled to 512px short side (cheap tokens)."""
    paths = []
    fracs = [0.1, 0.5, 0.9] if n == 3 else [(i + 0.5) / n for i in range(n)]
    for i, fr in enumerate(fracs):
        t = max(0.0, min(dur - 0.1, dur * fr))
        out = os.path.join(tmp, f"f{i}.jpg")
        subprocess.run(["ffmpeg", "-v", "quiet", "-ss", f"{t:.2f}", "-i", clip,
                        "-frames:v", "1", "-vf", "scale=-2:512", "-q:v", "6", "-y", out],
                       check=False)
        if os.path.exists(out):
            paths.append(out)
    return paths


def transcribe(clip: str, tmp: str, max_retries: int) -> str:
    aud = os.path.join(tmp, "a.mp3")
    subprocess.run(["ffmpeg", "-v", "quiet", "-i", clip, "-ac", "1", "-ar", "16000",
                    "-y", aud], check=False)
    if not os.path.exists(aud):
        return ""
    # Read bytes once: on a 429 retry the SDK re-reads the payload, so a spent file
    # handle would upload empty audio. A (name, bytes) tuple is safe to resend.
    with open(aud, "rb") as f:
        data = f.read()
    try:
        r = _call_with_retry(
            lambda: CLIENT.audio.transcriptions.create(
                model="gpt-4o-transcribe", file=("a.mp3", data)),
            max_retries=max_retries, label="audio")
        return (r.text or "").strip()
    except Exception as e:
        return f"[transcription error: {str(e)[:80]}]"


def b64img(p: str) -> str:
    with open(p, "rb") as f:
        return "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()


def analyze_clip(clip: str, fname: str, n_frames: int, model: str, do_audio: bool,
                 instruction: str, max_retries: int) -> dict:
    dur = probe_duration(clip)
    ts = parse_ts(fname)
    error = None
    with tempfile.TemporaryDirectory() as tmp:
        frames = extract_frames(clip, dur, n_frames, tmp)
        transcript = transcribe(clip, tmp, max_retries) if do_audio else ""
        sys_p = ("You analyze one ~60s clip from a wearable/POV camera that auto-captures "
                 "a 1-minute clip every ~10 minutes across a day. The clips will be edited "
                 "into a short, music-synced DAY-RECAP. Judge how worth-keeping this moment is. "
                 + (f"Editing instruction: {instruction!r}. " if instruction else ""))
        user_content = [{"type": "text", "text":
                         f"Keyframes from the clip (start→end). "
                         f"Transcript of its audio: {transcript[:1200] or '(silence/none)'}"}]
        for fp in frames:
            user_content.append({"type": "image_url", "image_url": {"url": b64img(fp), "detail": "low"}})
        try:
            resp = _call_with_retry(
                lambda: CLIENT.chat.completions.create(
                    model=model,
                    messages=[{"role": "system", "content": sys_p},
                              {"role": "user", "content": user_content}],
                    response_format={"type": "json_schema",
                                     "json_schema": {"name": "worthiness", "schema": WORTHINESS_SCHEMA, "strict": True}},
                ),
                max_retries=max_retries, label=fname)
            data = json.loads(resp.choices[0].message.content)
        except Exception as e:
            # Failed to analyze (e.g. rate limit survived all retries). Flag it explicitly
            # with worthiness=None so a downstream consumer never confuses a dropped clip
            # with a genuine low-worthiness one (worthiness 0.0, error=None).
            error = _error_kind(e)
            data = {"activity": "", "place": "", "caption": f"[vision error: {str(e)[:100]}]",
                    "worthiness": None, "worthiness_reason": "error",
                    "has_meaningful_speech": False, "notable_audio": ""}
    data.update({"file": fname, "timestamp": ts.isoformat() if ts else None,
                 "duration_s": round(dur, 1), "transcript": transcript, "error": error})
    return data


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--clips", default="")
    ap.add_argument("--from-index", dest="from_index", default="",
                    help="index.json from tools/index_volume.py (analyze a capture-day from a volume)")
    ap.add_argument("--day", default="", help="capture day YYYY-MM-DD to pull from the index")
    ap.add_argument("--use-proxy", dest="use_proxy", action="store_true",
                    help="analyze the low-res .lrv proxy (cheap) instead of full-res")
    ap.add_argument("--music", default="")
    ap.add_argument("--instruction", default="")
    ap.add_argument("--subset", type=int, default=6, help="evenly-spaced sample size")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--frames", type=int, default=3)
    ap.add_argument("--model", default="gpt-4o")
    ap.add_argument("--no-audio", action="store_true")
    ap.add_argument("--workers", type=int, default=2,
                    help="concurrent clips; kept low by default to avoid 429 bursts on low tiers")
    ap.add_argument("--max-retries", dest="max_retries", type=int, default=8,
                    help="per-call retries on 429/5xx/connection errors before a clip is flagged 'error'")
    ap.add_argument("--out", default="")
    a = ap.parse_args()

    # Preflight: fail fast (and cheaply) if the key has no quota / is invalid. Retry it
    # too, so a transient rate limit on this one tiny call doesn't abort the whole run.
    try:
        _call_with_retry(
            lambda: CLIENT.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "ok"}], max_tokens=1),
            max_retries=a.max_retries, label="preflight")
    except Exception as e:
        msg = str(e)
        if "insufficient_quota" in msg:
            print("ABORT: OpenAI key has no billing quota (insufficient_quota).\n"
                  "  Add credit at platform.openai.com → Billing, or use a funded key. "
                  "Then re-run this command.", file=sys.stderr)
        else:
            print(f"ABORT: OpenAI preflight failed: {msg[:200]}", file=sys.stderr)
        return 2

    if a.from_index:
        idx = json.load(open(a.from_index))
        day = next((d for d in idx.get("days", []) if d["day"] == a.day), None)
        if not day:
            print(f"day {a.day!r} not found in {a.from_index}", file=sys.stderr); return 2
        targets = []
        for s in day["sessions"]:
            for c in s["clips"]:
                p = c.get("proxy") if (a.use_proxy and c.get("proxy")) else c.get("full")
                if p and os.path.exists(p):
                    targets.append((p, os.path.basename(p)))
    else:
        files = sorted(f for f in os.listdir(a.clips) if f.lower().endswith(".mp4"))
        targets = [(os.path.join(a.clips, f), f) for f in files if parse_ts(f)]
    if not a.all and a.subset < len(targets):
        sel = [round(i * (len(targets) - 1) / (a.subset - 1)) for i in range(a.subset)]
        targets = [targets[i] for i in sorted(set(sel))]
    print(f"Analyzing {len(targets)} clips with {a.model} "
          f"({a.frames} frames/clip, audio={'off' if a.no_audio else 'on'}, "
          f"{'proxy' if a.use_proxy else 'full-res'})...\n")

    results = []
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(analyze_clip, path, name, a.frames, a.model,
                          not a.no_audio, a.instruction, a.max_retries): name
                for path, name in targets}
        for fut in as_completed(futs):
            r = fut.result(); results.append(r)
            w = r["worthiness"]
            cell = f"{w:.2f}" if isinstance(w, (int, float)) else " ERR"
            print(f"  [{cell}] {r['timestamp'][11:16] if r['timestamp'] else '--:--'}  "
                  f"{r['activity'][:22]:<22} @ {r['place'][:18]:<18} | {r['caption'][:70]}")

    results.sort(key=lambda r: r["timestamp"] or "")
    n_err = sum(1 for r in results if r.get("error"))
    music_dur = probe_duration(a.music) if a.music else 0.0
    artifact = {"music": os.path.basename(a.music), "music_duration_s": round(music_dur, 1),
                "instruction": a.instruction, "model": a.model, "n_clips": len(results),
                "n_errors": n_err, "clips": results}
    out = a.out or (f"analysis/volume/{a.day}_analysis.json" if a.from_index
                    else os.path.join(a.clips, os.pardir, "lore_out", "day_recap_analysis.json"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(artifact, f, indent=2)

    # --- the two Lore artifacts: the day arc, and the worthiness shortlist ---
    print("\n=== DAY ARC (time-ordered place→activity) ===")
    prev = None
    for r in results:
        t = r["timestamp"][11:16] if r["timestamp"] else "--:--"
        gap = ""
        if prev and r["timestamp"]:
            dt = (datetime.fromisoformat(r["timestamp"]) - prev).total_seconds() / 60
            gap = f"  (+{dt:.0f}m)"
        prev = datetime.fromisoformat(r["timestamp"]) if r["timestamp"] else prev
        print(f"  {t}{gap:<9} {r['place'][:20]:<20} — {r['activity']}")
    print("\n=== WORTHINESS SHORTLIST (what a recap should keep) ===")
    ranked = [r for r in results if r.get("worthiness") is not None]
    for r in sorted(ranked, key=lambda r: -r["worthiness"])[:max(3, len(ranked) // 2)]:
        spk = "🗣" if r["has_meaningful_speech"] else " "
        aud = f"  🔊{r['notable_audio']}" if r["notable_audio"] else ""
        print(f"  {r['worthiness']:.2f} {spk} {r['timestamp'][11:16]}  {r['caption'][:78]}{aud}")
    if n_err:
        print(f"\n⚠ {n_err}/{len(results)} clips failed to analyze and were flagged "
              f"(error≠null, worthiness=null) — not scored 0.")
    print(f"\nartifact → {os.path.normpath(out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
