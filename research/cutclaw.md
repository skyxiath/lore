# CutClaw — Verified Teardown

> Primary sources, fetched and cross-checked 2026-06-05. Paper: [arXiv:2603.29664](https://arxiv.org/abs/2603.29664) ([HTML](https://arxiv.org/html/2603.29664v1)) · Code: [github.com/GVCLab/CutClaw](https://github.com/GVCLab/CutClaw) · Lab: GVCLab. **Everything here is checked against the actual paper/repo, not the unreliable pasted conversation that kicked off this project.**

## One sentence

CutClaw is an agentic (multi-MLLM) system that takes **hours-long footage + a music track + a text instruction** and produces a **short, beat-synchronized, instruction-following montage**, by using the music's structure as a fixed temporal skeleton and pruning the intractable global timeline search into many cheap local retrieve-and-trim loops.

## The wedge (why Lore exists) — VERIFIED

CutClaw's benchmark "raw footage" is **5 feature-length films + 5 long-duration vlogs** (1–3 hours each, ~24 hours total). Films and vlogs are **already-edited, professionally-shot footage** — every frame is intentional, framed, lit, and graded.

Two consequences make CutClaw's headline ("hours-long **raw** footage editing") quietly untested in the regime Lore targets:

1. **Shot boundaries are handed to it for free.** Running PySceneDetect on a finished film recovers *the human editor's cuts*. The single hardest part of truly raw capture — finding where meaningful units begin/end in one continuous take — never arises.
2. **There is no garbage to discard.** Every shot is pre-selected by professionals, so CutClaw has **no upstream worthiness-*selection* gate** — its Reviewer does only *post-hoc perceptual-quality rejection* of an already-chosen candidate (auditing low-level visual saliency), never "is this hour-long stretch worth keeping at all." Its `Q_vis` aesthetic term operates in a world where everything is already good. The "throw away 90% of dead time" problem — the core skill of a human editor on raw footage — literally does not exist in its data. (Verified against the paper; don't overstate it as "no quality control at all.")

Lore's regime (POV/action-cam, smart glasses, interval capture) is the inverse: one continuous take or auto-triggered clips, no editorial cuts, wind/dead time everywhere, **no on-screen protagonist** (the wearer is behind the camera), often no dialogue. This is where CutClaw is structurally untested.

## The formal objective — VERIFIED

CutClaw frames editing as finding the edit `E*` maximizing a weighted sum of four terms:

> **E\* = arg max_E [ λ_v·Q_vis(E) + λ_n·Q_narr(E) + λ_c·Q_cond(E, I) + λ_s·Q_sync(E, M) ]**

- **Q_vis** — Visual Quality: "aesthetic appeal **and protagonist prominence**."
- **Q_narr** — Narrative Flow: coherent storytelling between adjacent clips.
- **Q_cond** — Semantic Alignment: fidelity of selected content to the instruction `I`.
- **Q_sync** — Rhythmic Alignment: visual cuts synchronize with musical beats in `M`.

The global search over hours of footage is intractable and blows past any MLLM context window, so CutClaw never solves this directly — the whole architecture is a coarse-to-fine **approximation** of this objective.

## Stage 1 — Bottom-up Multimodal Deconstruction — VERIFIED

**Video → searchable units:**
- **Shot detection:** PySceneDetect cuts the footage into atomic shots `s_i`.
- **Captioning:** an MLLM (**Qwen3-VL-30B-A3B**) extracts semantic attributes `A(s_i)` covering cinematography, character dynamics, environment.
- **Scene aggregation:** adjacent shots are merged by attribute similarity; a **scene boundary is induced when the similarity score drops below a threshold τ**.
- **Character grounding / Identity Injection:** character identities `H` (names + roles, inferred partly from dialogue via ASR) are injected as textual conditioning during scene analysis, so "a man" becomes "**Joker**" for consistent cross-scene tracking.

**Audio → searchable units:**
- **Keypoint detection:** three candidate-cut types — downbeats `K_db`, pitch changes `K_pc`, spectral-energy changes `K_se` — unioned into a pool `K_0 = K_db ∪ K_pc ∪ K_se`.
- **Structural segmentation:** an MLLM (**Qwen3-Omni-30B-A3B**) partitions the track into coarse structural units `U = {u_j}` (e.g. verse, chorus).
- **Refinement:** keypoints scored `score(t) = β^T · i(t)` (intensity-weighted by detection type); only the strongest keypoints per structural unit are kept.

## Stage 2 — Playwriter (global planner) — VERIFIED, and the key move

The Playwriter (**Gemini3-Pro**) uses the **musical structure as an invariant temporal anchor** and maps scenes onto it. Crucially it does **NOT output final timestamps**. For each shot it emits a **retrieval specification**:

> **p_i = (τ_i, z_id, d_i)** = (target duration, source scene index, semantic visual description)

- `τ_i` — target duration, derived directly from the audio segment.
- `z_id` — source scene index, restricting the Editor's search space.
- `d_i` — semantic description (plot/emotion) guiding content matching.

Two **hard constraints enforced by construction:**
1. **Disjoint Resource Allocation:** `Z_uj ∩ Z_uk = ∅` (j≠k) — a scene is assigned to only one musical section; no reuse across blocks.
2. **Structural Temporal Anchoring:** `Σ Duration(p) ≡ |u_j|` — planned shot durations sum *exactly* to the section length.

**This binding is the central trick:** turning one giant global search into many small local ones. Each shot spec is a *constraint*, not a final cut — the Editor resolves it locally.

## Stage 3 — Editor (ReAct agent) — VERIFIED

The Editor (**MiniMax-M2.1**) resolves each `p_i` with three actions:
1. **Semantic Neighborhood Retrieval:** initialize local search space `Ω_i` = shots in scene `z_id`; **Adaptive Expansion** to adjacent structural units if no good candidate is found.
2. **Fine-Grained Shot Trimming:** pick the sub-segment maximizing
   > **c_i\* = arg max_{c⊂s, |c|=τ_i} [ α·S_aes(c) + β·R_prot(c | H) ]**
   where `S_aes` = aesthetic score and **`R_prot` = Protagonist Presence Ratio** (cross-referenced against the character set `H`).
3. **Commit:** submit to Reviewer; **backtrack** if rejected.

## Stage 4 — Reviewer (rejection-sampling gate) — VERIFIED

The Reviewer (**MiniMax-M2.1**) is a quality gate with three checks; any violation → structured feedback → Editor backtracks:
1. **Semantic Identity Verification:** recompute `R_prot` via hierarchical MLLM sampling to filter false positives where the target character is merely a **background extra**.
2. **Temporal & Structural Integrity:** enforce non-overlap (`∩ E_prev = ∅`) and duration fidelity to the rhythmic grid.
3. **Perceptual Quality Assurance:** audit low-level visual quality/saliency.

## Implementation (repo) — VERIFIED

- Entry points: `app.py` (Streamlit UI) and `local_run.py` (CLI). Core logic in `src/`, rendering in `render/`, inputs in `resource/`, demos in `asset/`.
- **LiteLLM** as a unified gateway to all models (Video model, Audio model, Agent model). Example configs reference `openai/MiniMax-2.7` and `Gemini-3`.
- Config in `src/config.py` (CLI overridable), e.g. `--config.MAIN_CHARACTER_NAME`, `VIDEO_FPS: 2`, `PARALLEL_SHOT_MAX_WORKERS: 4`, `AUDIO_DETECTION_METHODS` (downbeat / pitch / mel-energy), `AUDIO_MIN_SEGMENT_DURATION: 3.0s`, `AUDIO_MAX_SEGMENT_DURATION: 5.0s`.
- Video decode via **Decord** (optional NVDEC); ASR via **Whisper** (`whisper_cpp` local option). No benchmark/dataset is released in the repo (gallery demos only).
- Pipeline artifacts named in docs: deconstruction → `shot_plan` → `shot_point` (+ validation).

## Experimental setup — VERIFIED

| Role | Model |
|---|---|
| Playwriter | Gemini3-Pro |
| Editor + Reviewer | MiniMax-M2.1 |
| Visual captioning | Qwen3-VL-30B-A3B |
| Audio/music captioning | Qwen3-Omni-30B-A3B |
| ASR | Whisper-v3-turbo |
| Shot detection | PySceneDetect |

- Preprocessing: **360p short-side, 2 FPS**.
- Benchmark: 10 source pairs (5 films + 5 vlogs), 1–3 h each, ~24 h total; 10 music tracks (Pop/Jazz/OST/Rock/R&B); target edits 20 s–1 min; **20 test cases** = 10 pairs × 2 instruction types (**Character-Centric** and **Narrative-Centric**).

## Metrics & key ablation — VERIFIED

- **Visual Quality** and **Instruction Following** auto-scored by **GPT-5.2**.
- **AV Harmony:** minimum temporal offset `Δt` between audio onsets (downbeats, pitch) and video scene cuts, rewarding alignment within a perceptual threshold (**Δt ≤ 0.1 s**).
- **User study:** 25 participants, ~2,000 opinions, rating Visual Quality, Instruction Following, Audio-Visual Harmony, **Human-Likeness**.

Ablation (Avg): Visual Quality / Instruction Following / AV Harmony
| Config | VQ | IF | AVH |
|---|---|---|---|
| w/o Audio | 75.5 | 68.9 | **77.2** |
| w/o Editor | 77.0 | 65.6 | 85.4 |
| w/o Reviewer | 76.0 | 69.8 | 87.2 |
| **CutClaw (full)** | **77.6** | **70.0** | **86.5** |

**Single biggest hit:** removing beat-aware audio analysis (fixed-length segmentation) drops AV Harmony **86.5 → 77.2**. This validates that the *music-sync machinery is the load-bearing innovation* — which is exactly the part Lore keeps.

## What Lore keeps vs. guts (summary)

| CutClaw component | Lore decision |
|---|---|
| Music-as-skeleton, keypoint grid, `Q_sync`, AV-Harmony | **KEEP** — it's the validated core and transfers directly |
| Playwriter → retrieval-spec → Editor/Reviewer loop structure | **KEEP** the structure; **re-anchor** the planner on activity/place/time instead of protagonist |
| PySceneDetect shot boundaries | **REPLACE** — raw footage has no editorial cuts → need event/activity segmentation |
| Identity Injection, `R_prot`, Semantic Identity Verification | **GUT** — no on-screen protagonist; replace with activity/place/attention anchor |
| Implicit assumption "every shot is usable" | **ADD a missing stage** — joint audio+visual highlight-worthiness gate upstream of the Playwriter |
| Diegetic audio used only for ASR→names | **PROMOTE** footage audio to a first-class *selection* signal (impact, cheer, laughter, wind-drop) |

See [north-star.md](../NORTH_STAR.md) for the thesis and [architecture.md](../plan/architecture.md) for the redesigned pipeline.
