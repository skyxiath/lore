"""Source patches applied to the cloned CutClaw (in the Modal image and locally).

Keeps our fixes to upstream's code version-controlled and in one place. Idempotent.
Usage: python patches/cutclaw_patches.py [CUTCLAW_DIR]   (default /root/CutClaw)
"""
import os
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "/root/CutClaw"

# CutClaw sends audio as an image_url data-URI (works on Qwen-Omni OpenAI-compatible
# endpoints) but OpenAI's gpt-audio models require the `input_audio` content type.
AUDIO_IMG = '{"type": "image_url", "image_url": {"url": f"data:audio/mp3;base64,{audio_b64}"}}'
AUDIO_FIX = '{"type": "input_audio", "input_audio": {"data": audio_b64, "format": "mp3"}}'


def edit(rel, fn):
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        print(f"  skip (missing): {rel}"); return
    s = open(p).read()
    ns = fn(s)
    if ns != s:
        open(p, "w").write(ns); print(f"  patched: {rel}")
    else:
        print(f"  no-op:   {rel}")


print(f"Patching CutClaw at {ROOT}")
# 1) Upstream typo: a stray standalone 'w' line in local_run.py → IndentationError.
edit("local_run.py", lambda s: "\n".join(ln for ln in s.split("\n") if ln != "w"))
# 2) Audio content type: image_url → input_audio (audio captioning + ASR paths).
edit("src/audio/litellm_client.py", lambda s: s.replace(AUDIO_IMG, AUDIO_FIX))
edit("src/video/preprocess/asr.py", lambda s: s.replace(AUDIO_IMG, AUDIO_FIX))

# 3) Upstream's local_run.py (vlog path) imports src.core_vlog, but that file is missing
#    from the repo. Shim it to src.core's EditorCoreAgent — with protagonist checks off
#    via config, the film Editor behaves like the vlog one.
cv = os.path.join(ROOT, "src", "core_vlog.py")
if not os.path.exists(cv):
    open(cv, "w").write("from src.core import EditorCoreAgent  # Lore shim: upstream omits core_vlog\n")
    print("  created: src/core_vlog.py (shim -> src.core)")
else:
    print("  exists:  src/core_vlog.py")
print("CutClaw patches done")
