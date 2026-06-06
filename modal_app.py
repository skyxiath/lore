"""Run the full CutClaw composition spine on Modal (Linux + GPU).

Why: CutClaw's stack (torch 2.8 / madmom / decord / pyannote) won't install on the
local Apple-silicon / Python-3.14 box. Modal gives a Linux GPU container where it
does. We route CutClaw's three LiteLLM endpoints to OpenAI, feed it the interval
footage (concatenated for the M0 baseline), and render a day-recap.

STATUS: scaffold — authored against the verified code map (notes/cutclaw-code-map.md)
but NOT yet run (needs Modal auth + OpenAI quota). The first `modal run` is a debug
pass; the FLAGGED lines below are the expected iteration points.

Setup (see MODAL.md):
  ./.venv/bin/modal token new                       # auth
  modal secret create openai OPENAI_API_KEY=sk-...  # key as a Modal secret
  # transcode + upload data into the volume (MODAL.md has the ffmpeg one-liner)
  ./.venv/bin/modal run modal_app.py --instruction "a day, building to night"
"""
from __future__ import annotations

import modal

app = modal.App("lore-cutclaw")

# --- Image: Linux + ffmpeg + build tools + CutClaw deps -----------------------
# madmom needs Cython+numpy at build time; pin numpy<2 first (madmom is old).
# Verified working recipe (see modal_smoke.py): CutClaw's full stack builds + imports.
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg", "git", "build-essential")
    .run_commands("git clone --depth 1 https://github.com/GVCLab/CutClaw.git /root/CutClaw")
    .pip_install("cython", "numpy<2")
    .run_commands("pip install -r /root/CutClaw/requirements.txt")
    # requirements pull numpy 2.x back in → breaks madmom/aubio (numpy 1.x ABI). Pin last.
    .run_commands("pip install --force-reinstall --no-deps 'numpy==1.26.4'")
    # torchcodec native lib won't load and CutClaw decodes via decord → remove it.
    .run_commands("pip uninstall -y torchcodec || true")
    # boto3 for LiteLLM→Bedrock auth (CutClaw's reqs omit it; it was OpenAI/Qwen-only).
    .pip_install("boto3")
    # Source patches to upstream CutClaw (stray-'w' IndentationError; audio image_url →
    # input_audio for OpenAI gpt-audio). Last layers so the heavy pip layers stay cached.
    .add_local_file("patches/cutclaw_patches.py", "/root/cutclaw_patches.py", copy=True)
    .run_commands("python /root/cutclaw_patches.py /root/CutClaw")
)


def _compat_shims():
    """Re-add pre-3.10 collections aliases + pre-numpy-1.24 dtype aliases that madmom
    and other old deps in CutClaw's stack still reference. Call before importing CutClaw."""
    import collections, collections.abc, numpy as np
    for _n in ("MutableSequence", "MutableMapping", "Mapping", "Sequence", "Callable", "Iterable"):
        if not hasattr(collections, _n):
            setattr(collections, _n, getattr(collections.abc, _n))
    for _a, _t in (("float", float), ("int", int), ("bool", bool), ("object", object),
                   ("complex", complex), ("str", str)):
        if not hasattr(np, _a):
            setattr(np, _a, _t)

# Persistent storage for inputs (clips+music) and outputs (the render).
vol = modal.Volume.from_name("lore-data", create_if_missing=True)
DATA = "/data"          # populate via `modal volume put lore-data ...` (see MODAL.md)
OUT = "/data/Output"

# Self-hosted Qwen3-VL (modal_vllm.py) — the model CutClaw was actually built for.
VLLM_URL = "https://skyxiath--lore-qwen3vl-serve.modal.run/v1"
VLLM_KEY = "lore-vllm-key"


@app.function(image=image, gpu="L4", timeout=60 * 60, memory=16384,
              volumes={DATA: vol},
              secrets=[modal.Secret.from_name("openai"), modal.Secret.from_name("aws")])
def run_cutclaw(instruction: str, video_rel: str = "concat.mp4",
                music_rel: str = "Frisky.mp3", max_minutes: int | None = None,
                total_shots: int = 80):
    """Run CutClaw (vlog/POV regime, protagonist off) on the uploaded footage."""
    import os, subprocess, sys
    _compat_shims()
    os.chdir("/root/CutClaw")
    sys.path.insert(0, "/root/CutClaw")

    video = os.path.join(DATA, video_rel)
    music = os.path.join(DATA, music_rel)
    assert os.path.exists(video), f"missing {video} — upload via modal volume put"
    assert os.path.exists(music), f"missing {music}"

    # CutClaw's content-based AdaptiveDetector finds ~0 cuts on a homogeneous concat of
    # our worthy clips. We made the concat, so we know the cuts: seed shot_scenes.txt
    # (CutClaw skips detection when it exists). Upload <vid>_shots.txt alongside the video.
    import shutil
    vid = os.path.splitext(os.path.basename(video))[0]
    shots_src = os.path.join(DATA, f"{vid}_shots.txt")
    if os.path.exists(shots_src):
        frames_dir = os.path.join(OUT, "Video", vid, "frames")
        os.makedirs(frames_dir, exist_ok=True)
        shutil.copy(shots_src, os.path.join(frames_dir, "shot_scenes.txt"))
        print(f"[lore] seeded {sum(1 for _ in open(shots_src))} shot boundaries → shot_scenes.txt")

    # Route CutClaw's 3 LiteLLM endpoints to OpenAI. FLAG: AUDIO model expects an
    # audio-understanding model (Qwen3-Omni); gpt-4o may need a text-only fallback
    # for music-structure captioning — verify on first run.
    cfg = {
        "VIDEO_DATABASE_FOLDER": OUT + "/",
        "VIDEO_TYPE": "vlog",                 # Lore's POV regime branches from vlog
        "MAIN_CHARACTER_NAME": "",            # gut protagonist
        "ENABLE_FACE_QUALITY_CHECK": "False",
        "ENABLE_TRIM_SHOT_CHARACTER_ANALYSIS": "False",
        # The captioner + agent both run on our self-hosted Qwen3-VL (the intended model),
        # via its OpenAI-compatible vLLM endpoint. No external rate limits.
        "VIDEO_ANALYSIS_MODEL": "openai/Qwen3-VL",
        "VIDEO_ANALYSIS_ENDPOINT": VLLM_URL,
        "VIDEO_ANALYSIS_API_KEY": VLLM_KEY,
        "AGENT_LITELLM_MODEL": "openai/Qwen3-VL",
        "AGENT_LITELLM_URL": VLLM_URL,
        "AGENT_LITELLM_API_KEY": VLLM_KEY,
        "AUDIO_LITELLM_MODEL": "openai/gpt-audio-mini",  # audio-INPUT model (plain gpt-4o can't take audio)
        "AUDIO_LITELLM_BASE_URL": "https://api.openai.com/v1",
        "AUDIO_LITELLM_API_KEY": os.environ["OPENAI_API_KEY"],
        "ASR_BACKEND": "litellm",
        "AUDIO_TOTAL_SHOTS": str(total_shots),
        "CORE_MAX_FRAMES": "24",   # cap frames/Editor call (TPM + cost)
        # Caption requests were ~46K tokens each × 64 parallel → saturated even mini's
        # 200K TPM. Halve frames/request (VIDEO_FPS) and throttle parallelism.
        "VIDEO_FPS": "1",
        "CAPTION_BATCH_SIZE": "12",   # Bedrock Nova has high throughput; can parallelize more
    }
    if max_minutes:
        cfg["VIDEO_MAX_MINUTES"] = str(max_minutes)

    cmd = ["python", "local_run.py", "--type", "vlog",
           "--Video_Path", video, "--Audio_Path", music, "--Instruction", instruction]
    for k, v in cfg.items():
        cmd += [f"--config.{k}", str(v)]
    # src/audio/litellm_client.py reads model/key/base_url from THESE env vars at import
    # time (before --config overrides apply), so set them directly or it uses key "EMPTY".
    env = os.environ.copy()
    env["AUDIO_MODEL"] = "openai/gpt-audio-mini"
    env["AUDIO_API_KEY"] = os.environ["OPENAI_API_KEY"]
    env["AUDIO_BASE_URL"] = "https://api.openai.com/v1"
    # Bedrock auth for LiteLLM/boto3 (the access key + secret come from the 'aws' secret).
    region = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION") or "us-east-1"
    env["AWS_REGION_NAME"] = region
    env["AWS_DEFAULT_REGION"] = region
    print("RUN:", " ".join(cmd[:8]), "... (+%d config overrides)" % len(cfg))
    rc = subprocess.run(cmd, env=env).returncode
    vol.commit()
    return {"returncode": rc, "output_dir": OUT}


@app.local_entrypoint()
def main(instruction: str = "A day out, from afternoon light into night",
         video_rel: str = "concat.mp4", music_rel: str = "Frisky.mp3",
         max_minutes: int = 0, total_shots: int = 80):
    res = run_cutclaw.remote(instruction=instruction, video_rel=video_rel, music_rel=music_rel,
                             max_minutes=(max_minutes or None), total_shots=total_shots)
    print("done:", res)
