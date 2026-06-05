# Status vs. the Original Plan — honest gap analysis

> Where Lore actually is (2026-06-05) against [NORTH_STAR.md](../NORTH_STAR.md) + [plan/architecture.md](../plan/architecture.md) + [plan/project-plan.md](../plan/project-plan.md). Legend: ✅ built · ⚠️ prototype/partial · ❌ missing.

## The one-line truth

**A real end-to-end pipeline runs and produces watchable, beat-synced, diegetic-audio recaps from raw footage** — but it's a *thin* path. The two things the plan called the headline (the protagonist-free **narrative arc**) and a first-class deliverable (the **evaluation suite**) are the least built. We have a working demo, not yet the contribution.

## Pipeline (architecture stages 1–8)

| Stage | Planned | Now | Gap |
|---|---|---|---|
| 1. Ingestion + metadata | decode + **GPMF/Aria sensors (IMU/GPS/gaze)** + WhisperX | ⚠️ filename **timestamps only** → day-arc + chapters ([metadata_arc.json](../tests/test%201/lore_out/metadata_arc.json)); OpenAI transcription instead of WhisperX | No IMU/GPS/gaze ingested (Insta360 may carry some); metadata used only for *ordering*, not as a worthiness/arc signal |
| 2. Event/activity segmentation | 3-layer cascade (change-points → video-LLM → aggregate), replaces PySceneDetect | ⚠️ **sidestepped** — interval clips are pre-segmented (1 clip = 1 event) | Real segmentation of *continuous* footage not built; we only handle the interval regime |
| 3. ★ Worthiness gate ★ | joint **CLIP+SlowFast + PANNs/BEATs/CLAP + dialogue + metadata**, learned/recurrence | ⚠️ **MLLM-as-scorer** (gpt-4o vision + transcript) → per-clip worthiness ([day_recap_probe.py](../tools/day_recap_probe.py)) | No real **audio-event** features (PANNs/CLAP); **metadata not fused**; **no diversity/redundancy penalty** (the repetitive-car-shots bug); not the planned recurrence model |
| 4. Music deconstruction | madmom **beats + downbeats + structure** (verse/chorus/drop) | ⚠️ librosa **beats only** ([compose_recap.py](../tools/compose_recap.py)) | No downbeats/structure → **no dynamic pacing** (can't go sparse-in-verse / dense-on-drop) |
| 5. Playwriter (re-anchored) — **the headline** | activity/place/time **narrative arc**, instruction-following, gaps-as-ellipsis | ⚠️ **chronological sort** of top-worthiness clips | **Biggest gap.** No genuine arc reasoning, **no instruction-following**, no ellipsis logic. Currently "sort by time," not "tell the day's story" |
| 6. Editor (re-scored) | ReAct trim, **S_activity**, motion-on-beat | ⚠️ **center-trim** to slot length | No sub-clip optimization, no activity/attention scoring of *where* to cut, no motion-on-beat |
| 7. Reviewer (re-checked) | coherence + quality gate, backtracking | ❌ **none** | No output QA at all |
| 8. Render | ffmpeg + diegetic audio | ✅ ffmpeg, **diegetic audio mixed + ducked** ([recap_audio.mp4](../tests/test%201/lore_out/recap_audio.mp4)) | done |

## Contributions (NORTH_STAR)

| Contribution | Status |
|---|---|
| 1. Protagonist-free **narrative spine** (headline) | ⚠️ **weakest** — chronological only; the actual *arc* reasoning is unbuilt |
| 2. **Worthiness gate** (enabling) | ⚠️ works as an MLLM prototype; missing audio-event + metadata + diversity |
| 3. **Evaluation suite** (called first-class) | ❌ **not started** — no Kendall τ vs human labels, no AV-Harmony measurement, no human study |
| 4. Dataset (stretch) | ⚠️ we now have a real 1,175-clip archive indexed; no worthiness ground-truth labels yet |

## Milestones (project-plan)

- **M0 — break CutClaw on raw footage:** ❌ **skipped.** We built Lore's own pipeline instead of first running CutClaw-as-is to *show* it breaks. The motivating experiment still owes a figure.
- **M1 — data + eval harness:** ⚠️ data ✅ (test-1 + the indexed archive); eval harness ❌.
- **M2 — worthiness gate:** ⚠️ prototype built; the planned ablation (visual vs +acoustic vs +dialogue vs +metadata, by Kendall τ) ❌.
- **M3 — segmentation + metadata:** ⚠️ partial (interval pre-segmentation; timestamps only).
- **M4 — re-anchored Playwriter/Editor/Reviewer:** ❌ (replaced by the minimal composer).
- **M5 — end-to-end + flagship:** ✅ **achieved early** (recap renders) — but via the minimal composer, not the agent spine.
- **M6 — eval + human study:** ❌.

## CutClaw-on-Modal (the planned "real composer" upgrade)
⚠️ **scaffolded, not run** ([modal_app.py](../modal_app.py), [MODAL.md](../MODAL.md)). Modal + OpenAI are authenticated; the image build + OpenAI-routing are the untested first-run steps.

## What this means — priorities to close the gap

1. **Make the composer actually *compose* (stage 5)** — the headline. Even without the CutClaw agent: order by the day's *arc* (chapters/sessions, build-and-release), follow a text instruction, handle gaps as ellipses. Right now "chronological sort" undersells the whole thesis.
2. **Diversity penalty in the gate (stage 3)** — kills the repetitive-shots problem; small change, big visible win; it's the recurrence idea.
3. **Downbeats + dynamic pacing (stage 4)** — madmom/allin1 so cut density tracks the music.
4. **Stand up *any* evaluation (contribution 3)** — even a small pairwise human-likeness A/B (chronological vs arc-aware vs CutClaw) and an AV-Harmony number. The plan called this first-class; it's at zero.
5. **The M0 "break CutClaw" figure** — still the cheapest, most persuasive artifact for the writeup.
6. **Run CutClaw on Modal** — to compare the agent spine against the minimal composer.
