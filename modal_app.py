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
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg", "git", "build-essential")
    .run_commands("git clone --depth 1 https://github.com/GVCLab/CutClaw.git /root/CutClaw")
    .pip_install("numpy<2", "cython")                      # FLAG: madmom build prereqs
    .run_commands("pip install -r /root/CutClaw/requirements.txt")  # FLAG: torch 2.8/decord/madmom build
)

# Persistent storage for inputs (clips+music) and outputs (the render).
vol = modal.Volume.from_name("lore-data", create_if_missing=True)
DATA = "/data"          # populate via `modal volume put lore-data ...` (see MODAL.md)
OUT = "/data/Output"


@app.function(image=image, gpu="L4", timeout=60 * 60,
              volumes={DATA: vol},
              secrets=[modal.Secret.from_name("openai")])
def run_cutclaw(instruction: str, video_rel: str = "concat.mp4",
                music_rel: str = "Frisky.mp3", max_minutes: int | None = None,
                total_shots: int = 80):
    """Run CutClaw (vlog/POV regime, protagonist off) on the uploaded footage."""
    import os, subprocess, sys
    os.chdir("/root/CutClaw")
    sys.path.insert(0, "/root/CutClaw")

    video = os.path.join(DATA, video_rel)
    music = os.path.join(DATA, music_rel)
    assert os.path.exists(video), f"missing {video} — upload via modal volume put"
    assert os.path.exists(music), f"missing {music}"

    # Route CutClaw's 3 LiteLLM endpoints to OpenAI. FLAG: AUDIO model expects an
    # audio-understanding model (Qwen3-Omni); gpt-4o may need a text-only fallback
    # for music-structure captioning — verify on first run.
    cfg = {
        "VIDEO_DATABASE_FOLDER": OUT + "/",
        "VIDEO_TYPE": "vlog",                 # Lore's POV regime branches from vlog
        "MAIN_CHARACTER_NAME": "",            # gut protagonist
        "ENABLE_FACE_QUALITY_CHECK": "False",
        "ENABLE_TRIM_SHOT_CHARACTER_ANALYSIS": "False",
        "VIDEO_ANALYSIS_MODEL": "openai/gpt-4o",
        "VIDEO_ANALYSIS_ENDPOINT": "https://api.openai.com/v1",
        "VIDEO_ANALYSIS_API_KEY": os.environ["OPENAI_API_KEY"],
        "AGENT_LITELLM_MODEL": "openai/gpt-4o",
        "AGENT_LITELLM_URL": "https://api.openai.com/v1",
        "AGENT_LITELLM_API_KEY": os.environ["OPENAI_API_KEY"],
        "AUDIO_LITELLM_MODEL": "openai/gpt-4o",   # FLAG (see above)
        "AUDIO_LITELLM_BASE_URL": "https://api.openai.com/v1",
        "AUDIO_LITELLM_API_KEY": os.environ["OPENAI_API_KEY"],
        "ASR_BACKEND": "litellm",
        "AUDIO_TOTAL_SHOTS": str(total_shots),
    }
    if max_minutes:
        cfg["VIDEO_MAX_MINUTES"] = str(max_minutes)

    cmd = ["python", "local_run.py", "--type", "vlog",
           "--Video_Path", video, "--Audio_Path", music, "--Instruction", instruction]
    for k, v in cfg.items():
        cmd += [f"--config.{k}", str(v)]
    print("RUN:", " ".join(cmd[:8]), "... (+%d config overrides)" % len(cfg))
    rc = subprocess.run(cmd).returncode
    vol.commit()
    return {"returncode": rc, "output_dir": OUT}


@app.local_entrypoint()
def main(instruction: str = "A day out, from afternoon light into night",
         max_minutes: int = 0, total_shots: int = 80):
    res = run_cutclaw.remote(instruction=instruction,
                             max_minutes=(max_minutes or None),
                             total_shots=total_shots)
    print("done:", res)
