
tell me about the state of the art highlight detectors. If nothing exists that considers Video + language + raw audio, then I want to combine the results of multiple detectors. Check different benchmarks, such as TVSum, and describe to me what the top scorers are doing

I'll research the current state of the art in highlight detection for you. This is directly relevant to your Lore project, so let me dig into the benchmarks and methods carefully. Let me load my web research tools first.

Used ToolSearch
Let me fan out across the key benchmarks and the audio-multimodal question in parallel.


Browsed the web
Good signal already. Let me pull the actual leaderboards and dig into the audio-aware methods, since that's the crux of your question.


Browsed the web
PWC now redirects to HuggingFace (it's being sunset), and the leaderboard tables are JS-rendered. Let me go straight to the primary papers, which carry the comparison tables and — crucially — say which modalities each method uses.


Browsed the web
UMT's PDF didn't parse (binary). Let me grab it from the HTML mirror, pull the very recent MLLM-based work (relevant to your Qwen2.5-VL approach), and nail down the supervised TVSum numbers and the audio-branch question.


Browsed the web
Clear picture emerging. Let me anchor the supervised TVSum/QVHighlights numbers with the VideoLights comparison tables, and check the bleeding edge — omni-modal video-LLMs that ingest native audio — since that's exactly the trimodal gap you're probing.


Browsed the web
Two final threads — the exact supervised TVSum numbers, and ChronusOmni, which looks like it directly targets the audio+video+language temporal-grounding gap you're asking about.


Browsed the web
I've got enough to give you a precise picture. Here's the synthesis, organized around your three asks: (1) the trimodal gap, (2) the benchmark leaderboards, and (3) what the top scorers actually do.

Short answer to the core question
No single model is the SOTA on highlight detection by jointly exploiting free-form language + video + raw audio. The field has bifurcated:

The strong text-query benchmark (QVHighlights) is dominated by video + text models. When people bolt audio onto them, it barely moves the needle (numbers below).
The audio-rich work lives on TVSum / SumMe / YouTube-HL, where the "language" is just a title or category — so those methods are really video + audio, with weak/no language.
Two caveats on "raw audio": essentially nobody consumes raw waveforms. Classic methods use AudioSet-pretrained PANN/VGGish features; the modern omni-LLMs use Whisper + BEATs/CLAP encoders (near-raw, learned). The closest thing to a true language + video + raw-audio temporal model is the omni-LLM line (ChronusOmni, Qwen2.5-Omni, video-SALMONN) — but those do moment retrieval / grounding, not highlight detection, and aren't benchmarked on QVHighlights.
So your instinct to fuse multiple detectors is well-founded — there's a genuine hole here. More on that at the end.

The benchmark landscape (they are not the same task)
Benchmark	What it tests	"Language" signal	Audio common?	Metric
QVHighlights	Joint moment retrieval + highlight detection, free-form text query	Strong (per-clip query)	Rare / marginal	mAP@avg, HIT@1
TVSum	Title-based highlight detection, 10 categories	Weak (video title/category)	Yes	top-5 mAP
SumMe	Generic video summarization	None	Yes	F-score
YouTube Highlights	Domain-specific HD (6 domains)	Weak (domain label)	Yes	mAP
Mr.HiSum	Large-scale HD/summarization (31k YouTube "most-replayed")	None	Sometimes	mAP / rank corr
Charades-STA / ActivityNet / TACoS	Moment retrieval (grounding), not HD	Strong	Rare	R@1@IoU
The takeaway: when people say "SOTA highlight detector" they're usually talking about two different worlds, and audio's value depends entirely on which world you're in.

QVHighlights (the text-query world) — top scorers
Method	Year	Modalities	mAP@avg	HIT@1	What it does
Moment-DETR	2021	V+T	~30–33	55.6	The original: DETR set-prediction over clips
QD-DETR	2023	V+T (+A opt.)	~40	62.4	Query-dependent video rep + negative-pair learning + saliency token
CG-DETR	2023	V+T	48.4	66.2	Correlation-guided query-dependency calibration (dummy tokens to control cross-attn)
TR-DETR	2024	V+T	42.6–49	63.4	Exploits the reciprocity between MR and HD tasks
UVCOM	2024	V+T	43.2	64.2	Unifies multi-granularity comprehension across the two tasks
Mr. BLIP	2024	V+T (BLIP-2 LLM)	~60.5	—	Reframes MR as a seq-to-seq LLM problem
SG-DETR	2024	V+T (InternVideo2-1B)	58.8	71.0	Saliency-guided cross-attention + hybrid ATSS/DINO-DETR head + saliency amplifier
BLIP-3 frame-seg	2025	V+T (MLLM)	35.3	56.7	LLM emits a 0/1 string (one token per frame); logits double as saliency
TempSamp-R1	2025	V+T (MLLM+RL)	—	57.6	RL-tuned temporal sampling on an MLLM
Two things to notice:

The jump from ~43 → ~60 mAP came from backbones, not just architecture. SG-DETR's leap is largely InternVideo2-1B features + pretraining on InterVid-MR; Mr.BLIP's is the BLIP-2 LLM. Architecture (DETR head) plateaued around 43–49 with the old SlowFast+CLIP features.
The frontier is splitting into two camps: polished DETR detectors (SG-DETR) vs video-LLMs that generate timestamps or per-frame labels (Mr.BLIP, LLaVA-MR, BLIP-3 frame-seg, TempSamp-R1). The latter is the camp your Lore/Qwen2.5-VL approach lives in.
The audio evidence on QVHighlights — this is the key table for your question. From the CKA paper's ablation, adding PANN audio to strong video+text models:

Method	Video only	Video + Audio
UMT	—	36.1 mAP
QD-DETR	39.9	40.2
TR-DETR	42.6	43.1
UVCOM	43.2	43.3
CKA (2025)	45.7	45.5 (audio slightly hurt)
Audio buys +0.1 to +0.5 mAP at best, and sometimes hurts, once the video+text signal is strong. That's why the QVHighlights leaders dropped it.

TVSum (the audio world) — top scorers
Here the "query" is just the title, so audio carries real weight. Supervised top-5 mAP:

Method	Year	Modalities	TVSum top-5 mAP	Mechanism
UMT	2022	V + A + T	83.1	Bottleneck-token fusion of visual+audio; text-guided "query generator"; MR as keypoint detection
QD-DETR	2023	V+T (+A)	85.0	(as above)
UVCOM	2024	V+T	86.3	(as above)
TR-DETR	2024	V+T	88.1	(as above)
CKA ("Watch Video, Catch Keyword")	2025	V+T	88.7	Context-aware keyword attention — aligns salient query keywords to clips
⚠️ Metric caution: there's a separate, harder unsupervised TVSum protocol where numbers sit ~50–60 (e.g., the 2024 audio-visual recurrence method hits 60.3 vs CHD 52.8). Don't compare those to the ~85–88 supervised numbers — different splits/protocol. TVSum is notorious for this.

UMT is the one canonical method that genuinely fuses all three (text query + PANN audio + video) in a unified transformer — it's the closest classic answer to your "V + L + audio" wish. But it predates the strong-feature era, so it's now mid-pack.

SumMe / YouTube-HL / the audio-visual thread
This is where audio research concentrates:

A2Summ (CVPR 2023): aligned audio-visual multimodal transformer; SOTA on TVSum + SumMe for summarization.
Audio-Visual Recurrence (2024, unsupervised): clusters videos into pseudo-categories, then mines clips that recur across same-category videos in both audio (PANN) and visual space as pseudo-highlights. No language at all.
Deep audio-visual summarization models: ~79% F1 TVSum / ~67% SumMe.
Language-Audio Moment Retrieval (AMR) (2024): CLAP-based, retrieves audio segments from a text query — the audio analogue of moment retrieval, useful if you want a true language→audio branch.
What the top scorers are "doing," distilled
Four method families:

Query-dependent DETR detectors (QD/CG/TR/UVCOM/SG-DETR): a cross-modal transformer makes the video representation depend on the query, a saliency token/head scores each clip for HD, and DETR-style spans handle MR. Recent gains = saliency-guided attention + much stronger features (InternVideo2).
Video-LLMs / MLLMs (Mr.BLIP, LLaVA-MR, BLIP-3 frame-seg, TempSamp-R1): treat localization as text generation (emit timestamps) or per-frame binary segmentation; some add RL because LM loss alone localizes poorly. This is your camp.
Audio-visual fusion (UMT, A2Summ, recurrence): bottleneck/cross-attention fusion of visual + PANN/BEATs audio; language is weak or absent.
Omni-LLMs (Qwen2.5-Omni, video-SALMONN, ChronusOmni Dec-2025): natively ingest video + near-raw audio (Whisper+BEATs) + text. ChronusOmni's finding is relevant to you — it argues learned temporal positional embeddings (as in Qwen2.5-Omni) are weak for localization, and fixes it by interleaving explicit text timestamps ("second{t}") with the audio/visual tokens. Notably, in their data audio-to-time localization (R@0.5 = 90.5) beat video-to-time (63.2) — i.e., audio can be the stronger temporal cue when present.
Implication for Lore (combining detectors)
Since no trimodal HD SOTA exists, fusing is the right call. Two empirical facts should shape it:

Audio is near-useless on top of strong video+text when the language query is rich (QVHighlights, +0.1–0.5 mAP).
Audio is high-value when language is weak/absent (TVSum, omni-LLM audio-to-time) — which is exactly the music-synced montage regime where there's often no per-moment text query. So for Lore, audio likely matters more than the QVHighlights numbers imply.
A concrete late-fusion recipe:

Resample everything to a common clip grid (2s clips, matching Qwen2.5-VL / QVHighlights convention).
Run 3 saliency heads producing per-clip curves:
Video+text semantic relevance — your frozen Qwen2.5-VL (or CG-DETR/SG-DETR).
Audio saliency — BEATs/PANN novelty + energy, or the audio-visual-recurrence scorer (captures cheering, laughter, music drops, sound events the VLM misses).
Language→audio match — CLAP similarity between the query and each audio clip (only if you have a text query).
Normalize each curve (z-score or rank-normalize per video — important since the scales differ wildly), then combine by weighted sum or rank aggregation (Borda/RRF). RRF is robust and parameter-light; a tiny learned logistic layer over the 3 normalized scores is the next step up.
Let audio break ties / boost rather than dominate — gate its weight up when the text signal is weak (short/empty query), which is precisely where the literature says it pays off.
This mirrors what UMT does internally (fuse then score), but as late fusion of independent off-the-shelf detectors it lets you reuse the frozen Qwen2.5-VL you already have, add a cheap audio branch, and avoid retraining a joint trimodal model — which nobody has shown to beat the strong unimodal-feature detectors anyway.

Sources
SG-DETR (Saliency-Guided DETR), 2024
[Mr.BLIP / referenced in SG-DETR comparison]
VideoLights, 2024 · GitHub
CKA — "Watch Video, Catch Keyword", 2025 (source of the TVSum + QVHighlights V vs V+A tables)
UMT — Unified Multi-modal Transformers, CVPR 2022
QD-DETR, CVPR 2023 · CG-DETR
Unsupervised HD via Audio-Visual Recurrence, 2024
Moment/Highlight Detection via MLLM Frame Segmentation (BLIP-3), 2025
ChronusOmni — time-aware omni-LLM, 2025
QVHighlights / Moment-DETR, 2021
Lighthouse library (supports audio moment retrieval)
Want me to dig deeper into any one thread — e.g., the exact audio branch in Lighthouse/QD-DETR (so you can reuse their PANN/CLAP pipeline), or pull the CLAP-based AMR setup for the language→audio branch?

I'll note the strategic finding to memory since it directly shapes Lore's direction.


Recalled 2 memories, saved 2 memories
Saved to memory (ref_highlight_detection_sota.md) and indexed — so next session I won't re-derive the landscape, and the audio caveat is on record (it predicts your audio+visual QVHighlights pass will show little lift, which is expected, not a plumbing bug).

The offer stands: I can pull the Lighthouse/QD-DETR PANN+CLAP audio branch so you can reuse it directly for the audio-saliency detector, or set up the CLAP language→audio branch for the fusion stack — whichever unblocks Lore next.

is it possible to build something that takes all the clips generated by the video + text model, and then the clipss from an audio highlight detector, and fuse the timestamps? 

Also, I want to be able to just load pretrained SOTA models, rather than train my own entire thing, since I am on a short timeframe

Yes — this is very doable, and it's actually the lightest part of the whole project. The fusion layer is ~100 lines of numpy, no training. The pretrained models do all the heavy lifting. Let me verify the exact off-the-shelf model APIs so I hand you correct identifiers, not approximate ones.


Browsed the web
Yes — totally possible, and it's the easiest part. Fusing timestamps from two detectors is ~100 lines of numpy with zero training. The only models you load are pretrained and off-the-shelf. Here's the concrete plan.

The mental model
Both detectors ultimately produce, per video, either:

a saliency curve (a score per time-bin), or
a set of (start, end, score) intervals.
You put both on a common time grid, normalize (critical — the scales are wildly different), combine, then peak-pick back into final intervals. That's it.

There are two fusion flavors; pick based on what your detectors emit:

When to use	How
Score-level (recommended)	You have continuous scores (you do — Qwen emits saliency, CLAP emits similarity)	Rasterize both to a grid → z-normalize each → weighted sum → threshold/peak-pick
Interval-level	You only have discrete clips, no comparable scores	Cluster overlapping intervals by 1-D IoU → merge (Weighted Box Fusion / NMS)
Pretrained models you can just load() — no training
You already have the video+text side (frozen Qwen2.5-VL → {windows, saliency}). So you only need to add an audio detector. Ranked by how little new code they cost:

Role	Model	Load it with	Notes
Audio + language ⭐	LAION-CLAP	ClapModel.from_pretrained("laion/larger_clap_general") (HF)	Slide text query over audio windows → per-window similarity curve. Use larger_clap_music if it's a music montage. 48 kHz mono.
Audio + language (MR) ⭐	Lighthouse AMR	QDDETRPredictor(ckpt, feature_name='clap')	Pretrained on Clotho-Moment/CASTELLA (Zenodo). Returns pred_relevant_windows + saliency — same API as the video model.
Audio events (already in your pipeline)	AST	you already run it	Sum AudioSet "exciting" class probs (cheering, applause, laughter, music, shouting) → curve. Free, no new dep.
Loudness proxy	librosa	librosa.feature.rms, onset_strength	Zero model. Cheap "excitement" signal; great for cheering/drops.
(optional) extra video+text detector	Lighthouse CG-DETR / UVCOM	CGDETRPredictor(ckpt, feature_name='clip_slowfast')	A real SOTA MR/HD model alongside Qwen — nice for ablations in the report.
Lighthouse install + API (verified):

pip install 'git+https://github.com/line/lighthouse.git'   # needs ffmpeg + torch
from lighthouse.models import CGDETRPredictor   # video+text
m = CGDETRPredictor('cg_detr_qvhighlights.ckpt', device='cuda', feature_name='clip_slowfast')
vid = m.encode_video('clip.mp4')
out = m.predict('people celebrating', vid)
# out['pred_relevant_windows'] -> [[start, end, score], ...]
# out['pred_saliency_scores']  -> per-clip saliency

from lighthouse.models import QDDETRPredictor   # audio+text (AMR), same shape
am = QDDETRPredictor('qd_detr_clotho_moment.ckpt', device='cuda', feature_name='clap')
aud = am.encode_audio('clip.wav')
aout = am.predict('crowd cheering', aud)
The CLAP audio-saliency curve (the simplest audio detector)
import numpy as np, librosa, torch
from transformers import ClapModel, ClapProcessor

clap = ClapModel.from_pretrained("laion/larger_clap_general").eval()
proc = ClapProcessor.from_pretrained("laion/larger_clap_general")

def clap_saliency(wav_path, query, win=2.0, hop=1.0, sr=48000):
    y, _ = librosa.load(wav_path, sr=sr, mono=True)
    tq = proc(text=[query], return_tensors="pt")
    with torch.no_grad():
        t = torch.nn.functional.normalize(clap.get_text_features(**tq), dim=-1)
    times, sims = [], []
    for start in np.arange(0, len(y)/sr - win, hop):
        seg = y[int(start*sr):int((start+win)*sr)]
        ai = proc(audios=[seg], sampling_rate=sr, return_tensors="pt")
        with torch.no_grad():
            a = torch.nn.functional.normalize(clap.get_audio_features(**ai), dim=-1)
        times.append(start + win/2)
        sims.append(float((a @ t.T)))          # cosine similarity
    return np.array(times), np.array(sims)
The fusion layer (score-level — your main ask)
import numpy as np

def rasterize_intervals(intervals, duration, fps=2.0):
    """intervals: [(start, end, score)] -> per-bin curve on a common grid."""
    grid = np.zeros(int(np.ceil(duration*fps)), np.float32)
    for s, e, sc in intervals:
        i0, i1 = int(s*fps), int(np.ceil(e*fps))
        grid[i0:i1] = np.maximum(grid[i0:i1], sc)
    return grid

def resample_curve(times, vals, duration, fps=2.0):
    """irregular (times, vals) e.g. from CLAP -> uniform grid."""
    grid_t = np.arange(0, duration, 1/fps)
    return np.interp(grid_t, times, vals)

def znorm(x):
    sd = x.std()
    return (x - x.mean())/sd if sd > 1e-6 else x*0.0

def fuse(curves, weights):
    """curves: equal-length per-bin arrays. Per-video normalize, then weighted sum."""
    stack = np.stack([znorm(c) for c in curves])
    return (stack * np.asarray(weights)[:,None]).sum(0)

def curve_to_intervals(fused, fps=2.0, thresh=0.5, min_len=1.0, merge_gap=0.5):
    above = fused > thresh
    out, i, n = [], 0, len(fused)
    while i < n:
        if above[i]:
            j = i
            while j < n and above[j]: j += 1
            out.append([i/fps, j/fps, float(fused[i:j].max())]); i = j
        else: i += 1
    merged = []
    for iv in out:
        if merged and iv[0]-merged[-1][1] <= merge_gap:
            merged[-1][1] = iv[1]; merged[-1][2] = max(merged[-1][2], iv[2])
        else: merged.append(iv)
    return [tuple(iv) for iv in merged if iv[1]-iv[0] >= min_len]

# --- wire it together ---
duration, fps = 120.0, 2.0
vt_curve = rasterize_intervals(qwen_windows, duration, fps)        # from Qwen {windows, saliency}
t, s     = clap_saliency('clip.wav', 'the most exciting moment')
au_curve = resample_curve(t, s, duration, fps)                     # from CLAP

fused      = fuse([vt_curve, au_curve], weights=[1.0, 0.6])        # tune the 0.6
highlights = curve_to_intervals(fused, fps, thresh=0.5)            # final (start, end, score)
If you genuinely only have clips with no usable scores, swap the last step for 1-D Weighted Box Fusion: sort intervals by score, cluster anything with IoU ≥ 0.3, and emit one confidence-weighted interval per cluster (union = max recall, intersection = max precision, WBF = the balanced middle). I can hand you that ~20-line variant if you want it.

Two gotchas that decide whether it works
Normalize per video before combining. Qwen saliency, CLAP cosine sim, and AST probs live on different scales — z-norm (or rank-norm) each curve first, or the loudest-scaled detector silently dominates.
Align the timelines. Account for each detector's clip length / fps when rasterizing. Everything must land on the same grid (I used 2 fps = 0.5 s bins, matching the QVHighlights convention).
What I'd actually do given your timeframe
Reuse Qwen as-is, add CLAP as the audio branch (the snippet above — ~30 lines, no checkpoints to hunt down), fuse with the code above. That's the whole thing, runnable today. Then, if you want a stronger story for the CS231n writeup, drop in Lighthouse's pretrained CG-DETR + AMR as two additional bona-fide SOTA detectors and show the fused result beating each alone — that's a clean ablation table and it's all pretrained.

Want me to (a) write the 1-D Weighted Box Fusion variant, or (b) sketch the AST "exciting-class" curve so you reuse the sound-tagger already in your Lore pipeline instead of adding CLAP?

Sources: Lighthouse · LAION-CLAP (PyPI) · CLAP on HF Transformers · larger_clap_music

build me the ipynb file

On it. Since you gave the go-ahead to create the file, I'll generate a complete, runnable notebook. It runs end-to-end on a synthetic demo out of the box (just numpy + matplotlib — no video or model downloads needed to test the plumbing), then you flip flags to plug in real Qwen + CLAP.

I'll build it at /Users/tejasvityagi/Documents/Claude/highlight_fusion.ipynb (next to your cutclaw_run.ipynb). I'm only writing the file — not installing anything or running your pipeline.

Ran
Generate highlight_fusion.ipynb notebook
Notebook written and JSON-validated. Let me do one more check — compile every code cell so I'm handing you a notebook with no Python syntax errors (this doesn't execute anything, just parses).

Ran
Syntax-check all code cells
Done. Both checks pass — valid notebook, all 13 code cells compile.

highlight_fusion.ipynb is ready (23 cells). Here's what you've got:

Runs offline, right now. Hit Run All and it executes the full pipeline on a synthetic 60s clip (fake audio with 3 loud bursts + a fake Qwen prediction), prints the fused highlights, and plots the per-detector curves + fused curve with the selected windows shaded. Only needs numpy + matplotlib — no downloads, no GPU, no video. This is your plumbing smoke-test, in the same spirit as your Lore quicktest.

Three flips to go real:

Wire run_qwen_vt() to your frozen Qwen2.5-VL predict() — the adapter already speaks your {windows, saliency} contract.
Set USE_REAL_CLAP = True (and feed real audio via extract_audio → load_wav).
Tune WEIGHTS — and crank audio up for music montages, where the text query is weak and audio earns its keep.
Both things you asked about are in there:

1-D Weighted Box Fusion (weighted_box_fusion_1d) — the interval-level merge for when you only have discrete clips, no curves.
AST exciting-class curve (ast_excitement_curve) — reuses the AudioSet sound-tagger from your Lore pipeline as an optional 3rd fusion input.
Plus a commented Lighthouse path (CG-DETR for video+text, QD-DETR AMR for audio+text) if you want two bona-fide pretrained SOTA detectors alongside Qwen for an ablation table in the writeup.

I only wrote and validated the file — didn't install anything or run your models. I jotted the notebook's location into memory so I can pick it up next session.

One thing worth deciding when you plug in real inputs: the demo uses an RMS-energy stand-in for the audio branch. Energy is a fine loudness proxy, but CLAP (language-conditioned) vs. AST (event-class) vs. energy will give noticeably different audio curves — want me to add a small cell that overlays all three so you can eyeball which one best matches your trip footage before committing?

Let me record the artifact location.


Saved a memory
The notebook is built, validated, and recorded. You're set to start with the offline demo and plug in real Qwen + CLAP whenever you're ready. Let me know if you want that three-way audio-signal comparison cell (CLAP vs. AST vs. energy) — it's a quick add and would help you pick the right audio branch for your trip footage before you commit.

hello

Hey! 👋 We just wrapped up building highlight_fusion.ipynb — the late-fusion pipeline that combines your Qwen2.5-VL video+text detector with a CLAP audio branch, no training required. It runs offline on a synthetic demo out of the box.

Where we left off, I'd offered to add a quick cell that overlays the three audio-signal options (CLAP vs. AST vs. energy) so you can pick the best one for your trip footage.

What would you like to do — pick that up, plug in real Qwen/CLAP inputs, or something else entirely?





Before I hand you code, one correction that matters a lot for your thesis — and then I'll explain exactly how the three conditions are built today. Let me verify the current model APIs so I don't send you down a wrong path.


Browsed the web, used a tool
I verified the model landscape, and there's one important correction before the how-to:

The key correction: VL ≠ audio
Qwen3-VL does not take raw audio. The "VL" line is vision + text only. The Qwen model that natively ingests a raw audio waveform is the Omni line.

Model	Inputs	Raw audio?	Fits A100-40GB?
Qwen2.5-VL-3B (current)	frames + text	❌ (audio→text only)	✅
Qwen3-VL (2B/8B/30B-A3B)	frames + text	❌ still no audio	✅ (8B)
Qwen2.5-Omni-7B	frames + raw audio + text	✅ use_audio_in_video=True	✅
Qwen3-Omni-30B-A3B	frames + raw audio + text	✅	⚠️ only AWQ-4bit
So: if you literally want the model to hear waves/birds, you want Qwen2.5-Omni-7B (best fit for your GPU + deadline), or Qwen3-Omni-30B if you insist on "Qwen3" (heavier, needs the AWQ-4bit build to fit 40 GB).

Part 1 — How the three conditions work right now (Qwen2.5-VL)
The crucial thing to understand: today, no raw audio touches the model. All three conditions feed the same video frames; they differ only in what text is appended to the prompt. Tracing Cell 6:

Shared for all 3 — frame sampling. fps = min(BASE_FPS, MAX_FRAMES/dur) → decord samples ~128 frames spanning the whole video. There is no separate shot-segmentation model — "segments" are just uniform time bins (TVSum's standard 2 s shots). We actually ask the VLM for MAX_SEG=40 coarse segment scores and expand() stretches them onto the 2 s bins.

Audio → text, once per video (audio_blocks):

Whisper transcribes speech → sp = lines like [12-15s] "go left here".
AST (audio tagger) labels 10 s windows → so = lines like [20-30s] [sound: Stream, Wind, Bird] (Speech filtered out).
The three prompts (build_prompt) — same frames, different text:

V → frames + "rate using the visual content." (no sp, no so)
V+C → frames + the speech transcript block sp.
V+C+A → frames + speech transcript sp + sound-event text so.
Then run_qwen([frames + prompt]) → JSON saliency. So your current "+A" is AST sound labels as text, not the waveform. That's a legitimate ablation (does sound-event text help on top of speech text?), but it's not "raw audio" in the literal sense.

Part 2 — Switching to Qwen2.5-Omni-7B (true raw audio)
Now "+A" becomes the actual audio track, fed via use_audio_in_video=True. The model hears the waveform aligned to the frames — no AST needed.

Cell 4 (replace — Omni deps):

# 4) Modal app, image, Volume  (Qwen2.5-Omni: native raw-audio + video)
import modal
app   = modal.App("lore-tvsum")
vol   = modal.Volume.from_name(VOL_NAME, create_if_missing=True)
image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("ffmpeg")
    .pip_install("torch", "torchvision", "accelerate",
                 "transformers>=4.52",          # Qwen2.5-Omni support (use git+ source if import fails)
                 "qwen-omni-utils[decord]",
                 "librosa", "soundfile",
                 "openai-whisper")              # still used for the V+C speech-caption text
    .env({"HF_HOME": f"{DATA}/hf"})
)
Cell 6 (replace — Omni Predictor):

# 6) GPU worker - Qwen2.5-Omni-7B: V (frames) / V+C (frames+ASR text) / V+C+A (frames+ASR text+RAW AUDIO)
import modal

@app.cls(image=image, gpu=FULL_GPU, volumes={DATA: vol}, timeout=60*60, max_containers=10, serialized=True)
class Predictor:
    @modal.enter()
    def load(self):
        import torch
        from transformers import Qwen2_5OmniForConditionalGeneration, Qwen2_5OmniProcessor
        import whisper
        self.torch = torch
        self.model = Qwen2_5OmniForConditionalGeneration.from_pretrained(
            "Qwen/Qwen2.5-Omni-7B", torch_dtype="auto", device_map="auto",
            enable_audio_output=False)          # text-only -> skip the speech 'talker' (~10GB saved)
        # if that kwarg errors on your transformers: drop it, then call self.model.disable_talker()
        self.processor = Qwen2_5OmniProcessor.from_pretrained("Qwen/Qwen2.5-Omni-7B")
        self.asr = whisper.load_model("base", download_root=f"{DATA}/whisper")

    @modal.method()
    def predict_batch(self, job):
        import re, os
        import numpy as np
        torch = self.torch
        from qwen_omni_utils import process_mm_info
        examples, cfg = job["examples"], job["cfg"]
        CLIP_LEN, DATA = cfg["CLIP_LEN"], cfg["DATA"]
        MAX_FRAMES, BASE_FPS = cfg["MAX_FRAMES"], cfg["BASE_FPS"]
        MAX_PIXELS, MAX_NEW, CONDS = cfg["MAX_PIXELS"], cfg["MAX_NEW_TOKENS"], cfg["CONDITIONS"]
        MAX_SEG, DEBUG = cfg.get("MAX_SEG", 40), cfg.get("DEBUG", False)
        SYS = {"role": "system", "content": [{"type": "text",
               "text": "You are Qwen, a helpful assistant that watches and listens to videos."}]}

        def build_prompt(title, duration, n_seg, seg_len, speech=None, has_audio=False):
            p = ("You are rating an amateur video" + (f' titled "{title}"' if title else "")
                 + f" for a highlights reel.\nThe {duration:.0f}s video is split into {n_seg} equal "
                 f"segments of ~{seg_len:.0f}s each, in time order.\n")
            if speech: p += "\nSPEECH TRANSCRIPT ([start-end]s):\n" + speech + "\n"
            srcs = "the visual frames"
            if speech: srcs += " and the speech transcript"
            if has_audio: srcs += " and the video's RAW AUDIO (ambient sounds: water, wind, birds, crowd, engines, plus speech tone)"
            p += ("\nUsing " + srcs + f", rate how highlight-worthy each of the {n_seg} segments is on a "
                  "0-4 scale (4 = must-keep highlight, 0 = boring). Use the FULL range. Reply with ONLY "
                  f"compact JSON of exactly {n_seg} integers, no prose:\n" + '{"saliency":[s0,s1,...]}')
            return p

        def parse_nums(reply):
            m = (re.search(r'saliency"?\s*:\s*\[([^\]]*)\]', reply, re.DOTALL)
                 or re.search(r'saliency"?\s*:\s*\[([0-9,\s\.\+\-eE]*)', reply, re.DOTALL)
                 or re.search(r'\[([0-9][0-9,\s\.\+\-eE]*)\]', reply, re.DOTALL))
            nums = []
            if m:
                for tok in m.group(1).split(","):
                    tok = tok.strip()
                    if not tok: continue
                    try: nums.append(float(tok))
                    except ValueError: pass
            return nums

        def expand(nums, n):
            if not nums: return [0.0]*n
            k = len(nums)
            return [nums[min(k-1, int(j*k/n))] for j in range(n)]

        @torch.inference_mode()
        def run_omni(vp, prompt, fps, use_audio, temperature):
            conv = [SYS, {"role": "user", "content": [
                {"type": "video", "video": vp, "fps": fps, "max_pixels": MAX_PIXELS},
                {"type": "text", "text": prompt}]}]
            text = self.processor.apply_chat_template(conv, add_generation_prompt=True, tokenize=False)
            audios, images, videos = process_mm_info(conv, use_audio_in_video=use_audio)
            inp = self.processor(text=text, audio=audios, images=images, videos=videos,
                                 return_tensors="pt", padding=True,
                                 use_audio_in_video=use_audio).to(self.model.device)
            gen = dict(max_new_tokens=MAX_NEW, do_sample=temperature > 0, return_audio=False)
            if temperature > 0: gen.update(temperature=temperature, top_p=0.9)
            torch.manual_seed(1234)
            out = self.model.generate(**inp, **gen)
            ids = out[0] if isinstance(out, (tuple, list)) else out      # tuple if talker enabled
            return self.processor.batch_decode(ids[:, inp["input_ids"].shape[1]:], skip_special_tokens=True)[0]

        def scores_for(vp, prompt, fps, use_audio):
            nums, reply = [], ""
            for temp in (0.7, 1.0):
                reply = run_omni(vp, prompt, fps, use_audio, temp)
                nums = parse_nums(reply)
                if len({round(x, 3) for x in nums}) > 1: break
            return nums, reply

        def speech_text(vid):
            wav = f"{DATA}/videos/{vid}.16k.wav"
            src = wav if os.path.exists(wav) else f"{DATA}/videos/{vid}.mp4"
            lines = []
            for sg in self.asr.transcribe(src, fp16=True)["segments"]:
                t = sg["text"].strip()
                if t: lines.append((sg["start"], sg["end"], '"' + t + '"'))
            return "\n".join(f"[{a:.0f}-{b:.0f}s] {x}" for a, b, x in sorted(lines))

        results = []
        for ex in examples:
            dur = ex["duration"]; n = int(round(dur / CLIP_LEN)); vp = f"{DATA}/videos/{ex['vid']}.mp4"
            rec = {"vid": ex["vid"], "title": ex.get("title", ""), "duration": dur, "n": n}
            if not os.path.exists(vp):
                for c in CONDS: rec[c] = [0.0]*n
                results.append(rec); continue
            n_seg = max(2, min(MAX_SEG, n)); seg_len = dur / n_seg
            fps = min(BASE_FPS, MAX_FRAMES / max(dur, 1.0))
            sp = speech_text(ex["vid"])
            plan = {"v":   (build_prompt(ex.get("title", ""), dur, n_seg, seg_len), False),
                    "vc":  (build_prompt(ex.get("title", ""), dur, n_seg, seg_len, speech=sp or None), False),
                    "vca": (build_prompt(ex.get("title", ""), dur, n_seg, seg_len, speech=sp or None, has_audio=True), True)}
            raw = {}
            for c in CONDS:
                prompt, use_audio = plan[c]
                nums, reply = scores_for(vp, prompt, fps, use_audio)
                raw[c] = reply
                rec[c] = expand(nums, n)
            if DEBUG: rec["raw"] = {c: raw[c][:600] for c in CONDS}
            results.append(rec)
        return results
Cell 2 — one change so you don't overwrite your VL results: set RECORDS_PATH = "records_omni.json". (Keep both files → the paper can compare audio-as-text VL vs raw-audio Omni, which is itself a strong result.)

Part 3 — How each condition now flows through the model
V → process_mm_info(..., use_audio_in_video=False) → only frames reach the model; prompt mentions visuals only.
V+C → same frames, use_audio_in_video=False, + Whisper transcript text in the prompt. Still no waveform.
V+C+A → use_audio_in_video=True → process_mm_info pulls the mp4's audio track, the processor interleaves it with the frames (Omni's TMRoPE aligns audio↔video in time), so the model literally hears the segment while seeing it, plus the transcript text. This is the genuine raw-audio condition.
The "shot segmentation" is unchanged: uniform 2 s bins, model emits a score per coarse segment, expand() maps to bins, evaluated by Spearman/Kendall vs TVSum ground truth.

Part 4 — Deadline reality check
This is a real rewrite with three risks: (1) first run downloads ~20 GB Omni weights to the Volume (one-time; your .prefetch_done marker won't cover it, that's fine); (2) raw audio + long video is memory-heavy — start with the shorter TVSum videos (set N_VIDEOS=8) and MAX_FRAMES=96 for the smoke; (3) use_audio_in_video at very low fps can warn about A/V sync (usually non-fatal).

My strong advice given the clock: let your current Qwen2.5-VL run finish first (Cells 10–12 — it works, it's your guaranteed result), then swap to Omni and run Cell 9 (smoke) → Cell 10. If Omni cooperates, it's your hero result; if not, you still have a complete ablation. Don't throw away the working pipeline.

Want me to write the Omni version into a second notebook (lore_tvsum_omni.ipynb) so both run independently and you don't lose the VL one?

Sources:

Qwen2.5-Omni-7B (model card)
Qwen2.5-Omni — transformers docs
Qwen3-Omni-30B-A3B-Instruct · Qwen3-Omni-MoE docs
Qwen3-VL-8B-Instruct · Qwen3-VL docs
✓ Initialized. View run at https://modal.com/apps/tejasvityagi1414/main/ap-RLm4s78t2w0vCf6zrSMWtB
✓ Created objects.
├── 🔨 Created function fetch_videos.
├── 🔨 Created function list_videos.
├── 🔨 Created function extract_audio.
├── 🔨 Created function prefetch_models.
└── 🔨 Created function Predictor.*.
[transformers] Model config: tts_text_start_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151860. This may result in unexpected behavior.
[transformers] Model config: tts_text_end_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151861. This may result in unexpected behavior.
[transformers] Model config: tts_text_pad_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151859. This may result in unexpected behavior.
[transformers] Model config: vision_start_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151652. This may result in unexpected behavior.
[transformers] Model config: vision_end_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151653. This may result in unexpected behavior.
[transformers] Model config: audio_start_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151647. This may result in unexpected behavior.
[transformers] Model config: audio_end_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151648. This may result in unexpected behavior.
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
Fetching 5 files:   0%|          | 0/5 [00:00<?, ?it/s]Fetching 5 files: 100%|██████████| 5/5 [00:00<00:00, 2030.16it/s]
Loading weights:   0%|          | 0/1346 [00:00<?, ?it/s]Loading weights:   4%|▍         | 60/1346 [00:00<00:02, 564.81it/s]Loading weights:   9%|▉         | 123/1346 [00:00<00:02, 596.80it/s][transformers] Model config: tts_text_start_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151860. This may result in unexpected behavior.
[transformers] Model config: tts_text_end_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151861. This may result in unexpected behavior.
[transformers] Model config: tts_text_pad_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151859. This may result in unexpected behavior.
[transformers] Model config: vision_start_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151652. This may result in unexpected behavior.
[transformers] Model config: vision_end_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151653. This may result in unexpected behavior.
Loading weights:  14%|█▎        | 183/1346 [00:00<00:01, 597.57it/s][transformers] Model config: audio_start_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151647. This may result in unexpected behavior.
[transformers] Model config: audio_end_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151648. This may result in unexpected behavior.
Loading weights:  18%|█▊        | 247/1346 [00:00<00:01, 595.66it/s]Loading weights:  25%|██▍       | 333/1346 [00:00<00:01, 672.32it/s]Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
Loading weights:  30%|███       | 410/1346 [00:00<00:01, 704.19it/s]Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
Fetching 5 files:   0%|          | 0/5 [00:00<?, ?it/s]Loading weights:  36%|███▌      | 487/1346 [00:00<00:01, 724.10it/s][transformers] Model config: tts_text_start_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151860. This may result in unexpected behavior.
[transformers] Model config: tts_text_end_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151861. This may result in unexpected behavior.
[transformers] Model config: tts_text_pad_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151859. This may result in unexpected behavior.
[transformers] Model config: vision_start_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151652. This may result in unexpected behavior.
[transformers] Model config: vision_end_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151653. This may result in unexpected behavior.
[transformers] Model config: audio_start_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151647. This may result in unexpected behavior.
[transformers] Model config: audio_end_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151648. This may result in unexpected behavior.
Fetching 5 files: 100%|██████████| 5/5 [00:00<00:00, 2507.06it/s]
Fetching 5 files:   0%|          | 0/5 [00:00<?, ?it/s]Fetching 5 files: 100%|██████████| 5/5 [00:00<00:00, 1629.24it/s]
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
[transformers] Model config: tts_text_start_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151860. This may result in unexpected behavior.
[transformers] Model config: tts_text_end_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151861. This may result in unexpected behavior.
[transformers] Model config: tts_text_pad_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151859. This may result in unexpected behavior.
[transformers] Model config: vision_start_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151652. This may result in unexpected behavior.
[transformers] Model config: vision_end_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151653. This may result in unexpected behavior.
[transformers] Model config: audio_start_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151647. This may result in unexpected behavior.
[transformers] Model config: audio_end_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151648. This may result in unexpected behavior.
Fetching 5 files:   0%|          | 0/5 [00:00<?, ?it/s]Fetching 5 files: 100%|██████████| 5/5 [00:00<00:00, 3107.81it/s]
Loading weights:   0%|          | 0/1346 [00:00<?, ?it/s]Loading weights:   4%|▍         | 59/1346 [00:00<00:02, 585.43it/s][transformers] Model config: tts_text_start_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151860. This may result in unexpected behavior.
Loading weights:  10%|▉         | 128/1346 [00:00<00:01, 622.81it/s][transformers] Model config: tts_text_end_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151861. This may result in unexpected behavior.
[transformers] Model config: tts_text_pad_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151859. This may result in unexpected behavior.
[transformers] Model config: vision_start_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151652. This may result in unexpected behavior.
[transformers] Model config: vision_end_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151653. This may result in unexpected behavior.
[transformers] Model config: audio_start_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151647. This may result in unexpected behavior.
[transformers] Model config: audio_end_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151648. This may result in unexpected behavior.
Loading weights:  15%|█▌        | 203/1346 [00:00<00:01, 679.45it/s]Loading weights:   0%|          | 0/1346 [00:00<?, ?it/s]Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
Loading weights:  20%|██        | 272/1346 [00:00<00:01, 675.74it/s]Loading weights:   4%|▍         | 54/1346 [00:00<00:02, 515.83it/s]Loading weights:  27%|██▋       | 359/1346 [00:00<00:01, 742.67it/s]Loading weights:   8%|▊         | 113/1346 [00:00<00:02, 558.17it/s]Fetching 5 files:   0%|          | 0/5 [00:00<?, ?it/s]Loading weights:  33%|███▎      | 441/1346 [00:00<00:01, 767.91it/s]Fetching 5 files: 100%|██████████| 5/5 [00:00<00:00, 1833.34it/s]
Loading weights:  13%|█▎        | 177/1346 [00:00<00:01, 594.98it/s]Loading weights:  19%|█▉        | 254/1346 [00:00<00:01, 663.04it/s]Loading weights:  26%|██▌       | 348/1346 [00:00<00:01, 739.75it/s]Loading weights:   0%|          | 0/1346 [00:00<?, ?it/s]Loading weights:  32%|███▏      | 427/1346 [00:00<00:01, 751.56it/s]Loading weights:   4%|▍         | 51/1346 [00:00<00:02, 508.57it/s]Loading weights:   8%|▊         | 108/1346 [00:00<00:02, 533.85it/s]Loading weights:  42%|████▏     | 560/1346 [00:03<00:08, 87.71it/s] Loading weights:  13%|█▎        | 174/1346 [00:00<00:02, 578.76it/s]Loading weights:  18%|█▊        | 246/1346 [00:00<00:01, 605.86it/s]Loading weights:  24%|██▍       | 327/1346 [00:00<00:01, 675.86it/s]Loading weights:  29%|██▉       | 397/1346 [00:00<00:01, 663.49it/s]Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
Loading weights:  36%|███▌      | 483/1346 [00:00<00:01, 723.92it/s][transformers] Model config: tts_text_start_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151860. This may result in unexpected behavior.
[transformers] Model config: tts_text_end_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151861. This may result in unexpected behavior.
[transformers] Model config: tts_text_pad_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151859. This may result in unexpected behavior.
[transformers] Model config: vision_start_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151652. This may result in unexpected behavior.
[transformers] Model config: vision_end_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151653. This may result in unexpected behavior.
[transformers] Model config: audio_start_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151647. This may result in unexpected behavior.
[transformers] Model config: audio_end_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151648. This may result in unexpected behavior.
Loading weights:   0%|          | 0/1346 [00:00<?, ?it/s]Loading weights:  45%|████▌     | 611/1346 [00:04<00:09, 78.01it/s]Loading weights:   5%|▍         | 63/1346 [00:00<00:02, 628.35it/s]Fetching 5 files:   0%|          | 0/5 [00:00<?, ?it/s]Loading weights:  37%|███▋      | 502/1346 [00:01<00:05, 161.72it/s]Loading weights:   9%|▉         | 126/1346 [00:00<00:01, 623.82it/s]Fetching 5 files: 100%|██████████| 5/5 [00:00<00:00, 2189.09it/s]
Loading weights:  14%|█▍        | 189/1346 [00:00<00:01, 614.16it/s]Loading weights:  38%|███▊      | 518/1346 [00:02<00:06, 118.43it/s]Loading weights:  19%|█▊        | 251/1346 [00:00<00:01, 603.93it/s]Loading weights:  24%|██▍       | 324/1346 [00:00<00:01, 645.73it/s]Loading weights:  48%|████▊     | 648/1346 [00:04<00:09, 73.27it/s]Loading weights:  29%|██▉       | 397/1346 [00:00<00:01, 659.06it/s]Loading weights:  36%|███▌      | 486/1346 [00:00<00:01, 705.40it/s]Loading weights:  41%|████      | 555/1346 [00:02<00:07, 110.57it/s][transformers] Model config: tts_text_start_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151860. This may result in unexpected behavior.
[transformers] Model config: tts_text_end_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151861. This may result in unexpected behavior.
[transformers] Model config: tts_text_pad_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151859. This may result in unexpected behavior.
[transformers] Model config: vision_start_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151652. This may result in unexpected behavior.
[transformers] Model config: vision_end_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151653. This may result in unexpected behavior.
[transformers] Model config: audio_start_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151647. This may result in unexpected behavior.
[transformers] Model config: audio_end_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151648. This may result in unexpected behavior.
Loading weights:  50%|█████     | 675/1346 [00:05<00:09, 68.16it/s]Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
Loading weights:  42%|████▏     | 572/1346 [00:03<00:08, 93.72it/s] Fetching 5 files:   0%|          | 0/5 [00:00<?, ?it/s]Fetching 5 files: 100%|██████████| 5/5 [00:00<00:00, 1221.83it/s]
Loading weights:  52%|█████▏    | 696/1346 [00:05<00:09, 69.40it/s]Loading weights:   0%|          | 0/1346 [00:00<?, ?it/s]Loading weights:   4%|▍         | 53/1346 [00:00<00:02, 522.21it/s]Loading weights:  44%|████▍     | 593/1346 [00:03<00:07, 95.99it/s] Loading weights:   8%|▊         | 112/1346 [00:00<00:02, 547.05it/s]Loading weights:  53%|█████▎    | 713/1346 [00:05<00:09, 64.67it/s]Loading weights:  13%|█▎        | 172/1346 [00:00<00:02, 568.47it/s]Loading weights:  18%|█▊        | 239/1346 [00:00<00:01, 602.04it/s]Loading weights:  45%|████▌     | 611/1346 [00:04<00:08, 83.13it/s]Loading weights:  54%|█████▍    | 726/1346 [00:06<00:09, 64.85it/s]Loading weights:  41%|████▏     | 556/1346 [00:03<00:09, 87.05it/s] Loading weights:  24%|██▍       | 327/1346 [00:00<00:01, 699.61it/s]Loading weights:  46%|████▌     | 621/1346 [00:03<00:07, 92.38it/s]Loading weights:  30%|██▉       | 398/1346 [00:00<00:01, 671.33it/s]Loading weights:  55%|█████▍    | 737/1346 [00:06<00:09, 62.67it/s]Loading weights:  36%|███▌      | 484/1346 [00:00<00:01, 711.90it/s]Loading weights:  55%|█████▌    | 747/1346 [00:06<00:09, 60.39it/s]Loading weights:  48%|████▊     | 643/1346 [00:04<00:08, 82.35it/s]Loading weights:  47%|████▋     | 639/1346 [00:04<00:09, 74.68it/s]Loading weights:  56%|█████▌    | 757/1346 [00:06<00:09, 64.85it/s]Loading weights:  57%|█████▋    | 766/1346 [00:06<00:08, 65.26it/s]Loading weights:   0%|          | 0/1346 [00:00<?, ?it/s]Loading weights:  49%|████▉     | 660/1346 [00:04<00:08, 80.84it/s]Loading weights:   4%|▍         | 51/1346 [00:00<00:02, 495.51it/s]Loading weights:  49%|████▉     | 660/1346 [00:04<00:09, 73.99it/s]Loading weights:  58%|█████▊    | 774/1346 [00:06<00:10, 57.07it/s]Loading weights:   8%|▊         | 107/1346 [00:00<00:02, 507.46it/s]Loading weights:  45%|████▌     | 607/1346 [00:04<00:09, 77.20it/s]Loading weights:  50%|█████     | 674/1346 [00:04<00:09, 73.47it/s]Loading weights:  13%|█▎        | 172/1346 [00:00<00:02, 544.70it/s]Loading weights:  58%|█████▊    | 781/1346 [00:07<00:10, 54.14it/s]Loading weights:  18%|█▊        | 237/1346 [00:00<00:01, 580.16it/s]Loading weights:  59%|█████▉    | 792/1346 [00:07<00:08, 63.10it/s]Loading weights:  50%|█████     | 677/1346 [00:05<00:09, 67.28it/s]Loading weights:  24%|██▍       | 322/1346 [00:00<00:01, 672.66it/s]Loading weights:  41%|████▏     | 557/1346 [00:03<00:09, 84.51it/s] Loading weights:  51%|█████     | 686/1346 [00:04<00:10, 65.99it/s]Loading weights:  59%|█████▉    | 800/1346 [00:07<00:09, 57.82it/s]Loading weights:  29%|██▉       | 390/1346 [00:00<00:01, 670.08it/s]Loading weights:  52%|█████▏    | 696/1346 [00:05<00:09, 67.86it/s]Loading weights:  51%|█████▏    | 690/1346 [00:05<00:09, 65.80it/s]Loading weights:  36%|███▌      | 483/1346 [00:00<00:01, 735.84it/s]Loading weights:  60%|█████▉    | 807/1346 [00:07<00:11, 47.95it/s]Loading weights:  52%|█████▏    | 705/1346 [00:05<00:09, 69.37it/s]Loading weights:  52%|█████▏    | 701/1346 [00:05<00:10, 62.61it/s]Loading weights:  48%|████▊     | 644/1346 [00:04<00:09, 70.83it/s]Loading weights:  61%|██████    | 818/1346 [00:07<00:09, 56.16it/s]Loading weights:  53%|█████▎    | 714/1346 [00:05<00:09, 65.02it/s]Loading weights:  63%|██████▎   | 842/1346 [00:07<00:05, 92.36it/s]Loading weights:  53%|█████▎    | 710/1346 [00:05<00:10, 62.30it/s]Loading weights:  54%|█████▎    | 722/1346 [00:05<00:10, 58.18it/s]Loading weights:  66%|██████▌   | 886/1346 [00:07<00:02, 166.42it/s]Loading weights:  53%|█████▎    | 719/1346 [00:05<00:09, 64.04it/s]Loading weights:  70%|██████▉   | 936/1346 [00:07<00:01, 243.65it/s]Loading weights:  55%|█████▍    | 734/1346 [00:05<00:09, 65.04it/s]Loading weights:  50%|████▉     | 671/1346 [00:05<00:09, 69.81it/s]Loading weights:  75%|███████▌  | 1011/1346 [00:08<00:00, 368.73it/s]Loading weights:  54%|█████▍    | 727/1346 [00:06<00:10, 59.04it/s]Loading weights:  55%|█████▌    | 742/1346 [00:05<00:09, 66.68it/s]Loading weights:  81%|████████  | 1093/1346 [00:08<00:00, 487.49it/s]Loading weights:  45%|████▌     | 606/1346 [00:04<00:10, 71.45it/s]Loading weights:  88%|████████▊ | 1178/1346 [00:08<00:00, 580.95it/s]Loading weights:  56%|█████▌    | 750/1346 [00:05<00:09, 61.42it/s]Loading weights:  55%|█████▍    | 734/1346 [00:06<00:11, 51.23it/s]Loading weights:  93%|█████████▎| 1254/1346 [00:08<00:00, 628.77it/s]Loading weights:  55%|█████▌    | 744/1346 [00:06<00:10, 56.54it/s]Loading weights:  51%|█████▏    | 692/1346 [00:05<00:09, 66.77it/s]Loading weights:  56%|█████▌    | 757/1346 [00:06<00:11, 51.79it/s]Loading weights: 100%|█████████▉| 1342/1346 [00:08<00:00, 689.53it/s]Loading weights:  56%|█████▌    | 751/1346 [00:06<00:10, 57.71it/s]Loading weights: 100%|██████████| 1346/1346 [00:08<00:00, 158.26it/s]
Loading weights:  57%|█████▋    | 769/1346 [00:06<00:09, 63.28it/s]Loading weights:  56%|█████▋    | 758/1346 [00:06<00:10, 55.62it/s]Loading weights:  58%|█████▊    | 777/1346 [00:06<00:09, 59.35it/s]Loading weights:  53%|█████▎    | 709/1346 [00:05<00:10, 63.44it/s]Loading weights:  57%|█████▋    | 765/1346 [00:06<00:10, 57.97it/s]Loading weights:  48%|████▊     | 642/1346 [00:04<00:10, 67.24it/s]Loading weights:  58%|█████▊    | 784/1346 [00:06<00:10, 55.25it/s]Loading weights:  41%|████▏     | 556/1346 [00:03<00:09, 80.96it/s] Loading weights:  57%|█████▋    | 772/1346 [00:07<00:10, 52.52it/s]Loading weights:  54%|█████▎    | 722/1346 [00:06<00:10, 59.93it/s]Loading weights:  59%|█████▉    | 794/1346 [00:06<00:10, 54.98it/s]Loading weights:  58%|█████▊    | 782/1346 [00:07<00:09, 57.25it/s]Loading weights:  59%|█████▉    | 792/1346 [00:07<00:08, 64.80it/s][transformers] Qwen2_5OmniForConditionalGeneration LOAD REPORT from: Qwen/Qwen2.5-Omni-7B
Key                                                                                                      | Status     |  |
---------------------------------------------------------------------------------------------------------+------------+--+-
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.activations.{0, 1, 2, 3, 4, 5}.act.alpha             | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_v.bias                                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.ff.ff.{0, 3}.weight                             | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.ff.ff.{0, 3}.bias                               | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.convs1.{0, 1, 2}.bias                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_k.weight                                | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.k_proj.weight                                                     | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.convs2.{0, 1, 2}.weight                              | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.activations.{0, 1, 2, 3, 4, 5}.act.beta              | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.convs2.{0, 1, 2}.bias                                | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.convs1.{0, 1, 2}.weight                              | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.q_proj.bias                                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn_norm.linear.weight                         | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_k.bias                                  | UNEXPECTED |  |
talker.model.layers.{0...23}.input_layernorm.weight                                                      | UNEXPECTED |  |
talker.model.layers.{0...23}.post_attention_layernorm.weight                                             | UNEXPECTED |  |
talker.model.layers.{0...23}.mlp.down_proj.weight                                                        | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.v_proj.weight                                                     | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.ups.{0, 1, 2, 3, 4, 5}.0.bias                                           | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_q.weight                                | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.ups.{0, 1, 2, 3, 4, 5}.0.weight                                         | UNEXPECTED |  |
talker.model.layers.{0...23}.mlp.gate_proj.weight                                                        | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn_norm.linear.bias                           | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.q_proj.weight                                                     | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.v_proj.bias                                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_out.0.weight                            | UNEXPECTED |  |
token2wav.code2wav_dit_model.time_embed.time_mlp.{0, 2}.bias                                             | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.se_block.conv1.weight              | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_out.0.bias                              | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.se_block.conv2.weight              | UNEXPECTED |  |
talker.model.layers.{0...23}.mlp.up_proj.weight                                                          | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.k_proj.bias                                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_q.bias                                  | UNEXPECTED |  |
talker.model.norm.weight                                                                                 | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.se_block.conv2.bias                | UNEXPECTED |  |
token2wav.code2wav_dit_model.proj_out.weight                                                             | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.conv_pre.weight                                                         | UNEXPECTED |  |
token2wav.code2wav_dit_model.time_embed.time_mlp.{0, 2}.weight                                           | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.o_proj.weight                                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_v.weight                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.norm_out.linear.bias                                                        | UNEXPECTED |  |
talker.thinker_to_talker_proj.weight                                                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.res2net_block.blocks.0.conv.bias   | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.tdnn2.conv.bias                    | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.tdnn1.conv.bias                    | UNEXPECTED |  |
talker.model.embed_tokens.weight                                                                         | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.se_block.conv1.bias                | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.res2net_block.blocks.0.conv.weight | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.fc.weight                                           | UNEXPECTED |  |
talker.codec_head.weight                                                                                 | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.activation_post.act.beta                                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.0.conv.bias                                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.proj.bias                                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.text_embed.codec_embed.weight                                               | UNEXPECTED |  |
token2wav.code2wav_dit_model.proj_out.bias                                                               | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.mfa.conv.weight                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.0.conv.weight                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.tdnn1.conv.weight                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.mfa.conv.bias                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.asp.conv.weight                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.asp.conv.bias                                       | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.activation_post.act.alpha                                               | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.tdnn2.conv.weight                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.inputLoading weights:  54%|█████▍    | 733/1346 [00:06<00:10, 59.60it/s]_embed.spk_encoder.fc.bias                                             | UNEXPECTED |  |
token2wav.code2wav_dit_model.rotary_embed.inv_freq                                                       | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.conv_post.weight                                                        | UNEXPECTED |  |
talker.thinker_to_talker_proj.bias                                                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.norm_out.linear.weight                                                      | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.conv_pre.bias                                                           | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.asp.tdnn.conv.weight                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.asp.tdnn.conv.bias                                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.proj.weight                                                     | UNEXPECTED |  |

Notes:
- UNEXPECTED:   can be ignored when loading from different task/architecture; not ok if you expect identical arch.
Loading weights:  60%|█████▉    | 805/1346 [00:06<00:09, 58.27it/s]Loading weights:  50%|████▉     | 668/1346 [00:05<00:10, 65.02it/s]Loading weights:  59%|█████▉    | 799/1346 [00:07<00:09, 59.80it/s]Loading weights:  61%|██████    | 815/1346 [00:07<00:08, 63.73it/s]Loading weights:  55%|█████▌    | 742/1346 [00:06<00:10, 59.20it/s]Loading weights:  60%|█████▉    | 806/1346 [00:07<00:09, 55.75it/s]Loading weights:  61%|██████    | 822/1346 [00:07<00:08, 60.92it/s]Loading weights:  56%|█████▌    | 750/1346 [00:06<00:10, 55.26it/s]Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
Loading weights:  65%|██████▍   | 871/1346 [00:07<00:03, 153.61it/s]Loading weights:  60%|██████    | 814/1346 [00:07<00:09, 56.95it/s][transformers] Model config: tts_text_start_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151860. This may result in unexpected behavior.
Loading weights:  56%|█████▌    | 757/1346 [00:06<00:10, 56.94it/s]Loading weights:  69%|██████▉   | 928/1346 [00:07<00:01, 249.64it/s][transformers] Model config: tts_text_end_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151861. This may result in unexpected behavior.
[transformers] Model config: tts_text_pad_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151859. This may result in unexpected behavior.
[transformers] Model config: vision_start_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151652. This may result in unexpected behavior.
[transformers] Model config: vision_end_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151653. This may result in unexpected behavior.
[transformers] Model config: audio_start_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151647. This may result in unexpected behavior.
[transformers] Model config: audio_end_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151648. This may result in unexpected behavior.
Loading weights:  41%|████▏     | 557/1346 [00:03<00:08, 93.42it/s] Loading weights:  61%|██████    | 820/1346 [00:07<00:10, 51.37it/s]Loading weights:  51%|█████     | 688/1346 [00:05<00:10, 60.32it/s]Loading weights:  75%|███████▍  | 1007/1346 [00:07<00:00, 382.37it/s]Loading weights:  57%|█████▋    | 764/1346 [00:07<00:10, 56.02it/s]Loading weights:  65%|██████▍   | 873/1346 [00:07<00:02, 158.54it/s]Loading weights:  45%|████▌     | 606/1346 [00:04<00:10, 71.56it/s]Loading weights:  81%|████████  | 1088/1346 [00:07<00:00, 492.23it/s]Fetching 5 files:   0%|          | 0/5 [00:00<?, ?it/s]Loading weights:  69%|██████▉   | 928/1346 [00:08<00:01, 249.94it/s]Loading weights:  88%|████████▊ | 1186/1346 [00:07<00:00, 624.16it/s]Fetching 5 files: 100%|██████████| 5/5 [00:00<00:00, 684.23it/s]
Loading weights:  52%|█████▏    | 704/1346 [00:06<00:10, 60.99it/s]Loading weights:  57%|█████▋    | 771/1346 [00:07<00:11, 48.26it/s]Loading weights:  75%|███████▍  | 1003/1346 [00:08<00:00, 377.44it/s]Loading weights:  94%|█████████▍| 1264/1346 [00:07<00:00, 660.93it/s]Loading weights:  58%|█████▊    | 780/1346 [00:07<00:10, 52.53it/s]Loading weights:  80%|███████▉  | 1076/1346 [00:08<00:00, 459.01it/s]Loading weights: 100%|██████████| 1346/1346 [00:07<00:00, 169.10it/s]Loading weights:  58%|█████▊    | 786/1346 [00:07<00:10, 53.39it/s]Loading weights:  53%|█████▎    | 717/1346 [00:06<00:10, 59.97it/s]
Loading weights:  87%|████████▋ | 1168/1346 [00:08<00:00, 573.08it/s]Loading weights:  92%|█████████▏| 1238/1346 [00:08<00:00, 600.35it/s]Loading weights:  59%|█████▉    | 794/1346 [00:07<00:10, 55.12it/s]Loading weights:  54%|█████▍    | 728/1346 [00:06<00:10, 58.10it/s]Loading weights:  99%|█████████▉| 1337/1346 [00:08<00:00, 706.52it/s]Loading weights:  60%|█████▉    | 803/1346 [00:07<00:08, 61.42it/s]Loading weights:  48%|████▊     | 642/1346 [00:05<00:10, 66.64it/s]Loading weights:  45%|████▌     | 609/1346 [00:03<00:08, 82.16it/s]Loading weights: 100%|██████████| 1346/1346 [00:08<00:00, 155.77it/s]
Loading weights:  60%|██████    | 810/1346 [00:07<00:10, 52.43it/s]Loading weights:  55%|█████▍    | 737/1346 [00:06<00:10, 55.45it/s][transformers] Qwen2_5OmniForConditionalGeneration LOAD REPORT from: Qwen/Qwen2.5-Omni-7B
Key                                                                                                      | Status     |  |
---------------------------------------------------------------------------------------------------------+------------+--+-
talker.model.layers.{0...23}.self_attn.o_proj.weight                                                     | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.activations.{0, 1, 2, 3, 4, 5}.act.alpha             | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_k.weight                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_k.bias                                  | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.convs1.{0, 1, 2}.bias                                | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.v_proj.bias                                                       | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.activations.{0, 1, 2, 3, 4, 5}.act.beta              | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.ff.ff.{0, 3}.weight                             | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_q.weight                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn_norm.linear.weight                         | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.ff.ff.{0, 3}.bias                               | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.ups.{0, 1, 2, 3, 4, 5}.0.weight                                         | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.convs2.{0, 1, 2}.bias                                | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.convs1.{0, 1, 2}.weight                              | UNEXPECTED |  |
talker.model.layers.{0...23}.post_attention_layernorm.weight                                             | UNEXPECTED |  |
talker.model.layers.{0...23}.mlp.down_proj.weight                                                        | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.q_proj.weight                                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_q.bias                                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_v.weight                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.se_block.conv2.bias                | UNEXPECTED |  |
talker.model.layers.{0...23}.input_layernorm.weight                                                      | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.convs2.{0, 1, 2}.weight                              | UNEXPECTED |  |
talker.model.layers.{0...23}.mlp.up_proj.weight                                                          | UNEXPECTED |  |
token2wav.code2wav_dit_model.proj_out.weight                                                             | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_out.0.bias                              | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.res2net_block.blocks.0.conv.weight | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.v_proj.weight                                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_v.bias                                  | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.k_proj.weight                                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.mfa.conv.bias                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_out.0.weight                            | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.q_proj.bias                                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.se_block.conv2.weight              | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.k_proj.bias                                                       | UNEXPECTED |  |
talker.model.layers.{0...23}.mlp.gate_proj.weight                                                        | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn_norm.linear.bias                           | UNEXPECTED |  |
token2wav.code2wav_dit_model.time_embed.time_mlp.{0, 2}.weight                                           | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.fc.bias                                             | UNEXPECTED |  |
talker.codec_head.weight                                                                                 | UNEXPECTED |  |
token2wav.code2wav_dit_model.time_embed.time_mlp.{0, 2}.bias                                             | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.tdnn2.conv.weight                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.tdnn1.conv.weight                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.norm_out.linear.weight                                                      | UNEXPECTED |  |
talker.thinker_to_talker_proj.bias                                                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.mfa.conv.weight                                     | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.ups.{0, 1, 2, 3, 4, 5}.0.bias                                           | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.res2net_block.blocks.0.conv.bias   | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.tdnn1.conv.bias                    | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.se_block.conv1.bias                | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.asp.conv.weight                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.fc.weight                                           | UNEXPECTED |  |
token2wav.code2wav_dit_model.norm_out.linear.bias                                                        | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.asp.tdnn.conv.weight                                | UNEXPECTED |  |
talker.model.embed_tokens.weight                                                                         | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.se_block.conv1.weight              | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.asp.tdnn.conv.bias                                  | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.conv_pre.bias                                                           | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.activation_post.act.alpha                                               | UNEXPECTED |  |
talker.thinker_to_talker_proj.weight                                                                     | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.conv_post.weight                                                        | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.tdnn2.conv.bias                    | UNEXPECTED |  |
token2wav.code2wav_dit_model.rotary_embed.inv_freq                                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.asp.conv.bias                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.inputLoading weights:  61%|██████    | 818/1346 [00:08<00:09, 53.89it/s]Loading weights:  55%|█████▌    | 745/1346 [00:06<00:11, 53.42it/s]Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
_embed.proj.bias                                                       | UNEXPECTED |  | 
token2wav.code2wav_bigvgan_model.activation_post.act.beta                                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.proj.weight                                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.0.conv.bias                                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.0.conv.weight                                | UNEXPECTED |  |
talker.model.norm.weight                                                                                 | UNEXPECTED |  |
token2wav.code2wav_dit_model.proj_out.bias                                                               | UNEXPECTED |  |
token2wav.code2wav_dit_model.text_embed.codec_embed.weight                                               | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.conv_pre.weight                                                         | UNEXPECTED |  |

Notes:
- UNEXPECTED:   can be ignored when loading from different task/architecture; not ok if you expect identical arch.
Loading weights:  62%|██████▏   | 841/1346 [00:08<00:05, 92.98it/s][transformers] Model config: tts_text_start_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151860. This may result in unexpected behavior.
Loading weights:  50%|████▉     | 669/1346 [00:05<00:10, 65.68it/s]Loading weights:  56%|█████▌    | 753/1346 [00:07<00:10, 56.49it/s]Loading weights:  66%|██████▌   | 886/1346 [00:08<00:02, 178.02it/s][transformers] Model config: tts_text_end_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151861. This may result in unexpected behavior.
[transformers] Model config: tts_text_pad_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151859. This may result in unexpected behavior.
[transformers] Model config: vision_start_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151652. This may result in unexpected behavior.
[transformers] Model config: vision_end_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151653. This may result in unexpected behavior.
[transformers] Model config: audio_start_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151647. This may result in unexpected behavior.
[transformers] Model config: audio_end_token_id must be None or an integer within the vocabulary (between 0 and 8447), got 151648. This may result in unexpected behavior.
Loading weights:  56%|█████▋    | 760/1346 [00:07<00:10, 53.93it/s]Loading weights:  71%|███████   | 954/1346 [00:08<00:01, 300.43it/s]Loading weights:  48%|████▊     | 647/1346 [00:04<00:09, 76.46it/s]Loading weights:  57%|█████▋    | 768/1346 [00:07<00:10, 57.68it/s]Fetching 5 files:   0%|          | 0/5 [00:00<?, ?it/s]Loading weights:  77%|███████▋  | 1034/1346 [00:08<00:00, 422.28it/s][transformers] Qwen2_5OmniForConditionalGeneration LOAD REPORT from: Qwen/Qwen2.5-Omni-7B
Key                                                                                                      | Status     |  |
---------------------------------------------------------------------------------------------------------+------------+--+-
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.convs1.{0, 1, 2}.bias                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_v.bias                                  | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.activations.{0, 1, 2, 3, 4, 5}.act.beta              | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.activations.{0, 1, 2, 3, 4, 5}.act.alpha             | UNEXPECTED |  |
talker.model.layers.{0...23}.mlp.up_proj.weight                                                          | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.convs1.{0, 1, 2}.weight                              | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.convs2.{0, 1, 2}.weight                              | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.v_proj.bias                                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn_norm.linear.weight                         | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.res2net_block.blocks.0.conv.weight | UNEXPECTED |  |
token2wav.code2wav_dit_model.text_embed.codec_embed.weight                                               | UNEXPECTED |  |
token2wav.code2wav_dit_model.norm_out.linear.weight                                                      | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.o_proj.weight                                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_q.weight                                | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.q_proj.bias                                                       | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.k_proj.bias                                                       | UNEXPECTED |  |
talker.model.layers.{0...23}.mlp.down_proj.weight                                                        | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn_norm.linear.bias                           | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_k.weight                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_out.0.weight                            | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.convs2.{0, 1, 2}.bias                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_v.weight                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.ff.ff.{0, 3}.bias                               | UNEXPECTED |  |
talker.model.layers.{0...23}.input_layernorm.weight                                                      | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_k.bias                                  | UNEXPECTED |  |
talker.model.layers.{0...23}.post_attention_layernorm.weight                                             | UNEXPECTED |  |
token2wav.code2wav_dit_model.time_embed.time_mlp.{0, 2}.bias                                             | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.fc.bias                                             | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.v_proj.weight                                                     | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.k_proj.weight                                                     | UNEXPECTED |  |
talker.model.layers.{0...23}.mlp.gate_proj.weight                                                        | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_out.0.bias                              | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.q_proj.weight                                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.fc.weight                                           | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_q.bias                                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.ff.ff.{0, 3}.weight                             | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.se_block.conv1.weight              | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.ups.{0, 1, 2, 3, 4, 5}.0.bias                                           | UNEXPECTED |  |
token2wav.code2wav_dit_model.proj_out.bias                                                               | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.0.conv.bias                                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.asp.tdnn.conv.bias                                  | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.activation_post.act.alpha                                               | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.se_block.conv2.bias                | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.tdnn2.conv.weight                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.tdnn1.conv.weight                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.se_block.conv2.weight              | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.0.conv.weight                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.tdnn1.conv.bias                    | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.res2net_block.blocks.0.conv.bias   | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.ups.{0, 1, 2, 3, 4, 5}.0.weight                                         | UNEXPECTED |  |
talker.thinker_to_talker_proj.weight                                                                     | UNEXPECTED |  |
talker.model.norm.weight                                                                                 | UNEXPECTED |  |
talker.model.embed_tokens.weight                                                                         | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.conv_pre.bias                                                           | UNEXPECTED |  |
token2wav.code2wav_dit_model.norm_out.linear.bias                                                        | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.activation_post.act.beta                                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.mfa.conv.bias                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.tdnn2.conv.bias                    | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.proj.bias                                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.se_block.conv1.bias                | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.conv_pre.weight                                                         | UNEXPECTED |  |
token2wav.code2wav_dit_model.rotary_embed.inv_freq                                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.proj.weight                                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.asp.conv.bias                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.proj_out.weight                                                             | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.asp.conv.weight                                     | UNEXPECTED |  |
talker.thinker_to_talker_proj.bias                                                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.time_embed.time_mlp.{0, 2}.weight                                           | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.asp.tdnn.conv.weight                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.mfa.conv.weight                                     | UNEXPECTED |  |
talker.codec_head.weight                                                                                 | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.conv_post.weight                                                        | UNEXPECTED |  |

Notes:
- UNEXPECTED:   can be ignored when loading from different task/architecture; not ok if you expect identical arch.
Fetching 5 files: 100%|██████████| 5/5 [00:00<00:00, 1101.62it/s]
Loading weights:  58%|█████▊    | 775/1346 [00:07<00:09, 57.94it/s]Loading weights:  51%|█████▏    | 690/1346 [00:05<00:10, 62.45it/s]Loading weights:  83%|████████▎ | 1114/1346 [00:08<00:00, 512.85it/s]Loading weights:  90%|████████▉ | 1208/1346 [00:08<00:00, 617.66it/s]Loading weights:  58%|█████▊    | 782/1346 [00:07<00:10, 53.31it/s]Loading weights:  97%|█████████▋| 1303/1346 [00:08<00:00, 707.83it/s]Loading weights:  59%|█████▉    | 792/1346 [00:07<00:09, 60.81it/s]Loading weights:  52%|█████▏    | 706/1346 [00:06<00:10, 62.26it/s]Loading weights: 100%|██████████| 1346/1346 [00:08<00:00, 152.35it/s]
Loading weights:  50%|█████     | 675/1346 [00:05<00:09, 69.89it/s]Loading weights:  59%|█████▉    | 799/1346 [00:07<00:10, 53.77it/s]Loading weights:  53%|█████▎    | 719/1346 [00:06<00:10, 59.24it/s]Loading weights:  60%|█████▉    | 805/1346 [00:08<00:12, 43.96it/s]Loading weights:  52%|█████▏    | 696/1346 [00:05<00:09, 71.06it/s]Loading weights:  54%|█████▍    | 730/1346 [00:06<00:10, 59.88it/s]Loading weights:  61%|██████    | 817/1346 [00:08<00:09, 57.03it/s]Loading weights:  61%|██████    | 824/1346 [00:08<00:09, 54.26it/s][transformers] Qwen2_5OmniForConditionalGeneration LOAD REPORT from: Qwen/Qwen2.5-Omni-7B
Key                                                                                                      | Status     |  |
---------------------------------------------------------------------------------------------------------+------------+--+-
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.activations.{0, 1, 2, 3, 4, 5}.act.beta              | UNEXPECTED |  |
talker.model.layers.{0...23}.mlp.up_proj.weight                                                          | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.activations.{0, 1, 2, 3, 4, 5}.act.alpha             | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_v.bias                                  | UNEXPECTED |  |
talker.model.layers.{0...23}.post_attention_layernorm.weight                                             | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn_norm.linear.weight                         | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.ff.ff.{0, 3}.bias                               | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.o_proj.weight                                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn_norm.linear.bias                           | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.convs2.{0, 1, 2}.weight                              | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.ff.ff.{0, 3}.weight                             | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.fc.bias                                             | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.k_proj.weight                                                     | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.convs1.{0, 1, 2}.bias                                | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.q_proj.bias                                                       | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.conv_pre.bias                                                           | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.q_proj.weight                                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_out.0.bias                              | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_k.bias                                  | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.convs2.{0, 1, 2}.bias                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.proj_out.weight                                                             | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_k.weight                                | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.conv_post.weight                                                        | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_q.weight                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_v.weight                                | UNEXPECTED |  |
talker.model.layers.{0...23}.mlp.gate_proj.weight                                                        | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.convs1.{0, 1, 2}.weight                              | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.v_proj.weight                                                     | UNEXPECTED |  |
talker.model.embed_tokens.weight                                                                         | UNEXPECTED |  |
talker.model.layers.{0...23}.mlp.down_proj.weight                                                        | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.se_block.conv2.bias                | UNEXPECTED |  |
talker.codec_head.weight                                                                                 | UNEXPECTED |  |
talker.model.layers.{0...23}.input_layernorm.weight                                                      | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_q.bias                                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.tdnn2.conv.bias                    | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.tdnn1.conv.bias                    | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.proj.bias                                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.res2net_block.blocks.0.conv.bias   | UNEXPECTED |  |
talker.thinker_to_talker_proj.bias                                                                       | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.v_proj.bias                                                       | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.k_proj.bias                                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.asp.conv.weight                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.rotary_embed.inv_freq                                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.se_block.conv1.weight              | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.tdnn1.conv.weight                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_out.0.weight                            | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.ups.{0, 1, 2, 3, 4, 5}.0.weight                                         | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.fc.weight                                           | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.res2net_block.blocks.0.conv.weight | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.ups.{0, 1, 2, 3, 4, 5}.0.bias                                           | UNEXPECTED |  |
token2wav.code2wav_dit_model.text_embed.codec_embed.weight                                               | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.proj.weight                                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.se_block.conv2.weight              | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.se_block.conv1.bias                | UNEXPECTED |  |
token2wav.code2wav_dit_model.time_embed.time_mlp.{0, 2}.weight                                           | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.0.conv.weight                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.tdnn2.conv.weight                  | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.activation_post.act.beta                                                | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.conv_pre.weight                                                         | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.0.conv.bias                                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.proj_out.bias                                                               | UNEXPECTED |  |
token2wav.code2wav_dit_model.norm_out.linear.bias                                                        | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.activation_post.act.alpha                                               | UNEXPECTED |  |
token2wav.code2wav_dit_model.time_Loading weights:  55%|█████▍    | 740/1346 [00:06<00:10, 59.01it/s]embed.time_mlp.{0, 2}.bias                                             | UNEXPECTED |  |
talker.thinker_to_talker_proj.weight                                                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.asp.conv.bias                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.norm_out.linear.weight                                                      | UNEXPECTED |  |
talker.model.norm.weight                                                                                 | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.mfa.conv.bias                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.asp.tdnn.conv.bias                                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.mfa.conv.weight                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.asp.tdnn.conv.weight                                | UNEXPECTED |  |

Notes:
- UNEXPECTED:   can be ignored when loading from different task/architecture; not ok if you expect identical arch.
Loading weights:  65%|██████▍   | 872/1346 [00:08<00:03, 145.94it/s]Loading weights:  53%|█████▎    | 713/1346 [00:05<00:09, 67.19it/s]Loading weights:  68%|██████▊   | 916/1346 [00:08<00:02, 211.99it/s]Loading weights:  56%|█████▌    | 748/1346 [00:07<00:10, 55.12it/s]Loading weights:  73%|███████▎  | 981/1346 [00:08<00:01, 320.94it/s]Loading weights:  54%|█████▍    | 727/1346 [00:05<00:09, 65.43it/s]Loading weights:  78%|███████▊  | 1048/1346 [00:08<00:00, 411.04it/s]Loading weights:  56%|█████▌    | 757/1346 [00:07<00:11, 49.11it/s]Loading weights:  83%|████████▎ | 1116/1346 [00:08<00:00, 483.52it/s]Loading weights:  55%|█████▍    | 738/1346 [00:06<00:09, 63.26it/s]Loading weights:  57%|█████▋    | 769/1346 [00:07<00:09, 58.39it/s]Loading weights:  90%|████████▉ | 1205/1346 [00:09<00:00, 595.79it/s]Loading weights:  95%|█████████▍| 1274/1346 [00:09<00:00, 612.76it/s]Loading weights:  58%|█████▊    | 777/1346 [00:07<00:09, 57.56it/s]Loading weights:  56%|█████▌    | 748/1346 [00:06<00:09, 60.35it/s]Loading weights: 100%|██████████| 1346/1346 [00:09<00:00, 146.25it/s]
Loading weights:  56%|█████▋    | 758/1346 [00:06<00:09, 62.49it/s]Loading weights:  58%|█████▊    | 784/1346 [00:07<00:10, 51.70it/s]Loading weights:  57%|█████▋    | 766/1346 [00:06<00:08, 64.87it/s]Loading weights:   0%|          | 0/1346 [00:00<?, ?it/s]Loading weights:  59%|█████▉    | 794/1346 [00:07<00:09, 57.17it/s]Loading weights:   2%|▏         | 32/1346 [00:00<00:04, 275.51it/s]Loading weights:  60%|█████▉    | 803/1346 [00:07<00:08, 62.07it/s]Loading weights:  58%|█████▊    | 774/1346 [00:06<00:09, 58.27it/s]Loading weights:  60%|██████    | 810/1346 [00:08<00:09, 55.31it/s]Loading weights:  58%|█████▊    | 782/1346 [00:07<00:10, 52.55it/s]Loading weights:  61%|██████    | 818/1346 [00:08<00:09, 55.54it/s]Loading weights:  59%|█████▉    | 794/1346 [00:07<00:09, 59.33it/s]Loading weights:   4%|▍         | 60/1346 [00:00<00:14, 90.54it/s] [transformers] Qwen2_5OmniForConditionalGeneration LOAD REPORT from: Qwen/Qwen2.5-Omni-7B
Key                                                                                                      | Status     |  |
---------------------------------------------------------------------------------------------------------+------------+--+-
talker.model.layers.{0...23}.input_layernorm.weight                                                      | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.activations.{0, 1, 2, 3, 4, 5}.act.alpha             | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.convs1.{0, 1, 2}.weight                              | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.ff.ff.{0, 3}.bias                               | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.q_proj.bias                                                       | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.convs2.{0, 1, 2}.bias                                | UNEXPECTED |  |
talker.model.layers.{0...23}.post_attention_layernorm.weight                                             | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_q.weight                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.0.conv.bias                                  | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.k_proj.weight                                                     | UNEXPECTED |  |
talker.model.layers.{0...23}.mlp.down_proj.weight                                                        | UNEXPECTED |  |
talker.model.layers.{0...23}.mlp.gate_proj.weight                                                        | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_out.0.weight                            | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.activations.{0, 1, 2, 3, 4, 5}.act.beta              | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.v_proj.bias                                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_v.weight                                | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.convs2.{0, 1, 2}.weight                              | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.convs1.{0, 1, 2}.bias                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_out.0.bias                              | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.asp.tdnn.conv.bias                                  | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.conv_pre.weight                                                         | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_k.weight                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.ff.ff.{0, 3}.weight                             | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn_norm.linear.weight                         | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.v_proj.weight                                                     | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.q_proj.weight                                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_v.bias                                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.tdnn1.conv.weight                  | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.k_proj.bias                                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_k.bias                                  | UNEXPECTED |  |
talker.model.layers.{0...23}.mlp.up_proj.weight                                                          | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.tdnn2.conv.bias                    | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_q.bias                                  | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.conv_post.weight                                                        | UNEXPECTED |  |
token2wav.code2wav_dit_model.proj_out.bias                                                               | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn_norm.linear.bias                           | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.o_proj.weight                                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.proj.bias                                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.tdnn1.conv.bias                    | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.tdnn2.conv.weight                  | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.ups.{0, 1, 2, 3, 4, 5}.0.bias                                           | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.asp.conv.weight                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.norm_out.linear.weight                                                      | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.se_block.conv2.bias                | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.fc.weight                                           | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.ups.{0, 1, 2, 3, 4, 5}.0.weight                                         | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.res2net_block.blocks.0.conv.weight | UNEXPECTED |  |
token2wav.code2wav_dit_model.time_embed.time_mlp.{0, 2}.weight                                           | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.activation_post.act.alpha                                               | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.activation_post.act.beta                                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.res2net_block.blocks.0.conv.bias   | UNEXPECTED |  |
token2wav.code2wav_dit_model.time_embed.time_mlp.{0, 2}.bias                                             | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.mfa.conv.weight                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.text_embed.codec_embed.weight                                               | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.se_block.conv1.bias                | UNEXPECTED |  |
token2wav.code2wav_dit_model.rotary_embed.inv_freq                                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.se_block.conv2.weight              | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.mfa.conv.bias                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.asp.tdnn.conv.weight                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.proj_out.weight                                                             | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.asp.conv.bias                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.proj.weight                                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.norm_out.linear.bias                                                        | UNEXPECTED |  |
talker.model.embed_tokens.weight                                                                         | UNEXPECTED |  |
talker.thinker_to_talker_proj.bias                                                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.fc.bias                                             | UNEXPECTED |  |
talker.model.norm.weight                                                                                 | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.se_block.conv1.weight              | UNEXPECTED |  |
talker.thinker_to_talker_proj.weight                                                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.0.conv.weight                                | UNEXPECTED |  |
talker.codec_head.weight                                                                                 | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.conv_pre.bias                                                           | UNEXPECTED |  |

Notes:
- UNEXPECTED:   can be ignored when loading from different task/architecture; not ok if you expect identical arch.
Loading weights:  62%|██████▏   | 841/1346 [00:08<00:05, 93.14it/s]Loading weights:  60%|█████▉    | 803/1346 [00:07<00:08, 63.97it/s]Loading weights:  66%|██████▌   | 888/1346 [00:08<00:02, 179.99it/s]Loading weights:   6%|▌         | 75/1346 [00:00<00:15, 84.14it/s]Loading weights:  72%|███████▏  | 968/1346 [00:08<00:01, 327.32it/s]Loading weights:  60%|██████    | 811/1346 [00:07<00:08, 60.57it/s]Loading weights:  78%|███████▊  | 1048/1346 [00:08<00:00, 444.04it/s]Loading weights:  61%|██████    | 818/1346 [00:07<00:09, 57.22it/s]Loading weights:   7%|▋         | 93/1346 [00:00<00:13, 89.69it/s]Loading weights:  84%|████████▍ | 1128/1346 [00:08<00:00, 537.16it/s]Loading weights:  63%|██████▎   | 854/1346 [00:07<00:04, 122.13it/s]Loading weights:  91%|█████████ | 1222/1346 [00:08<00:00, 639.49it/s]Loading weights:  67%|██████▋   | 898/1346 [00:07<00:02, 196.70it/s]Loading weights:   8%|▊         | 105/1346 [00:01<00:16, 76.49it/s]Loading weights:  98%|█████████▊| 1316/1346 [00:09<00:00, 719.55it/s]Loading weights:  72%|███████▏  | 971/1346 [00:07<00:01, 330.63it/s]Loading weights: 100%|██████████| 1346/1346 [00:09<00:00, 148.67it/s]
Loading weights:  11%|█         | 144/1346 [00:01<00:09, 129.07it/s]Loading weights:  78%|███████▊  | 1050/1346 [00:08<00:00, 442.39it/s]Loading weights:  12%|█▏        | 168/1346 [00:01<00:08, 146.22it/s]Loading weights:  85%|████████▌ | 1145/1346 [00:08<00:00, 579.21it/s]Loading weights:  91%|█████████▏| 1230/1346 [00:08<00:00, 653.29it/s]Loading weights:  99%|█████████▉| 1338/1346 [00:08<00:00, 772.93it/s]Loading weights: 100%|██████████| 1346/1346 [00:08<00:00, 161.44it/s]
Loading weights:  14%|█▍        | 187/1346 [00:01<00:11, 103.29it/s]Loading weights:  15%|█▌        | 202/1346 [00:01<00:10, 109.95it/s]Loading weights:  16%|█▌        | 217/1346 [00:02<00:10, 112.04it/s][transformers] Qwen2_5OmniForConditionalGeneration LOAD REPORT from: Qwen/Qwen2.5-Omni-7B
Key                                                                                                      | Status     |  |
---------------------------------------------------------------------------------------------------------+------------+--+-
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_k.weight                                | UNEXPECTED |  |
talker.model.layers.{0...23}.input_layernorm.weight                                                      | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_v.bias                                  | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.activations.{0, 1, 2, 3, 4, 5}.act.beta              | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_out.0.bias                              | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.activations.{0, 1, 2, 3, 4, 5}.act.alpha             | UNEXPECTED |  |
talker.model.norm.weight                                                                                 | UNEXPECTED |  |
talker.model.layers.{0...23}.mlp.down_proj.weight                                                        | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.q_proj.weight                                                     | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.convs2.{0, 1, 2}.weight                              | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.v_proj.bias                                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.ff.ff.{0, 3}.bias                               | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.k_proj.weight                                                     | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.convs2.{0, 1, 2}.bias                                | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.convs1.{0, 1, 2}.bias                                | UNEXPECTED |  |
talker.model.layers.{0...23}.post_attention_layernorm.weight                                             | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.ups.{0, 1, 2, 3, 4, 5}.0.bias                                           | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.convs1.{0, 1, 2}.weight                              | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_out.0.weight                            | UNEXPECTED |  |
token2wav.code2wav_dit_model.text_embed.codec_embed.weight                                               | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_q.bias                                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_q.weight                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.ff.ff.{0, 3}.weight                             | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.o_proj.weight                                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn_norm.linear.bias                           | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.q_proj.bias                                                       | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.conv_pre.bias                                                           | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.v_proj.weight                                                     | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.ups.{0, 1, 2, 3, 4, 5}.0.weight                                         | UNEXPECTED |  |
talker.model.layers.{0...23}.mlp.gate_proj.weight                                                        | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_v.weight                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.res2net_block.blocks.0.conv.weight | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_k.bias                                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn_norm.linear.weight                         | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.mfa.conv.bias                                       | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.k_proj.bias                                                       | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.conv_pre.weight                                                         | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.tdnn1.conv.bias                    | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.fc.bias                                             | UNEXPECTED |  |
talker.model.layers.{0...23}.mlp.up_proj.weight                                                          | UNEXPECTED |  |
talker.model.embed_tokens.weight                                                                         | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.tdnn2.conv.weight                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.asp.tdnn.conv.weight                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.tdnn2.conv.bias                    | UNEXPECTED |  |
token2wav.code2wav_dit_model.time_embed.time_mlp.{0, 2}.weight                                           | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.activation_post.act.alpha                                               | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.0.conv.weight                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.se_block.conv1.weight              | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.res2net_block.blocks.0.conv.bias   | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.asp.conv.weight                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.proj_out.bias                                                               | UNEXPECTED |  |
talker.thinker_to_talker_proj.weight                                                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.tdnn1.conv.weight                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.se_block.conv1.bias                | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.se_block.conv2.bias                | UNEXPECTED |  |
token2wav.code2wav_dit_model.norm_out.linear.weight                                                      | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.se_block.conv2.weight              | UNEXPECTED |  |
token2wav.code2wav_dit_model.time_embed.time_mlp.{0, 2}.bias                                             | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.proj.weight                                                     | UNEXPECTED |  |
talker.codec_head.weight                                                                                 | UNEXPECTED |  |
token2wav.code2wav_dit_model.rotary_embed.inv_freq                                                       | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.activation_post.act.beta                                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.proj_out.weight                                                             | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.conv_post.weight                                                        | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.asp.conv.bias                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.0.conv.bias                                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.asp.tdnn.conv.bias                                  | UNEXPECTED |  |
talker.thinker_to_talker_proj.bias                                                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.norm_out.linear.bias                                                        | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.proj.bias                                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.fc.weight                                           | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.mfa.conv.weight                                     | UNEXPECTED |  |

Notes:
- UNEXPECTED:   can be ignored when loading from different task/architecture; not ok if you expect identical arch.
Loading weights:  18%|█▊        | 249/1346 [00:02<00:07, 154.04it/s]Loading weights:  20%|█▉        | 268/1346 [00:02<00:06, 160.83it/s]Loading weights:  23%|██▎       | 312/1346 [00:02<00:04, 228.62it/s][transformers] Qwen2_5OmniForConditionalGeneration LOAD REPORT from: Qwen/Qwen2.5-Omni-7B
Key                                                                                                      | Status     |  |
---------------------------------------------------------------------------------------------------------+------------+--+-
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.ff.ff.{0, 3}.weight                             | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.q_proj.weight                                                     | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.activations.{0, 1, 2, 3, 4, 5}.act.alpha             | UNEXPECTED |  |
talker.model.layers.{0...23}.mlp.up_proj.weight                                                          | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.o_proj.weight                                                     | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.convs2.{0, 1, 2}.bias                                | UNEXPECTED |  |
talker.model.layers.{0...23}.mlp.gate_proj.weight                                                        | UNEXPECTED |  |
talker.model.norm.weight                                                                                 | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.convs1.{0, 1, 2}.bias                                | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.k_proj.bias                                                       | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.convs1.{0, 1, 2}.weight                              | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_out.0.weight                            | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.v_proj.bias                                                       | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.activations.{0, 1, 2, 3, 4, 5}.act.beta              | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_v.weight                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_q.weight                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn_norm.linear.bias                           | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_out.0.bias                              | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_k.weight                                | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.convs2.{0, 1, 2}.weight                              | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_q.bias                                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.time_embed.time_mlp.{0, 2}.weight                                           | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.k_proj.weight                                                     | UNEXPECTED |  |
talker.model.layers.{0...23}.input_layernorm.weight                                                      | UNEXPECTED |  |
talker.model.layers.{0...23}.mlp.down_proj.weight                                                        | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_k.bias                                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.ff.ff.{0, 3}.bias                               | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.se_block.conv2.weight              | UNEXPECTED |  |
talker.model.layers.{0...23}.post_attention_layernorm.weight                                             | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.se_block.conv1.bias                | UNEXPECTED |  |
token2wav.code2wav_dit_model.time_embed.time_mlp.{0, 2}.bias                                             | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.v_proj.weight                                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.norm_out.linear.bias                                                        | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.ups.{0, 1, 2, 3, 4, 5}.0.bias                                           | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.q_proj.bias                                                       | UNEXPECTED |  |
talker.model.embed_tokens.weight                                                                         | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.res2net_block.blocks.0.conv.bias   | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.tdnn1.conv.bias                    | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_v.bias                                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn_norm.linear.weight                         | UNEXPECTED |  |
token2wav.code2wav_dit_model.norm_out.linear.weight                                                      | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.tdnn1.conv.weight                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.se_block.conv2.bias                | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.asp.tdnn.conv.weight                                | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.activation_post.act.alpha                                               | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.res2net_block.blocks.0.conv.weight | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.0.conv.bias                                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.tdnn2.conv.bias                    | UNEXPECTED |  |
talker.codec_head.weight                                                                                 | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.asp.conv.bias                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.tdnn2.conv.weight                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.0.conv.weight                                | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.ups.{0, 1, 2, 3, 4, 5}.0.weight                                         | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.se_block.conv1.weight              | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.proj.weight                                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.asp.conv.weight                                     | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.conv_pre.weight                                                         | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.activation_post.act.beta                                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.rotary_embed.inv_freq                                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.proj.bias                                                       | UNEXPECTED |  |
talker.thinker_to_talker_proj.bias                                                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.asp.tdnn.conv.bias                                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.fc.weight                                           | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.mfa.conv.bias                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.proj_out.bias                                                               | UNEXPECTED |  |
talker.thinker_to_talker_proj.weight                                                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.mfa.conv.weight                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.proj_out.weight                                                             | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.conv_post.weight                                                        | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.fc.bias                                             | UNEXPECTED |  |
token2wav.code2wav_dit_model.text_embed.codec_embed.weight                                               | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.conv_pre.bias                                                           | UNEXPECTED |  |

Notes:
- UNEXPECTED:   can be ignored when loading from different task/architecture; not ok if you expect identical arch.
Loading weights:  25%|██▌       | 339/1346 [00:02<00:05, 190.51it/s]Loading weights:  27%|██▋       | 370/1346 [00:02<00:04, 217.41it/s]Loading weights:  30%|██▉       | 400/1346 [00:02<00:04, 220.34it/s]Loading weights:  32%|███▏      | 425/1346 [00:02<00:04, 225.48it/s]Loading weights:   0%|          | 0/1346 [00:00<?, ?it/s]Loading weights:  35%|███▌      | 474/1346 [00:02<00:02, 293.47it/s]Loading weights:   2%|▏         | 32/1346 [00:00<00:04, 300.91it/s]Loading weights:   5%|▍         | 63/1346 [00:00<00:07, 172.45it/s]Loading weights:   7%|▋         | 95/1346 [00:00<00:05, 213.71it/s]Loading weights:  10%|█         | 135/1346 [00:00<00:04, 269.64it/s]Loading weights:  14%|█▎        | 183/1346 [00:00<00:03, 326.09it/s]Loading weights:  16%|█▋        | 220/1346 [00:00<00:03, 337.61it/s]Loading weights:  19%|█▉        | 262/1346 [00:00<00:03, 349.50it/s]Loading weights:  23%|██▎       | 316/1346 [00:00<00:02, 390.21it/s]Loading weights:  27%|██▋       | 357/1346 [00:01<00:02, 369.22it/s]Loading weights:  30%|██▉       | 399/1346 [00:01<00:02, 379.52it/s]Loading weights:  34%|███▍      | 459/1346 [00:01<00:02, 440.17it/s]Loading weights:  38%|███▊      | 506/1346 [00:05<00:20, 41.75it/s] Loading weights:  39%|███▉      | 529/1346 [00:06<00:20, 39.67it/s]Loading weights:  37%|███▋      | 504/1346 [00:03<00:13, 63.90it/s] Loading weights:  41%|████      | 546/1346 [00:06<00:21, 36.80it/s]Loading weights:  42%|████▏     | 559/1346 [00:07<00:22, 35.49it/s]Loading weights:  40%|███▉      | 536/1346 [00:04<00:15, 51.71it/s]Loading weights:  42%|████▏     | 569/1346 [00:07<00:24, 32.27it/s]Loading weights:  43%|████▎     | 577/1346 [00:07<00:25, 30.18it/s]Loading weights:  43%|████▎     | 583/1346 [00:08<00:24, 31.44it/s]Loading weights:  44%|████▍     | 589/1346 [00:08<00:24, 31.07it/s]Loading weights:  42%|████▏     | 560/1346 [00:05<00:18, 43.23it/s]qwen-vl-utils using decord to read video.
Loading weights:  44%|████▍     | 594/1346 [00:08<00:27, 26.89it/s]Loading weights:  43%|████▎     | 577/1346 [00:05<00:18, 40.94it/s]Loading weights:  45%|████▍     | 601/1346 [00:08<00:29, 25.05it/s]Loading weights:  45%|████▍     | 605/1346 [00:08<00:28, 26.21it/s]Loading weights:  45%|████▌     | 611/1346 [00:09<00:24, 29.95it/s]Loading weights:  44%|████▍     | 590/1346 [00:06<00:20, 37.01it/s]qwen-vl-utils using decord to read video.
Loading weights:  45%|████▍     | 600/1346 [00:06<00:20, 37.14it/s]Loading weights:  45%|████▌     | 608/1346 [00:06<00:19, 37.10it/s]Loading weights:  46%|████▌     | 615/1346 [00:09<00:50, 14.41it/s]Loading weights:  46%|████▋     | 624/1346 [00:10<00:34, 20.72it/s]Loading weights:  46%|████▌     | 615/1346 [00:07<00:22, 32.38it/s]Loading weights:  46%|████▌     | 622/1346 [00:07<00:22, 32.01it/s]Loading weights:  47%|████▋     | 628/1346 [00:10<00:41, 17.37it/s]Loading weights:  47%|████▋     | 633/1346 [00:10<00:38, 18.66it/s]Loading weights:  47%|████▋     | 627/1346 [00:07<00:23, 30.22it/s]qwen-vl-utils using decord to read video.
Loading weights:  47%|████▋     | 636/1346 [00:10<00:38, 18.38it/s]Loading weights:  47%|████▋     | 635/1346 [00:08<00:23, 30.53it/s]Loading weights:  47%|████▋     | 639/1346 [00:11<00:42, 16.83it/s]Loading weights:  47%|████▋     | 639/1346 [00:08<00:26, 27.14it/s]Loading weights:  48%|████▊     | 646/1346 [00:08<00:21, 32.03it/s]Loading weights:  48%|████▊     | 649/1346 [00:11<00:30, 22.90it/s]Loading weights:  48%|████▊     | 652/1346 [00:11<00:33, 21.02it/s]Loading weights:  48%|████▊     | 650/1346 [00:08<00:29, 23.94it/s]Loading weights:  49%|████▉     | 659/1346 [00:08<00:21, 32.49it/s]Loading weights:  49%|████▉     | 660/1346 [00:11<00:25, 26.75it/s]Loading weights:  49%|████▉     | 663/1346 [00:11<00:28, 23.78it/s]Loading weights:  49%|████▉     | 664/1346 [00:09<00:26, 26.05it/s]Loading weights:  50%|████▉     | 670/1346 [00:12<00:24, 27.48it/s]Loading weights:  50%|████▉     | 670/1346 [00:09<00:22, 29.83it/s]Loading weights:  50%|█████     | 674/1346 [00:12<00:26, 25.66it/s]Loading weights:  50%|█████     | 677/1346 [00:12<00:25, 25.89it/s]Loading weights:  50%|█████     | 674/1346 [00:09<00:27, 24.73it/s]Loading weights:  51%|█████     | 681/1346 [00:12<00:24, 26.77it/s]Loading weights:  50%|█████     | 678/1346 [00:09<00:26, 25.30it/s]Loading weights:  51%|█████     | 682/1346 [00:09<00:26, 24.80it/s]Loading weights:  51%|█████     | 686/1346 [00:12<00:30, 21.87it/s]Loading weights:  52%|█████▏    | 695/1346 [00:13<00:24, 26.54it/s]Loading weights:  51%|█████     | 686/1346 [00:10<00:34, 19.03it/s]Loading weights:  52%|█████▏    | 695/1346 [00:10<00:25, 25.99it/s]Loading weights:  52%|█████▏    | 699/1346 [00:13<00:27, 23.41it/s]Loading weights:  52%|█████▏    | 706/1346 [00:13<00:22, 28.09it/s]Loading weights:  52%|█████▏    | 699/1346 [00:10<00:29, 21.91it/s]Loading weights:  52%|█████▏    | 705/1346 [00:10<00:24, 26.13it/s]Loading weights:  53%|█████▎    | 710/1346 [00:13<00:26, 23.99it/s]Loading weights:  53%|█████▎    | 719/1346 [00:13<00:19, 32.89it/s]Loading weights:  53%|█████▎    | 710/1346 [00:11<00:25, 25.42it/s]Loading weights:  53%|█████▎    | 713/1346 [00:11<00:25, 24.46it/s]Loading weights:  53%|█████▎    | 718/1346 [00:11<00:21, 28.72it/s]Loading weights:  54%|█████▎    | 723/1346 [00:14<00:28, 22.05it/s]Loading weights:  54%|█████▍    | 731/1346 [00:14<00:20, 29.43it/s]Loading weights:  54%|█████▎    | 722/1346 [00:11<00:29, 20.96it/s]Loading weights:  54%|█████▍    | 730/1346 [00:11<00:21, 28.55it/s]Loading weights:  55%|█████▍    | 734/1346 [00:11<00:21, 28.11it/s]qwen-vl-utils using decord to read video.
Loading weights:  55%|█████▍    | 738/1346 [00:12<00:21, 27.69it/s]Loading weights:  55%|█████▍    | 736/1346 [00:14<00:32, 18.94it/s]Loading weights:  55%|█████▌    | 744/1346 [00:12<00:19, 31.67it/s]Loading weights:  55%|█████▌    | 744/1346 [00:15<00:32, 18.74it/s]Loading weights:  56%|█████▌    | 748/1346 [00:12<00:27, 21.47it/s]Loading weights:  56%|█████▌    | 753/1346 [00:15<00:22, 26.49it/s]Loading weights:  56%|█████▋    | 758/1346 [00:15<00:21, 26.82it/s]Loading weights:  56%|█████▌    | 753/1346 [00:12<00:27, 21.79it/s]Loading weights:  56%|█████▋    | 759/1346 [00:13<00:23, 24.53it/s]Loading weights:  57%|█████▋    | 763/1346 [00:15<00:22, 25.58it/s]Loading weights:  57%|█████▋    | 768/1346 [00:13<00:17, 33.87it/s]Loading weights:  57%|█████▋    | 768/1346 [00:16<00:20, 28.40it/s]Loading weights:  57%|█████▋    | 773/1346 [00:13<00:19, 29.95it/s]Loading weights:  57%|█████▋    | 772/1346 [00:16<00:24, 23.26it/s]Loading weights:  58%|█████▊    | 777/1346 [00:13<00:19, 29.69it/s]Loading weights:  58%|█████▊    | 779/1346 [00:16<00:18, 30.50it/s]Loading weights:  58%|█████▊    | 782/1346 [00:13<00:19, 29.11it/s]Loading weights:  58%|█████▊    | 786/1346 [00:13<00:18, 30.42it/s]Loading weights:  58%|█████▊    | 784/1346 [00:16<00:22, 24.81it/s]Loading weights:  59%|█████▉    | 791/1346 [00:13<00:18, 30.71it/s]Loading weights:  59%|█████▊    | 790/1346 [00:16<00:18, 29.96it/s]Loading weights:  59%|█████▉    | 794/1346 [00:17<00:19, 28.52it/s]Loading weights:  59%|█████▉    | 798/1346 [00:17<00:19, 27.69it/s]Loading weights:  59%|█████▉    | 795/1346 [00:14<00:25, 21.53it/s]qwen-vl-utils using decord to read video.
Loading weights:  60%|█████▉    | 803/1346 [00:14<00:18, 28.77it/s]Loading weights:  60%|█████▉    | 807/1346 [00:14<00:23, 23.31it/s]Loading weights:  60%|█████▉    | 804/1346 [00:17<00:28, 19.29it/s]Loading weights:  60%|██████    | 812/1346 [00:17<00:19, 27.26it/s]Loading weights:  60%|██████    | 813/1346 [00:14<00:20, 25.85it/s]Loading weights:  61%|██████    | 817/1346 [00:17<00:17, 30.86it/s]Loading weights:  61%|██████    | 822/1346 [00:18<00:18, 28.26it/s]Loading weights:  61%|██████    | 818/1346 [00:15<00:23, 22.00it/s]Loading weights:  63%|██████▎   | 854/1346 [00:18<00:06, 80.24it/s]Loading weights:  64%|██████▍   | 863/1346 [00:15<00:05, 86.57it/s]Loading weights:  65%|██████▌   | 881/1346 [00:18<00:04, 114.71it/s]Loading weights:  66%|██████▌   | 882/1346 [00:15<00:04, 103.79it/s]Loading weights:  67%|██████▋   | 901/1346 [00:18<00:03, 133.23it/s]Loading weights:  67%|██████▋   | 908/1346 [00:15<00:03, 135.08it/s]Loading weights:  71%|███████   | 954/1346 [00:18<00:01, 219.72it/s]Loading weights:  71%|███████   | 954/1346 [00:15<00:01, 205.03it/s]Loading weights:  74%|███████▍  | 996/1346 [00:18<00:01, 268.11it/s]Loading weights:  74%|███████▍  | 999/1346 [00:15<00:01, 263.50it/s]Loading weights:  77%|███████▋  | 1032/1346 [00:18<00:01, 287.22it/s]Loading weights:  77%|███████▋  | 1040/1346 [00:15<00:01, 299.06it/s]Loading weights:  81%|████████  | 1086/1346 [00:18<00:00, 354.55it/s]Loading weights:  80%|████████  | 1082/1346 [00:15<00:00, 325.28it/s]Loading weights:  84%|████████▎ | 1125/1346 [00:16<00:00, 350.84it/s]Loading weights:  84%|████████▎ | 1125/1346 [00:18<00:00, 351.37it/s]Loading weights:  87%|████████▋ | 1177/1346 [00:16<00:00, 385.27it/s]Loading weights:  88%|████████▊ | 1178/1346 [00:19<00:00, 398.16it/s]Loading weights:  91%|█████████▏| 1230/1346 [00:19<00:00, 432.37it/s]Loading weights:  91%|█████████ | 1228/1346 [00:16<00:00, 419.58it/s]Loading weights:  95%|█████████▍| 1274/1346 [00:16<00:00, 430.99it/s]Loading weights:  95%|█████████▍| 1275/1346 [00:19<00:00, 418.32it/s]Loading weights:  99%|█████████▉| 1339/1346 [00:16<00:00, 493.64it/s]Loading weights: 100%|█████████▉| 1342/1346 [00:19<00:00, 463.44it/s]Loading weights: 100%|██████████| 1346/1346 [00:16<00:00, 81.58it/s] 
Loading weights: 100%|██████████| 1346/1346 [00:19<00:00, 69.45it/s] 
qwen-vl-utils using decord to read video.
[transformers] Qwen2_5OmniForConditionalGeneration LOAD REPORT from: Qwen/Qwen2.5-Omni-7B
Key                                                                                                      | Status     |  |
---------------------------------------------------------------------------------------------------------+------------+--+-
talker.model.layers.{0...23}.mlp.gate_proj.weight                                                        | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.activations.{0, 1, 2, 3, 4, 5}.act.beta              | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.ff.ff.{0, 3}.weight                             | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.convs1.{0, 1, 2}.weight                              | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.ups.{0, 1, 2, 3, 4, 5}.0.bias                                           | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.activations.{0, 1, 2, 3, 4, 5}.act.alpha             | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_v.bias                                  | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.convs2.{0, 1, 2}.weight                              | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_v.weight                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_k.weight                                | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.k_proj.weight                                                     | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.o_proj.weight                                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn_norm.linear.bias                           | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_out.0.weight                            | UNEXPECTED |  |
talker.model.layers.{0...23}.mlp.up_proj.weight                                                          | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_q.weight                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_q.bias                                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_out.0.bias                              | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.q_proj.weight                                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.ff.ff.{0, 3}.bias                               | UNEXPECTED |  |
talker.model.layers.{0...23}.post_attention_layernorm.weight                                             | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.convs2.{0, 1, 2}.bias                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.mfa.conv.bias                                       | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.v_proj.bias                                                       | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.convs1.{0, 1, 2}.bias                                | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.k_proj.bias                                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.se_block.conv1.weight              | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.v_proj.weight                                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.0.conv.weight                                | UNEXPECTED |  |
talker.model.layers.{0...23}.input_layernorm.weight                                                      | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.tdnn1.conv.bias                    | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.q_proj.bias                                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.proj.weight                                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_k.bias                                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.res2net_block.blocks.0.conv.weight | UNEXPECTED |  |
talker.model.layers.{0...23}.mlp.down_proj.weight                                                        | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.proj.bias                                                       | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.conv_post.weight                                                        | UNEXPECTED |  |
token2wav.code2wav_dit_model.time_embed.time_mlp.{0, 2}.weight                                           | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn_norm.linear.weight                         | UNEXPECTED |  |
talker.codec_head.weight                                                                                 | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.fc.bias                                             | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.se_block.conv1.bias                | UNEXPECTED |  |
talker.model.norm.weight                                                                                 | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.tdnn1.conv.weight                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.tdnn2.conv.weight                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.time_embed.time_mlp.{0, 2}.bias                                             | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.res2net_block.blocks.0.conv.bias   | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.se_block.conv2.bias                | UNEXPECTED |  |
talker.model.embed_tokens.weight                                                                         | UNEXPECTED |  |
token2wav.code2wav_dit_model.norm_out.linear.weight                                                      | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.tdnn2.conv.bias                    | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.0.conv.bias                                  | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.activation_post.act.alpha                                               | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.asp.conv.weight                                     | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.conv_pre.weight                                                         | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.asp.tdnn.conv.weight                                | UNEXPECTED |  |
talker.thinker_to_talker_proj.bias                                                                       | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.conv_pre.bias                                                           | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.ups.{0, 1, 2, 3, 4, 5}.0.weight                                         | UNEXPECTED |  |
token2wav.code2wav_dit_model.rotary_embed.inv_freq                                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.text_embed.codec_embed.weight                                               | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.se_block.conv2.weight              | UNEXPECTED |  |
token2wav.code2wav_dit_model.norm_out.linear.bias                                                        | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.mfa.conv.weight                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.asp.tdnn.conv.bias                                  | UNEXPECTED |  |
talker.thinker_to_talker_proj.weight                                                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.fc.weight                                           | UNEXPECTED |  |
token2wav.code2wav_dit_model.proj_out.weight                                                             | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.activation_post.act.beta                                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.asp.conv.bias                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.proj_out.bias                                                               | UNEXPECTED |  |

Notes:
- UNEXPECTED:   can be ignored when loading from different task/architecture; not ok if you expect identical arch.
[transformers] Qwen2_5OmniForConditionalGeneration LOAD REPORT from: Qwen/Qwen2.5-Omni-7B
Key                                                                                                      | Status     |  |
---------------------------------------------------------------------------------------------------------+------------+--+-
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.convs1.{0, 1, 2}.weight                              | UNEXPECTED |  |
talker.model.layers.{0...23}.mlp.up_proj.weight                                                          | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_v.weight                                | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.ups.{0, 1, 2, 3, 4, 5}.0.weight                                         | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.convs2.{0, 1, 2}.weight                              | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn_norm.linear.weight                         | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_q.bias                                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.ff.ff.{0, 3}.bias                               | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.activations.{0, 1, 2, 3, 4, 5}.act.beta              | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_out.0.weight                            | UNEXPECTED |  |
talker.model.layers.{0...23}.post_attention_layernorm.weight                                             | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.activations.{0, 1, 2, 3, 4, 5}.act.alpha             | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.q_proj.weight                                                     | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.v_proj.bias                                                       | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.v_proj.weight                                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.ff.ff.{0, 3}.weight                             | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_q.weight                                | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.q_proj.bias                                                       | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.k_proj.weight                                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_out.0.bias                              | UNEXPECTED |  |
talker.model.layers.{0...23}.input_layernorm.weight                                                      | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.convs1.{0, 1, 2}.bias                                | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.conv_pre.bias                                                           | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.ups.{0, 1, 2, 3, 4, 5}.0.bias                                           | UNEXPECTED |  |
talker.model.layers.{0...23}.mlp.down_proj.weight                                                        | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_k.weight                                | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.o_proj.weight                                                     | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.resblocks.{0...17}.convs2.{0, 1, 2}.bias                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_k.bias                                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.0.conv.weight                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn.to_v.bias                                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.proj.bias                                                       | UNEXPECTED |  |
talker.model.norm.weight                                                                                 | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.tdnn2.conv.bias                    | UNEXPECTED |  |
token2wav.code2wav_dit_model.transformer_blocks.{0...21}.attn_norm.linear.bias                           | UNEXPECTED |  |
talker.model.layers.{0...23}.mlp.gate_proj.weight                                                        | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.se_block.conv1.weight              | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.tdnn2.conv.weight                  | UNEXPECTED |  |
talker.model.layers.{0...23}.self_attn.k_proj.bias                                                       | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.conv_pre.weight                                                         | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.tdnn1.conv.weight                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.se_block.conv2.bias                | UNEXPECTED |  |
token2wav.code2wav_dit_model.time_embed.time_mlp.{0, 2}.bias                                             | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.activation_post.act.beta                                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.norm_out.linear.weight                                                      | UNEXPECTED |  |
token2wav.code2wav_dit_model.norm_out.linear.bias                                                        | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.tdnn1.conv.bias                    | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.fc.weight                                           | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.se_block.conv2.weight              | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.res2net_block.blocks.0.conv.bias   | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.se_block.conv1.bias                | UNEXPECTED |  |
talker.thinker_to_talker_proj.bias                                                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.{1, 2, 3}.res2net_block.blocks.0.conv.weight | UNEXPECTED |  |
token2wav.code2wav_dit_model.time_embed.time_mlp.{0, 2}.weight                                           | UNEXPECTED |  |
token2wav.code2wav_dit_model.rotary_embed.inv_freq                                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.asp.tdnn.conv.bias                                  | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.activation_post.act.alpha                                               | UNEXPECTED |  |
talker.model.embed_tokens.weight                                                                         | UNEXPECTED |  |
token2wav.code2wav_bigvgan_model.conv_post.weight                                                        | UNEXPECTED |  |
token2wav.code2wav_dit_model.proj_out.weight                                                             | UNEXPECTED |  |
talker.codec_head.weight                                                                                 | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.asp.conv.bias                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.blocks.0.conv.bias                                  | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.fc.bias                                             | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.asp.tdnn.conv.weight                                | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.mfa.conv.bias                                       | UNEXPECTED |  |
token2wav.code2wav_dit_model.proj_out.bias                                                               | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.mfa.conv.weight                                     | UNEXPECTED |  |
talker.thinker_to_talker_proj.weight                                                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.text_embed.codec_embed.weight                                               | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.spk_encoder.asp.conv.weight                                     | UNEXPECTED |  |
token2wav.code2wav_dit_model.input_embed.proj.weight                                                     | UNEXPECTED |  |

Notes:
- UNEXPECTED:   can be ignored when loading from different task/architecture; not ok if you expect identical arch.
qwen-vl-utils using decord to read video.
qwen-vl-utils using decord to read video.
qwen-vl-utils using decord to read video.
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
⠋ Running (9/9 containers active)... View app at 
https://modal.com/apps/tejasvityagi1414/main/ap-RLm4s78t2w0vCf6zrSMWtB
╭───────────────────────────────────────────────────────────────────────

What happened

Nothing's wrong — that's your Omni full run succeeding. The last line, Running (9/9 containers active), means all 9 GPU workers are live and processing the 50 videos right now. The giant wall of text is just startup noise. Decoding it:

Scary-looking output	What it actually is
talker.* / token2wav.* … UNEXPECTED (the huge LOAD REPORT)	This is the success signal. Your enable_audio_output=False worked — the model loaded only the thinker (the part that understands video+audio+text→text) and skipped the talker + vocoder (speech output), which you don't need. Those checkpoint weights have nowhere to go, so they're listed as "unexpected." The note literally says "can be ignored." Saved you ~10 GB.
tts_text_start_token_id … got 151860, between 0 and 8447	Same thing — config warnings about the unused TTS/speech head. Benign.
Warning: unauthenticated requests to the HF Hub	No HF token set → just slower downloads / rate limits. Harmless.
librosa … __audioread_load Deprecated	Version-deprecation FutureWarning from audio loading. Harmless.
qwen-vl-utils using decord to read video (×many)	Each condition decoding the video frames. Normal.
LOAD REPORT printed ~9 times	Once per container — all 9 workers loaded Omni-7B in parallel. Normal.
So: the thinker loaded correctly on all 9 containers, raw audio is flowing (the +A pass reads each clip's audio track), and the shards are running.

What happens next: let it run. Omni is heavier than the VL model — especially the V+C+A pass ingesting raw audio over long clips — so expect ~30–60 min wall-clock for all 50. When it finishes you'll see:

got 50 predictions -> cached to records_omni.json
Then run Cell 11 (metrics table) → Cell 12 (plot). That's your raw-audio result.

One thing to watch: a container could hit CUDA OOM on the longest videos (up to 648 s) during the raw-audio pass — you'd see a traceback and end up with fewer than 50 predictions. If that happens, in Cell 2 set MAX_FRAMES = 64 (and optionally N_VIDEOS = 30 to skip the longest ones), then re-run Cell 6 → Cell 10. So far, 9/9 active with no crash = it's surviving fine.

Don't re-run anything while it's active — just wait for the got N predictions line, then paste me Cell 11's table and we'll see whether V+C+A (raw audio) > V+C > V.

# 10) Full run across GPU containers + cache results (idempotent: reuses records_tvsum.json)
import json, os
def chunk(xs, k): return [xs[i:i+k] for i in range(0, len(xs), k)]
cfg = {"CLIP_LEN": CLIP_LEN, "DATA": DATA, "MAX_FRAMES": MAX_FRAMES, "BASE_FPS": BASE_FPS,
       "MAX_PIXELS": MAX_PIXELS, "MAX_NEW_TOKENS": MAX_NEW_TOKENS, "CONDITIONS": CONDITIONS, "MAX_SEG": MAX_SEG}

records = []
if os.path.exists(RECORDS_PATH) and not FORCE_INFER:
    try: records = json.load(open(RECORDS_PATH))
    except Exception: records = []

if records and not FORCE_INFER:                       # only trust a NON-empty cache
    print(f"loaded cached {len(records)} records from {RECORDS_PATH} (FORCE_INFER=True to recompute)")
else:
    assert eval_set, "eval_set is empty - run Cell 8 and confirm videos are on the Volume first"
    jobs = [{"examples": s, "cfg": cfg} for s in chunk(eval_set, 5)]   # ~5 videos/container
    records = []
    with modal.enable_output(), app.run():
        async for b in Predictor().predict_batch.map.aio(jobs):
            records.extend(b)
    json.dump(records, open(RECORDS_PATH, "w"))
    print(f"got {len(records)} predictions -> cached to {RECORDS_PATH}")
468 s
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
/usr/local/lib/python3.12/site-packages/librosa/core/audio.py:172: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
Stopping app - keyboard interrupt received. Use modal run --detach to prevent KeyboardInterrupts from killing apps.
Runner terminated.
Runner terminated.
Runner terminated.

The run was interrupted ~8 min in (keyboard interrupt received → Runner terminated), not crashed. And your Cell 10 only writes the cache after all 50 finish — so the interrupt threw away all 8 minutes of work. The endless librosa … __audioread_load lines are normal: that's process_mm_info loading each clip's raw audio for the +A pass. Nothing was wrong; Omni is just slow and something (a stop click, or Colab disconnecting/timing out) killed the cell before it finished.

Two fixes: make the run resumable (so an interrupt never costs you more than one shard), and shrink it so it finishes fast.

Cell 10 — replace with this resumable version (saves after every shard, skips videos already done, survives a single OOM):

# 10) Full run - RESUMABLE: saves after each shard, skips done videos, tolerates shard failures
import json, os
def chunk(xs, k): return [xs[i:i+k] for i in range(0, len(xs), k)]
cfg = {"CLIP_LEN": CLIP_LEN, "DATA": DATA, "MAX_FRAMES": MAX_FRAMES, "BASE_FPS": BASE_FPS,
       "MAX_PIXELS": MAX_PIXELS, "MAX_NEW_TOKENS": MAX_NEW_TOKENS, "CONDITIONS": CONDITIONS, "MAX_SEG": MAX_SEG}

records = []
if os.path.exists(RECORDS_PATH) and not FORCE_INFER:
    try: records = json.load(open(RECORDS_PATH))
    except Exception: records = []
done = {r["vid"] for r in records}
todo = [e for e in eval_set if e["vid"] not in done]
print(f"{len(done)} already done, {len(todo)} to go (of {len(eval_set)})")

if todo:
    jobs = [{"examples": s, "cfg": cfg} for s in chunk(todo, 2)]   # small shards = frequent checkpoints
    with modal.enable_output(), app.run():
        async for b in Predictor().predict_batch.map.aio(jobs, return_exceptions=True):
            if isinstance(b, Exception):
                print("  shard failed (skipped):", repr(b)[:120]); continue
            records.extend(b)
            json.dump(records, open(RECORDS_PATH, "w"))     # checkpoint immediately
            print(f"  saved {len(records)}/{len(eval_set)}")
print(f"total {len(records)} predictions in {RECORDS_PATH}")
Cell 2 — shrink so it completes in one sitting (you can bump back up later; it'll resume, only doing the missing ones):

MAX_FRAMES = 96     # was 128 — fewer frames = faster + less memory for the raw-audio pass
N_VIDEOS   = 15     # was 50 — a clean subset that finishes in ~8-12 min
Run: Cell 2 → Cell 3 → Cell 8 → Cell 10. Then let it run — do not stop it. The librosa/HF lines are harmless; your real progress is the saved 2/15, saved 4/15 … lines. When it prints total 15 predictions, run Cell 11 → 12.

Because it's now resumable: if Colab disconnects again, just re-run Cell 10 — it reloads what's saved and only processes the missing videos. Want all 50 afterward? Set N_VIDEOS=50, re-run Cell 3 → 8 → 10; it resumes from your 15 and does the other 35.

Safety net: if Omni keeps fighting the clock, your Qwen2.5-VL pipeline was fast and working (the smoke passed). Re-paste the VL Cell 4 + Cell 6, set RECORDS_PATH="records_tvsum.json", and you'll have the full V/V+C/V+C+A (audio-as-text) table in ~20 min as your guaranteed result — then Omni on a subset is the bonus "raw audio" comparison. Don't let the fancier model cost you a submitted result.

explain to me what spearman, kendall, and top 5 map are

All three answer the same question — does the model's importance ranking of the 2-second segments match what humans thought was important? — but in different ways. For each video you have two vectors over the segments:

p = the model's predicted saliency per segment (your 0–4 scores, expanded to 2s bins)
g = the human ground-truth importance per segment (the averaged TVSum scores)
The metrics compare p against g, per video, then average over all videos.

Why ranks instead of raw values? The model's "2" and a human's "3.8" aren't on the same scale, and the absolute numbers don't matter for editing — what matters is relative ordering (which moments are more highlight-worthy than others). Otani et al. (2019) showed the older F1-summary metric on TVSum is basically saturated/unreliable, so rank correlation became the standard. That's why two of your three metrics are rank-based.

1. Spearman's ρ (rho) — "do the orderings agree?"
Turn both vectors into ranks (1st most important, 2nd, 3rd, …), then take the ordinary correlation between those two rank lists.

+1 = model ranks the segments in exactly the same order humans do
0 = no relationship
−1 = exactly reversed
It captures any monotonic agreement (as human importance goes up, predicted score tends to go up), not just linear. It's the headline TVSum metric.

2. Kendall's τ (tau) — "what fraction of pairs are ordered correctly?"
Look at every pair of segments (A, B). The pair is concordant if the model and humans agree on which one is more important, discordant if they disagree.

τ
=
#
concordant
−
#
discordant
#
pairs
τ= 
#pairs
#concordant−#discordant
​
 

+1 = every pair ordered the same way humans do
0 = agree on half the pairs (chance)
−1 = every pair reversed
It measures the same thing as Spearman but is more conservative and robust to noise — its magnitude is almost always smaller than Spearman's, so don't be alarmed when τ < ρ. Reporting both is just the TVSum convention.

Mini-example: humans rank segments A > B > C; the model says A > C > B. Pairs: (A,B) agree ✓, (A,C) agree ✓, (B,C) disagree ✗ → τ = (2−1)/3 = 0.33.

3. top-5 mAP — "are the true highlights near the top of your ranked list?"
This reframes it as retrieval instead of correlation. In your _top5_ap:

Define the true highlights = the top ~20% most-important segments by g.
Sort all segments by the model's predicted score, highest first.
Walk down that ranked list; each time you hit a true highlight, record the precision so far (hits ÷ position). Average Precision (AP) is the mean of those — it's high when the real highlights sit at the top of your ranking.
mAP = mean AP across all videos.
So mAP rewards a model that puts the good moments first — which is exactly what you need for an auto-editor that keeps the top clips. Random guessing scores ≈ the positive rate (~0.2 here), so mAP meaningfully above ~0.2 means real signal.

⚠️ Naming caveat for your paper: the classic literature "Top-5 mAP" protocol varies by paper. Your code's definition is "positives = top-20% segments, AP over the predicted ranking." Just state that definition explicitly so it's reproducible — don't imply it's identical to another paper's number.

Reading them together
Metric	Range	Chance	Captures	Note
Spearman ρ	−1 … +1	0	overall ordering agreement	most sensitive
Kendall τ	−1 … +1	0	pairwise ordering agreement	smaller, more robust
top-5 mAP	0 … 1	≈0.2	are true highlights ranked first	retrieval-style
Two reality checks so you don't panic at the table: (1) TVSum numbers are small by nature — published zero-shot/weakly-supervised Spearman is often only ~0.05–0.20, so ρ ≈ 0.12 is a genuinely decent result, not a bug. (2) Your "audio helps" claim is supported if V+C+A ≥ V+C ≥ V on all three — the direction and consistency of the gap matters more than the absolute size, especially on a 15-video subset where any single number is noisy.





i want to add a cell at the end that visualizes the performance. Dont edit the file, just give me a cell to run at the end

I'll read the notebook to understand what the model does and what metrics/variables are available.

Read
fusion-model.ipynb
The notebook is large. Let me read it in parts.

Read
fusion-model.ipynb
(1–400, 1–150)
The Read tool counts the whole file. Let me extract just the cell sources with jq instead.

Ran
Extract notebook cell sources
Let me see the rest of the notebook, especially the fusion logic and how results are produced.

Ran
Extract more notebook cells
Let me see the final cells of the notebook.

Ran
Extract final notebook cells
This notebook runs everything on Modal and commits results to the tvsum-data volume as JSON (routed_fusion_results.json from the last/routed version, fusion_results.json from the weight-sweep version). So the cleanest visualization cell reads those JSONs straight from the volume and plots them — no rerun needed.

Paste this as the last cell:

# ============================================================
#  Visualize fusion performance — reads results from the volume
# ============================================================
import json
import numpy as np
import modal
try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    import sys, subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "matplotlib"])
    import matplotlib.pyplot as plt

vol = modal.Volume.from_name("tvsum-data")

def load_json(name):
    try:
        return json.loads(b"".join(vol.read_file(name)).decode())
    except Exception:
        return None

# prefer the domain-routed result; fall back to the weight-sweep result
res       = load_json("routed_fusion_results.json") or load_json("fusion_results.json")
sweep_res = load_json("fusion_results.json")          # for the audio-weight sweep panel
assert res, "No results JSON in the volume yet — run the fusion job first."

fused_label = (f"Fusion (w_audio={sweep_res['best_w']})"
               if "best_w" in res else "Routed Fusion (CLAP→BK)")

doms   = sorted(res["vt"]["per_domain"])
labels = doms + ["AVG"]
vt = [res["vt"]["per_domain"][d]               for d in doms] + [res["vt"]["avg"]]
cl = [res["clap"]["per_domain"].get(d, np.nan) for d in doms] + [res["clap"]["avg"]]
fu = [res["fused"]["per_domain"][d]            for d in doms] + [res["fused"]["avg"]]

has_sweep = sweep_res is not None and "sweep" in sweep_res
fig, axes = plt.subplots(1, 2 if has_sweep else 1,
                         figsize=(15 if has_sweep else 11, 5))
ax = axes[0] if has_sweep else axes

# ---- per-domain grouped bars ----
x, w = np.arange(len(labels)), 0.27
for off, vals, lab, col in [(-w, vt, "CG-DETR (video+lang)", "#4C72B0"),
                            (0.0, cl, "CLAP (audio)",        "#DD8452"),
                            (+w, fu, fused_label,            "#55A868")]:
    bars = ax.bar(x + off, vals, w, label=lab, color=col)
    for b, v in zip(bars, vals):
        if not np.isnan(v):
            ax.text(b.get_x() + b.get_width()/2, v + 0.005, f"{v:.2f}",
                    ha="center", va="bottom", fontsize=7)

ax.axvspan(len(doms) - 0.5, len(doms) + 0.5, color="gold", alpha=0.12)  # spotlight AVG
ax.set_xticks(x); ax.set_xticklabels(labels)
ax.get_xticklabels()[-1].set_fontweight("bold")
ax.set_ylabel("Top-5 mAP")
ax.set_ylim(0, np.nanmax(vt + cl + fu) * 1.18)
ax.set_title(f"TVSum Top-5 mAP per domain  (n={res['n']} videos)")
ax.legend(loc="upper left", fontsize=9); ax.grid(axis="y", alpha=0.3)

# ---- audio-weight sweep (only if the sweep result exists) ----
if has_sweep:
    ax2 = axes[1]
    ks = sorted(sweep_res["sweep"], key=float)
    ws = [float(k) for k in ks]
    ys = [sweep_res["sweep"][k] for k in ks]
    ax2.plot(ws, ys, "-o", color="#55A868", label="fused mAP")
    bw = float(sweep_res["best_w"]); bi = ws.index(bw)
    ax2.scatter([ws[bi]], [ys[bi]], s=170, facecolors="none",
                edgecolors="red", linewidths=2, zorder=5, label=f"best (w={bw})")
    ax2.axhline(sweep_res["vt"]["avg"],   ls="--", color="#4C72B0", label="CG-DETR only")
    ax2.axhline(sweep_res["clap"]["avg"], ls="--", color="#DD8452", label="CLAP only")
    ax2.set_xlabel("audio weight  (video weight = 1.0)")
    ax2.set_ylabel("fused Top-5 mAP")
    ax2.set_title("Audio-weight sweep")
    ax2.legend(fontsize=8); ax2.grid(alpha=0.3)

plt.tight_layout(); plt.show()

# ---- one-line numeric summary ----
delta = res["fused"]["avg"] - res["vt"]["avg"]
print(f"{fused_label}: {res['fused']['avg']:.4f}  |  CG-DETR: {res['vt']['avg']:.4f}  "
      f"|  CLAP: {res['clap']['avg']:.4f}  |  Δ vs CG-DETR: {'+' if delta >= 0 else ''}{delta:.4f}")
What it shows:

Left panel — grouped bars of Top-5 mAP per TVSum domain for CG-DETR vs CLAP vs your fused model, with the AVG group highlighted.
Right panel — the audio-weight sweep curve (only renders if fusion_results.json from the sweep version is present), with the best weight circled and dashed reference lines for the two single-modality baselines.
A couple of notes:

It auto-picks the routed result if present, otherwise the sweep result, so it works whether or not you ran the final routed tvsum_fusion.py.
It reads via vol.read_file(...), which works from the Modal notebook process. If read_file ever errors in your environment, the fallback is !modal volume get tvsum-data routed_fusion_results.json . then json.load(open(...)).


Build me a code that runs cutclaw. Simply take a downloaded movie and run it through cutclaw and get me the output. Give me the ipynb file

I want to make sure I build the right thing — "cutclaw" isn't a tool I recognize off the top of my head. Let me search for it.


Browsed the web, used a tool
Found it — CutClaw is a real project (GVCLab/CutClaw). Let me read its README to get the actual install/run commands right.

Fetched
https://github.com/GVCLab/CutClaw
Let me pull the precise config details — particularly how LiteLLM/model keys are wired up, since that's the part most likely to trip up a run.


Browsed the web, ran a command
The README is lowercase. Let me grab the README, local_run.py, and src/config.py to get the exact arguments and where API keys go.


Ran 2 commands
Let me read the full local_run.py and config.py from the saved output to nail down the exact flow and where API keys/LiteLLM base URL get set.

Read
bbm4912b3.txt
Let me check requirements.txt, the ASR module, and render_video.py so the notebook's commands and dependencies are exactly right.


Ran 2 commands
Let me grab the render_video.py argument parser (the main/argparse section).


Ran 2 commands
Let me double-check one suspicious line in local_run.py (a stray w appeared near line 452) — I want to know if it's a real bug before the notebook relies on the script.


Ran 2 commands
I now have everything I need — the exact CLI, config fields, render args, dependencies, and I confirmed an upstream bug (a stray w on line 452 of local_run.py that breaks python local_run.py) which the notebook will patch automatically.

You asked for the .ipynb file as the deliverable, so I'll generate it in your working directory. I'll build it programmatically to guarantee valid notebook JSON.

Created
make_cutclaw_nb.py
+268
-0
Now I'll run the generator to produce the notebook, then validate it parses as a real notebook.

Ran
Generate notebook and validate code cells parse
The notebook is generated and validated — all 14 cells parse, and it's valid nbformat 4.5 JSON.

📓 Deliverable: cutclaw_run.ipynb (in Documents/Claude/)

Let me save a quick note connecting this to your Lore work, then I'll summarize.


Recalled a memory, saved 2 memories
Done. Here's what I built and the one thing to know going in.

cutclaw_run.ipynb
A 14-cell notebook that takes your downloaded movie and runs it end-to-end through CutClaw:

Install — clones the repo, installs ffmpeg + Python deps (with a madmom-from-source fallback, since it's flaky on 3.12).
Configure — one cell where you set your movie/music paths, instruction, and API access. The next cell copies the files into CutClaw's resource/ layout and writes your settings into src/config.py.
Run pipeline — local_run.py, streaming progress live (deconstruct → plan shots → pick timestamps).
Render — finds the generated shot_plan/shot_point JSON and renders output/final.mp4.
Watch — plays the result inline.
The one catch worth flagging upfront
CutClaw cuts footage to a separate music track — so it needs a movie and an .mp3/.wav, not just the movie. That's fundamental to how it works (the movie's own audio is only used for dialogue/character analysis). The config cell has a required MUSIC_PATH for this. If you genuinely only have the movie, you'd need to pick a song to sync to.

Also baked in
You need LiteLLM-compatible API access for 3 roles (vision, audio, agent) — your Stanford AI Gateway would fit here, just point BASE_URL/API_KEY at it and use a vision-capable model. The config cell defaults to OpenAI as a placeholder.
Auto-patches an upstream bug: local_run.py ships with a stray w on line 452 that crashes python local_run.py with an IndentationError. The notebook strips it automatically so the run actually starts.
First-run knobs: CLIP_MINUTES=5 and TOTAL_SHOTS=60 are set low so your first run is fast/cheap — bump them up once it works. A GPU is strongly recommended; CPU works but is slow.
I did not clone or run anything on your machine — the notebook is the deliverable, ready for you to open and run. Want me to adjust any defaults (e.g. wire BASE_URL to the Stanford Gateway, or make it Colab-specific)?

what do i need to set it up properly.

Here's the full setup checklist — what you actually need before the notebook will run successfully.

1. A machine with the right specs
GPU (CUDA) strongly recommended. It runs on CPU, but a full movie will crawl. A Colab GPU runtime or any CUDA box works.
Python 3.12 is what the repo targets — but madmom (the beat-tracking dep) is smoothest on 3.10 / 3.11. If install fights you, that's the lever to pull.
Disk space — frames get extracted at low res, but budget a few GB per movie for intermediates.
2. Two input files (both required)
File	Format	Role
Movie	.mp4 / .mkv (libx264 reads most reliably)	the raw footage
Music track	.mp3 / .wav	the montage is cut to this — not optional
If your movie is in a weird codec and the pipeline hangs, re-encode first:
ffmpeg -i in.mkv -c:v libx264 -c:a aac out.mp4

3. API access — a LiteLLM-compatible endpoint
This is the part people miss. CutClaw calls models for three roles, and you fill these into the config cell:

Config field	What it does	Requirement
VIDEO_MODEL	scene/shot understanding	must be vision-capable
AGENT_MODEL	the editing agent (plans + picks shots)	must be vision-capable
AUDIO_MODEL	captions music segments	multimodal; same model usually fine
Plus BASE_URL + API_KEY for the OpenAI-compatible endpoint. Model names use LiteLLM form, e.g. openai/gpt-4o.

→ Your Stanford AI Gateway fits here — it's an OpenAI-compatible LiteLLM endpoint. Point BASE_URL/API_KEY at it. One caveat: it serves Claude Sonnet, which is vision-capable (good for video + agent), so you can set all three roles to the same Sonnet model. If a role 404s, that model name isn't provisioned on the gateway.

4. System tools
ffmpeg — required for rendering. The install cell auto-installs it on Colab/Linux; on macOS run brew install ffmpeg.
git — to clone the repo (the notebook does the clone).
5. Speech-to-text — already handled, no action needed
The notebook defaults ASR_BACKEND="whisper_cpp" (runs locally, no API key, downloads a small model itself) and disables diarization so you don't need a gated HuggingFace token. Optional: drop in your own .srt via SRT_PATH to skip transcription entirely.

Minimum to start
A movie + a song + a working BASE_URL/API_KEY with one vision model. Then in the config cell set those plus MOVIE_PATH and MUSIC_PATH, keep CLIP_MINUTES=5 for the first run, and go top to bottom.

Want me to pre-fill the config cell to use your Stanford Gateway (so all three model roles point at Sonnet), so you only have to paste the movie/music paths and your key?

does a google cloud api key work

Short answer: a Gemini API key from Google AI Studio works great — a raw Google Cloud / Vertex AI key is a different, more painful animal. The distinction matters, so let me be precise.

The two "Google" keys
1. Google AI Studio (Gemini API) key ✅ — the one from aistudio.google.com, looks like AIza...
This is what you want. Gemini exposes an OpenAI-compatible endpoint, which slots straight into CutClaw's config (it expects base_url + api_key + an openai/<model> name). Gemini models are vision-capable, and the CutClaw README actually recommends Gemini for the video and audio roles.

2. Google Cloud / Vertex AI key ⚠️ — created in the GCP Console under Credentials
Vertex AI doesn't authenticate with a plain API-key string; it wants a GCP project + region + service-account credentials (ADC / OAuth). LiteLLM supports it via the vertex_ai/ provider, but it's real setup and doesn't fit the base_url+api_key slots cleanly. Skip this unless you specifically need Vertex.

Config-cell values for an AI Studio key
API_KEY  = "AIza..."                                                   # your Gemini key
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"  # Gemini's OpenAI-compatible endpoint

VIDEO_MODEL = "openai/gemini-2.5-pro"      # vision
AUDIO_MODEL = "openai/gemini-2.5-flash"    # cheaper is fine here
AGENT_MODEL = "openai/gemini-2.5-pro"      # the editing agent
Use whatever Gemini model your key actually has access to — keep the openai/ prefix (that tells LiteLLM to hit the endpoint over the OpenAI protocol). Flash for audio keeps cost down; Pro for video/agent for quality.

One caution that will bite you
CutClaw fires many concurrent requests (parallel shot workers + batched captioning). Google AI Studio's free tier has tight rate limits — you'll get throttled hard on a real movie. Enable billing on the key, and/or lower PARALLEL_SHOT_MAX_WORKERS and the batch sizes if you see 429s.

ASR (subtitles) stays local via whisper_cpp, so the Gemini key isn't used there — no Google Speech setup needed.

Want me to wire these Gemini values into the config cell of the notebook so it's ready to go with just your key + file paths pasted in?





