# SOTA Visual Highlight Detection & Moment Retrieval

> Lore research dossier · topic key: `highlight-detection` · verification confidence: **high** · generated 2026-06-05 via verified web research.

## Video Highlight Detection & Moment Retrieval for Lore (2024–2026)

This dossier maps the current MR-HD (moment retrieval + highlight detection) landscape onto Lore's regime — raw POV/glasses/interval footage with ~90% dead time, no editorial cuts, and no on-screen protagonist — and is blunt about what does NOT yet exist.

### 1. The benchmark: QVHighlights, and why it is NOT Lore's regime

QVHighlights ([Lei et al., NeurIPS 2021](https://arxiv.org/abs/2107.09609)) is the field's anchor: 10,000+ YouTube vlog/news videos, each ~150s, segmented into **2-second clips**. Each clip gets a text query, a relevant moment window, and **5-point saliency scores**. The two tasks: **moment retrieval** (find the window matching the query) and **highlight detection** (score clip saliency). It is the only standard set that supports BOTH jointly.

Critical caveat for Lore: QVHighlights videos are already curated/edited YouTube content with queries pre-written by annotators who watched the video. It is **query-conditioned** and assumes a relatively short clip where a highlight exists. Lore's footage has no query, no guarantee anything is worth keeping, and runs for hours. The benchmark structurally does not test "is there any signal in this 9-minute gap of someone walking."

### 2. The DETR lineage and current leaderboard

Modern MR-HD descends from **Moment-DETR** (the QVHighlights baseline; DETR-style encoder-decoder, set prediction, no proposals/NMS, CLIP+SlowFast inputs). The lineage:

- **QD-DETR** (CVPR 2023): query-*dependent* video representation via cross-attention + negative-pair learning. First big jump.
- **UniVTG** (ICCV 2023): unifies VTG labels/tasks (retrieval, highlight, summarization) under one formulation; enables large-scale pretraining.
- **TR-DETR** (AAAI 2024, [arXiv 2401.02309](https://arxiv.org/pdf/2401.02309)): "task-reciprocal" transformer exploiting MR↔HD reciprocity, with local-global multimodal alignment.
- **UVCOM** (CVPR 2024): unified comprehension framework bridging the MR/HD gap.
- **CG-DETR** ([arXiv/repo](https://github.com/wjun0830/CGDETR)): correlation-guided query-dependency calibration; current top of the *standard reproducible* leaderboard for highlight detection.
- **R2-Tuning** (ECCV 2024, [arXiv 2404.00801](https://arxiv.org/html/2404.00801v2)): parameter-efficient image-to-video transfer; a 2.7M-param "R² Block" (≈1.5% of params) on **frozen CLIP-B/32 only** — no SlowFast, no audio — yet competitive.

**Reproducible QVHighlights numbers (Lighthouse toolkit, CLIP+SlowFast features)** ([Lighthouse, EMNLP 2024 Demo](https://arxiv.org/html/2408.02901v1)). The table below uses the Lighthouse **test-split** reproductions (the paper reports both val and test; numbers move by 1–3 points between splits, so cite the split explicitly):

| Model | R1@0.5 | R1@0.7 | mAP avg | HIT@1 |
|---|---|---|---|---|
| Moment-DETR | 54.4 | 33.9 | 32.6 | 56.7 |
| EaTR | 57.2 | 38.9 | 36.6 | 57.9 |
| QD-DETR | 62.1 | 44.6 | 38.8 | 61.6 |
| UVCOM | 62.6 | 47.6 | 39.6 | 62.8 |
| TR-DETR | 65.2 | 48.8 | 39.8 | 62.1 |
| **CG-DETR** | 64.9 | 48.1 | **40.7** | **67.0** |

On Lighthouse's CLIP+SlowFast **test** numbers, **CG-DETR leads on highlight detection** (mAP avg 40.7, HIT@1 67.0) and **TR-DETR leads R1@0.5** (65.2). (Note: on the **val** split the leaders shift slightly — e.g. CG-DETR R1@0.7 jumps to 52.1 and TR-DETR HIT@1 to 66.2 — so any single-number claim must name the split. An earlier draft of this dossier quoted inflated mAP figures, e.g. CG-DETR 43.3 / TR-DETR 42.6 / UVCOM 42.5; those do not match the Lighthouse paper's reproductions and have been corrected.)

R2-Tuning reports (CLIP-only): R1@0.5 **68.0**, R1@0.7 **49.4**, mAP avg **40.8**, HIT@1 **64.2** — competitive with or beating the SlowFast-augmented DETR specialists on R1 with ~4× fewer learnable parameters. Note that its mAP avg (40.8) is roughly on par with CG-DETR's reproduced 40.7, not far above the field; the genuine standout is its R1 with a frozen-CLIP-only backbone and a 2.7M-param adapter.

### 3. MLLM/LLM-based temporal grounding

A parallel, fast-rising line uses (M)LLMs to *generate* timestamps. From the [VTG-with-MLLM survey (2025)](https://arxiv.org/pdf/2508.10922): **TimeChat** (time-aware frame encoding + sliding video Q-Former), **VTG-LLM** (absolute-time tokens), **Momentor** (time encoder to fix token-quantization error + temporal position encodings), **Grounded-VideoLLM** / **VideoMind** (structured temporal reasoning), and **TRACE** ([arXiv 2410.05643](https://arxiv.org/html/2410.05643), causal event modeling — strong across YouCook2/Charades/QVHighlights).

The standout for retrieval accuracy is **Mr.BLIP / Chrono** ([Meinardus et al., arXiv 2406.18113](https://arxiv.org/html/2406.18113v2)): BLIP-2 (frozen image encoder + Q-Former) + Flan-T5, with ~19M trainable params via LoRA (rank 8), representing time as **integer-second tokens interleaved with frame tokens**. QVHighlights test: R1@0.5 **74.77**, R1@0.7 **60.51** — well above the DETR specialists on retrieval. BUT: it does **moment retrieval only** (no saliency/HIT@1), samples a **fixed 60 frames** for a 150s video (one frame ~every 2.5s), and uses **no additional input signal — no transcript and no audio**. The authors explicitly note it struggles with "very short moments in long videos" and "high-frequency jump cuts" given the frame-sampling resolution.

Takeaway: MLLMs win on language-conditioned retrieval and generalization; DETR specialists still own joint highlight *saliency*.

### 4. THE KEY QUESTION FOR LORE — what features do these actually consume?

**They are overwhelmingly visual + text.** The canonical QVHighlights feature set is **CLIP + SlowFast** (2s clips). The toolkit truth, from [Lighthouse](https://github.com/line/lighthouse): the library supports video and audio feature extractors including ResNet152+GloVe, CLIP, CLIP+SlowFast, **CLIP+SlowFast+PANNs (audio)**, I3D+CLIP, and CLAP. So audio *is plumbed in via PANNs* (AudioSet-pretrained), but:

- **Audio is optional and marginal for query-conditioned MR-HD.** It is an add-on feature config, not a core driver; the Lighthouse ablations show **CLIP+SlowFast** generally beats CLIP alone, and both beat ResNet152+GloVe — the SOTA leaders in the table above run CLIP+SlowFast (no audio). PANNs audio gives small gains at best in this regime and none of the leaders rely on it.
- **None score narratively-important DIALOGUE.** PANNs is an *acoustic event / audio-tagging* model (trained on AudioSet's 527 sound classes — sounds and sound events, not speech content). No widely-cited MR-HD model on QVHighlights ingests ASR/transcripts of *what is said*, to our knowledge. The literature observation that "lexical content from transcripts is the most informative modality for meeting hotspots" exists, but is **not** integrated into QVHighlights-style detectors. This is a genuine open gap.

Where audio genuinely matters is **query-free** highlight detection. [Unsupervised Audio-Visual Recurrence HD (arXiv 2407.13933)](https://arxiv.org/html/2407.13933v1) is the most Lore-relevant: it is **completely query-free**, uses PANNs audio + visual features (ResNet-34 for YouTube-HL/TVSum; SlowFast+CLIP for QVHighlights), K-means pseudo-categories (over UMAP-reduced features), and cosine-similarity *recurrence* scoring. Its ablation shows **audio-only pseudo-highlights beat visual-only** (e.g. YouTube-HL 66.36 vs 62.76; TVSum 58.34 vs 53.35), and combining helps (YouTube-HL **68.3** mAP; TVSum **60.3** top-5 mAP). This is direct evidence that audio is a strong, sometimes dominant, highlight cue — exactly what Lore needs for its worth-keeping gate. Separately, **Audio Moment Retrieval (AMR)** is now its own task: Lighthouse's [Clotho-Moment (synthetic; language-based AMR, ICASSP 2025)](https://github.com/line/lighthouse) and **CASTELLA** (human-annotated long-audio captions+temporal boundaries, [arXiv 2511.15131](https://arxiv.org/abs/2511.15131), ICASSP 2026) localize moments in *audio* from text — useful if Lore wants the music/ambient track to drive selection. (CASTELLA also seeds a [DCASE 2026 challenge task on audio moment retrieval from long audio](https://dcase.community/challenge2026/task-audio-moment-retrieval-from-long-audio).)

### 5. Metrics

- **Moment retrieval:** R1@0.5, R1@0.7 (recall@1 at IoU thresholds), mIoU; mAP averaged over IoU thresholds.
- **Highlight detection:** **mAP** and **HIT@1** (whether the top-scored clip is a "Very Good" highlight). TVSum uses **top-5 mAP**; YouTube-HL uses mAP.

### 6. Hours-long raw footage vs short trimmed clips

This is the hard wall. Every method above is built for ~150s (QVHighlights) or ~30s (Charades-STA) clips:
- **DETR specialists** densely encode all 2s clips — fine for minutes, but compute/memory scale with clip count, and the saliency head was trained on edited video where highlights are common.
- **MLLMs** sample a fixed 20–60 frames *regardless of length*, so a 1-hour video collapses to roughly one frame per minute — destroying the fine boundaries Lore's cuts need.
- The realistic long-form precedent is **Ego4D NLQ / Goal-Step / Moment Queries** ([Ego4D, 3000 hrs egocentric](https://openaccess.thecvf.com/content/CVPR2022/papers/Grauman_Ego4D_Around_the_World_in_3000_Hours_of_Egocentric_Video_CVPR_2022_paper.pdf)) — videos up to hours, moments of a few seconds. 2025 challenge work (e.g. OSGNet, GazeNLQ, Bayesian temporal-order priors) targets exactly this needle-in-haystack, **egocentric (glasses/POV)** setting — the closest existing analog to Lore's Aria/Ray-Ban regime — but it is still query-conditioned and not query-free worthiness scoring.

### 7. Transferable to Lore's "worth-keeping" gate — and what's missing

**Transferable:** (a) CLIP+SlowFast (or frozen-CLIP à la R2-Tuning) as a cheap, strong per-clip feature backbone; (b) PANNs/CLAP audio features as a parallel stream — already plumbed in Lighthouse; (c) the **query-free recurrence/saliency** paradigm from the unsupervised AV-recurrence work, which is the right shape for "is this even worth keeping" with no query and no protagonist; (d) HIT@1 / mAP saliency heads from CG-DETR/UVCOM as a worthiness scorer; (e) Ego4D long-form chunking strategies for hours of footage.

**Missing (= Lore's opportunities):** No widely-cited MR-HD model, to our knowledge, (1) **scores narratively-important dialogue/speech content** (PANNs hears sound events, not words; ASR is unused in QVHighlights-style detectors); (2) runs **natively, query-free, on hours of raw unedited POV/interval footage** with 90% dead time — every standard benchmark assumes edited video where highlights are dense; (3) exploits **capture metadata** (timestamps, GPS, IMU) as a worthiness prior; (4) handles **pre-segmented interval clips with 9-minute gaps**. The combination Lore needs — *query-free + audio-aware (including speech) + long-form raw + metadata-grounded worthiness* — does not appear to exist as a single published system today.

## Sources
- https://arxiv.org/abs/2107.09609 (QVHighlights / Moment-DETR, NeurIPS 2021)
- https://arxiv.org/pdf/2107.09609
- https://arxiv.org/html/2408.02901v1 (Lighthouse, EMNLP 2024 Demo — QVHighlights val/test reproductions)
- https://github.com/line/lighthouse (Lighthouse repo; audio/PANNs, Clotho-Moment, CASTELLA, AMR)
- https://github.com/wjun0830/CGDETR (CG-DETR)
- https://arxiv.org/pdf/2401.02309 (TR-DETR, AAAI 2024)
- https://github.com/EasonXiao-888/UVCOM (UVCOM, CVPR 2024)
- https://arxiv.org/html/2404.00801v2 (R2-Tuning, ECCV 2024)
- https://arxiv.org/html/2406.18113v2 (Mr.BLIP / Chrono)
- https://arxiv.org/pdf/2508.10922 (Survey: Video Temporal Grounding with MLLMs, 2025)
- https://arxiv.org/html/2410.05643 (TRACE)
- https://arxiv.org/html/2407.13933v1 (Unsupervised Audio-Visual Recurrence Highlight Detection)
- https://openaccess.thecvf.com/content/CVPR2022/papers/Grauman_Ego4D_Around_the_World_in_3000_Hours_of_Egocentric_Video_CVPR_2022_paper.pdf (Ego4D)
- https://arxiv.org/html/2506.03710v1 (OSGNet @ Ego4D Episodic Memory 2025)
- https://github.com/wjun0830/QD-DETR (QD-DETR, CVPR 2023)
- https://arxiv.org/abs/1912.10211 (PANNs: Large-Scale Pretrained Audio Neural Networks — AudioSet audio tagging / sound event detection)
- https://arxiv.org/abs/2511.15131 (CASTELLA: Long Audio Dataset with Captions and Temporal Boundaries, ICASSP 2026)
- https://dcase.community/challenge2026/task-audio-moment-retrieval-from-long-audio (DCASE 2026 Audio Moment Retrieval from Long Audio task)
