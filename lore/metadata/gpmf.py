"""GoPro GPMF telemetry extraction (GPS path, speed, elevation, g-force, scene, faces).

GoPro Quik proves sensor metadata can drive selection; Lore adds semantics on top.
GPMF is muxed into the MP4 as a data track; parse via the `gpmf` package or ffmpeg.
Ref: research/music-edit-landscape.md, research/interval-recap.md.
"""
from __future__ import annotations

from . import CaptureMetadata


def extract_gpmf(video_path: str) -> CaptureMetadata:
    """Parse GPMF telemetry from a GoPro MP4 into a CaptureMetadata.

    Tracks of interest: gps (lat/lon/alt), speed, gforce/accel, scene tags, faces.
    Implemented in M3 (metadata ingestion).
    """
    raise NotImplementedError("GPMF extraction lands in M3; see plan/project-plan.md")
