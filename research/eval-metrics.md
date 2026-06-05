# Evaluation Methodology for Selection & Edits

> Lore research dossier · topic key: `eval-metrics` · verification confidence: **high** · generated 2026-06-05 via verified web research.

## Evaluation Methodology for Highlight Selection and Music-Synced Edits — A Dossier for Project Lore

Lore must evaluate three distinct stages: (i) highlight/worthiness SELECTION on raw, mostly-dead-time footage, (ii) MUSIC SYNC, and (iii) overall HUMAN-LIKENESS. These map onto three separate research literatures with very different maturity and reliability. This dossier grounds each in 2024–2026 primary sources, names which [CutClaw](https://arxiv.org/abs/2603.29664) metrics transfer, and is explicit about what does not yet exist.

### (a) Highlight-detection and moment-retrieval metrics — and why they only half-apply to Lore

The standard benchmark is [QVHighlights](https://papers.neurips.cc/paper/2021/file/62e0973455fd26eb03e91d5741a4a3bb-Paper.pdf) (10,148 YouTube videos with text queries, ground-truth spans, and 5-point saliency annotations on a Likert scale from "Very Good" to "Very Bad"). Its metrics: **Moment Retrieval** uses Recall@1 at IoU 0.5 and 0.7 (R1@0.5, R1@0.7) and mean Average Precision averaged over IoU thresholds [0.5:0.05:0.95] (mAP@Avg). **Highlight Detection** uses mAP and **HIT@1** — the hit ratio of the single highest-scored clip, counted correct if its saliency is "Very Good." These metrics measure *localization against human-labeled spans*: they presuppose a query and a ground-truth annotation per video. Lore has neither a query-conditioned span benchmark nor labels on its raw POV/Aria/interval footage. So mAP/R@1/HIT@1 are **usable only on a labeled internal benchmark Lore would have to build** (or by repurposing TVSum's importance scores). They do, however, define the right *shape* of the worthiness metric: rank clips by predicted worthiness, then measure agreement with a held-out worthiness label.

### (b) Video-summarization F1 is broken — use rank correlation (CRITICAL for Lore)

The most important single finding for Lore is [Otani et al., "Rethinking the Evaluation of Video Summaries," CVPR 2019](https://openaccess.thecvf.com/content_CVPR_2019/papers/Otani_Rethinking_the_Evaluation_of_Video_Summaries_CVPR_2019_paper.pdf). Using a randomization test, they showed **randomly generated summaries achieve F1 comparable to or better than SOTA** on SumMe and TVSum, and in some cases the random summaries outperform even the human-generated summaries. The cause: the F1 score is dominated by the *video segmentation* step (KTS / two-peak segmentation) and the knapsack subset-selection, not by the importance scores — verbatim, "the contribution of the importance scores were completely ignored by the benchmark tests." The knapsack solver implicitly discards long segments, so for a 15% summary "most of the segments are expected to be shared between generated and reference summaries regardless of [their] associated importance scores."

Their proposed fix: evaluate the **importance-score ranking** with rank-correlation against human annotations. Table 2 (TVSum) gives exact values — Kendall's **tau**: dppLSTM 0.042, DR-DSN 0.020, Random 0.000, **Human 0.177**; Spearman's **rho**: dppLSTM 0.055, DR-DSN 0.026, Random 0.000, **Human 0.204** (all four values for each coefficient verified directly against the paper's Table 2). Two implications for Lore: (1) report tau/rho, never F1-via-knapsack; (2) even the *human upper bound is low* (~0.18 tau) because importance is subjective with multiple valid answers — so Lore should expect and design for low absolute correlations and emphasize relative gains over a random baseline. This is the single most defensible, citable methodological choice Lore can make for its selection stage.

### (c) Aesthetic / visual-quality scorers as automated proxies

These map to CutClaw's "Visual Quality" axis and run with no ground truth. **NIMA**, **MUSIQ** ([Google, ICCV 2021](https://research.google/blog/musiq-assessing-image-aesthetic-and-technical-quality-with-multi-scale-transformers/), patch-based multi-scale, native-resolution), **LAION-Aesthetics** (CLIP-based predictor), and **BRISQUE/TOPIQ** are all available off-the-shelf in [IQA-PyTorch](https://github.com/chaofengc/IQA-PyTorch). The current SOTA proxy is [**Q-Align** (ICML 2024)](https://github.com/Q-Future/Q-Align), an LMM trained to predict discrete text-defined rating levels (excellent / good / fair / poor / bad) that is SOTA on image quality (IQA), image aesthetics (IAA), *and* video quality (VQA), unified into a single model called OneAlign. **Recommendation for Lore:** use Q-Align (VQA mode) as the primary aesthetic proxy and MUSIQ/LAION-Aesthetics as a secondary, faster signal. Caveat: aesthetic scorers reward *pretty* frames, not *narratively important* ones — a blurry but meaningful moment scores low. They are a quality floor, not a worthiness signal.

### (d) Audio-visual SYNC metrics beyond AV-Harmony

CutClaw's **AV-Harmony** measures objective alignment between visual cut points and musical keypoints. Two complementary, citable metrics transfer cleanly. **AV-Align** ([Yariv et al., AAAI 2024](https://arxiv.org/abs/2309.16429); [code](https://github.com/guyyariv/TempoTokens/blob/master/av_align.py)): detect audio onsets (librosa onset envelope) and video peaks (local maxima of mean Farneback optical-flow magnitude, ignoring maxima below a 0.1 magnitude floor), match within a +/- 1-frame window (i.e. `1/fps` seconds; each video peak matched to at most one audio peak), and report IoU = matched / (audio_peaks + video_peaks - matched). All of these implementation details were verified directly against the reference `av_align.py`. **Beat-alignment F1**: treat ground-truth music beats (librosa beat tracking) as positives and predicted cut times as detections; a cut within a tolerance window of a beat is a true positive, yielding precision/recall/F1. As a reference point for what is achievable on this kind of onset-alignment task, [Visual Rhythm Prediction (arXiv 1901.10163)](https://arxiv.org/pdf/1901.10163) frames visual-rhythm onset prediction against musical-onset ground truth on professionally edited music videos and reports a best F1 of ~79.6 (its results table shows precision 78.2 / F1 79.2 for the all-features model; the conclusion reports F1 79.6). The **Beat Alignment Score** (mean absolute onset-to-cut offset) is used in dance/V2M work. **Recommendation:** report beat-alignment F1 (tolerance ~1 beat-period/8) and median onset-to-cut offset in ms as interpretable, human-meaningful sync metrics, with AV-Align as a motion-energy cross-check.

### (e) MLLM-as-judge: a cheap proxy that must be calibrated

For instruction-following and overall quality, MLLM judges are scalable. [**VideoScore** (EMNLP 2024)](https://arxiv.org/abs/2406.15252) (originally released as MantisScore) reaches **Spearman 77.1** with humans on VideoFeedback-test (about 50 points above prior best metrics, and an average ~54-point improvement over GPT-4o across the five evaluated aspects) and **72.1% average pairwise accuracy on VBench**, beating GPT-4o (60.8%) and Gemini-1.5-Pro (56.3%); these numbers were verified directly against the paper's results tables. [**VideoJudge** (2025)](https://arxiv.org/html/2509.21451) shows video input is essential (MLLM judges beat text-only LLM judges) and that rubric-guided 3B judges can match 72B baselines. But reliability is genuinely contested: documented [biases](https://arxiv.org/html/2410.02736v1) include positional bias, self-enhancement (judges favor their own outputs), verbosity bias, and judging on "superficial quality" while ignoring instruction alignment. **Recommendation:** use an MLLM judge (VideoScore or a rubric-prompted Gemini/GPT) only as a *pairwise* judge with randomized A/B order, an explicit criterion-separated rubric (worthiness, coherence, sync, instruction adherence), and validate it against a human subset (report judge-human Spearman). Never use a single pointwise MLLM score as the headline result.

### (f) A rigorous pairwise human study for human-likeness

This is the dimension Lore most cares about and the only one that directly measures the goal ("approaches a good human editor"). Best practice from 2024–2026 arena work ([GenArena](https://arxiv.org/pdf/2602.06013), [Inclusion Arena](https://arxiv.org/html/2508.11452v1)): collect **pairwise** comparisons (Lore vs. CutClaw-baseline vs. random-cut vs. human-edited reference vs. ablations), aggregate with the **Bradley-Terry** model or **Elo**, and prefer pairwise to pointwise — pairwise is more consistent and even lets off-the-shelf VLMs hit SOTA agreement. Report **inter-rater reliability** (Cohen's/Fleiss' kappa or Krippendorff's alpha); VideoJudge reports 94.8% agreement / Cohen's kappa 89.5 on its cleanest pairs as a target bar. Use a [Bayesian Bradley-Terry variant](https://arxiv.org/pdf/2510.09333) that models rater quality to down-weight unreliable crowdworkers (the cited paper, "Efficient Bayesian Inference from Noisy Pairwise Comparisons," extends Bradley-Terry with Bayesian annotator-reliability modeling — verified). Practical sizing: include a human-edited upper bound and a random-cut lower bound as anchors; aim for enough comparisons per pair that BT confidence intervals separate conditions (typically hundreds of comparisons per pair, 3+ raters each), and screen raters with attention/gold checks. Be aware Elo can be [unreliable under model misspecification](https://arxiv.org/html/2502.10985v1) — BT with reported CIs is safer for a small-N research study.

### Which CutClaw metrics transfer to Lore — and which don't

CutClaw ([arXiv 2603.29664](https://arxiv.org/abs/2603.29664), "CutClaw: Agentic Hours-Long Video Editing via Music Synchronization") reports Visual Quality, Instruction Following (split into object-centric and narrative-centric), and AV Harmony (alignment between visual cut points and musical keypoints, rewarding alignments within a perceptual threshold of ~Δt ≤ 0.1s), plus protagonist/identity metrics (Protagonist Presence Ratio and Semantic Identity Verification) and a human-likeness user study. These metric definitions were verified directly against the paper.

- **Transfer:** AV-Harmony / AV-Align / beat-F1 (music sync machinery is regime-independent); Visual Quality via Q-Align; pairwise human study; MLLM-as-judge for instruction adherence.
- **Do NOT transfer:** every **protagonist-anchored** metric — Protagonist Presence Ratio, Semantic Identity Verification, identity injection. Lore's wearer is behind the camera; there is no on-screen protagonist. These must be *gutted* and replaced with **activity/place/attention** coherence metrics (see gaps).
- **Partially transfer:** CutClaw's narrative-coherence judging, but it must be re-anchored away from a person to activity/scene continuity.

### What does NOT exist yet (gaps = Lore's contribution)

1. **No highlight-worthiness benchmark for dead-time wearable/POV footage.** QVHighlights/TVSum are query- or genre-curated; none model 90% dead time, 9-minute interval gaps, or no-protagonist framing. Lore likely must *build* a small labeled benchmark (clips rated for worthiness + human editor reference edits) — this is itself a citable artifact.
2. **No standard metric for audio-driven worthiness of narratively-important DIALOGUE.** Audio *is* used in highlight detection — [unsupervised AV recurrence (arXiv 2407.13933)](https://arxiv.org/html/2407.13933v2) uses PANN/AudioSet features and claims (in the authors' words, "to the best of our knowledge") to be "the first to exploit both audio and visual components in unsupervised learning for video highlight detection" without a large external dataset (YouTube Highlights mAP 68.30, TVSum top-5 mAP 60.34, QVHighlights mAP 18.38 / HIT@1 24.71; all numbers verified against the paper) — but it scores **general acoustic energy/recurrence (cheers, sizzling), not speech content**; it does not target or distinguish dialogue. Scoring a quiet but semantically important spoken sentence is an open problem and a direct Lore opportunity.
3. **No activity/place/attention narrative-coherence metric** to replace protagonist machinery.
4. **No widely-cited metric, to our knowledge, exploits capture metadata** (GPS/IMU/timestamps) for worthiness — essentially untouched in the highlight/summarization literature.
5. **No public dataset, to our knowledge, pairs raw lifestyle footage with human-editor ground-truth edits**, which is exactly what a defensible human-likeness study needs as its upper anchor.

### Recommended metric set for Lore

- **(i) Highlight selection:** Kendall's tau + Spearman's rho of predicted worthiness vs. held-out human worthiness labels (Otani protocol); plus mAP / HIT@1 on a small internal labeled benchmark. Always report a **random-selection baseline** and a **dead-time-filtering baseline**. Never F1-via-knapsack.
- **(ii) Music sync:** Beat-alignment F1 (1-beat-period/8 tolerance) + median onset-to-cut offset (ms) + AV-Align IoU. (Keep CutClaw AV-Harmony for comparability.)
- **(iii) Aesthetic floor:** Q-Align VQA (primary), MUSIQ/LAION-Aesthetics (secondary).
- **(iv) Instruction following & coherence:** rubric-based pairwise MLLM judge (VideoScore + a frontier MLLM), order-randomized, validated against a human subset (report judge-human Spearman).
- **(v) Human-likeness (headline):** pairwise human study, Bradley-Terry/Elo ratings with confidence intervals, against random-cut (floor) and human-edited (ceiling) anchors, with Cohen's/Krippendorff's reliability reported and rater quality modeling.

## Sources

- https://arxiv.org/abs/1903.11328
- https://openaccess.thecvf.com/content_CVPR_2019/papers/Otani_Rethinking_the_Evaluation_of_Video_Summaries_CVPR_2019_paper.pdf
- https://mayu-ot.github.io/rethinking-evaluation-of-video-summaries/
- https://papers.neurips.cc/paper/2021/file/62e0973455fd26eb03e91d5741a4a3bb-Paper.pdf
- https://arxiv.org/abs/2107.09609
- https://ar5iv.labs.arxiv.org/html/2107.09609
- https://github.com/jayleicn/moment_detr
- https://arxiv.org/html/2407.13933v2
- https://arxiv.org/pdf/2407.13933
- https://research.google/blog/musiq-assessing-image-aesthetic-and-technical-quality-with-multi-scale-transformers/
- https://github.com/Q-Future/Q-Align
- https://arxiv.org/abs/2312.17090
- https://github.com/chaofengc/IQA-PyTorch
- https://arxiv.org/abs/2309.16429
- https://github.com/guyyariv/TempoTokens/blob/master/av_align.py
- https://arxiv.org/pdf/1901.10163
- https://arxiv.org/abs/2406.15252
- https://arxiv.org/html/2406.15252v1
- https://tiger-ai-lab.github.io/VideoScore/
- https://arxiv.org/html/2509.21451
- https://arxiv.org/html/2410.02736v1
- https://arxiv.org/pdf/2602.06013
- https://arxiv.org/html/2508.11452v1
- https://arxiv.org/pdf/2510.09333
- https://arxiv.org/html/2502.10985v1
- https://arxiv.org/abs/2603.29664
- https://arxiv.org/html/2603.29664
- https://huggingface.co/papers/2603.29664
- https://github.com/GVCLab/CutClaw
