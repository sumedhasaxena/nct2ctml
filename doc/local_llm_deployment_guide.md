# Local LLM Deployment Guide

This document collects commands for running several local LLMs on GPU02 (gpu02.sbms.hku.hk).

## 1. `sglang` server (Qwen 3.5 35B, GPTQ Int4)

- Client-side settings:
- In `config.py`, set following variables:
  - `LLM_PLATFORM = "SGLang"`
  - `LLM_AI_MODEL = "Qwen/Qwen3.5-35B-A3B-GPTQ-Int4"` (or local path)
  - API endpoint port is defined in `utils/llm_platforms.py` (default 30000 for SGLang).

- Server side settings:
- Conda environment: `sglang-env` 

```bash
conda activate sglang-env
CUDA_VISIBLE_DEVICES=0,1 python -m sglang.launch_server \
  --model-path Qwen/Qwen3.5-35B-A3B-GPTQ-Int4 \
  --port 30000 \
  --tp-size 2 \
  --mem-fraction-static 0.8 \
  --context-length 262144 \
  --reasoning-parser qwen3
```

## 2. Ollama service (Gemma 3 27B, GGUF Q4_K_M)

- Client-side settings:
- In `config.py`, set following variables:
  - `LLM_PLATFORM = "Ollama"`
  - `LLM_AI_MODEL = "hf.co/unsloth/gemma-3-27b-it-GGUF:Q4_K_M"`
  - API endpoint port is defined in `utils/llm_platforms.py` (default 11434 for Ollama).

- Server side settings:
- Note: `ollama service` is already running on `gpu02.sbms.hku.hk`, so there is no need to run `ollama run {model}` manually.
- Use API calls directly; the service will use the model set via `LLM_AI_MODEL` if already downloaded, or load it automatically on first request.
- Check downloaded models with:
  - `curl http://gpu02.sbms.hku.hk:11434/api/tags`

```bash
# List downloaded/available models (tags):
curl http://localhost:11434/api/tags

# After sending request for a specific 'LLM_AI_MODEL', check if it was loaded:
ollama ps
```

## 3. `sglang` server (DeepSeek R1 (quantized))

- Client-side settings:
- In `config.py`, set following variables:
  - `LLM_PLATFORM = "SGLang"`
  - `LLM_AI_MODEL = "neuralmagic/DeepSeek-R1-Distill-Qwen-32B-quantized.w4a16"`
  - API endpoint port is defined in `utils/llm_platforms.py` (default 30000 for SGLang).

- Server side settings:
Option A: Direct command (assumes correct `conda` env is already active, or run this from within `vllm` env):

```bash
CUDA_VISIBLE_DEVICES=${GPU_DEVICE:-2} python3 -m sglang.launch_server \
  --model neuralmagic/DeepSeek-R1-Distill-Qwen-32B-quantized.w4a16 \
  --context-length 131072 \
  --trust-remote-code \
  --host 0.0.0.0
```

Option B: Run helper script (activates the correct env inside):

```bash
./run_deepseek_sglang.sh
```

> Tip: `run_deepseek_sglang.sh` needs `CUDA_VISIBLE_DEVICES` set. If not set, the script defaults to GPU 2.
> 
> Ensure it is set explicitly when required, e.g. `export CUDA_VISIBLE_DEVICES=0`.
