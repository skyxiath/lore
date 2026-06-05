# Lore — Open Questions

> Unresolved forks, each with the trade-off and a current lean. These are decisions to make deliberately, not drift into. Pulled from the verified dossiers ([research/](research/)) and the strategic framing ([NORTH_STAR.md](NORTH_STAR.md)).

## Strategic

### Q1. Primary claim: selection vs. composition? — ✅ RESOLVED (2026-06-05): composition
**Decision:** the **composition side** (the re-anchored Playwriter / protagonist-free narrative spine) is the headline contribution; the **selection side** (worthiness gate) is the enabling front end — built "good enough to unblock composition," not over-invested as the primary claim.
- **Rationale:** composition is where "human-edited feel" lives and where the flagship day-recap is judged; selection is genuinely load-bearing (garbage in → garbage out) but supporting.
- **Guardrail (do not forget):** composition is the more *contested* novelty axis (CutClaw composes; [2509.16811](https://arxiv.org/abs/2509.16811) composes with dialogue+beats). The contribution MUST foreground the **new narrative anchor** — protagonist-free activity/place/time arc, interval gaps-as-ellipsis, metadata-driven ordering. If it drifts to "CutClaw on different footage," it collapses. Lead with the anchor.

### Q2. How do we differentiate from [arXiv:2509.16811](https://arxiv.org/abs/2509.16811)?
That 2025 system already does instruction-conditioned selection + dialogue/speech scoring + beat-alignment. We cannot claim "first to score dialogue for editing."
- **Lean:** differentiate on **regime** (truly-raw POV/glasses/interval, 90% dead time — they target general multi-hour footage), **signal fusion** (capture metadata × semantics; they don't use IMU/GPS/gaze), **downbeat/structure-aware** timing, and the **protagonist-free activity/place anchor**. Read 2509.16811 in full and write a precise delta paragraph before finalizing the contribution list.

### Q3. Do we collect a dataset?
No public dataset pairs raw lifestyle footage with human-editor ground-truth edits, and none scores edit-worthiness on dead-time footage. This gates honest evaluation.
- **Options:** (a) bootstrap weak supervision from GoPro Quik / existing vlog edits; (b) collect a small self-annotated worthiness + keep/cut set; (c) both. **Lean:** (b) small + (a) weak-supervision to scale. A clean small dataset could itself be a contribution — but it's scope; decide based on timeline.

### Q4. How ambitious on audio re-composition?
The diegetic-audio decoupling idea (keep a clip's native sound under the music; J/L-cuts; sound bridges) is the most "human-editor" move and genuinely novel-feeling, but it explodes the search + eval space.
- **Lean:** **shelve as a scoped stretch** behind a working [1]–[7]. If pursued, constrain hard: keep timelines mostly aligned; only swap a wind-trashed segment's audio or do sound bridges at transitions. Don't allow free decoupling.

## Technical

### Q5. Worthiness gate: hand-built/zero-shot or learned?
- Zero-shot (CLIP+CLAP+LLM scoring) is fast to stand up and needs no training data. A learned head (CG-DETR/UVCOM-style saliency over CLIP+SlowFast+PANNs) is stronger but needs labels (Q3).
- **Lean:** start zero-shot to unblock the pipeline; add a learned head if M1 data supports it. The audio-visual **recurrence** approach ([Islam et al.](https://arxiv.org/abs/2407.13933)) is query-free and unsupervised — attractive, but **does its pseudo-category recurrence survive single-user heterogeneous lifestyle footage** (no "category" to recur against)? Test early.

### Q6. Interval footage: per-clip or cross-clip worthiness?
Score each 1-min clip independently, or use cross-clip context (novelty/recurrence) across the 9-min gaps?
- **Open.** Cross-clip likely helps narrative coherence but adds complexity. No prior work on gap-aware temporal modeling for interval capture. Prototype per-clip first; measure whether cross-clip context improves human-likeness.

### Q7. Defining the activity/place/attention anchor concretely (R1).
The conceptual crux. "Protagonist presence" is crisp; this isn't. What *exactly* is activity coherence? What makes a place transition legal? How does attention (gaze/motion/head-stabilization) score a moment with no on-screen subject?
- **Action:** write this as a spec *before* coding M4. No off-the-shelf activity/place coherence metric exists — defining one is a small contribution.

### Q8. Does the dialogue-importance LLM survive noisy unscripted ASR?
Extractive-importance and turning-point methods assume clean text (meetings, screenplays). Wearable ASR has wind, footsteps, crosstalk, disfluencies.
- **Open.** No benchmark exists for narrative-importance on noisy lifestyle transcripts. Validate on real WhisperX output, not clean transcripts.

### Q9. Music-sync metrics under dead time.
AV-Align is optical-flow-based; dead-time segments have near-zero motion energy, which could inflate or deflate the score.
- **Action:** sanity-check AV-Align behavior on low-motion segments; consider masking or normalizing.

### Q10. Compute: can saliency heads run densely over hours?
Every QVHighlights leader assumes ~150s clips; MLLMs collapse a 1-hour video to ~1 frame/minute. At what length does memory force chunking (Ego4D-style)?
- **Action:** the change-point + worthiness front end must chunk like Ego4D NLQ/Goal-Step rather than feed footage whole. Profile early.

## Acknowledged related work to cite (not gaps)
- [arXiv:2509.16811](https://arxiv.org/abs/2509.16811) — Prompt-Driven Agentic Video Editing (nearest neighbor; see Q2).
- "Picturesque Highlights from Egocentric Vacation Videos" (arXiv 1601.04406) — aesthetic ego-highlight + GPS (frame-level, not segment worthiness).
- EgoEdit (arXiv 2512.06065, CVPR 2026) — egocentric *instruction-guided visual edits*, not keep/cut worthiness.
- Repurpose-10K (AAAI 2025), E-SyncVidStory — dialogue-unit repurposing for UGC.
