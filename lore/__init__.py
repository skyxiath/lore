"""Lore — music-synced editing of raw lifestyle footage.

Lore re-targets CutClaw (external/CutClaw) from already-edited films to genuinely
raw POV / smart-glasses / interval footage. It KEEPS CutClaw's music-sync spine,
GUTS the on-screen-protagonist machinery, and ADDS a joint audio+visual worthiness
gate plus event/activity segmentation upstream of the planner.

See NORTH_STAR.md (thesis), plan/architecture.md (pipeline),
notes/cutclaw-code-map.md (where each stage plugs into CutClaw).

Package layout mirrors the pipeline:
    lore.metadata      — GPMF / Aria capture-metadata ingestion          [stage 1]
    lore.segmentation  — event/activity segmentation (replaces PySceneDetect) [stage 2]
    lore.worthiness    — the worthiness gate (the enabling contribution)  [stage 3]
    lore.compose       — protagonist-free re-anchor of the planner/editor [stages 5-7]
    lore.pipeline      — orchestrator CLI (reuses CutClaw stages 4-8)
"""

__version__ = "0.0.1"

# The four regimes Lore distinguishes. "film"/"vlog" are CutClaw's; Lore adds:
REGIMES = ("film", "vlog", "pov", "interval")
LORE_REGIMES = ("pov", "interval")
