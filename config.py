
GPU_SERVER_HOSTNAME = "http://gpu02.sbms.hku.hk"
#Local_ai
#AI_PORT = 49152
#CHAT_ENDPOINT = "chat/completions"

#vllm
#AI_PORT = 8000
#CHAT_ENDPOINT = "v1/chat/completions"

#SGLang
AI_PORT = 30000
CHAT_ENDPOINT = "v1/chat/completions"

#AI_MODEL = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
#AI_MODEL = "deepseek-ai/DeepSeek-R1-Distill-Llama-8B"
AI_MODEL = "neuralmagic/DeepSeek-R1-Distill-Qwen-32B-quantized.w4a16"

ONCOTREE_TXT_FILE_PATH = "ref/oncotree_file.txt"
GENE_LIST_FILE_PATH = "ref/genes.txt"



# List of words to remove
keywords_to_remove = {"cancer", 
                      "advanced", 
                      "neoplasms",
                      "neoplasm",
                      "or", 
                      "and",
                      "melanoma"
                      "metastatic", 
                      "carcinoma",
                      "tumor",
                      "tumors",
                      "limited",
                      "stage",
                      "Advanced",
                      "Acute"
                      }

intervention_types = ['DRUG','BIOLOGICAL','COMBINATION_PRODUCT']