"""Event/activity segmentation — replaces PySceneDetect for raw footage.

Raw POV/glasses footage has no editorial cuts, so we manufacture meaningful units
with a 3-layer cascade: cheap multimodal change-points -> video-LLM semantic pass
-> attribute+metadata aggregation. Output is written in CutClaw's scene JSON format
so the downstream agents consume it unchanged. Ref: notes/cutclaw-code-map.md.
"""
from .event_segmenter import Event, segment_events, write_cutclaw_scenes  # noqa: F401
