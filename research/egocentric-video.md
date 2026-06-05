# Egocentric / POV / Smart-Glasses Video Understanding

> Lore research dossier · topic key: `egocentric-video` · verification confidence: **high** · generated 2026-06-05 via verified web research.

## Egocentric / POV / Smart-Glasses Video Understanding for Lore: SOTA and Gaps

This dossier surveys what exists (2024–2026) for turning continuous, raw first-person footage into structured, segmentable, edit-worthy events — and, just as importantly, what does not exist. It is written against Lore's regime: ~90% dead time, no editorial cuts, no on-screen protagonist, often no dialogue, plus interval footage (1-min clip every ~10 min) and capture metadata.

### 1. The benchmark landscape: localizing moments in untrimmed ego video

The dominant resource is **Ego4D** (3,670 hours of daily-life video from 931 wearers across 9 countries / 74 locations; the [egocentric vision survey](https://arxiv.org/html/2503.15275v1) notes this is still the largest, and tiny next to web-scale image data). Its **Episodic Memory** suite is the closest existing analog to "find moments in wearable footage":

- **Moment Queries (MQ)** — localize *all* instances of an action category in an untrimmed clip and label them. This is essentially temporal action localization on ego video, evaluated by **mAP** and **Recall@k at temporal-IoU**. State of the art is modest: a 2022 ActionFormer-based submission hit ~21.76% avg mAP (itself a 2nd-place leaderboard solution, [ActionFormer for Ego4D MQ, arXiv 2211.09074](https://arxiv.org/abs/2211.09074)); a 2023 submission reached **~26.62% avg mAP and 45.69% R@1 at tIoU=0.5** — also explicitly a *2nd-place* solution to the 2023 challenge, which improved results via SoftNMS threshold tuning ([NMS Threshold matters paper, arXiv 2307.02025](https://arxiv.org/abs/2307.02025)). Clips average >10 min and instances span ~1 s to minutes — directly comparable to Lore's footage.
- **Natural Language Queries (NLQ)** — given a text question, return the temporal window containing the answer. 2024's ObjectNLQ reached **mean R@1 ≈ 23.15** (2nd place, CVPR 2024 EgoVis workshop, [ObjectNLQ, arXiv 2406.15778](https://arxiv.org/abs/2406.15778)). Low absolute numbers signal how hard precise temporal grounding in raw ego video remains.
- **EgoSchema** (derived from Ego4D; 5,000+ MCQ, ~3-min clips) tests long-form understanding; the 2024 challenge winner **HCQA hit ~75%** via a hierarchical caption-then-reason pipeline (fine-grained captioning → context summarization → inference) ([HCQA, arXiv 2406.15771](https://arxiv.org/abs/2406.15771)). For reference, the prior best (LifelongMemory) was ~68%.
- **X-LeBench** (EMNLP 2025 Findings) targets *extremely long* ego video (minutes to >1 hour) and finds that current video-LLMs "struggle to aggregate information across long temporal spans, maintain narrative consistency, and handle rapid scene transitions" ([X-LeBench](https://aclanthology.org/2025.findings-emnlp.822.pdf)) — precisely Lore's failure modes.

**Ego-Exo4D** (1,286 h, 740 wearers, 13 cities, 5,035 takes of 1–42 min each) adds multi-view tasks: keystep recognition (278 classes; top-1 accuracy metric), proficiency estimation, ego-pose, relations, and task graphs ([Ego-Exo4D keystep docs](https://docs.ego-exo4d-data.org/benchmarks/keystep/keystep_recoginition/); [CVPR 2024 paper](https://openaccess.thecvf.com/content/CVPR2024/html/Grauman_Ego-Exo4D_Understanding_Skilled_Human_Activity_from_First-_and_Third-Person_Perspectives_CVPR_2024_paper.html)). Notably the keystep benchmark lets models use gaze, IMU, point clouds, camera pose, and audio at *training* time but restricts test-time input to ego-view RGB only (audio, narrations, exo video, and metadata are explicitly excluded at test) — confirming the field treats these sensors as auxiliary, not core, for this task.

**Gap #1:** Every one of these Ego4D/Ego-Exo4D tasks is *semantic localization or recognition*. None scores **aesthetic/narrative worthiness** ("would a human editor keep this?"). MQ tells you *where* a "chopping" action is, not whether it belongs in a 60-second music edit, and there is no Ego4D "highlight-worthiness" track. The gap is narrower than "nothing exists," though: there is an older line of *aesthetic* ego-highlight work — e.g. "Discovering Picturesque Highlights from Egocentric Vacation Videos" (2016) ranks frames by composition/symmetry/color-vibrancy and uses GPS to weight locations ([arXiv 1601.04406](https://arxiv.org/abs/1601.04406)) — and "Videogenic" uses professional photos as a worthiness prior. But these select *aesthetic still frames* (not narrative video segments for keep/cut), are not tuned for dead-time-heavy raw footage, and predate modern video-LLM reasoning. To our knowledge there is no widely-cited benchmark that scores *narrative/edit worthiness of video segments* in raw, continuously-recorded ego footage.

### 2. Smart-glasses platforms and released datasets

**Project Aria** (Meta research glasses; Gen 2 announced Feb 2025) is the richest sensor source. The **Aria Everyday Activities (AEA)** dataset (143 sequences, ~7.3 h total, released Feb 2024) ships, per the [AEA paper](https://arxiv.org/html/2402.13349v1): high-res RGB (20 fps, 1408×1408), two monochrome tracking cameras, eye-tracking video, **two IMU streams (≈800 Hz and 1000 Hz), 7-channel spatial audio (48 kHz), magnetometer, barometer**, plus Machine Perception Service (MPS) outputs — **closed-loop globally-aligned 6DoF 1 kHz trajectories (VIO/SLAM)**, semi-dense scene point cloud, **per-frame 3D gaze**, and **time-aligned speech (ASR) transcription**. **Nymeria** (ECCV 2024; 300 h, 264 participants, 50 locations) adds full-body ground-truth motion and **hierarchical motion-language annotations** (301.5K sentences) ([Nymeria, arXiv 2406.09905](https://arxiv.org/abs/2406.09905)). Other 2024–25 Aria datasets: HOT3D (hand/object 3D), Look-and-Tell (synchronized gaze+speech+video grounding), egoEMOTION (physiological signals).

**Ray-Ban Meta** consumer glasses have no comparable public research dataset; they are a *capture/UX analog*, not a data source. GoPro/FPV likewise lack research datasets, but GoPro's **Quik app already auto-generates beat-synced highlight videos** with music and effects from raw footage, and uses on-device **HiLight tagging** — the closest commercial cousin to Lore, and evidence the product need is real, but it is a black box with no published worthiness model.

**Gap #2:** Aria gives Lore exactly the metadata it wants (GPS-like SLAM trajectory, IMU, gaze, timestamps, speech transcripts), but **to our knowledge no published method fuses these multimodal Aria-style signals into a highlight/edit pipeline.** Datasets exist; the application does not. (Note: EgoEdit, CVPR 2026 / [arXiv 2512.06065](https://arxiv.org/abs/2512.06065), is a recent egocentric video *editing* dataset/model/benchmark, but it does instruction-guided *visual* edits — object substitution/removal under hand occlusion and egomotion — not worthiness scoring or music-synced highlight assembly, so it does not fill this gap.)

### 3. Egocentric summarization & highlight detection — what makes a "moment"

Classic ego-summarization literature defines importance via the wearer's *interaction*: nearness to hands, **gaze**, frequency of object occurrence, and important people/objects (e.g. "Predicting Important Objects" / "Discovering important people and objects" lines of work; see [survey](https://arxiv.org/html/2503.15275v1)). The survey frames this as **Content Summarization** and names the core problem bluntly: "wearable devices are typically in a default active state, continuously recording, while the content of interest often requires the model to autonomously identify it" — i.e. the dead-time problem is acknowledged but unsolved at scale.

On the general (non-ego) side, **highlight detection / moment retrieval** is mature on **QVHighlights** (10K videos), **TVSum**, **YouTube Highlights**, with strong 2024 methods (UVCOM, TR-DETR, MomentDETR-lineage; the [Lighthouse library](https://github.com/line/lighthouse) reproduces many). Audio matters but in a *shallow* way: the unsupervised audio-visual recurrence method ([arXiv 2407.13933](https://arxiv.org/html/2407.13933v2)) extracts audio with **PANN** (pre-trained on AudioSet) and scores moments by acoustic *recurrence* ("cheers," "sizzling"), reaching 68.30 mAP (YouTube Highlights), 60.34 top-5 mAP (TVSum), 18.38 mAP (QVHighlights) — and audio-alone *beat* visual-alone on TVSum (58.34 vs 53.35 top-5 mAP). But it explicitly does **not transcribe or reason over dialogue**, and does not handle audio-absent or constant-noise (wind/footsteps) footage.

**Gap #3 (answers Lore's open question):** Existing highlight detectors *do* use audio, but as generic acoustic texture, **not as narratively-important speech.** No mainstream highlight benchmark scores "this sentence is the emotional core of the clip." A worthiness gate that reads ASR/dialogue semantics (e.g. via a video-LLM over Aria's speech transcription) would, to our knowledge, be genuinely novel.

### 4. IMU / head-motion / gaze as signals

There is real, recent momentum here. ECCV 2024's **Masked Video + body-worn IMU autoencoder** learns joint video-motion representations for ego action recognition; **COMODO** (2025) distills video into IMU for efficient HAR; gaze prediction improves when fusing video + head IMU (accelerometer/gyro). Datasets newly include eye-tracking: Nymeria, Ego-Exo4D, EgoExoLearn. The signal is well-motivated — head IMU directly encodes the wearer's motion/attention — and is the natural substitute for the missing on-screen protagonist.

**Gap #4:** IMU/gaze are used for *recognition and gaze estimation*, almost never for **change-point segmentation or worthiness scoring**. Yet a gaze fixation or an IMU stillness-after-motion event is a strong cue that the wearer found something worth attending to. This is low-hanging fruit for Lore.

### 5. How Lore should segment raw POV footage (replacing PySceneDetect-on-films)

CutClaw's PySceneDetect assumes hard cuts a human editor already placed. Raw POV/interval footage has **none**; PySceneDetect would either over-fire on head-motion exposure swings or under-fire across long continuous takes. Recommended replacement — a three-layer cascade:

1. **Cheap multimodal change-point segmentation (no semantics).** Combine optical-flow/motion magnitude, **IMU stillness↔motion transitions**, **gaze fixation clustering**, scene-embedding shifts, and (Aria) SLAM-trajectory/place changes to cut continuous footage into candidate events. This mirrors the human "event segmentation" prior used in [Memory Storyboard, arXiv 2501.12254](https://arxiv.org/abs/2501.12254). For **interval footage**, the 9-min gaps are *free* hard boundaries — each 1-min clip is already a segment; treat metadata timestamps/GPS as the cross-clip narrative spine.
2. **Semantic event labeling via a video-LLM / keystep pass.** Run a dense-captioning or keystep-style model (TimeChat/VTimeLLM-lineage, or Gemini/GPT-4o with timestamps) over candidate segments to attach activity/place/attention labels — the new narrative anchor replacing CutClaw's protagonist identity injection.
3. **Joint audio+visual worthiness gate (the missing piece).** Score each segment for keep/cut using: visual saliency + gaze, acoustic recurrence/energy (PANN-style), AND **dialogue/ASR semantics** from Aria speech transcripts (novel vs. prior art). Only surviving segments enter CutClaw's music-sync machinery, which Lore keeps intact.

**Bottom line for Lore:** SOTA can *localize and label* events in raw ego video (MQ/NLQ/keystep) and *summarize by interaction* (gaze/hands), and metadata-rich glasses data exists (Aria/Nymeria). What does **not** appear to exist, to our knowledge, is (a) a worthiness gate tuned for raw, dead-time-heavy personal footage that scores *narrative video segments* (older work scores aesthetic *still frames*; EgoEdit does instruction-guided visual edits, not keep/cut), (b) any highlight method that scores narratively-important dialogue, and (c) any system fusing IMU/gaze/SLAM-metadata into a music-synced edit. Those three absences are Lore's contribution surface.

## Sources
- https://arxiv.org/html/2503.15275v1
- https://github.com/EGO4D/episodic-memory
- https://arxiv.org/abs/2406.15778
- https://arxiv.org/abs/2307.02025
- https://arxiv.org/abs/2211.09074
- https://arxiv.org/abs/2406.15771
- https://egoschema.github.io/
- https://aclanthology.org/2025.findings-emnlp.822.pdf
- https://docs.ego-exo4d-data.org/benchmarks/keystep/keystep_recoginition/
- https://ai.meta.com/blog/ego-exo4d-video-learning-perception/
- https://openaccess.thecvf.com/content/CVPR2024/html/Grauman_Ego-Exo4D_Understanding_Skilled_Human_Activity_from_First-_and_Third-Person_Perspectives_CVPR_2024_paper.html
- https://arxiv.org/html/2402.13349v1
- https://arxiv.org/abs/2406.09905
- https://ai.meta.com/blog/nymeria-dataset-reality-labs-research-egocentric-human-motion-understanding/
- https://www.projectaria.com/
- https://www.marktechpost.com/2024/02/27/meta-releases-aria-everyday-activities-aea-dataset-an-egocentric-multimodal-open-dataset-recorded-using-project-aria-glasses/
- https://arxiv.org/html/2407.13933v2
- https://github.com/line/lighthouse
- https://github.com/EasonXiao-888/UVCOM
- https://link.springer.com/chapter/10.1007/978-3-031-72649-1_18
- https://arxiv.org/abs/2501.12254
- https://community.gopro.com/s/article/GoPro-Quik-Auto-Highlight-Videos
- https://community.gopro.com/s/article/What-is-HiLight-Tagging-and-How-Does-it-Work
- https://arxiv.org/abs/1601.04406
- https://arxiv.org/abs/2512.06065
- https://github.com/snap-research/EgoEdit
