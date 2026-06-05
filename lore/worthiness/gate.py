"""Joint audio+visual+dialogue+metadata worthiness scoring and pruning.

Design evidence (research/highlight-detection.md, research/audio-highlight.md):
- Start query-free + audio-fused. The closest mainstream method is the audio-visual
  recurrence detector (Islam et al., WACV 2025, arXiv 2407.13933) whose AUDIO-ONLY
  stream BEATS visual-only — so audio is fused deliberately, not bolted on.
- Visual features: CLIP + SlowFast (or frozen-CLIP R2-Tuning style).
- Audio features: PANNs/BEATs sound-event embeddings + CLAP + loudness/onset.
- Dialogue: see lore.worthiness.dialogue (the novel content channel).
- Metadata: IMU/g-force/GPS bursts as a cheap interestingness prior.
Per Q1 (open-questions.md), the gate is built "good enough to unblock composition",
not over-invested as the headline.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..metadata import CaptureMetadata
from ..segmentation.event_segmenter import Event


@dataclass
class WorthinessScore:
    acoustic: float = 0.0   # PANNs/BEATs salience + loudness/onset
    visual: float = 0.0     # CLIP+SlowFast saliency head
    dialogue: float = 0.0   # narrative-importance of what was said
    metadata: float = 0.0   # IMU/g-force/GPS prior
    total: float = 0.0      # weighted fusion

    @classmethod
    def fuse(cls, parts: "WorthinessScore", weights: dict[str, float]) -> "WorthinessScore":
        parts.total = (
            weights.get("acoustic", 1.0) * parts.acoustic
            + weights.get("visual", 1.0) * parts.visual
            + weights.get("dialogue", 1.0) * parts.dialogue
            + weights.get("metadata", 0.5) * parts.metadata
        )
        return parts


def score_and_prune(
    events: list[Event],
    *,
    audio_path: str | None = None,
    transcript_segments: list[dict] | None = None,
    metadata: CaptureMetadata | None = None,
    instruction: str = "",
    weights: dict[str, float] | None = None,
    keep_fraction: float = 0.15,
) -> list[tuple[Event, WorthinessScore]]:
    """Score every event and return the kept top `keep_fraction`, descending.

    Headline ablation for M2: visual-only vs +acoustic vs +dialogue vs +metadata,
    evaluated by Kendall's tau / Spearman vs human worthiness labels against a
    random baseline (NOT TVSum/SumMe F1 — see eval-no-tvsum-f1 / Otani CVPR 2019).
    Implemented in M2.
    """
    raise NotImplementedError("Worthiness scoring lands in M2; see plan/project-plan.md")
