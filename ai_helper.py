import json
import config
import requests
import urllib.parse
import trial_data_helper as tdf
from loguru import logger

def get_level1_diagnosis_from_condition_keywords(nct_id:str, keywords: set, level1_oncotree: set) -> dict:    
    cancer_keywords_list = list(keywords)
    level1_oncotree_list = list(level1_oncotree) 
    
    prompt = get_ai_prompt_level1(cancer_keywords_list, level1_oncotree_list)
        
    ai_response = send_ai_request(nct_id, prompt)
    oncotree_diagnoses_dict = parse_ai_response(ai_response)
    return oncotree_diagnoses_dict

def get_level1_diagnosis_from_original_conditions(nct_id:str, original_conditions: dict, level1_oncotree: set) -> dict:    
    original_conditions_list = list(original_conditions)
    level1_oncotree_list = list(level1_oncotree) 
    
    prompt = get_ai_prompt_level1_for_original_conditions(original_conditions_list, level1_oncotree_list)
        
    ai_response = send_ai_request(nct_id, prompt)
    oncotree_diagnoses_dict = parse_ai_response(ai_response)
    return oncotree_diagnoses_dict

def get_child_level_diagnoses_from_condition(nct_id:str, child_nodes_oncotree:set, nct_condition: str) -> dict:

    child_nodes_oncotree_list = list(child_nodes_oncotree)

    prompt = get_ai_prompt_child_values(nct_condition, child_nodes_oncotree_list)

    ai_response = send_ai_request(nct_id, prompt)
    oncotree_diagnoses_dict = parse_ai_response(ai_response)   
    return oncotree_diagnoses_dict

def get_her2_er_pr_status(nct_id:str, eligibilityCriteria: str, keywords: list)-> dict:
    prompt = get_her2_er_pr_status_prompt(eligibilityCriteria, keywords)
    ai_response = send_ai_request(nct_id, prompt)
    her2_er_pr_status_dict = parse_ai_response(ai_response)   
    return her2_er_pr_status_dict

def get_pdl1_status(nct_id:str, eligibilityCriteria: str, keywords: list)-> dict:
    prompt = get_pdl1_status_prompt(eligibilityCriteria, keywords)
    ai_response = send_ai_request(nct_id, prompt)
    pdl1_status_dict = parse_ai_response(ai_response)   
    return pdl1_status_dict

def get_disease_status(nct_id:str, eligibilityCriteria: str, keywords: list)-> dict:
    prompt = get_disease_status_prompt(eligibilityCriteria, keywords)
    ai_response = send_ai_request(nct_id, prompt)
    disease_status_dict = parse_ai_response(ai_response)   
    return disease_status_dict

def get_genomic_criteria(nct_id:str, genes:list, eligibilityCriteria:str)-> dict:
    prompt = get_genomic_criteria_prompt(genes, eligibilityCriteria)
    ai_response = send_ai_request(nct_id, prompt)
    genomic_criteria_dict = parse_ai_response(ai_response)
    return genomic_criteria_dict

def parse_ai_response(ai_response):
    oncotree_diagnoses_dict = {}

    try:
        if type(ai_response) is dict and 'choices' in ai_response.keys() and type(ai_response['choices']) is list:
            answer = ai_response['choices'][0]
            ai_response_content = tdf.safe_get(answer,['message','content'])
            if ai_response_content:
                prefix_pos = ai_response_content.find('```json') #look for ```json in response string 
                if prefix_pos > -1:
                    begin_content = ai_response_content.find('```json')+len('```json')
                    end_content = ai_response_content.find('```', begin_content)
                    oncotree_diagnoses_response_string = ai_response_content[begin_content:end_content].strip()
                else:
                    prefix_pos = ai_response_content.find('</think>')# elseget everything after </think>
                    if prefix_pos > -1:
                        begin_content = ai_response_content.find('</think>')+len('</think>')
                        oncotree_diagnoses_response_string = ai_response_content[begin_content:].strip()
                    else:
                        oncotree_diagnoses_response_string = ai_response_content
                
                oncotree_diagnoses_dict = json.loads(oncotree_diagnoses_response_string)
    except json.JSONDecodeError as ex:
        logger.error(f"Unexpected response format: {ex=}, {type(ex)=}")
    return oncotree_diagnoses_dict

def send_ai_request(nct_id, prompt):
    req_body = {
    "model":config.AI_MODEL,
    "messages":[
        {"role": "system", "content": "You are a biomedical researcher."},
        {
          "role":"user", "content": prompt
        }
    ],
    "temperature": 0.5, #lower value of temperature results in more deterministric responses
    "max_tokens": 8192,
    "response_format": {
    "type": "json_object"
    },
    "stream":False
    }
    req_body_json = json.dumps(req_body)
    logger.debug(f"AI request | NCTID:{nct_id} | {req_body_json}")
    endpoint_url = f'{urllib.parse.urljoin(f"{config.GPU_SERVER_HOSTNAME}:{config.AI_PORT}", config.CHAT_ENDPOINT)}'

    response = requests.post(endpoint_url, data=req_body_json, headers={"Content-Type":"application/json"})
    response.raise_for_status()

    print(response.status_code)
    ai_response = response.json()
    logger.debug(f"AI response | NCTID:{nct_id} | {ai_response}")
    return ai_response

def get_ai_prompt_level1(cancer_keywords_list, level1_oncotree_list):
    prompt = f"""Task: Map the keywords of 'cancer conditions' to the types listed in 'Oncotree values' below.
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
    
    return prompt

def get_ai_prompt_level1_for_original_conditions(original_conditions_list, level1_oncotree_list):
    prompt = f"""Task: Map the list of 'cancer conditions' to the closest type listed in 'Oncotree values' below.
    Cancer conditions: {original_conditions_list}
    Oncotree values:{level1_oncotree_list}
    The output should be in the json format :
    {{
    "oncotree_diagnoses": [
        {{
        "cancer_condition": "",
        "oncotree_value": ""
        }}
    ]
    }}"""
    
    return prompt

def get_ai_prompt_child_values(nct_condition, child_nodes_oncotree_list):

    # cancer_condition: {nct_condition} E.g. -> Colorectal Cancer
    # Oncotree values: {child_nodes_oncotree} # E.g. -> {'Signet Ring Cell Adenocarcinoma of the Colon and Rectum', 'Colon Adenocarcinoma In Situ', 'Small Bowel Well-Differentiated Neuroendocrine Tumor', 'Gastrointestinal Neuroendocrine Tumors', 'Well-Differentiated Neuroendocrine Tumor of the Rectum', 'Small Bowel Cancer', 'Anal Squamous Cell Carcinoma', 'Anorectal Mucosal Melanoma', 'Low-grade Appendiceal Mucinous Neoplasm', 'Medullary Carcinoma of the Colon', 'Goblet Cell Adenocarcinoma of the Appendix', 'Mucinous Adenocarcinoma of the Appendix', 'Appendiceal Adenocarcinoma', 'Small Intestinal Carcinoma', 'Well-Differentiated Neuroendocrine Tumor of the Appendix', 'Signet Ring Cell Type of the Appendix', 'Colorectal Adenocarcinoma', 'High-Grade Neuroendocrine Carcinoma of the Colon and Rectum', 'Colonic Type Adenocarcinoma of the Appendix', 'Anal Gland Adenocarcinoma', 'Rectal Adenocarcinoma', 'Mucinous Adenocarcinoma of the Colon and Rectum', 'Duodenal Adenocarcinoma', 'Colon Adenocarcinoma', 'Tubular Adenoma of the Colon'}

    prompt = f"""
    Task: Map the cancer condition to the closest diagnoses from the list of 'Oncotree values' below.
    Cancer_condition: {nct_condition}
    Oncotree values: {child_nodes_oncotree_list}
    The output should be in the json format :
    {{
    "cancer_condition": "",
    "oncotree_diagnoses": []
    }}
    """
    return prompt

def get_her2_er_pr_status_prompt(eligibilityCriteria, keywords):
    prompt = f"""Task: From the eligibility criteria and the keywords mentioned below, find out if it mentions her2, pr or er status along with the required value (Positive/Negative/unknown).
         eligibilityCriteria: {eligibilityCriteria}
         keywords: {keywords}
         The output should be in the json format :
         {{
         "her2_status": "Positive/Negative/Unknown",
         "er_status": "Positive/Negative/Unknown",
         "pr_status": "Positive/Negative/Unknown"
         }}"""
         
    return prompt

def get_pdl1_status_prompt(eligibilityCriteria, keywords):
    prompt = f"""Task: From the eligibility criteria and the keywords mentioned below, find out if it mentions PDL1/PD-L1 status along with the required value (High/Low).
         eligibilityCriteria: {eligibilityCriteria}
         keywords: {keywords}
         The output should be in the json format :
         {{
         "pdl1_status": "High/Low/Unknown",
         }}"""
         
    return prompt

def get_disease_status_prompt(eligibilityCriteria, keywords):
    prompt = f"""Task: From the eligibility criteria and the keywords mentioned below, find out if it mentions disease status.
         The status can be from the following values: ['Untreated', 'Localized', 'Locally Advanced', 'Metastatic', 'Advanced', 'Recurrent', 'Refractory', 'Unresectable', "Early Stage"]
         eligibilityCriteria: {eligibilityCriteria}
         keywords: {keywords}
         The output should be in the json format :
         {{
         "disease_status": [],
         }}"""
         
    return prompt

def get_genomic_criteria_prompt(genes, eligibilityCriteria):
    prompt = f"""
    Task: Evaluate the clinical trial description against the provided gene list and variant categories to determine whether any mutations in the listed genes are included or excluded based on the eligibility criteria.

    Instructions:
    1. Identify if the clinical trial description mentions mutations in the given genes (inclusion) or specifies exclusions.
    2. Use the variant categories:
        Mutation
        Copy Number Variation
        Structural Variation
        Any Variation
        !Mutation
        !Copy Number Variation
        !Structural Variation
    
    Logic:
    1. If the genes are mentioned in trial's inlcusion criteria, use the 'or' operator along with appropriate variant categories.
    2. If the genes are mentioned in trial's exclusion criteria, use the 'and' operator along with variant categories (!Mutation/!Copy Number Variation/!Structural Variation).
    3. If applicable, combine inclusion and exclusion with a top level 'and' operator.
    
    Gene list: {genes}

    Clinical Trial Description: {eligibilityCriteria}

    Example A:
    Inclusion criteria:Subjects with advanced solid tumors harboring ROS1 or NTRK1 rearrangement will be included in this trial. 
    Output:
{{
    "or": [        
        {{
            "genomic": {{
                "hugo_symbol": "ROS1",
                "variant_category": "Structural Variation"
            }}
        }},
        {{
            "genomic": {{
                "hugo_symbol": "NTRK1",
                "variant_category": "Structural Variation"
            }}
        }}
    ]
}}

Example B:
Inclusion criteria:Patient should have mutation in geneA or geneB.
Exclusion criteria: Patient should not have a mutation in geneC or geneD

Output:
{{
    "and":[
        {{
            "or":[
                {{"genomic": {{"hugo_symbol": "geneA","variant_category": "Mutation"}}}},
                {{"genomic": {{"hugo_symbol": "geneB","variant_category": "Mutation"}}}}
            ]
        }},
        {{
            "and":[
                {{"genomic": {{"hugo_symbol": "geneC","variant_category": "!Mutation"}}}},
                {{"genomic": {{"hugo_symbol": "geneD","variant_category": "!Mutation"}}}}
            ]

        }}
    ]
}}

    """
    return prompt



def main():
    # cancer_keywords_list =  ["Colorectal","Hepatocellular"]    
    # level1_oncotree_list = ['Biliary Tract', 'Kidney', 'Myeloid', 'Skin', 'Soft Tissue', 'Pancreas', 'Bone', 'CNS/Brain', 'Peripheral Nervous System', 'Esophagus/Stomach', 'Prostate', 'Ovary/Fallopian Tube', 'Vulva/Vagina', 'Peritoneum', 'Adrenal Gland', 'Other', 'Bladder/Urinary Tract', 'Thyroid', 'Penis', 'Testis', 'Liver', 'Uterus', 'Head and Neck', 'Ampulla of Vater', 'Cervix', 'Bowel', 'Eye', 'Thymus', 'Breast', 'Pleura', 'Lymphoid', 'Lung']
    
    # get_level1_diagnosis_from_condition_keywords("",set(cancer_keywords_list),set(level1_oncotree_list))

    nct_condition = 'Colorectal Cancer'
    child_nodes_oncotree_list = ['Signet Ring Cell Adenocarcinoma of the Colon and Rectum', 'Colon Adenocarcinoma In Situ', 'Small Bowel Well-Differentiated Neuroendocrine Tumor', 'Gastrointestinal Neuroendocrine Tumors', 'Well-Differentiated Neuroendocrine Tumor of the Rectum', 'Small Bowel Cancer', 'Anal Squamous Cell Carcinoma', 'Anorectal Mucosal Melanoma', 'Low-grade Appendiceal Mucinous Neoplasm', 'Medullary Carcinoma of the Colon', 'Goblet Cell Adenocarcinoma of the Appendix', 'Mucinous Adenocarcinoma of the Appendix', 'Appendiceal Adenocarcinoma', 'Small Intestinal Carcinoma', 'Well-Differentiated Neuroendocrine Tumor of the Appendix', 'Signet Ring Cell Type of the Appendix', 'Colorectal Adenocarcinoma', 'High-Grade Neuroendocrine Carcinoma of the Colon and Rectum', 'Colonic Type Adenocarcinoma of the Appendix', 'Anal Gland Adenocarcinoma', 'Rectal Adenocarcinoma', 'Mucinous Adenocarcinoma of the Colon and Rectum', 'Duodenal Adenocarcinoma', 'Colon Adenocarcinoma', 'Tubular Adenoma of the Colon']
    get_child_level_diagnoses_from_condition("", set(child_nodes_oncotree_list), nct_condition)



if __name__ == "__main__":
    main()
