
#GPU_SERVER_HOSTNAME = "http://gpu02.sbms.hku.hk"
#GPU_SERVER_HOSTNAME = "http://127.0.0.1"
GPU_SERVER_HOSTNAME = "http://localhost"

#LLM_PLATFORM = "Ollama"  # Options: Local_ai, vllm, SGLang, Ollama
LLM_PLATFORM = "SGLang"

# deepseek library
#LLM_AI_MODEL = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
#LLM_AI_MODEL = "deepseek-ai/DeepSeek-R1-Distill-Llama-8B"
LLM_AI_MODEL = "neuralmagic/DeepSeek-R1-Distill-Qwen-32B-quantized.w4a16"

# gemma library
#LLM_AI_MODEL = "hf.co/unsloth/gemma-4-31B-it-GGUF:UD-Q4_K_XL"
#LLM_AI_MODEL = "cyankiwi/gemma-4-31B-it-AWQ-4bit"
#LLM_AI_MODEL = "gemma4:31b" # from official ollama library instead of hugging face
#LLM_AI_MODEL = "gemma4:26b" # from official ollama library instead of hugging face
#LLM_AI_MODEL = "hf.co/unsloth/medgemma-27b-text-it-GGUF:Q4_K_M"
#LLM_AI_MODEL = "hf.co/unsloth/gemma-3-27b-it-GGUF:Q4_K_M"
#LLM_AI_MODEL = "hf.co/bartowski/gemma-2-27b-it-GGUF:Q4_K_M"

# Qwen library
#LLM_AI_MODEL = "Qwen/Qwen3.5-35B-A3B-GPTQ-Int4"
#LLM_AI_MODEL = "Qwen/Qwen3.6-27B-FP8"
#LLM_AI_MODEL = "qwen3.6:27b" # from official ollama library instead of hugging face
#LLM_AI_MODEL = "qwen3.6:35b" # from official ollama library instead of hugging face

# GLM library
#LLM_AI_MODEL = "hf.co/mradermacher/GLM-4-32B-0414-GGUF:Q4_K_M"
#LLM_AI_MODEL = "hf.co/lmstudio-community/GLM-Z1-32B-0414-GGUF:Q4_K_M"

# moonshotai library
#LLM_AI_MODEL = "moonshotai/Moonlight-16B-A3B-Instruct"
#LLM_AI_MODEL = "hf.co/mmnga/Moonlight-16B-A3B-Instruct-gguf:Q8_0"

# minimax library
#LLM_AI_MODEL = "hf.co/mradermacher/SynLogic-32B-GGUF:Q4_K_M"



ONCOTREE_TXT_FILE_PATH = "ref/oncotree_file.txt"
GENE_LIST_FILE_PATH = "ref/genes.txt"

# Mapping configuration
# Number of days back to consider for mapping trials
# Trials with entry_last_updated_date within this many days will be mapped
MAPPING_CUTOFF_DAYS = 1