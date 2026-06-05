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
    .pip_install("cython", "numpy<2")                      # madmom build prereqs
    .run_commands("pip install -r /root/CutClaw/requirements.txt")
    # requirements pull numpy 2.x back in, which breaks madmom/aubio (compiled against
    # the numpy 1.x C-ABI → ImportError + SIGSEGV). Pin numpy 1.x as the FINAL layer.
    .run_commands("pip install --force-reinstall --no-deps 'numpy==1.26.4'")
    # torchcodec gets pulled in transitively but its native lib can't load (FFmpeg/CUDA
    # mismatch) and raises on import. CutClaw decodes with decord, so remove it → the
    # importing libs (torchaudio/torchvision) fall back gracefully.
    .run_commands("pip uninstall -y torchcodec || true")
)


@app.function(image=image, timeout=1800, memory=16384, gpu="L4")
def verify():
    import sys
    # madmom (and other old libs) use the pre-3.10 collections aliases — re-add them.
    import collections, collections.abc
    for _n in ("MutableSequence", "MutableMapping", "Mapping", "Sequence", "Callable", "Iterable"):
        if not hasattr(collections, _n):
            setattr(collections, _n, getattr(collections.abc, _n))
    import numpy as np   # restore numpy aliases madmom expects (removed in numpy>=1.24)
    for _a, _t in (("float", float), ("int", int), ("bool", bool), ("object", object),
                   ("complex", complex), ("str", str)):
        if not hasattr(np, _a):
            setattr(np, _a, _t)
    results = {}

    def step(m):
        # flush BEFORE importing: if the import segfaults the process, this line is
        # the last thing in the logs → names the culprit.
        print(f"importing {m} ...", flush=True)
        try:
            mod = __import__(m)
            v = getattr(mod, "__version__", "ok")
        except Exception as e:
            v = f"FAIL: {type(e).__name__}: {str(e)[:90]}"
        print(f"  -> {m}: {v}", flush=True)
        results[m] = v

    for m in ["numpy", "torch", "decord", "madmom", "aubio", "soundfile",
              "litellm", "scenedetect", "pyannote.audio"]:
        step(m)
    sys.path.insert(0, "/root/CutClaw")
    for m in ["src.config", "src.Screenwriter_scene_short", "src.core", "src.Reviewer"]:
        step(m)
    return results


@app.local_entrypoint()
def main():
    import json
    print("=== CutClaw-on-Modal import verification ===")
    print(json.dumps(verify.remote(), indent=2))
