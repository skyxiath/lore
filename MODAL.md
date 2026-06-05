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

## Flagged iteration points (expected on first run)
1. **Image build** — `madmom` (Cython/numpy<2) and `decord`/`torch==2.8.0` are the likely build failures; the image pins `numpy<2 cython` first. Adjust if the build errors.
2. **Audio model routing** — CutClaw's `AUDIO_LITELLM_MODEL` expects an audio-understanding model (Qwen3-Omni) for music-structure captioning; `openai/gpt-4o` may need a text-only fallback path. The madmom beat/downbeat detection itself is local DSP and unaffected.
3. **Config override plumbing** — confirm `--config.X` reaches the OpenAI-compatible client code (endpoint + key) as expected; `src/config.py` reads these but verify the LiteLLM client honors them.
4. **GPU tier** — `L4` is a cheap default; bump if pyannote/decode is slow. ASR-for-names is skipped on the vlog path, so diarization/HF-token isn't needed.
