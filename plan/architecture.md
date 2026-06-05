# Lore — Architecture

> The redesigned pipeline. Inherits CutClaw's music-sync spine ([research/cutclaw.md](../research/cutclaw.md)); replaces the film-era front end with a raw-footage front end. Every component cites the dossier that justifies it. Thesis: [NORTH_STAR.md](../NORTH_STAR.md).

## Pipeline at a glance

```
RAW INPUT (POV / glasses / interval clips) + music track + text instruction
   │
   ▼
[1] Ingestion & Metadata        decode + GPMF/Aria-MPS metadata + WhisperX ASR
   │
   ▼
[2] Event/Activity Segmentation  REPLACES PySceneDetect — change-points → video-LLM → events
   │
   ▼
[3] ★ WORTHINESS GATE ★          NEW — joint audio+visual+dialogue+metadata worthiness scoring
   │                              (prunes ~90% dead time → a shortlist of worthy events)
   ├──────────────┐
   ▼              ▼
[4] Music         (worthy events)
    Deconstruction (KEEP/upgrade: allin1 beats+downbeats+structure)
   │              │
   └──────┬───────┘
          ▼
[5] Playwriter (KEEP structure, RE-ANCHOR on activity/place/time)  → retrieval specs
          ▼
[6] Editor — ReAct (KEEP, RE-SCORE: activity/attention salience + motion-on-beat)
          ▼
[7] Reviewer (KEEP, RE-CHECK: activity/place coherence replaces identity verification)
          ▼
[8] Render (KEEP; optional diegetic-audio treatment / J-L cuts — scoped stretch)
          ▼
        SHORT MUSIC-SYNCED EDIT
```

Stages **[1]–[3]** are Lore's new front end. Stages **[4]–[8]** are CutClaw's spine, re-anchored.

---

## [1] Ingestion & Metadata Extraction

- **Decode:** Decord (as CutClaw), 360p / 2 FPS working resolution for the LLM passes; keep source for render.
- **Capture metadata (first-class, not throwaway):** parse **GPMF** for GoPro (GPS path, speed, elevation, g-force, scene tags, faces) and **Project Aria MPS / Aria Everyday Activities** streams for glasses (IMU ~800–1000 Hz, 6DoF SLAM trajectory, eye-gaze, spatial audio, time-aligned speech). These are exactly the signals Lore exploits and that CutClaw/films never have. ([research/egocentric-video.md](../research/egocentric-video.md), [research/music-edit-landscape.md](../research/music-edit-landscape.md))
- **ASR:** WhisperX (word-level timestamps + diarization) — needed for the dialogue-content channel, not just for names. ([research/interval-recap.md](../research/interval-recap.md))
- **Interval handling:** each auto-captured clip is an atomic unit; inter-clip gaps (timestamps) are recorded as deliberate ellipses for the Playwriter.

## [2] Event/Activity Segmentation — *replaces PySceneDetect*

Raw footage has no editorial cuts, so we manufacture meaningful boundaries with a **3-layer cascade** ([research/egocentric-video.md](../research/egocentric-video.md)):

1. **Cheap multimodal change-points:** IMU stillness↔motion transitions, gaze-fixation clustering, optical-flow magnitude change, SLAM place-change, audio-scene change. Cheap, runs over the whole stream, proposes candidate boundaries.
2. **Semantic pass:** a video-LLM (Qwen3-VL-class) dense-captions / keystep-labels each candidate segment → attributes: **activity, place, salient objects, who-is-speaking**. (This is CutClaw's captioning step, re-pointed at events instead of editorial shots.)
3. **Event aggregation:** merge adjacent segments by attribute **and metadata** similarity (extends CutClaw's similarity-threshold scene aggregation to be metadata-aware). Output: a sequence of **events** with attributes + time/place/activity tags.

> Precedent for the localization difficulty: Ego4D Moment Queries (~26.6% mAP, a *2nd-place* challenge result) and NLQ (~23% R@1) — i.e. this is genuinely hard, which is the point. We don't need their accuracy; we need usable event units feeding the gate.

## [3] ★ Worthiness Gate ★ — *the contribution*

Per event, fuse **four** signals into a worthiness score; keep the top events (massive pruning). This is the stage no prior system in this regime has. ([research/highlight-detection.md](../research/highlight-detection.md), [research/audio-highlight.md](../research/audio-highlight.md))

- **(a) Visual/acoustic salience (query-free):** per-clip **CLIP + SlowFast** visual features and **PANNs/BEATs** audio-event embeddings + **CLAP** + loudness/onset. Score with a query-free worthiness head — template from CG-DETR/UVCOM saliency heads or the **audio-visual recurrence** approach of [Islam et al. WACV 2025](https://arxiv.org/abs/2407.13933). *Motivating evidence:* in that work the **audio-only** stream beats visual-only (YouTube-HL 66.36 vs 62.76 mAP) — fuse audio in deliberately, don't bolt it on.
- **(b) Dialogue-content channel (the novel bit):** WhisperX transcript → an LLM scores **narrative importance of what was said**, conditioned on the instruction. Nearest prior art is [arXiv:2509.16811](https://arxiv.org/abs/2509.16811) (speech-act scoring + beat-abort-to-protect-narration) — cite and differentiate. Existing highlight detectors hear *sound*, not *words*; PANNs is AudioSet sound-event tagging, not speech understanding.
- **(c) Metadata worthiness prior:** IMU motion bursts, g-force spikes, GPS place-changes as a cheap interestingness prior (GoPro Quik proves sensor metadata can drive selection; Lore adds semantics on top).
- **(d) Instruction conditioning:** CLAP/CLIP-text and the LLM bias the score toward what the instruction asks for.

**Output:** a worthiness score + a keep-shortlist of events. Everything downstream operates only on the shortlist — this is what makes the regime tractable and is the human-editor "throw away 90%" skill made explicit.

## [4] Music Deconstruction — *KEEP as-is (madmom); optional upgrade*

**Verified against the clone:** CutClaw already implements this in `src/audio/` with **madmom** (downbeat + pitch + mel-energy detectors, `AUDIO_DETECTION_METHODS`) plus an LLM structure/keypoint-caption pass. Since composition is the primary claim (Q1), **keep madmom as-is** — it's the validated core; don't rebuild it.

*Optional, deprioritized upgrade:* **allin1** ([all-in-one](https://github.com/mir-aidj/all-in-one), WASPAA 2023) or **Beat This!** ([repo](https://github.com/CPJKU/beat_this), ISMIR 2024) for explicit functional structure (verse/chorus/drop), which would let **cut density track structure** (sparse in a verse, dense on a drop). Nice-to-have, not required. ([research/music-edit-landscape.md](../research/music-edit-landscape.md))

## [5] Playwriter — *KEEP structure, RE-ANCHOR*

Gemini-class global planner. Unchanged: music structure as the **invariant temporal anchor**; emits **retrieval specs** `p_i = (τ_i, event_index, semantic_description)` (same interface as CutClaw's `(τ_i, z_id, d_i)` — *constraints, not final timestamps*); same hard constraints (**disjoint allocation** across sections; planned durations **sum exactly** to section length).

**Re-anchored:** narrative spine is an **activity → place → time arc** instead of a protagonist. For interval footage the arc spans the day/trip and **9-minute gaps are deliberate ellipses** justified by place/activity change and absorbed by the music structure. Metadata-as-narrative-arc (vs mere clustering) appears to be an open gap. ([research/interval-recap.md](../research/interval-recap.md))

## [6] Editor (ReAct) — *KEEP, RE-SCORE*

Per spec: **Semantic Neighborhood Retrieval** over the assigned event (adaptive expansion to neighbors), then **trim** to `τ_i` maximizing:

> `c* = arg max [ α·S_aes(c) + β·S_activity(c) + γ·S_motion-on-beat(c) ]`

- `S_aes` — aesthetic score (Q-Align / MUSIQ as a floor).
- `S_activity` — **activity / attention salience** (gaze fixation, head-stabilization, subject-of-action) **replaces** CutClaw's Protagonist Presence Ratio.
- `S_motion-on-beat` *(new, optional)* — reward landing a **visual motion-energy peak on a musical beat** (the action-footage "cut on the turn/jump" feel). This is a *stronger* sync notion than CutClaw's "a cut sits on a beat." ([research/eval-metrics.md](../research/eval-metrics.md) — Visual Rhythm Prediction)

## [7] Reviewer — *KEEP, RE-CHECK*

Rejection-sampling gate; reject → structured feedback → Editor backtracks. Checks:
- **Activity/place coherence + attention** ← *replaces* Semantic Identity Verification (no protagonist to verify).
- **Temporal/structural integrity** (non-overlap; duration fidelity to the rhythmic grid) — *kept as-is*.
- **Perceptual quality** (kept).

## [8] Render — *KEEP; optional audio treatment*

Assemble on the music bed. **Scoped stretch** (see [open-questions.md](../open-questions.md)): selective **diegetic-audio treatment** — keep a clip's native sound (the impact, the cheer) under the music, or do **J/L-cuts / sound bridges** at transitions. Powerful and human, but expands the search/eval space — gate it behind a working [1]–[7].

---

## Model / tool table (starting choices)

| Function | Choice | Source dossier |
|---|---|---|
| Decode | Decord | cutclaw |
| Capture metadata | GPMF (GoPro), Aria MPS (glasses) | egocentric-video, music-edit-landscape |
| ASR | WhisperX (word ts + diarization) | interval-recap |
| Change-points | IMU/gaze/optical-flow/SLAM + audio-scene | egocentric-video |
| Visual features | CLIP + SlowFast (or frozen-CLIP R2-Tuning style) | highlight-detection |
| Audio features | PANNs / BEATs + CLAP + loudness/onset | audio-highlight |
| Worthiness head | query-free saliency (CG-DETR/UVCOM template) or AV-recurrence | highlight-detection, audio-highlight |
| Dialogue importance | WhisperX → LLM (instruction-conditioned) | audio-highlight, interval-recap |
| Beats/downbeats/structure | allin1 + Beat This! | music-edit-landscape |
| Video captioning / keystep | Qwen3-VL-class MLLM | cutclaw, egocentric-video |
| Playwriter | Gemini-class | cutclaw |
| Editor / Reviewer | strong agent LLM (MiniMax-class or equiv.) | cutclaw |
| Aesthetic floor | Q-Align / MUSIQ | eval-metrics |

> Model *choices* are swappable; the *interfaces* (events, worthiness scores, retrieval specs, keypoint grid) are the stable contract. Build against the interfaces.

---

## Implementation seams (verified against the clone)

Full map: [../notes/cutclaw-code-map.md](../notes/cutclaw-code-map.md). The four facts that shaped the scaffold:

1. **Stages hand off via JSON files** under `Output/` (`scenes/scene_0.json`, audio `captions.json`, `shot_plan_*.json`). → Lore injects by *transforming files* (write events as the scenes JSON; prune/annotate before the planner), not by rewriting agents.
2. **`pov`/`interval` branch from the existing `vlog` path** (which already skips ASR-for-names and "processes without subtitles"). → smaller change than a new regime from scratch.
3. **The protagonist machinery is config-toggleable** (`MAIN_CHARACTER_NAME=""`, `ENABLE_FACE_QUALITY_CHECK=False`, `ENABLE_TRIM_SHOT_CHARACTER_ANALYSIS=False`) and shot detection is **pluggable** (`SHOT_DETECTION_MODEL`). → most GUT/REPLACE decisions are config, not surgery. Encoded in `lore/config.py::LoreConfig.cutclaw_overrides`.
4. **Names:** the paper's *Playwriter* is the code's `Screenwriter` (`Screenwriter_scene_short.py`); the *Editor* is `EditorCoreAgent` (`core.py`, trim in `fine_grained_shot_trimming` ← swap `R_prot`→`S_activity`); the *Reviewer* is `Reviewer.Review_timeline`. CutClaw's Screenwriter already does "hook dialogue" selection — reuse it for the dialogue channel.

The `lore/` package wraps these seams; `python3 -m lore.pipeline plan` prints the live stage graph + overrides.
