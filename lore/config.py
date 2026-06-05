"""Lore configuration: the regime + the CutClaw config overrides it implies.

Lore does NOT fork CutClaw's config. It computes a set of `--config.PARAM VALUE`
overrides that re-point CutClaw into Lore's regime — chiefly: branch from the
`vlog` path, swap the segmenter, and switch OFF the protagonist machinery.
See notes/cutclaw-code-map.md for why each override exists.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from . import LORE_REGIMES


@dataclass
class LoreConfig:
    # --- inputs ---
    video_path: str = ""
    audio_path: str = ""
    instruction: str = ""
    regime: str = "pov"            # "pov" | "interval"
    instruction_type: str = "narrative"   # CutClaw: object | narrative

    # --- Lore front-end toggles ---
    segmenter: str = "lore_event"  # event/activity segmentation (replaces scenedetect)
    worthiness_gate: bool = True   # the enabling contribution (stage 3)
    use_metadata: bool = True      # GPMF / Aria metadata as worthiness + narrative prior
    dialogue_channel: bool = True  # score narratively-important dialogue (WhisperX -> LLM)

    # --- worthiness gate knobs ---
    keep_fraction: float = 0.15    # fraction of events the gate forwards to the planner
    gate_weights: dict = field(default_factory=lambda: {
        "acoustic": 1.0, "visual": 1.0, "dialogue": 1.0, "metadata": 0.5,
    })

    # --- target output ---
    target_seconds: float = 45.0

    def validate(self) -> list[str]:
        errs = []
        if self.regime not in LORE_REGIMES:
            errs.append(f"regime must be one of {LORE_REGIMES}, got {self.regime!r}")
        if not (0.0 < self.keep_fraction <= 1.0):
            errs.append(f"keep_fraction must be in (0,1], got {self.keep_fraction}")
        if self.instruction_type not in ("object", "narrative"):
            errs.append("instruction_type must be 'object' or 'narrative'")
        return errs

    def cutclaw_overrides(self) -> dict[str, object]:
        """The `--config.X` values Lore pushes into CutClaw's src/config.py.

        These are the concrete GUT + REPLACE decisions, made via config rather
        than code edits wherever possible (see code-map seams).
        """
        ov: dict[str, object] = {
            # Branch from the vlog (no-protagonist, no-subtitle) path.
            "VIDEO_TYPE": "vlog",
            # GUT the protagonist machinery.
            "MAIN_CHARACTER_NAME": "",
            "ENABLE_FACE_QUALITY_CHECK": False,
            "ENABLE_TRIM_SHOT_CHARACTER_ANALYSIS": False,
            # REPLACE shot detection with Lore's event segmenter.
            "SHOT_DETECTION_MODEL": self.segmenter,
            # KEEP the music spine as-is (madmom). Reviewer kept for perceptual QA.
            "ENABLE_REVIEWER": True,
        }
        if self.regime == "interval":
            # Interval clips are pre-segmented; gaps are deliberate ellipses.
            ov["MERGE_SHORT_SCENES"] = False
        return ov


# Stage graph: what Lore reuses from CutClaw vs. injects. Drives the dry-run view
# and documents the integration contract. (label, owner, artifact touched)
STAGE_GRAPH = [
    ("1. Ingestion + metadata",      "LORE+REUSE", "decode (CutClaw) + GPMF/Aria (lore.metadata) + WhisperX"),
    ("2. Event/activity segmentation","LORE",      "writes scenes/scene_0.json (replaces scenedetect)"),
    ("3. ★ Worthiness gate ★",        "LORE",      "prunes+scores scenes BEFORE the planner reads them"),
    ("4. Music deconstruction",       "REUSE",     "src/audio madmom (KEEP)"),
    ("5. Playwriter (re-anchored)",   "REUSE+PATCH","Screenwriter.run; activity/place/time anchor"),
    ("6. Editor (re-scored)",         "REUSE+PATCH","EditorCoreAgent.fine_grained_shot_trimming; S_activity"),
    ("7. Reviewer (re-checked)",      "REUSE+PATCH","Reviewer.Review_timeline; coherence not identity"),
    ("8. Render",                     "REUSE",     "render/render_video.py"),
]
