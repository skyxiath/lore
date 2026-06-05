"""Smoke test: does CutClaw's heavy stack build + import on Modal?

De-risks the hybrid before the full pipeline run. Builds the image (the risky part:
torch 2.8 / madmom / decord / pyannote on Linux) and verifies every dep + CutClaw's
own modules import. Run: ./.venv/bin/modal run modal_smoke.py
"""
import modal

app = modal.App("lore-cutclaw-smoke")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg", "git", "build-essential")
    .run_commands("git clone --depth 1 https://github.com/GVCLab/CutClaw.git /root/CutClaw")
    .pip_install("numpy<2", "cython")                      # madmom build prereqs
    .run_commands("pip install -r /root/CutClaw/requirements.txt")
)


@app.function(image=image, timeout=1800)
def verify():
    import sys
    results = {}
    for m in ["numpy", "torch", "decord", "madmom", "litellm", "scenedetect",
              "soundfile", "aubio", "pyannote.audio"]:
        try:
            mod = __import__(m)
            results[m] = getattr(mod, "__version__", "ok")
        except Exception as e:
            results[m] = f"FAIL: {type(e).__name__}: {str(e)[:90]}"
    sys.path.insert(0, "/root/CutClaw")
    for m in ["src.config", "src.Screenwriter_scene_short", "src.core", "src.Reviewer"]:
        try:
            __import__(m); results[f"CutClaw.{m}"] = "ok"
        except Exception as e:
            results[f"CutClaw.{m}"] = f"FAIL: {type(e).__name__}: {str(e)[:90]}"
    return results


@app.local_entrypoint()
def main():
    import json
    print("=== CutClaw-on-Modal import verification ===")
    print(json.dumps(verify.remote(), indent=2))
