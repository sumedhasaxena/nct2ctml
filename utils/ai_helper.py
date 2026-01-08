import json
import config
import requests
import urllib.parse
import utils.schema as schema
from loguru import logger
from utils.llm_platforms import create_llm_platform

# Initialize the LLM platform based on config
_llm_platform = create_llm_platform(
    platform_name=config.LLM_PLATFORM,
    model=config.LLM_AI_MODEL,
    hostname=config.GPU_SERVER_HOSTNAME
)

def get_level1_diagnosis_from_original_conditions(nct_id:str, original_conditions: dict, level1_oncotree: set) -> dict:    
    original_conditions_list = list(original_conditions)
    level1_oncotree_list = list(level1_oncotree) 
    
    prompt = get_ai_prompt_level1_for_original_conditions(original_conditions_list, level1_oncotree_list)


    logger.debug(f"NCTID: {nct_id} | AI Prompt for Level 1 diagnosis from original conditions: {prompt}")
        
    ai_response = send_ai_request(nct_id, prompt)
    oncotree_diagnoses_dict = parse_ai_response(ai_response)
    return oncotree_diagnoses_dict

def get_level1_diagnosis_from_original_extra_info(nct_id:str, extra_info: list, level1_oncotree: set) -> dict:    
    level1_oncotree_list = list(level1_oncotree) 
    
    prompt = get_ai_prompt_level1_from_supporting_info(extra_info, level1_oncotree_list)
        
    ai_response = send_ai_request(nct_id, prompt)
    oncotree_diagnoses_dict = parse_ai_response(ai_response)
    return oncotree_diagnoses_dict

def get_child_level_diagnoses_from_extra_info(nct_id:str, combined_child_nodes_oncotree:set, extra_info: set) -> dict:

    combined_child_nodes_oncotree_list = list(combined_child_nodes_oncotree)

    prompt = get_ai_prompt_child_values_from_supporting_info(extra_info, combined_child_nodes_oncotree_list)

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

def get_mmr_status(nct_id:str, eligibilityCriteria: str, keywords: list)-> dict:
    prompt = get_mmr_status_prompt(eligibilityCriteria, keywords)
    ai_response = send_ai_request(nct_id, prompt)
    mmr_status_dict = parse_ai_response(ai_response)   
    return mmr_status_dict

def get_disease_status(nct_id:str, eligibilityCriteria: str, keywords: list)-> dict:
    prompt = get_disease_status_prompt(eligibilityCriteria, keywords)
    ai_response = send_ai_request(nct_id, prompt)
    disease_status_dict = parse_ai_response(ai_response)   
    return disease_status_dict

def get_genomic_criteria(nct_id:str, genes:list, eligibilityCriteria:str)-> dict:
    json_schema, prompt = get_genomic_criteria_prompt(genes, eligibilityCriteria)
    ai_response = send_ai_request(nct_id, prompt, json_schema)
    genomic_criteria_dict = parse_ai_response(ai_response)
    return genomic_criteria_dict

def parse_ai_response(ai_response):
    return _llm_platform.parse_response(ai_response)

def send_ai_request(id, prompt, json_schema=None):
    """Send AI request using the configured platform."""
    req_body = _llm_platform.get_request_body(prompt, json_schema)
    req_body_json = json.dumps(req_body)
    logger.debug(f"AI request | ID:{id} | {req_body_json}")
    endpoint_url = _llm_platform.get_endpoint_url()
    print(endpoint_url)

    response = requests.post(endpoint_url, data=req_body_json, headers={"Content-Type":"application/json"})
    print(response)
    response.raise_for_status()

    print(response.status_code)
    ai_response = response.json()
    logger.debug(f"AI response | ID:{id} | {ai_response}")
    return ai_response

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

def get_ai_prompt_level1_from_supporting_info(trial_info, level1_oncotree_list):
    prompt = f"""Task: From the trial information, try to get the closest oncotree values that might define the diagnosis this trial is looking for.
    Trial information: {trial_info}
    Oncotree values:{level1_oncotree_list}
    The output should be in the json format :
    {{
    "oncotree_diagnoses": []
    }}"""
    
    return prompt

def get_ai_prompt_child_values_from_supporting_info(extra_info:set, child_nodes_oncotree_list):
    prompt = f"""
    Task: Map the trial info to the closest diagnoses from the list of 'Oncotree values' below.
    Trial Info: {extra_info}
    Oncotree values: {child_nodes_oncotree_list}
    The output should be in the json format :
    {{    
    "oncotree_diagnoses": []
    }}
    """
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
    prompt = f"""Task: From the eligibility criteria and the keywords mentioned below, find out if it mentions her2, pr or er status along with the required value. The value should be one of the listed allowed values.
         The '!' operator should be used if the criteria excludes a particular status.
         Allowed values: ['Positive', 'Negative', 'Unknown','!Positive','!Negative']
         eligibilityCriteria: {eligibilityCriteria}
         keywords: {keywords}
         The output should be in the json format :
         {{
         "her2_status": "value",
         "er_status": "value",
         "pr_status": "value"
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

def get_mmr_status_prompt(eligibilityCriteria, keywords):
    prompt = f"""Task: From the eligibility criteria and the keywords mentioned below, find out if it mentions MMR/MS status along with the value closen the below mentioned list of allowed values.
    Return empty JSON if the text does not talk about mismatch repair or microsatellite instability.
    Allowed values:
    mmr_status: ['MMR-Proficient', 'MMR-Deficient']
    ms_status: ['MSI-H', 'MSI-L', 'MSS']

    eligibilityCriteria: {eligibilityCriteria}
    keywords: {keywords}
    The output should be in the json format :
    {{
    "mmr_status": "MMR-Deficient",
    "ms_status": "MSI-H"
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
    1. If the genes are mentioned in trial's inclusion criteria, use the 'or' operator along with appropriate variant categories.
    2. If the genes are mentioned in trial's exclusion criteria, use the 'and' operator along with variant categories (!Mutation/!Copy Number Variation/!Structural Variation).
    3. If applicable, combine inclusion and exclusion with a top level 'and' operator.
        
    Potential gene list: {genes}

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
                "variant_category": "Mutation"
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
    return None, prompt

def safe_get(dict_data, keys):
    for key in keys:
        dict_data = dict_data.get(key, {})
    return dict_data