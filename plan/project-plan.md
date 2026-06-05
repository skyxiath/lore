# Lore — Project Plan

> Build order, milestones, the motivating experiment, and the evaluation suite. Sequenced by *de-risking*, not by pipeline order. Thesis: [NORTH_STAR.md](../NORTH_STAR.md) · Pipeline: [architecture.md](architecture.md).

## Critical path & dependency logic

The two things most likely to sink the project are **(R1) the protagonist-free anchor being too fuzzy to plan against** and **(R2) evaluation/ground-truth**. So we front-load both, and we front-load the cheap, devastating motivating experiment.

```
M0 Motivating experiment ──► M1 Data + eval harness ──► M2 Worthiness gate ──► M4 Re-anchored Playwriter+ ──► M5 End-to-end ──► M6 Study
(break CutClaw)              (de-risk R2)               (the contribution)     spine (de-risk R1)            (flagship demo)   (the claim)
                                         └──► M3 Segmentation front end ──────────┘
```

## M0 — Motivating experiment: break CutClaw *(do first; cheap, high-leverage)*

Run CutClaw **as-is** on raw POV/glasses/interval footage. Document, quantitatively, the three predicted failure modes:
- PySceneDetect finds no meaningful units (count spurious cuts on head-whips/doorways vs. true events).
- The protagonist gate misfires (no on-screen protagonist → identity injection / `R_prot` degenerate).
- `Q_vis` has no dead time to reject (it includes long dead stretches a human would cut).

**Deliverable:** a before/after figure — CutClaw on *Interstellar* (pristine, pre-cut) vs. CutClaw on an hour of raw GoPro. This *shows* the gap instead of arguing it, and de-risks the "is this novel?" question. ([research/cutclaw.md](../research/cutclaw.md))

## M1 — Data + evaluation harness *(de-risk R2 early)*

- **Data pools:** Ego4D, Aria Everyday Activities, Nymeria (have IMU/GPS/gaze/audio); GoPro/FPV/travel POV; a small self-captured **interval** set for the flagship demo. Honest constraint: no public dataset pairs raw footage with human-editor edits.
- **Ground truth:** collect **per-event worthiness ratings** and **human-editor keep/cut + ordering** on a small set (expect low inter-annotator agreement on "importance" — that's a known property, not a bug; τ≈0.18 human ceiling per Otani).
- **Build the eval harness now** (see Evaluation Suite below) so every later milestone reports numbers from day one.

## M2 — Worthiness gate *(the core contribution; build before the spine)*

Implement stage [3]. Start query-free + audio-fused (Islam-et-al.-style recurrence or a CG-DETR/UVCOM saliency head over CLIP+SlowFast+PANNs), then add the **dialogue-content channel** (WhisperX→LLM importance) and the **metadata prior**.
- **Key ablation (the headline result for this stage):** visual-only vs. +acoustic vs. +dialogue vs. +metadata. Expect each to lift worthiness rank-correlation. This is the clean "+component → metric up" story that de-risks the deliverable.
- Validate against M1 worthiness labels with **Kendall's τ / Spearman vs. a random baseline** (NOT F1).

## M3 — Segmentation front end *(parallel with M2)*

Implement stage [2] (change-points → video-LLM → event aggregation). For **interval footage this is mostly free** (clips are pre-segmented), so prototype the flagship demo path here first, then generalize to continuous POV/glasses. Metadata ingestion (GPMF / Aria MPS) lands here.

## M4 — Re-anchored Playwriter + Editor + Reviewer *(de-risk R1)*

Port CutClaw's spine; swap the anchor. **Pin down the activity/place/attention anchor concretely** (this is R1 — do it as a written spec before coding): what exactly is "activity coherence," what makes a place transition legal, how attention (gaze/motion) scores a moment. Re-anchor the Playwriter on the time/place/activity arc with gaps-as-ellipses; re-score the Editor (`S_activity`, optional `S_motion-on-beat`); re-check the Reviewer (coherence replaces identity verification). Keep music deconstruction (allin1) and the hard constraints unchanged.

## M5 — End-to-end + flagship demo

Wire [1]→[8]. Produce the **interval "day recap"**: a day captured 1-min-every-10, compressed to ~45s music-synced film. This is the headline artifact. Then a continuous-POV example and a glasses example.

## M6 — Evaluation & human study *(the claim)*

Run the full suite (below). Compare **Lore vs. CutClaw-as-is vs. a commercial baseline (GoPro Quik / Apple Memories) vs. human-edited ceiling**. The pairwise human study on **Human-Likeness** is the dimension that matters most.

---

## Evaluation Suite *(a first-class deliverable — design locked here)*

Three stages, three families of metric. What transfers from CutClaw and what must be discarded ([research/eval-metrics.md](../research/eval-metrics.md)):

**(i) Worthiness selection**
- **Kendall's τ / Spearman's ρ** of predicted worthiness vs. human worthiness ratings, **always reported against a random baseline**. Expect low absolute values (human ceiling τ≈0.18) — interpret relative to random, not in absolute.
- **DO NOT use TVSum/SumMe F1** — [Otani et al. CVPR 2019](https://arxiv.org/abs/1903.11328) showed random summaries match SOTA F1; it's segmentation-driven and near-meaningless.
- Precision@k of kept events vs. human keep-set, for an interpretable number.

**(ii) Music sync** *(transfers cleanly — keep the external beat)*
- **AV-Harmony** (CutClaw's min onset↔cut offset, Δt≤0.1s) — reuse directly.
- **Beat-alignment F1 / AV-Align** ([TempoTokens av_align.py](https://github.com/guyyariv/TempoTokens/blob/master/av_align.py), ±1-frame window). Watch the dead-time caveat: near-zero motion-energy segments can distort optical-flow-based AV-Align.

**(iii) Overall quality & Human-Likeness** *(the one we care about)*
- **MLLM-as-judge proxy** for fast iteration: [VideoScore](https://arxiv.org/abs/2406.15252) (~0.77 Spearman with humans; 72.1% pairwise vs GPT-4o 60.8%). Use rubric-based pairwise judging; revalidate on a Lore-specific subset since VideoScore is trained on generated-video artifacts (off-distribution risk).
- **Pairwise human study** (the real claim): Bradley-Terry / Elo over Lore vs. baselines vs. human ceiling; report **Krippendorff's α / Cohen's κ** for inter-rater reliability; pre-register sample size to separate Lore from the CutClaw baseline.
- **Aesthetic floor:** Q-Align / MUSIQ as a sanity check, not a primary metric.

**Discard from CutClaw:** Protagonist Presence Ratio, Semantic Identity Verification, identity injection — no on-screen protagonist. Replace with an **activity/place/attention coherence** metric (no off-the-shelf version exists → a small contribution to define one).

---

## Scope discipline

- Every milestone must yield a **clean ablation or a comparison figure**. If a feature doesn't produce one, it's a stretch goal, not core.
- Ambitious ideas (free audio/video decoupling, J/L-cuts, learned end-to-end worthiness) live in [open-questions.md](../open-questions.md) — scoped, not deleted.
- Cite [arXiv:2509.16811](https://arxiv.org/abs/2509.16811) as nearest neighbor; differentiate on regime (raw POV/glasses/interval, 90% dead time) + metadata×semantics fusion + protagonist-free anchor. Do not claim "first to score dialogue."
