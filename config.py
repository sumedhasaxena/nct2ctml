
GPU_SERVER_HOSTNAME = "http://gpu02.sbms.hku.hk"
LOCAL_AI_PORT = 49152
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