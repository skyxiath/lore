"""Capture-metadata ingestion — the signal films never have.

Lifestyle cameras and smart glasses stamp every moment with sensor metadata
(time, GPS, speed, g-force, IMU, SLAM pose, gaze). Lore promotes these from
throwaway to a first-class worthiness + narrative-arc signal. CutClaw uses none
of it (films have none).
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class MetadataTrack:
    """A single time-series sensor stream, sampled at `hz`."""
    name: str                      # e.g. "gps", "imu_accel", "gaze", "speed", "gforce"
    hz: float
    t: list[float] = field(default_factory=list)        # seconds from capture start
    values: list = field(default_factory=list)          # scalar or vector per sample


@dataclass
class CaptureMetadata:
    """All sensor tracks for one source, on a common timeline (seconds)."""
    source: str                    # "gopro" | "aria" | ...
    duration_s: float = 0.0
    tracks: dict[str, MetadataTrack] = field(default_factory=dict)
    # For interval footage: the wall-clock start of each pre-captured clip.
    clip_starts_s: list[float] = field(default_factory=list)

    def motion_energy(self) -> MetadataTrack | None:
        """Convenience: a derived motion-energy track (IMU/g-force/speed) used as a
        cheap worthiness prior. Implemented in M2."""
        raise NotImplementedError
