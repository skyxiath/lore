# Running CutClaw on Modal

The full CutClaw composition spine (torch 2.8 / madmom / decord) won't install on the local Mac (Python 3.14 / Apple silicon). Modal runs it in a Linux GPU container. App: [modal_app.py](modal_app.py). Code map: [notes/cutclaw-code-map.md](notes/cutclaw-code-map.md).

> Status: scaffold authored, not yet run (needs Modal auth + funded OpenAI key). First `modal run` is a debug pass — see Flagged iteration points.

## 1. Auth (one-time)

```bash
./.venv/bin/modal token new          # browser flow
# — or paste a token from modal.com/settings/tokens and I'll: modal token set ...
```

## 2. OpenAI key as a Modal secret

The GPU container needs the key (same funded key as local `.env`):

```bash
./.venv/bin/modal secret create openai OPENAI_API_KEY=sk-proj-...
```

## 3. Prep + upload data

CutClaw takes **one** video, so for the M0 baseline we transcode the 40 clips to 480p (matches CutClaw's 240–360p working res, ~50× smaller upload) and concatenate them. Run locally (Mac has ffmpeg):

```bash
cd "tests/test 1"
mkdir -p small
for f in "raw clips"/VID_*.mp4; do
  ffmpeg -y -i "$f" -vf scale=-2:480 -c:v libx264 -crf 26 -c:a aac "small/$(basename "$f")"
done
# concat in capture order
ls small/VID_*.mp4 | sort | sed "s/^/file '/;s/$/'/" > list.txt
ffmpeg -y -f concat -safe 0 -i list.txt -c copy concat.mp4

# upload into the Modal volume
cd ../..
./.venv/bin/modal volume put lore-data "tests/test 1/concat.mp4" concat.mp4
./.venv/bin/modal volume put lore-data "tests/test 1/Frisky.mp3" Frisky.mp3
```

> Note: concatenating discards the interval/gap structure — that's deliberate for **M0** ("does CutClaw, blind to the interval structure, break on raw footage?"). Lore's real interval path (later) keeps clips separate and feeds `lore.segmentation` + the metadata arc ([tests/test 1/lore_out/metadata_arc.json](tests/test%201/lore_out/metadata_arc.json)).

## 4. Run

```bash
# quick smoke test: first 10 min, few shots
./.venv/bin/modal run modal_app.py --instruction "a day out, into the night" --max-minutes 10 --total-shots 40
# full run
./.venv/bin/modal run modal_app.py --instruction "a day out, into the night"
```

## 5. Retrieve the render

```bash
./.venv/bin/modal volume get lore-data Output ./modal_out
```

## Build: VERIFIED ✅ (see `modal_smoke.py`)
CutClaw's full stack builds and imports on Modal (config, Screenwriter, core, Reviewer + madmom/torch/decord/aubio/scenedetect). Non-obvious fixes, baked into `modal_app.py`:
- **numpy**: requirements pull numpy 2.x → breaks madmom (ImportError) + aubio (SIGSEGV); both need the numpy 1.x ABI. Force `numpy==1.26.4` as the **last** pip layer.
- **torchcodec**: pulled transitively, native lib won't load and raises on import. CutClaw decodes with **decord**, so `pip uninstall -y torchcodec`.
- **runtime shims** (`_compat_shims()`): re-add pre-3.10 `collections` aliases + pre-numpy-1.24 dtype aliases (`np.float` etc.) before importing CutClaw.
- **pyannote.audio** fails on `libcudart.so.13` — diarization only, which the vlog/POV path skips. Not on our path.
- Container needs `memory=16384`.

## Still to verify on the first real RUN
1. **Audio model routing** — `AUDIO_LITELLM_MODEL` expects an audio model (Qwen3-Omni); `openai/gpt-4o` may need a text-only fallback. madmom beat/downbeat DSP is local and unaffected.
2. **Config override plumbing** — confirm `--config.X` reaches the OpenAI-compatible client (endpoint + key).
3. **Hybrid input** — feed CutClaw our worthiness-selected clips (concatenated), not the full archive.
