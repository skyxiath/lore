"""Serve the real Qwen3-VL-30B-A3B-Instruct on Modal via vLLM (OpenAI-compatible).

This is the model CutClaw was designed for (its visual captioner). We host it ourselves
instead of bending gpt-4o/Nova to fit. CutClaw then points VIDEO_ANALYSIS (and the agent)
at this endpoint. Weights (~60GB) cache in the hf-cache volume so we download once.

Deploy:  ./.venv/bin/modal deploy modal_vllm.py   → prints the web URL
Then set CutClaw's VIDEO_ANALYSIS_ENDPOINT to <url>/v1, model 'openai/Qwen3-VL', key VLLM_KEY.
"""
import modal

MODEL = "Qwen/Qwen3-VL-30B-A3B-Instruct"
SERVED = "Qwen3-VL"            # short served-model-name CutClaw calls
VLLM_KEY = "lore-vllm-key"     # simple bearer key for the endpoint

app = modal.App("lore-qwen3vl")

# vLLM >= 0.11 is required for Qwen3-VL support.
image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("vllm>=0.11.0", "huggingface_hub[hf_transfer]", "qwen-vl-utils")
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1", "VLLM_USE_V1": "1"})
)

hf_cache = modal.Volume.from_name("hf-cache", create_if_missing=True)


@app.function(
    image=image,
    gpu="H100",
    volumes={"/root/.cache/huggingface": hf_cache},
    timeout=60 * 60,
    scaledown_window=15 * 60,   # stay warm 15 min after last request
    max_containers=1,
)
@modal.concurrent(max_inputs=32)   # vLLM batches internally; allow concurrent HTTP
@modal.web_server(port=8000, startup_timeout=30 * 60)   # first boot downloads ~60GB
def serve():
    import subprocess
    cmd = (
        f"vllm serve {MODEL}"
        " --host 0.0.0.0 --port 8000"
        f" --served-model-name {SERVED}"
        f" --api-key {VLLM_KEY}"
        " --max-model-len 32768"
        " --limit-mm-per-prompt '{\"image\":32}'"   # CutClaw sends many frames/caption
        " --gpu-memory-utilization 0.92"
    )
    print("launching:", cmd, flush=True)
    subprocess.Popen(cmd, shell=True)
