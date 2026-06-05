# Progress Log & CutClaw-Modification Status

> Updated 2026-06-05. Companion to [status-vs-plan.md](status-vs-plan.md) (gap analysis). This doc = what we've *done* + the honest answer to "what have we modified in CutClaw."

## The honest headline on CutClaw

**We have not modified CutClaw's source code.** `external/CutClaw` is the pristine clone. Instead of editing CutClaw's heavy stack (which won't build locally — torch 2.8 / madmom / decord on Python 3.14 / Apple silicon), we **reimplemented its front-end ideas in Lore's own lightweight pipeline**, and we **scaffolded** the real CutClaw modifications without running them yet.

So "modifications to CutClaw" breaks into three layers:

1. **Conceptual (decided):** the keep / gut / add plan.
   - **Keep:** music-as-skeleton + cut-on-beat (we reimplemented this with librosa, not CutClaw's madmom).
   - **Gut:** the on-screen-protagonist machinery (identity injection, Protagonist Presence Ratio, Semantic Identity Verification).
   - **Add:** an upstream worthiness gate + a metadata day-arc — stages CutClaw never had.
2. **Scaffolded (written, not run):** the actual CutClaw config changes live in [`lore/config.py`](../lore/config.py) `cutclaw_overrides()` — `VIDEO_TYPE=vlog` (branch off the no-protagonist path), `MAIN_CHARACTER_NAME=""`, `ENABLE_FACE_QUALITY_CHECK=False`, `ENABLE_TRIM_SHOT_CHARACTER_ANALYSIS=False`, `SHOT_DETECTION_MODEL=lore_event` — plus [`modal_app.py`](../modal_app.py) to run CutClaw on a Modal GPU with its 3 LLM endpoints routed to OpenAI. **None of this has been executed against CutClaw yet.**
3. **Reimplemented (working):** Lore's current videos use **our own composer**, NOT CutClaw's agent spine. CutClaw's Playwriter/Editor/Reviewer are stand-in-replaced by deterministic selection + center-trim + ffmpeg.

**Bottom line:** the current working pipeline is *Lore-native and CutClaw-inspired*, not CutClaw-with-edits. Running/modifying CutClaw itself (via Modal) is still ahead of us.

## What maps to what (our tools → architecture stage → CutClaw relationship)

| Lore tool | Stage | vs. CutClaw |
|---|---|---|
| `tools/index_volume.py` | 1 (ingest) | **new** — index a raw archive by capture-time; CutClaw takes one film |
| `tools/metadata_arc.py` | 1 (metadata) | **new** — timestamp→day-arc + chapters; CutClaw has none |
| `tools/day_recap_probe.py` | 2–3 (segment + worthiness) | **new gate** (OpenAI vision + dialogue) replacing CutClaw's Qwen3-VL captioner *and* adding the worthiness scoring it lacks |
| `tools/select_clips.py` | 3 (diversity) | **new** — the redundancy penalty |
| `tools/compose_recap.py` | 4–8 (music→render) | **minimal stand-in** for CutClaw's whole agent spine: librosa beats (not madmom), chronological+diversity selection (not the Playwriter), center-trim (not the ReAct Editor), no Reviewer, ffmpeg render |

## Done so far (chronological)

1. **Research foundation** — verified CutClaw teardown + 6 fact-checked dossiers; [NORTH_STAR](../NORTH_STAR.md), [architecture](../plan/architecture.md), [plan](../plan/project-plan.md), [open-questions](../open-questions.md).
2. **CutClaw cloned + fully code-mapped** ([notes/cutclaw-code-map.md](cutclaw-code-map.md)) — found the key seams (file-based artifacts, vlog branch, config-toggleable protagonist).
3. **`lore/` package** — config + orchestrator scaffold (dry-run works).
4. **Working end-to-end pipeline (OpenAI + librosa/ffmpeg)** — the 5 tools above.
5. **Bugs fixed:** diegetic-audio mixing + ducking; mixed-aspect-ratio → fixed 1920×1080 canvas (was causing black frames on volume renders).
6. **Real videos rendered:**
   - test-1 interval day (2026-04-19): `recap.mp4` (silent) + `recap_audio.mp4` (diegetic audio).
   - Archive: 2026-01-18 waterfall hike, + a batch of the strong days (05-23 camping, 05-24 hike+roadtrip, 05-02 coastal, 05-09 hangout).
7. **Archive indexed:** 1,175 unique clips / 42 capture-days; top recap days identified with full-data worthiness.
8. **Infra:** OpenAI + Modal authenticated; Modal CutClaw runner scaffolded (unrun).

## Biggest things still undone
The CutClaw agent spine itself (run on Modal), the narrative-*arc* Playwriter (we only sort chronologically), downbeat-aware pacing, and **any** evaluation (Kendall-τ / AV-Harmony / human study). See [status-vs-plan.md](status-vs-plan.md).
