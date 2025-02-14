import json
import config
import requests
import urllib.parse


AI_MODEL = "qwen2.5-coder-1.5b-instruct"

CHAT_ENDPOINT = "chat/completions"

def get_level1_diagnosis_from_condition_keywords(nct_id:str, keywords: set, level1_oncotree: set):    
    #cancer_keywords_list = list(keywords)
    #level1_oncotree_list = list(level1_oncotree) 
    cancer_keywords_list =  ["Colorectal","Hepatocellular"]    
    level1_oncotree_list = ['Biliary Tract', 'Kidney', 'Myeloid', 'Skin', 'Soft Tissue', 'Pancreas', 'Bone', 'CNS/Brain', 'Peripheral Nervous System', 'Esophagus/Stomach', 'Prostate', 'Ovary/Fallopian Tube', 'Vulva/Vagina', 'Peritoneum', 'Adrenal Gland', 'Other', 'Bladder/Urinary Tract', 'Thyroid', 'Penis', 'Testis', 'Liver', 'Uterus', 'Head and Neck', 'Ampulla of Vater', 'Cervix', 'Bowel', 'Eye', 'Thymus', 'Breast', 'Pleura', 'Lymphoid', 'Lung']

    prompt_level1 = f"""Task: Map the keywords of 'cancer conditions' to the types listed in 'Oncotree values' below.
    Cancer conditions: {cancer_keywords_list}
    Oncotree values:{level1_oncotree_list}
    The output should be in the json format :
    {{
    "oncotree_diagnoses": [
        {{
        "cancer_condition_keyword": "",
        "oncotree_value": ""
        }}
    ]
    }}"""
        
    req_body = {
    "model":AI_MODEL,
    "messages":[
        {
          "role":"system",
          "content": prompt_level1
        }
    ],
    "stream":False
    }
    req_body_json = json.dumps(req_body)
    endpoint_url = f'{urllib.parse.urljoin(f"{config.GPU_SERVER_HOSTNAME}:{config.LOCAL_AI_PORT}", CHAT_ENDPOINT)}'

    response = requests.post(endpoint_url, data=req_body_json, headers={"Content-Type":"application/json"})

    print(response.status_code)
    print(response.json())
   

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

#def get_her2_er_pr_status(nct_id:str, eligibilityCriteria: str):
      # Prompt:
      
        # Task: From the eligibility criteria mentioned below, find out if it mentions Her2, pr or er status along with the required value (positive/negative/unknown).

        # eligibilityCriteria: 
        # Inclusion Criteria:\n\n1. Capable of giving signed informed consent prior to any study procedure.\n2. Participant must be at least 18 years or the legal age of consent in the jurisdiction in which the study is taking place at the time of signing the ICF.\n3. Histologically confirmed unresectable, locally advanced or metastatic adenocarcinoma of gastric, GEJ, or distal esophagus (distal third of the esophagus) and the following requirement:\n\n   (a) Participants with positive CLDN18.2 expression from archival tumor collected within past 24 months or from a fresh biopsy.\n4. Disease progression on or after at least one prior line of treatment (LoT) for advanced or metastatic disease, which included a fluoropyrimidine and a platinum, for advanced or metastatic disease.\n5. Must have at least one measurable or evaluable lesion assessed by the Investigator based on RECIST 1.1.\n6. ECOG performance status of 0 or 1 with no deterioration over the previous 2 weeks prior to baseline or day of first dosing.\n7. Predicted life expectancy of \u2265 12 weeks.\n8. Adequate organ and bone marrow function\n9. Body weight of \u2265 35 kg.\n10. Sex and Contraceptive Requirements\n\nExclusion Criteria:\n\n1. Participants with known HER2 positive status as defined as IHC 3+ or IHC 2+/ISH + (Cases with HER2: CEP17 ratio \u2265 2 or an average HER2 copy number \u2265 6.0 signals/cell are considered positive by ISH). Participants must undergo local (or have had) HER2 testing by IHC/ISH, and the most recent result of HER2 status will be used to determine the eligibility.\n2. Participant has significant or unstable gastric bleeding and/or untreated gastric ulcers.\n3. CNS metastases or CNS pathology including: epilepsy, seizures, aphasia, or stroke within 3 months prior to consent, severe brain injury, dementia, Parkinson's disease, neurodegenerative diseases, cerebellar disease, severe uncontrolled mental illness, psychosis, CNS involvement of autoimmune diseases.\n4. Participant has known clinically significant corneal disease (eg, active keratitis or corneal ulcerations).\n5. Persistent toxicities (CTCAE Grade \u2265 2) caused by previous anticancer therapy, excluding alopecia. Participants with irreversible toxicity that is not reasonably expected to be exacerbated by study intervention may be included (eg, hearing loss).\n6. Prior exposure to any ADC with MMAE payload or any CLDN18.2 targeting treatment other than naked monoclonal antibody (eg, CLDN18.2 targeting CAR-T cell therapy, multi-specific antibody including targeting CLDN18.2, etc)."

        # The output should be in the json format :

        # {
        # "her2_status": "Positive/Negative/Unknown",
        # "er_status": "Positive/Negative/Unknown",
        # "pr_status": "Positive/Negative/Unknown"

        # }

def main():
    get_level1_diagnosis_from_condition_keywords("",set(),set())


if __name__ == "__main__":
    main()
