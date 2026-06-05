# `lore/` — package overview

Lore's code. It does not fork CutClaw; it **wraps** it (`external/CutClaw`), injecting a new front end and re-anchoring the composition spine. See [../notes/cutclaw-code-map.md](../notes/cutclaw-code-map.md) for every seam.

| Module | Stage | Status | What it owns |
|---|---|---|---|
| `lore.metadata` | 1 | stub | GPMF (GoPro) + Aria (glasses) capture-metadata ingestion → `CaptureMetadata` |
| `lore.segmentation` | 2 | stub | event/activity segmentation → CutClaw scene JSON (replaces PySceneDetect) |
| `lore.worthiness` | 3 | stub | **the worthiness gate** — fuse acoustic/visual/dialogue/metadata, prune dead time |
| `lore.compose` | 5–7 | stub | protagonist-free **activity/place/attention** anchor (the headline contribution) |
| `lore.config` | — | ✅ | `LoreConfig` + the `--config.X` overrides Lore pushes into CutClaw |
| `lore.pipeline` | — | ✅ | orchestrator CLI (`lore plan` dry-run works today; `lore run` wires at M5) |

Data contracts already defined: `Event` (segmentation), `WorthinessScore` (gate), `CaptureMetadata`/`MetadataTrack` (metadata), `ActivityPlaceAnchor` (compose). Build against these; model choices are swappable.

Try it: `python3 -m lore.pipeline plan --regime interval --instruction "a day at the coast"`.

Build order and what fills each stub: [../plan/project-plan.md](../plan/project-plan.md).
