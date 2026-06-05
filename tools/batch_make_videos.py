"""Auto-make recaps for many capture-days: analyze (if needed) → quality-gate → render.

For each day: run the worthiness probe if it isn't analyzed yet, then render a recap
ONLY if the day has enough strong material (>= --min-strong clips at >= --strong-thr).
Days that are mostly dead time / one repetitive activity are reported and skipped, so
we spend render time only on genuinely good videos. Reads the volume read-only.

Usage:
  ./.venv/bin/python tools/batch_make_videos.py --music "tests/test 2/Count On Me.mp3" \
      --days 2026-04-25 2026-05-22 2026-03-26 ...
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = os.path.join(ROOT, ".venv", "bin", "python")
INDEX = os.path.join(ROOT, "analysis", "volume", "index.json")


def sh(cmd: list[str]) -> int:
    return subprocess.run(cmd, cwd=ROOT).returncode


def analyzed_ok(path: str) -> bool:
    if not os.path.exists(path):
        return False
    a = json.load(open(path))
    cl = a.get("clips", [])
    errs = sum(1 for c in cl if str(c.get("caption", "")).startswith("["))
    return bool(cl) and errs < 0.25 * len(cl)


def analyze(day: str) -> str:
    out = os.path.join(ROOT, "analysis", "volume", f"{day}_analysis.json")
    if analyzed_ok(out):
        return out
    sh([PY, "tools/day_recap_probe.py", "--from-index", INDEX, "--day", day,
        "--use-proxy", "--no-audio", "--all", "--frames", "2", "--workers", "2",
        "--model", "gpt-4o-mini", "--out", out])
    return out


def quality(path: str, thr: float) -> tuple[int, int, float]:
    a = json.load(open(path))
    ana = [c for c in a["clips"] if not str(c.get("caption", "")).startswith("[")]
    strong = [c for c in ana if float(c.get("worthiness", 0)) >= thr]
    mean = sum(float(c.get("worthiness", 0)) for c in ana) / max(1, len(ana))
    return len(ana), len(strong), mean


def render(day: str, music: str) -> str | None:
    out = os.path.join(ROOT, "analysis", "volume", f"{day}_recap.mp4")
    rc = sh([PY, "tools/compose_recap.py",
             "--analysis", os.path.join(ROOT, "analysis", "volume", f"{day}_analysis.json"),
             "--from-index", INDEX, "--day", day, "--music", music,
             "--target-seconds", "55", "--beats-per-cut", "4", "--duck",
             "--min-worthiness", "0.4", "--out", out])
    return out if rc == 0 and os.path.exists(out) else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", nargs="+", required=True)
    ap.add_argument("--music", required=True)
    ap.add_argument("--strong-thr", type=float, default=0.5)
    ap.add_argument("--min-strong", type=int, default=6)
    a = ap.parse_args()

    report = []
    for day in a.days:
        print(f"\n########## {day} ##########")
        path = analyze(day)
        try:
            n, strong, mean = quality(path, a.strong_thr)
        except Exception as e:
            report.append((day, "ERROR", str(e)[:60])); continue
        print(f"  analyzed {n} clips · {strong} strong(>={a.strong_thr}) · mean {mean:.2f}")
        if strong >= a.min_strong:
            out = render(day, a.music)
            report.append((day, "RENDERED" if out else "RENDER-FAIL",
                           f"{strong} strong, mean {mean:.2f}"))
        else:
            report.append((day, "skip-weak", f"only {strong} strong clips, mean {mean:.2f}"))

    print("\n================ REPORT ================")
    for day, status, note in report:
        print(f"  {day}  {status:<12} {note}")
    made = [d for d, s, _ in report if s == "RENDERED"]
    print(f"\n{len(made)} new videos: {', '.join(made) or '(none)'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
