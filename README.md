# Lore

**Take genuinely raw lifestyle-camera footage — POV/action-cam, smart glasses, interval capture — plus a music track and a text instruction, and produce a short, music-synced, narratively coherent edit that approaches a good human editor's.**

Lore builds on **CutClaw** ([arXiv:2603.29664](https://arxiv.org/abs/2603.29664)) — an agentic music-synced editor — but re-targets it from the regime CutClaw actually tested (*already-edited films*) to the regime its name implies (*raw footage*). The move: **keep** CutClaw's music-sync spine, **gut** its on-screen-protagonist machinery, and **add** the stage every prior system skips — a joint audio+visual *worthiness gate* that decides what's worth keeping in 90%-dead-time footage.

## Start here

| Doc | What it is |
|---|---|
| [NORTH_STAR.md](NORTH_STAR.md) | The thesis, the wedge, what we keep/gut/add, the contributions, the demo, the risks. **Read first.** |
| [GUIDELINES.md](GUIDELINES.md) | How we work: lead with the point, primary sources only, the keep-vs-gut discipline, eval as first-class. |
| [plan/architecture.md](plan/architecture.md) | The redesigned pipeline, component by component, with concrete models/tools. |
| [plan/project-plan.md](plan/project-plan.md) | Build order (de-risking-first), milestones M0–M6, the motivating experiment, the evaluation suite. |
| [open-questions.md](open-questions.md) | Unresolved forks with trade-offs and current leans. |

## Research dossiers (all verified + fact-checked, 2026-06-05)

| Dossier | Core finding for Lore |
|---|---|
| [research/cutclaw.md](research/cutclaw.md) | Verified teardown; benchmarked on edited films → the wedge. |
| [research/highlight-detection.md](research/highlight-detection.md) | SOTA is query-driven + visual-only; audio is a marginal add-on; none run query-free on raw long footage. |
| [research/audio-highlight.md](research/audio-highlight.md) | Audio = acoustic energy only, never dialogue *content*; the dialogue gap is real (modulo arXiv:2509.16811). |
| [research/egocentric-video.md](research/egocentric-video.md) | Rich data + localization tasks, but no edit-worthiness benchmark; replace PySceneDetect with a change-point→video-LLM cascade. |
| [research/music-edit-landscape.md](research/music-edit-landscape.md) | Beat tracking is solved; selection is the white space; pre-answers "isn't this just Apple Memories?". |
| [research/interval-recap.md](research/interval-recap.md) | Metadata used only for clustering, never as a narrative arc — Lore's Playwriter opening. |
| [research/eval-metrics.md](research/eval-metrics.md) | Don't use TVSum/SumMe F1 (near-random); keep AV-Harmony; Bradley-Terry human study for Human-Likeness. |

## Build

| Doc | What it is |
|---|---|
| [BUILD.md](BUILD.md) | Setup, the M0 "break CutClaw" baseline, how Lore plugs in. |
| [notes/cutclaw-code-map.md](notes/cutclaw-code-map.md) | Verified map of CutClaw's code — every seam Lore touches. |
| [lore/README.md](lore/README.md) | The `lore/` package: modules, data contracts, status. |

Try the scaffold (no deps): `python3 -m lore.pipeline plan --regime interval --instruction "a day at the coast"`

## Status

Foundation laid (2026-06-05): thesis, architecture, plan, six verified research dossiers, evaluation suite. **Primary claim → composition** (selection is the enabling front end; [open-questions.md](open-questions.md) Q1). **CutClaw cloned + code-mapped; `lore/` package scaffolded** — config + orchestrator dry-run run today; stage stubs (`metadata`, `segmentation`, `worthiness`, `compose`) carry real interfaces wired to the verified CutClaw seams. Next: **M0** (break CutClaw on raw footage), then **M2** (worthiness gate).
