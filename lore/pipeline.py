"""Lore orchestrator CLI.

`lore plan ...`  — dry-run: validate config and print the stage graph (reuse vs
                   inject). Runs with the Python standard library alone.
`lore run ...`   — execute the pipeline. Lazily imports CutClaw (from
                   external/CutClaw) and Lore's heavy stages; raises a clear
                   NotImplementedError for stages still under construction.

Heavy deps and the 3 LiteLLM endpoints are required only for `run` (see BUILD.md).
"""
from __future__ import annotations

import argparse
import os
import sys

from .config import LoreConfig, STAGE_GRAPH

_OWNER_LEGEND = {
    "LORE": "Lore (new)",
    "REUSE": "CutClaw (unchanged)",
    "REUSE+PATCH": "CutClaw (prompt/score patched)",
    "LORE+REUSE": "Lore + CutClaw",
}


def _print_plan(cfg: LoreConfig) -> int:
    errs = cfg.validate()
    print("Lore — execution plan (dry run)\n" + "=" * 48)
    print(f"  regime           : {cfg.regime}")
    print(f"  instruction_type : {cfg.instruction_type}")
    print(f"  video            : {cfg.video_path or '<unset>'}")
    print(f"  audio            : {cfg.audio_path or '<unset>'}")
    print(f"  instruction      : {cfg.instruction or '<unset>'}")
    print(f"  target seconds   : {cfg.target_seconds}")
    print(f"  worthiness gate  : on (keep {cfg.keep_fraction:.0%}, weights {cfg.gate_weights})"
          if cfg.worthiness_gate else "  worthiness gate  : OFF")
    print(f"  dialogue channel : {'on' if cfg.dialogue_channel else 'off'}   "
          f"metadata: {'on' if cfg.use_metadata else 'off'}")

    print("\nStage graph (→ = CutClaw artifact handoff):")
    for label, owner, note in STAGE_GRAPH:
        print(f"  [{_OWNER_LEGEND[owner]:<30}] {label:<32} {note}")

    print("\nCutClaw config overrides Lore will push:")
    for k, v in cfg.cutclaw_overrides().items():
        print(f"  --config.{k} = {v!r}")

    if errs:
        print("\nCONFIG ERRORS:")
        for e in errs:
            print(f"  ✗ {e}")
        return 1
    print("\nConfig OK. (Use `lore run ...` to execute — requires deps + API keys; see BUILD.md.)")
    return 0


def _run(cfg: LoreConfig) -> int:
    errs = cfg.validate()
    if errs:
        for e in errs:
            print(f"config error: {e}", file=sys.stderr)
        return 1
    cutclaw_dir = os.path.join(os.path.dirname(__file__), os.pardir, "external", "CutClaw")
    cutclaw_dir = os.path.abspath(cutclaw_dir)
    if not os.path.isdir(cutclaw_dir):
        print(f"external/CutClaw not found at {cutclaw_dir}. Clone it (see BUILD.md).", file=sys.stderr)
        return 2
    sys.path.insert(0, cutclaw_dir)  # make `import src...` resolve to CutClaw

    # Lazy: the heavy stages live behind these imports so `lore plan` stays light.
    from .segmentation.event_segmenter import segment_events  # noqa: F401
    from .worthiness.gate import score_and_prune              # noqa: F401
    from .compose.anchor import patch_for_pov_regime          # noqa: F401

    raise NotImplementedError(
        "End-to-end `run` is scaffolded but not wired yet.\n"
        "Build order (plan/project-plan.md): M0 break-CutClaw baseline → M2 worthiness gate\n"
        "→ M3 event segmentation → M4 re-anchored compose → M5 end-to-end.\n"
        "Until M5, drive CutClaw directly via external/CutClaw/local_run.py with the\n"
        "overrides printed by `lore plan` (notably VIDEO_TYPE=vlog + protagonist off)."
    )


def _cfg_from_args(a: argparse.Namespace) -> LoreConfig:
    return LoreConfig(
        video_path=a.video or "",
        audio_path=a.audio or "",
        instruction=a.instruction or "",
        regime=a.regime,
        instruction_type=a.instruction_type,
        worthiness_gate=not a.no_gate,
        use_metadata=not a.no_metadata,
        dialogue_channel=not a.no_dialogue,
        keep_fraction=a.keep_fraction,
        target_seconds=a.target_seconds,
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="lore", description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("plan", "run"):
        sp = sub.add_parser(name, help=f"{name} the Lore pipeline")
        sp.add_argument("--video"); sp.add_argument("--audio")
        sp.add_argument("--instruction")
        sp.add_argument("--regime", default="pov", choices=("pov", "interval"))
        sp.add_argument("--instruction-type", dest="instruction_type",
                        default="narrative", choices=("object", "narrative"))
        sp.add_argument("--keep-fraction", dest="keep_fraction", type=float, default=0.15)
        sp.add_argument("--target-seconds", dest="target_seconds", type=float, default=45.0)
        sp.add_argument("--no-gate", action="store_true")
        sp.add_argument("--no-metadata", action="store_true")
        sp.add_argument("--no-dialogue", action="store_true")
    a = p.parse_args(argv)
    cfg = _cfg_from_args(a)
    return _print_plan(cfg) if a.cmd == "plan" else _run(cfg)


if __name__ == "__main__":
    raise SystemExit(main())
