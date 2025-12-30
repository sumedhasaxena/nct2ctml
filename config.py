
#GPU_SERVER_HOSTNAME = "http://gpu02.sbms.hku.hk"
#GPU_SERVER_HOSTNAME = "http://127.0.0.1"
GPU_SERVER_HOSTNAME = "http://localhost"

LLM_PLATFORM = "Ollama"  # Options: Local_ai, vllm, SGLang, Ollama
#LLM_PLATFORM = "SGLang"

#LLM_AI_MODEL = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
#LLM_AI_MODEL = "deepseek-ai/DeepSeek-R1-Distill-Llama-8B"
#LLM_AI_MODEL = "neuralmagic/DeepSeek-R1-Distill-Qwen-32B-quantized.w4a16"
#LLM_AI_MODEL = "hf.co/unsloth/medgemma-27b-text-it-GGUF:Q4_K_M"
LLM_AI_MODEL = "hf.co/unsloth/gemma-3-27b-it-GGUF:Q4_K_M"
#LLM_AI_MODEL = "hf.co/bartowski/gemma-2-27b-it-GGUF:Q4_K_M"

ONCOTREE_TXT_FILE_PATH = "ref/oncotree_file.txt"
GENE_LIST_FILE_PATH = "ref/genes.txt"

# Mapping configuration
# Number of days back to consider for mapping trials
# Trials with entry_last_updated_date within this many days will be mapped
MAPPING_CUTOFF_DAYS = 1