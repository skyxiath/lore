"""The event segmenter (pipeline stage 2).

Replaces CutClaw's `SHOT_DETECTION_MODEL=scenedetect` + scene_merge with a cascade
suited to continuous raw footage. Registered as `SHOT_DETECTION_MODEL=lore_event`.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..metadata import CaptureMetadata


@dataclass
class Event:
    """A coherent unit of raw footage — Lore's analogue of a CutClaw 'scene'."""
    start_s: float
    end_s: float
    # Semantic attributes from the video-LLM pass (layer 2). The protagonist-free
    # anchor lives here: activity/place/attention instead of character identity.
    activity: str = ""
    place: str = ""
    objects: list[str] = field(default_factory=list)
    speaker_present: bool = False
    caption: str = ""
    # Provenance for interval footage (which pre-captured clip(s) this spans).
    clip_index: int | None = None

    @property
    def duration_s(self) -> float:
        return max(0.0, self.end_s - self.start_s)


def segment_events(
    video_path: str,
    metadata: CaptureMetadata | None = None,
    *,
    video_fps: float = 2.0,
    regime: str = "pov",
) -> list[Event]:
    """Produce Events from raw footage via the 3-layer cascade.

    Layer 1 — change-points: IMU stillness/motion, gaze-fixation clusters,
              optical-flow magnitude change, SLAM place-change, audio-scene change.
              (For regime='interval', clip boundaries are free change-points.)
    Layer 2 — semantic pass: a video-LLM dense-captions each candidate segment
              -> activity / place / objects / speaker_present.
    Layer 3 — aggregation: merge adjacent segments by attribute + metadata similarity.

    Implemented in M3. Ref: research/egocentric-video.md.
    """
    raise NotImplementedError("Event segmentation lands in M3; see plan/project-plan.md")


def write_cutclaw_scenes(events: list[Event], scenes_dir: str) -> str:
    """Serialize Events into CutClaw's `scenes/scene_0.json` schema so the
    Screenwriter/Editor read them unchanged.

    TODO(M3): match the exact schema emitted by
    external/CutClaw/src/video/deconstruction/scene_merge.save_scenes — confirm
    field names/units against the clone before relying on this.
    """
    raise NotImplementedError("Scene serialization lands in M3; confirm save_scenes schema first")
