"""Propose a diversity-aware clip selection (EDL) from a day's worthiness analysis.

Implements the diversity/redundancy penalty (gap-analysis priority #2): greedily take
high-worthiness clips but down-rank ones too similar to already-picked moments, so a
recap doesn't repeat near-identical shots. Returns clips in capture-time (story) order.
"""
from __future__ import annotations

import argparse
import json


def similar(a: dict, b: dict) -> bool:
    # crude redundancy test: same activity AND same place reads as a duplicate beat
    return (a.get("activity", "").lower() == b.get("activity", "").lower()
            and a.get("place", "").lower() == b.get("place", "").lower())


def select(clips: list[dict], n: int, max_per_activity: int = 4) -> list[dict]:
    ana = [c for c in clips if not str(c.get("caption", "")).startswith("[")]
    ranked = sorted(ana, key=lambda c: -float(c.get("worthiness", 0)))
    picked: list[dict] = []
    act_count: dict[str, int] = {}
    for c in ranked:
        if len(picked) >= n:
            break
        if float(c.get("worthiness", 0)) <= 0:
            break
        act = c.get("activity", "").lower()
        if any(similar(c, p) for p in picked):       # skip near-duplicates
            continue
        if act_count.get(act, 0) >= max_per_activity:  # cap any single activity
            continue
        picked.append(c)
        act_count[act] = act_count.get(act, 0) + 1
    return sorted(picked, key=lambda c: c.get("timestamp", ""))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--analysis", required=True)
    ap.add_argument("-n", type=int, default=14)
    ap.add_argument("--max-per-activity", type=int, default=4)
    a = ap.parse_args()
    data = json.load(open(a.analysis))
    sel = select(data["clips"], a.n, a.max_per_activity)
    print(f"{a.analysis}: proposed {len(sel)} clips (story order)")
    for c in sel:
        t = str(c.get("timestamp", ""))[11:16]
        spk = "🗣" if c.get("has_meaningful_speech") else " "
        print(f"  {float(c['worthiness']):.2f} {spk} {t}  {c.get('activity','')[:22]:<22} {str(c.get('caption',''))[:62]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
