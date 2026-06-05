# Audio-Aware Highlighting & Dialogue/Narrative Importance

> Lore research dossier · topic key: `audio-highlight` · verification confidence: **high** · generated 2026-06-05 via verified web research.

## Audio-Aware & Audio-Visual Highlight Detection + Dialogue Narrative-Importance Scoring — Research Dossier for Project Lore

### Scope and why this matters for Lore

CutClaw (the system Lore builds on) handles already-edited footage and needs no worthiness gate. Lore's regime — raw POV/glasses/interval footage that is ~90% dead time, no editorial cuts, no on-screen protagonist, often sparse dialogue — requires an upstream answer to *"what is even worth keeping?"* This dossier surveys (a) audio-visual highlight detection, (b) the audio backbones usable as saliency features, (c) speech/prosody saliency, and most importantly (d) whether anyone scores the **content of dialogue** for narrative importance. The short answer to (d): partially solved for clean text transcripts, essentially an **open gap** for raw video editing.

### (a) Audio-visual highlight detection: audio is used, but as energy/recurrence, not meaning

The strongest recent primary result is **"Unsupervised Video Highlight Detection by Learning from Audio and Visual Recurrence"** (Saskatchewan + Google Research, [arXiv 2407.13933](https://arxiv.org/abs/2407.13933)). It computes separate audio and visual pseudo-highlight scores via cross-video recurrence, fuses them with uni/bimodal attention, and uses **PANNs pretrained on AudioSet** for audio features. It reports mAP 68.30 on YouTube Highlights (prior best, CHD, 65.39), top-5 mAP 60.34 on TVSum (prior best, CHD, 52.76), and mAP 18.38 / HIT@1 24.71 on QVHighlights. Crucially, its audio signal is *generic recurrence* — "loud cheers and claps" or "the sizzling sound of food being cooked" — measured as how repetitive audio features are within a pseudo-category via cosine similarity; it explicitly does **not** distinguish speech, music, or dialogue, nor score what is said. (All four numbers and the prior-best baselines independently verified against arXiv 2407.13933v2, June 2026.)

The benchmark landscape: **QVHighlights** ([arXiv 2107.09609](https://arxiv.org/abs/2107.09609)) is the dominant moment-retrieval + highlight benchmark (10k+ YouTube videos incl. lifestyle vlogs, free-form query, 5-point saliency), with Moment-DETR as the seminal baseline and 2024-2025 SOTA shifting toward MLLM + RL methods. **Mr.HiSum** ([NeurIPS 2023](https://openreview.net/forum?id=tz7XkY6S9Z)) is the largest highlight dataset (31,892 videos, 1,788 hours, labels from YouTube "Most replayed" aggregated over 50k+ users/video). Notably, the dominant query-driven detectors (Moment-DETR lineage, QD-DETR, TR-DETR, UVCOM, TaskWeave) are largely **visual + text-query**; audio is an optional add-on (e.g., UMT incorporates audio, and the QD-DETR repo offers optional audio training), not core. This is itself a finding: most widely-cited "SOTA" highlight detection on the public leaderboards does **not** ingest the audio track at all.

### Sports highlights: the home of audio-as-excitement

Sports is where audio saliency is most developed. **"Automated Detection of Sport Highlights from Audio and Video Sources"** ([arXiv 2501.16100](https://arxiv.org/pdf/2501.16100)) encodes audio chunks as **mel-spectrograms** fed to a 2D-CNN to detect commentators' and fans' reactions; it is **acoustic-only** — measuring *when* people are excited (vocal intensity captured in human-voice frequency bands), not *what* commentators say (no speech-to-text/content analysis). This lineage traces to IBM's "Excitement of Sports" (CVPRW 2018) and "Automatic Curation of Golf Highlights using Multimodal Excitement Features" ([arXiv 1707.07075](https://arxiv.org/pdf/1707.07075)), which fuse crowd cheering, commentator tone, player reactions, and even referee-whistle detection. **EchoNet++** ([Sci. Reports 2026](https://www.nature.com/articles/s41598-026-39884-8)) is a multilingual soccer-match audio commentary dataset (transcription/translation pipeline over broadcast audio). Takeaway for Lore: crowd/cheer/commentator-excitement detection is mature, but it is energy-based and sport-specific; lifestyle footage rarely has a "crowd," so Lore needs analogous *everyday* acoustic salience (impact sounds, laughter, exclamations, environmental events).

### (b) Audio backbones usable as saliency features

The standard AudioSet-pretrained backbones are well-characterized: **PANNs** (CNNs, [arXiv 1912.10211](https://ar5iv.labs.arxiv.org/html/1912.10211), 527 classes, frame-wise SED via DecisionLevelMax), **AST** (Audio Spectrogram Transformer), **BEATs** (modern SSL audio backbone with acoustic tokenizer), and **CLAP** ([LAION CLAP](https://github.com/LAION-AI/CLAP), [Microsoft CLAP](https://github.com/microsoft/CLAP)), which embeds audio and free-text into a joint space enabling **zero-shot** sound classification (90.14% on ESC-50 with the LAION `music_audioset` checkpoint; other LAION variants report ~89.2–90.0%). CLAP is the most interesting for Lore: it lets you *query audio with natural language* ("laughter," "a dog barking," "waves crashing," "someone shouting") without a fixed taxonomy — directly useful for a text-instruction-conditioned worthiness gate. For temporally-localized audio-visual events, **UnAV-100 / Dense-Localizing Audio-Visual Events** ([arXiv 2303.12930](https://arxiv.org/abs/2303.12930), CVPR 2023; AAAI 2025 cross-modal extension [arXiv 2412.12628](https://arxiv.org/html/2412.12628v1)) provides 10k untrimmed videos (avg ~42.1s) across 100 event categories, 30k+ events (avg ~2.8 per video, often overlapping/co-occurring) — the closest existing benchmark to "find salient events in untrimmed real footage," but its taxonomy is sound *events*, not narrative dialogue.

### (c) Speech / prosody saliency

Prosody-based saliency exists in pieces but is not wired into highlight pipelines. Laughter detection from prosody (PLP, MFCC) is established and improves with multimodal (face + voice) cues; **SMILE-Next** ([arXiv 2605.28084](https://arxiv.org/html/2605.28084)) teaches LLMs to detect/classify/reason about laughter. Speech-emotion and "tone of voice" prosody research shows nonverbal vocalizations (shouts, laughter) and emotional prosody are rapidly detectable affect signals. But these are mostly affect-recognition studies, **not** systems that use prosody to *select highlight moments in raw video*. So "speech loudness / laughter / impact sounds as a highlight cue" is technically feasible and partly demonstrated (sports cheering, laughter detection) but **not integrated** into a general lifestyle-footage worthiness gate.

### (d) THE KEY QUESTION: does anyone score dialogue CONTENT for narrative importance?

This is where the gap is sharpest. Two mature literatures exist but neither solves Lore's problem:

1. **Important-utterance / extractive transcript summarization (text-only).** "Leveraging Discourse Structure for Extractive Meeting Summarization" ([arXiv 2405.11055](https://arxiv.org/abs/2405.11055)) builds discourse graphs over utterances and uses a GNN to classify utterances as important, beating prior systems on AMI/ICSI. Earlier work uses **dialogue acts** (inform/suggest) to flag important utterances ([Interspeech 2022](https://www.isca-archive.org/interspeech_2022/nihei22_interspeech.pdf)) and **word-importance** corpora for spoken transcripts ([arXiv 1801.09746](https://arxiv.org/pdf/1801.09746)). These genuinely score "does this utterance matter," but on **clean text**, decoupled from audio, video, and the editing/music-sync objective.

2. **Movie/screenplay narrative structure (text-only).** **TRIPOD** / "Movie Plot Analysis via Turning Point Identification" ([arXiv 1908.10328](https://arxiv.org/abs/1908.10328), EMNLP 2019) identifies narrative turning points (the 5 classic pivots: opportunity, change of plans, point of no return, major setback, climax) over screenplays + plot synopses with an end-to-end neural model, enabling screenplay summarization (SUMMER). **MovieNet** provides large-scale movie understanding annotations. But these operate on professionally-written **screenplays/synopses**, not raw spontaneous speech, and identify *plot structure*, not edit-worthy utterances.

3. **Automated trailer generation.** Two recent threads illustrate the boundary. The CNN-based "Automatic trailer generation for movies" ([Nature Sci. Rep. 2025](https://www.nature.com/articles/s41598-025-91084-y)) does genre identification + genre-based shot selection, drawing on subtitle text (TF-IDF over preprocessed subtitles) alongside poster/visual features. By contrast, the transformer-based "Towards Automated Movie Trailer Generation" (TGT, [arXiv 2404.03477](https://arxiv.org/html/2404.03477v1)) is **purely visual** — it "solely relies on the movie sequence and does not use templates, additional metadata, or audio features," scoring shots via a CLIP-based "trailerness" encoder — and its authors explicitly state that "the current method does not incorporate dialogue and sound modeling, which are crucial for fine editing… could be addressed in future work." In both cases the systems start from **already-edited films** (with subtitles/scripts available), and neither models the *narrative importance of spontaneous dialogue*; fine dialogue/sound editing is acknowledged as not yet incorporated. (Note: we found no clearly LLM-orchestrated trailer pipeline among the cited works; that characterization has been removed.)

**Verdict on (d): essentially an open gap.** To our knowledge, no published system takes *raw, unscripted lifestyle audio*, transcribes it, and scores each utterance's *narrative importance to drive a video edit*. Highlight detectors treat speech as undifferentiated audio energy; narrative-importance NLP ignores the raw audio/video signal and assumes clean text; trailer/movie tools assume pre-edited material with scripts/subtitles. The intersection — **"narratively important dialogue detection for editing raw footage"** — does not appear to exist in the widely-cited literature.

### What audio features Lore should extract (concrete recommendation)

- **Acoustic salience channel:** PANNs or BEATs frame-wise embeddings + AudioSet event posteriors (laughter, cheering, applause, impact/crash, dog bark, music onset) for an energy/event worthiness score; add RMS loudness, spectral flux, and onset envelope for sync-friendly transients.
- **Open-vocabulary query channel:** CLAP embeddings to let the *text instruction* condition audio worthiness ("find the moment someone laughs / the wave crashes / the crowd reacts") with no fixed taxonomy.
- **Speech channel:** Whisper-class ASR for transcript + word timestamps; prosody features (pitch/energy contours, speaking-rate, shouts/laughter) as an affect-salience score; then an **LLM-scored narrative-importance head** over the transcript (adapting dialogue-act / important-utterance ideas) — the novel piece.
- **Fusion:** combine acoustic-salience, prosody-affect, dialogue-content-importance, and visual worthiness into one per-clip "keep" score feeding CutClaw's planner, while keeping CutClaw's music-sync machinery for the beat-aligned final cut.

### The concrete gap Lore can claim

Lore can plausibly claim the **first joint audio+visual worthiness gate that scores spoken-dialogue CONTENT for narrative importance in raw, unedited lifestyle footage** to drive a music-synced edit. Each prior ingredient exists in isolation — PANNs/CLAP audio salience, sports crowd-excitement, prosody/laughter detection, extractive-utterance importance, TRIPOD turning points — but none, to our knowledge, combines (i) generic acoustic/visual salience, (ii) prosodic affect, and (iii) *semantic narrative-importance of unscripted speech* in service of editing untrimmed footage with 90% dead time and no on-screen protagonist. That join, plus interval-footage/gap handling and capture-metadata exploitation, is defensible novelty.

## Sources
- https://arxiv.org/abs/2407.13933
- https://arxiv.org/html/2407.13933v2
- https://syncedreview.com/2024/07/25/automating-video-highlights-breakthrough-unsupervised-method-leverages-audio-and-visual-cues/
- https://arxiv.org/pdf/2501.16100
- https://arxiv.org/html/2501.16100v1
- https://arxiv.org/pdf/1707.07075
- https://research.ibm.com/publications/the-excitement-of-sports-automatic-highlights-using-audiovisual-cues
- https://www.nature.com/articles/s41598-026-39884-8
- https://pmc.ncbi.nlm.nih.gov/articles/PMC12988046/
- https://github.com/MrFahad/EchoNet
- https://arxiv.org/abs/2107.09609
- https://openreview.net/forum?id=tz7XkY6S9Z
- https://github.com/MRHiSum/MR.HiSum
- https://github.com/wjun0830/QD-DETR
- https://ar5iv.labs.arxiv.org/html/1912.10211
- https://github.com/LAION-AI/CLAP
- https://github.com/microsoft/CLAP
- https://arxiv.org/html/2211.06687v4
- https://arxiv.org/abs/2303.12930
- https://unav100.github.io/
- https://arxiv.org/html/2412.12628v1
- https://arxiv.org/html/2605.28084
- https://www.isca-archive.org/interspeech_2022/nihei22_interspeech.pdf
- https://arxiv.org/pdf/1801.09746
- https://arxiv.org/abs/2405.11055
- https://arxiv.org/abs/1908.10328
- https://github.com/ppapalampidi/TRIPOD
- https://ppapalampidi.github.io/posts/2020/08/screenplay-summarization/
- https://github.com/ppapalampidi/SUMMER
- https://arxiv.org/html/2404.03477v1
- https://www.nature.com/articles/s41598-025-91084-y
- https://ego4d-data.org/
- https://arxiv.org/pdf/2110.07058
