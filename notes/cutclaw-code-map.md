# CutClaw Code Map (verified against the clone, 2026-06-05)

> Ground truth for where Lore plugs in. Read from `external/CutClaw/` at clone time. Paper teardown: [../research/cutclaw.md](../research/cutclaw.md). Pipeline design: [../plan/architecture.md](../plan/architecture.md).

## Run entry point: `local_run.py`

CLI args:
- `--Video_Path`, `--Audio_Path`, `--Instruction`, `--SRT_Path`
- `--instruction_type {object,narrative}` (paper's Character-Centric vs Narrative-Centric)
- `--type {film,vlog}` ← **Lore adds `pov` / `interval` here**
- `--config.PARAM VALUE` overrides (e.g. `--config.VIDEO_FPS 1`)

Pipeline runs as **3 concurrent threads**, then plan → edit → render:
- **Thread A — ASR + Character ID** (`run_asr`, `assign_speakers_to_srt`, `analyze_subtitles`). **Skipped entirely for `vlog`.** ← the identity/protagonist front end Lore guts.
- **Thread B — Video deconstruction:** `decode_video_to_frames` → shot detection → `video_caption.process_video` → `scene_merge.OptimizedSceneSegmenter.segment` → `scene_analysis_video.SceneVideoAnalyzer.analyze_scenes_dir`. For `vlog` it explicitly "processes without subtitles" and "analyzes scenes without subtitles."
- **Thread C — Audio:** `audio_caption_madmom.caption_audio_with_madmom_segments` (madmom downbeats + pitch + mel-energy + LLM structure/keypoint captions).
- **Plan:** `Screenwriter(...).run(instruction)` → `shot_plan_{instruction_id}.json` (`subtitle_path` passed **only for film**).
- **Edit:** `if type==film: from src.core import EditorCoreAgent; elif vlog: from src.core_vlog import EditorCoreAgent`. `ParallelShotOrchestrator` if `PARALLEL_SHOT_ENABLED`.
- **Render:** `render/render_video.py`.

> **Lore's `pov`/`interval` regime branches from the `vlog` path** (no ASR-for-names, no subtitles assumed), then adds: event segmentation (swap shot detection), the worthiness gate (new stage), metadata ingestion, and activity-anchored planning.

## Stages communicate via JSON artifact files (the stable contract)

Everything between stages is a file on disk under `VIDEO_DATABASE_FOLDER` (default `./Output/`):

| Artifact | Path (per `local_run.py`) | Produced by | Consumed by |
|---|---|---|---|
| Shot boundaries | `.../frames/shot_scenes.txt` | shot detection | scene merge |
| Captions | `.../captions/captions.json` | `video_caption.process_video` | scene analysis |
| **Scenes** | `.../captions/scenes/scene_0.json` | `scene_merge.save_scenes` | Screenwriter, Editor |
| Scene summaries | `.../captions/scene_summaries_video/` | `SceneVideoAnalyzer` | Screenwriter |
| **Audio captions** | `.../Audio/<id>/captions/captions.json` | madmom audio caption | Screenwriter, Editor |
| Transcript/SRT | `srt_with_characters` (film only) | ASR + char ID | Screenwriter, Editor |
| **shot_plan** | `.../<vid>_<aid>/shot_plan_<iid>.json` | `Screenwriter.run` | `EditorCoreAgent.run` |
| **shot_point** | Editor output list | `EditorCoreAgent` | render |

**Implication:** Lore injects by **transforming these JSON files** — insert event-segmenter output as `scenes/scene_0.json`, run the worthiness gate to prune/annotate scenes before the Screenwriter reads them — with minimal agent rewrites.

## Key classes / functions

- **Screenwriter** = paper's *Playwriter* — `src/Screenwriter_scene_short.py`
  - `class Screenwriter` (L1014), `.run(instruction)` (L1024) → shot_plan
  - `select_audio_segment` (L151), `generate_structure_proposal` (L343), `generate_shot_plan` (L469)
  - **Already does dialogue handling:** `select_hook_dialogue` (L793), `_match_dialogue_lines_to_subtitles` (L623), `refresh_hook_dialogue_in_shot_plan` (L969). *Relevant to the dialogue channel AND to differentiating from arXiv 2509.16811 — note CutClaw already touches "hook dialogue."*
- **Editor** = `EditorCoreAgent` — `src/core.py` L803; `.run(shot_plan_path)` (L1381) → list of shot results
  - ReAct tools: `commit` (L124), `semantic_neighborhood_retrieval` (L274), `fine_grained_shot_trimming` (L449) ← **the `α·S_aes + β·R_prot` trim; swap `R_prot`→`S_activity` here**, `review_clip` (L395)
  - `ParallelShotOrchestrator` (L1550) for film-mode parallelism
  - `src/core_vlog.py` is imported for vlog mode (separate Editor variant — confirm it exists / is released)
- **Reviewer** — `src/Reviewer.py`, `Review_timeline(timeline)` (L47); face/protagonist + aesthetic checks
- **Deconstruction** — `src/video/deconstruction/`: `get_character.analyze_subtitles` (identity injection via `CHARACTER_IDENTIFICATION_PROMPT`) ← **GUT**; `scene_merge.OptimizedSceneSegmenter`; `scene_analysis_video.SceneVideoAnalyzer`; `video_caption.process_video`
- **Audio** — `src/audio/`: `audio_caption_madmom`, `audio_Madmom`, `structure.py`, `detectors.py` (KEEP — this is the validated core)
- **Prompts** — `src/prompt.py` (incl. `CHARACTER_IDENTIFICATION_PROMPT`; Screenwriter/Editor/Reviewer prompts to re-anchor)
- **Config** — `src/config.py`

## Config seams Lore uses (`src/config.py`)

- `SHOT_DETECTION_MODEL` ∈ {`scenedetect`,`autoshot`,`transnetv2`,`Qwen3VL`} — **pluggable; Lore adds a `lore_event` segmenter.**
- `VIDEO_TYPE` ∈ {`film`,`vlog`} — **Lore adds `pov`,`interval`.**
- Protagonist machinery — **toggle OFF for Lore:** `MAIN_CHARACTER_NAME=""`, `ENABLE_FACE_QUALITY_CHECK=False`, `ENABLE_TRIM_SHOT_CHARACTER_ANALYSIS=False`, `MIN_PROTAGONIST_RATIO`/`VLM_MIN_BOX_SIZE` (n/a).
- Audio: `AUDIO_DETECTION_METHODS=["downbeat","pitch","mel_energy"]`, `AUDIO_TOTAL_SHOTS=200` (drop to 30–80 for debug), madmom params. **KEEP.**
- `VIDEO_RESOLUTION=240` (paper says 360p; configurable), `VIDEO_FPS=2`, `VIDEO_MAX_MINUTES=None` (set 3–10 for debug).
- Models via **LiteLLM**, 3 separate endpoints — all blank by default, must be set: `VIDEO_ANALYSIS_{MODEL,ENDPOINT,API_KEY}`, `AUDIO_LITELLM_{MODEL,API_KEY,BASE_URL}`, `AGENT_LITELLM_{MODEL,URL,API_KEY}`. `ASR_BACKEND ∈ {whisper_cpp, litellm}`.

## Notable: upstream roadmap overlaps Lore
CutClaw's own roadmap lists "Talking-Head + Visual Mixing" (narration-driven + supporting visual — adjacent to our J/L-cut idea) and a "Playwriter Upgrade." Cite as concurrent direction; Lore's raw-footage/worthiness/metadata angle is distinct.

## Practical gotchas
- `external/CutClaw` was cloned `--depth 1`; it carries its own `.git` (git-ignored by Lore). Re-clone via [../BUILD.md](../BUILD.md).
- Heavy deps (torch 2.8, madmom, pyannote, decord) + ffmpeg + 3 LLM API endpoints are required to run end-to-end. The `lore` package dry-run needs none of these.
