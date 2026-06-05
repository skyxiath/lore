"""Project Aria / smart-glasses metadata extraction.

Aria MPS streams (via projectaria-tools): IMU (~800-1000 Hz), 6DoF SLAM trajectory,
eye-gaze, spatial audio, and time-aligned speech. These are exactly the signals
Lore's worthiness gate and activity/place anchor want. Ref: research/egocentric-video.md.
"""
from __future__ import annotations

from . import CaptureMetadata


def extract_aria(vrs_path: str) -> CaptureMetadata:
    """Parse an Aria .vrs (+ MPS outputs) into a CaptureMetadata.

    Tracks of interest: imu_accel/imu_gyro, slam_pose (for place-change), gaze
    (attention proxy), audio. Implemented in M3.
    """
    raise NotImplementedError("Aria extraction lands in M3; see plan/project-plan.md")
