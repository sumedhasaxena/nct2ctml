import json


AI_MODEL = ""

LOCAL_AI_URL = "Lab GPU server:port"
ENDPOINT = "chat/completions"

def get_level1_diagnosis_from_condition_keywords(nct_id:str, keywords: set, level1_oncotree: set) -> dict:

    # Prompt:
    # Task: Map the keywords of 'cancer conditions' to the types listed in 'Oncotree values' below.
    # cancer conditions: {keywords}
    # E.g. -> {'Colorectal', 'Hepatocellular'}

    # Oncotree values:
    # level1_oncotree: {level1_oncotree}
    # E.g. -> {'Biliary Tract', 'Kidney', 'Myeloid', 'Skin', 'Soft Tissue', 'Pancreas', 'Bone', 'CNS/Brain', 'Peripheral Nervous System', 'Esophagus/Stomach', 'Prostate', 'Ovary/Fallopian Tube', 'Vulva/Vagina', 'Peritoneum', 'Adrenal Gland', 'Other', 'Bladder/Urinary Tract', 'Thyroid', 'Penis', 'Testis', 'Liver', 'Uterus', 'Head and Neck', 'Ampulla of Vater', 'Cervix', 'Bowel', 'Eye', 'Thymus', 'Breast', 'Pleura', 'Lymphoid', 'Lung'}

    # The output should be in the json format :
    # {
    # "oncotree_diagnoses": [
    #     {
    #     "cancer_condition": "",
    #     "oncotree_value": ""
    #     },
    #     {
    #     "cancer_condition": "",
    #     "oncotree_value": ""
    #     }
    # ]
    # }

    ## for now, get the mock response
    level1_oncotree_values_dict = {}
    file_path = f"results/AI/{nct_id}_level1.json"
    with open(file_path, 'r') as json_file:
            level1_oncotree_values_dict = json.load(json_file)
    return level1_oncotree_values_dict

def get_child_level_diagnoses_from_condition(nct_id:str, child_nodes_oncotree:set, nct_condition: str) -> dict:

    # Prompt:
    # Task: Map the cancer condition to the closest diagnoses from the ist of 'Oncotree values' below.

    # cancer_condition: {nct_condition} E.g. -> Colorectal Cancer

    # Oncotree values: {child_nodes_oncotree}
    # E.g. -> {'Signet Ring Cell Adenocarcinoma of the Colon and Rectum', 'Colon Adenocarcinoma In Situ', 'Small Bowel Well-Differentiated Neuroendocrine Tumor', 'Gastrointestinal Neuroendocrine Tumors', 'Well-Differentiated Neuroendocrine Tumor of the Rectum', 'Small Bowel Cancer', 'Anal Squamous Cell Carcinoma', 'Anorectal Mucosal Melanoma', 'Low-grade Appendiceal Mucinous Neoplasm', 'Medullary Carcinoma of the Colon', 'Goblet Cell Adenocarcinoma of the Appendix', 'Mucinous Adenocarcinoma of the Appendix', 'Appendiceal Adenocarcinoma', 'Small Intestinal Carcinoma', 'Well-Differentiated Neuroendocrine Tumor of the Appendix', 'Signet Ring Cell Type of the Appendix', 'Colorectal Adenocarcinoma', 'High-Grade Neuroendocrine Carcinoma of the Colon and Rectum', 'Colonic Type Adenocarcinoma of the Appendix', 'Anal Gland Adenocarcinoma', 'Rectal Adenocarcinoma', 'Mucinous Adenocarcinoma of the Colon and Rectum', 'Duodenal Adenocarcinoma', 'Colon Adenocarcinoma', 'Tubular Adenoma of the Colon'}

    # The output should be in the json format :
    # {
    # "cancer_condition": "",
    # "oncotree_diagnoses": []
    # }
    oncotree_diagnoses = {}

    file_path = f"results/AI/{nct_id}_leaf.json"
    with open(file_path, 'r') as json_file:
            oncotree_diagnoses = json.load(json_file)
    return oncotree_diagnoses
