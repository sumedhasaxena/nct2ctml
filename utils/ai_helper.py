import json
import config
import requests
import urllib.parse
import utils.schema as schema
from inspect import cleandoc
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

def get_inclusion_genomic_criteria(nct_id:str, genes:list, eligibilityCriteria:str)-> list:
    json_schema, prompt = get_inclusion_genomic_criteria_prompt(genes, eligibilityCriteria)
    ai_response = send_ai_request(nct_id, prompt, json_schema)
    genomic_criteria = parse_ai_response(ai_response)
    return genomic_criteria

def get_exclusion_genomic_criteria(nct_id:str, genes:list, eligibilityCriteria:str)-> list:
    json_schema, prompt = get_exclusion_genomic_criteria_prompt(genes, eligibilityCriteria)
    ai_response = send_ai_request(nct_id, prompt, json_schema)
    genomic_criteria = parse_ai_response(ai_response)
    return genomic_criteria

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
    prompt = f"""Task: Map CancerConditions to the closest cancer type in OncotreeValues.
        CancerConditions: {original_conditions_list}
        OncotreeValues: {level1_oncotree_list}
        Output in JSON format:
        {{
        "oncotree_diagnoses": [
            {{
            "cancer_condition": "",
            "oncotree_value": ""
            }}
        ]
        }}"""
    return cleandoc(prompt)

def get_ai_prompt_level1_from_supporting_info(trial_info, level1_oncotree_list):
    prompt = f"""Task: From the TrialInfo, extract the closest OncotreeValues corresponding to the medical conditions the trial is recruiting for.
        TrialInfo: {trial_info}
        OncotreeValues: {level1_oncotree_list}
        Output in JSON format:
        {{
        "oncotree_diagnoses": []
        }}"""
    
    return cleandoc(prompt)

def get_ai_prompt_child_values_from_supporting_info(extra_info:set, child_nodes_oncotree_list):
    prompt = f"""
        Task: Map TrialInfo to the closest cancer diagnoses in OncotreeValues.
        TrialInfo: {extra_info}
        OncotreeValues: {child_nodes_oncotree_list}
        Output in JSON format:
        {{    
        "oncotree_diagnoses": []
        }}
        """
    return cleandoc(prompt)

def get_ai_prompt_child_values(nct_condition, child_nodes_oncotree_list):

    # cancer_condition: {nct_condition} E.g. -> Colorectal Cancer
    # Oncotree values: {child_nodes_oncotree} # E.g. -> {'Signet Ring Cell Adenocarcinoma of the Colon and Rectum', 'Colon Adenocarcinoma In Situ', 'Small Bowel Well-Differentiated Neuroendocrine Tumor', 'Gastrointestinal Neuroendocrine Tumors', 'Well-Differentiated Neuroendocrine Tumor of the Rectum', 'Small Bowel Cancer', 'Anal Squamous Cell Carcinoma', 'Anorectal Mucosal Melanoma', 'Low-grade Appendiceal Mucinous Neoplasm', 'Medullary Carcinoma of the Colon', 'Goblet Cell Adenocarcinoma of the Appendix', 'Mucinous Adenocarcinoma of the Appendix', 'Appendiceal Adenocarcinoma', 'Small Intestinal Carcinoma', 'Well-Differentiated Neuroendocrine Tumor of the Appendix', 'Signet Ring Cell Type of the Appendix', 'Colorectal Adenocarcinoma', 'High-Grade Neuroendocrine Carcinoma of the Colon and Rectum', 'Colonic Type Adenocarcinoma of the Appendix', 'Anal Gland Adenocarcinoma', 'Rectal Adenocarcinoma', 'Mucinous Adenocarcinoma of the Colon and Rectum', 'Duodenal Adenocarcinoma', 'Colon Adenocarcinoma', 'Tubular Adenoma of the Colon'}

    prompt = f"""
        Task: Map CancerCondition to the closest cancer diagnoses in OncotreeValues.
        CancerCondition: {nct_condition}
        OncotreeValues: {child_nodes_oncotree_list}

        Output in JSON format:
        {{
        "cancer_condition": "",
        "oncotree_diagnoses": []
        }}
        """
    return cleandoc(prompt)

def get_her2_er_pr_status_prompt(eligibilityCriteria, keywords):
    prompt = f"""
        Task: From the EligibilityCriteria and TrialKeywords, return the required Her2, PR or ER status.
        Use the '!' operator if the criteria excludes a status.
        EligibilityCriteria: {eligibilityCriteria}
        TrialKeywords: {keywords}

        Output in JSON format:
        {{
        "her2_status": "value",
        "er_status": "value",
        "pr_status": "value"
        }}
        where "value" must be in ["Positive", "Negative", "Unknown", "!Positive", "!Negative"]
        """
    return cleandoc(prompt)

def get_pdl1_status_prompt(eligibilityCriteria, keywords):
    prompt = f"""
        Task: From the EligibilityCriteria and TrialKeywords, return the required PDL1 (PD-L1) status.
        EligibilityCriteria: {eligibilityCriteria}
        TrialKeywords: {keywords}

        Output in JSON format:
        {{
        "pdl1_status": "value",
        }}
        where "value" is in ["High", "Low", "Unknown"].
        """
    return cleandoc(prompt)

def get_mmr_status_prompt(eligibilityCriteria, keywords):
    prompt = f"""
        Task: From the EligibilityCriteria and TrialKeywords, return the required mismatch repair (MMR) and/or microsatellite (MS) status;
        return an empty JSON if the text does not mention MMR or MS status.
        EligibilityCriteria: {eligibilityCriteria}
        TrialKeywords: {keywords}

        Output in JSON format:
        {{
        "mmr_status": "value1",
        "ms_status": "value2"
        }}
        where "value1" is in ["MMR-Proficient", "MMR-Deficient",'!MMR-Proficient', '!MMR-Deficient']. 
        and "value2" is in ['MSI-H', 'MSI-L', 'MSS','!MSI-H', '!MSI-L'].
        """
    return cleandoc(prompt)

def get_disease_status_prompt(eligibilityCriteria, keywords):
    prompt = f"""Task: From the EligibilityCriteria and TrialKeywords, return the required disease statuses of the cancer.
        EligibilityCriteria: {eligibilityCriteria}
        TrialKeywords: {keywords}

        Output in JSON format:
        {{
        "disease_status": [],
        }}
        where each disease_status is in ["Untreated", "Localized", "Locally Advanced", "Metastatic", "Advanced", "Recurrent", "Refractory", "Unresectable", "Early Stage"].
        """
    return cleandoc(prompt)

# a lot of trial criteria mention exclusion too in inclusion criteria hence the prompt supplies both inclusion and exclusion instructions
def get_inclusion_genomic_criteria_prompt(genes, inclusion_criteria):
    prompt = f"""Task: Evaluate the clinical trial criteria to return a JSON-formatted eligibility criteria involving genetic variants in any genes such as those in the GeneList.
    EligibilityCritieria: {inclusion_criteria}
    Possible GeneList: {genes}

    Output in JSON format such that:
    1. "variant_category" must be in ["Mutation", "Copy Number Variation", "Structural Variation", "Any Variation","!Mutation", "!Copy Number Variation", "!Structural Variation", "!Any Variation"],
       where "Mutation" is defined narrowly to include only single nucleotide variants (SNVs) and indels.
    2. If a specific amino acid substitution is required, return this in the "protein_change" field.
    3. In EligibilityCriteria, the term "mutant" means "Any Variation"
    4. Include any genes that may not be present in the provided GeneList if they are clearly indicated in the criteria.

    Example 1:
    Criteria: Subjects with advanced solid tumors harboring NTRK1 rearrangement or KRAS G12C will be included in this trial. 
    Output:
    [
        {{
            "genomic": {{
                "hugo_symbol": "NTRK1",
                "variant_category": "Structural Variation"
            }}
        }},
        {{
            "genomic": {{
                "hugo_symbol": "KRAS",
                "variant_category": "Mutation",
                "protein_change": "p.G12C"
            }}
        }}
    ]

    Example 2:
    Criteria: Any solid tumor type with MET amplification and negative test results for epidermal growth factor receptor (EGFR) and proto-oncogene1 (ROS1) actionable genomic alterations based on analysis of tumor tissue.
    Output:
    [
        {{
            "genomic": {{
                "hugo_symbol": "MET",
                "variant_category": "Copy Number Variation"
            }}
        }},
        {{
            "genomic": {{
                "hugo_symbol": "EGFR",
                "variant_category": "!Any Variation"
            }}
        }},
        {{
            "genomic": {{
                "hugo_symbol": "ROS1",
                "variant_category": "!Any Variation"
            }}
        }}
    ]
    """
    json_schema = None # Define JSON schema if needed. It will be injected in teh request body to LLM
    return json_schema, cleandoc(prompt)

def get_exclusion_genomic_criteria_prompt(genes, exclusion_criteria):
    prompt = f"""Task: Evaluate the clinical trial exclusion criteria to return a JSON-formatted eligibility criteria involving genetic variants in any genes such as those in the GeneList.
    EligibilityCritieria: {exclusion_criteria}
    Possible GeneList: {genes}

    Output in JSON format such that:
    1. "variant_category" must be in ["!Mutation", "!Copy Number Variation", "!Structural Variation", "!Any Variation"],
       where "Mutation" is defined narrowly to include only single nucleotide variants (SNVs) and indels.
    2. If a specific amino acid substitution is required, return this in the "protein_change" field.
    3. In EligibilityCriteria, the term "mutant" means "Any Variation".    
    4. Include any genes that may not be present in the provided GeneList if they are clearly indicated in the criteria.

    Example 1:
    Criteria: Exclude - Patients who have EGFR, ALK or ROS1 driver mutations
    Output:
    [
        {{
            "genomic": {{
                "hugo_symbol": "EGFR",
                "variant_category": "!Any Variation"
            }}
        }},
        {{
            "genomic": {{
                "hugo_symbol": "ALK",
                "variant_category": "!Any Variation"
            }}
        }},
        {{
            "genomic": {{
                "hugo_symbol": "ROS1",
                "variant_category": "!Any Variation"
            }}
        }}
    ]

    """
    json_schema = None # Define JSON schema if needed. It will be injected in teh request body to LLM
    return json_schema, cleandoc(prompt)

def safe_get(dict_data, keys):
    for key in keys:
        dict_data = dict_data.get(key, {})
    return dict_data
