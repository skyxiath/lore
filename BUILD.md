# Build & Run

Setup, the CutClaw baseline (M0), and how Lore's scaffold plugs in. Architecture: [plan/architecture.md](plan/architecture.md) · Code map: [notes/cutclaw-code-map.md](notes/cutclaw-code-map.md).

## 0. The Lore scaffold (works today, no heavy deps)

The orchestrator's dry-run runs on the standard library alone — use it to see the stage graph and the exact CutClaw overrides Lore pushes:

```bash
cd /Users/sky/Developer/Stanford/Lore
python3 -m lore.pipeline plan --regime pov \
  --instruction "A morning ski run, building to the big drop" \
  --video /path/to/raw.mp4 --audio /path/to/track.mp3
# or, after `pip install -e .`:  lore plan --regime interval ...
```

`lore run ...` is scaffolded but intentionally raises until M5 (it tells you what to build next). Until then, drive CutClaw directly (below) with the printed overrides.

## 1. Clone CutClaw (already done; reproduce with)

```bash
git clone --depth 1 https://github.com/GVCLab/CutClaw.git external/CutClaw
```

`external/` is git-ignored by Lore (don't track the upstream clone).

## 2. Environment for running the real pipeline

Heavy deps + ffmpeg + GPU recommended. Lore reuses CutClaw's environment.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r external/CutClaw/requirements.txt   # torch 2.8, madmom, pyannote, decord, litellm, ...
pip install -e .                                    # the `lore` package + console script
# system dep: ffmpeg must be on PATH
```

> Apple-silicon note: `madmom` and `decord` can be finicky to build; a CUDA Linux box is the path of least resistance for full runs.

## 3. API keys (CutClaw needs three LiteLLM endpoints)

CutClaw calls models via LiteLLM with **separate** endpoints for video analysis, audio, and the agents. Set them in `external/CutClaw/src/config.py` or via `--config.X` overrides:

- `VIDEO_ANALYSIS_{MODEL,ENDPOINT,API_KEY}` — Qwen3-VL-class captioner
- `AUDIO_LITELLM_{MODEL,API_KEY,BASE_URL}` — Qwen3-Omni-class audio captioner
- `AGENT_LITELLM_{MODEL,URL,API_KEY}` — the Screenwriter/Editor/Reviewer agent LLM
- `ASR_BACKEND` = `whisper_cpp` (local) or `litellm` (cloud)

## 4. M0 — the motivating experiment (break CutClaw on raw footage)

Run CutClaw **unmodified** on raw POV/glasses footage and document the three failure modes (PySceneDetect finds no real units; protagonist gate misfires; no dead time gets rejected). Baseline vs. raw:

```bash
cd external/CutClaw
# (a) intended regime — a film (sanity baseline):
python local_run.py --type film --instruction_type narrative \
  --Video_Path Dataset/Video/Movie/La_La_Land.mkv --Audio_Path <track>.mp3 \
  --Instruction "..." --config.VIDEO_MAX_MINUTES 10 --config.AUDIO_TOTAL_SHOTS 60

# (b) Lore's regime — raw GoPro/POV (expect breakage):
python local_run.py --type vlog \
  --Video_Path <raw_pov>.mp4 --Audio_Path <track>.mp3 --Instruction "..." \
  --config.VIDEO_MAX_MINUTES 10 --config.AUDIO_TOTAL_SHOTS 60 \
  --config.MAIN_CHARACTER_NAME "" --config.ENABLE_FACE_QUALITY_CHECK False
```

Capture: spurious-cut count, protagonist-gate behavior, and fraction of dead time retained. This is the figure that *shows* the gap (plan M0).

## 5. How Lore plugs in (per milestone — see plan/project-plan.md)

- **M2 worthiness gate** → `lore/worthiness/` scores+prunes the scenes JSON before the Screenwriter reads it.
- **M3 segmentation + metadata** → `lore/segmentation/` writes `scenes/scene_0.json` (registered as `SHOT_DETECTION_MODEL=lore_event`); `lore/metadata/` ingests GPMF/Aria.
- **M4 re-anchor** → `lore/compose/` + prompt patches in `external/CutClaw/src/prompt.py`; protagonist already off via config.
- **M5** → `lore run` wires it end-to-end.
