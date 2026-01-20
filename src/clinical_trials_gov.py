"""
This script contains methods that deal with extraction and manipulation
of data from clinicaltrials.gov
"""
import sys
import os
import csv
from typing import Dict, List

sys.path.append(os.path.abspath('../'))

import src.trial_config as config
import requests
import urllib.parse
import src.ctml_schema as cs
import utils.ai_helper as ai
import src.trial_data_helper as tdh
import utils.oncotree as onct
import src.trial_criteria_to_genes as ctg
import src.match_criteria_mapper as mcm
from loguru import logger


def map_nct_to_ctml(trial_data: dict, genes:list, gene_synonym_mapping: Dict[str, List[str]]) -> dict:
    """
    Logic to map the fields from https://clinicaltrials.gov/ API response to the clinical trial schema required by matchminer
    Parameters
    ----------
    trial_data: dict
        Dictionary containing the response from https://clinicaltrials.gov/ API for a particular trial

    Returns
    -------
    trial_schema: dict
        Dictionary containing the keys and values for a trial as per the clinical trial schema for matchminer
    """

    trial_schema = cs.get_ctml_schema()

    trial_schema = map_ctml_general_fields(trial_schema, trial_data)   

    trial_schema = map_prior_treatment_requirements(trial_schema, trial_data)

    clinical_ctml = map_ctml_match_clinical_criteria(trial_data)
    genomic_ctml = map_ctml_match_genomic_criteria(trial_data, gene_synonym_mapping)
    match_result = mcm.combine_clinical_and_genomic_ctml(clinical_ctml, genomic_ctml)
    match_list = trial_schema['treatment_list']['step'][0]['match']
    match_list.append(match_result)
    logger.debug(f"CTML: After mapping clinical and genomic match criteria | {trial_schema}")

    return trial_schema

def map_ctml_general_fields(trial_schema, trial_data) -> dict:

    nct_id = trial_data['protocolSection']['identificationModule']['nctId']

    try:    
        trial_schema['nct_id'] = nct_id
        trial_schema['long_title'] = trial_data['protocolSection']['identificationModule']['officialTitle']
        trial_schema['principal_investigator_institution'] = trial_data['protocolSection']['identificationModule']['organization']['fullName']
        trial_schema['principal_investigator'] = 'NA' # overwrriten later if a PI is found in overall officials list

        phases = trial_data['protocolSection']['designModule']['phases']
        trial_schema['phase'] = phases[0] if len(phases) > 0 else ''
        trial_schema['short_title'] = trial_data['protocolSection']['identificationModule']['briefTitle']
        trial_schema['summary'] = trial_data['protocolSection']['descriptionModule']['briefSummary']
        trial_schema['protocol_target_accrual'] = trial_data['protocolSection']['designModule']['enrollmentInfo']['count']
        trial_schema['sponsor_list']['sponsor'].append(
            {
                'is_principal_sponsor': 'Y',
                'sponsor_name':trial_data['protocolSection']['sponsorCollaboratorsModule']['leadSponsor']['name'],
                'sponsor_protocol_no':'',
                'sponsor_roles': 'sponsor'
            }
        )

        trial_schema['curated_on'] = trial_data['protocolSection']['statusModule']['studyFirstPostDateStruct']['date']
        trial_schema['last_updated'] = trial_data['protocolSection']['statusModule']['lastUpdatePostDateStruct']['date']

        start_date_struct = tdh.safe_get(trial_data, ['protocolSection','statusModule','startDateStruct'])
        if start_date_struct and start_date_struct.get('type') == 'ACTUAL':
            trial_schema['study_start_date'] = start_date_struct['date']
        else: 
            trial_schema['study_start_date'] = None
        completion_date_struct = tdh.safe_get(trial_data, ['protocolSection','statusModule','completionDateStruct'])
        if completion_date_struct and completion_date_struct.get('type') == 'ACTUAL':
            trial_schema['study_completion_date'] = completion_date_struct['date']
        else:
            trial_schema['study_completion_date'] = None
        officials = tdh.safe_get(trial_data, ['protocolSection','contactsLocationsModule','overallOfficials'])
        if officials:
            for official in officials:
                if official['role'] == 'PRINCIPAL_INVESTIGATOR':
                    trial_schema['principal_investigator'] = official['name']
                    trial_schema['principal_investigator_institution'] = official['affiliation']
                    break

        # Populate arms and drug_list
        drug_list = set()
        arm_internal_id = 0
        for trial_data_arm in trial_data['protocolSection']['armsInterventionsModule']['armGroups']:
            arm_description = tdh.safe_get(trial_data_arm, ['description'])
            schema_arm = {
                    'arm_code': trial_data_arm['label'],
                    'arm_internal_id': arm_internal_id,
                    'arm_description': arm_description if arm_description else tdh.safe_get(trial_data_arm, ['label']),
                    'arm_suspended': 'N',
                    'dose_level': []            
                }

            trial_schema['treatment_list']['step'][0]['arm'].append(schema_arm)
            dose_level_code = 0
            for intervention in tdh.safe_get(trial_data_arm, ['interventionNames']):
                if intervention:
                    drug_list.add(intervention) 
                    schema_arm['dose_level'].append({
                        'level_code': f'{dose_level_code}',
                        'level_description': intervention,
                        'level_internal_id': dose_level_code,
                        'level_suspended': 'N'
                    })
                    dose_level_code = dose_level_code + 1
            arm_internal_id = arm_internal_id + 1
        trial_schema['drug_list']['drug'] =[{'drug_name': drug} for drug in drug_list]
    except KeyError as ke:
        logger.error(f"Key {ke} not found in NCT study {nct_id}")
        raise
        
    #logger.debug(f"CTML: After general mapping | {trial_schema}")
    return trial_schema

def map_ctml_match_clinical_criteria(trial_data: dict):
    clinical_critera = {}
    oncotree_diagnoses_list = map_oncotree_primary_diagnosis(trial_data)
    clinical_critera['oncotree_primary_diagnosis'] = oncotree_diagnoses_list
    
    age_numerical_str = map_age_numerical(trial_data)
    if age_numerical_str:
        clinical_critera['age_numerical'] = age_numerical_str
    
    gender_str = map_gender(trial_data)
    if gender_str:
        clinical_critera['gender'] = gender_str

    her2_er_pr_dict = map_her2_er_pr_status(trial_data)
    filtered_her2_er_pr_dict = {k:v for k,v in her2_er_pr_dict.items() if v.lower() in ["positive", "negative","!positive","!negative"]}
    clinical_critera.update(filtered_her2_er_pr_dict)
    
    pdl1_status_dict = map_pdl1_status(trial_data)
    filtered_pdl1_status_dict = {k:v for k,v in pdl1_status_dict.items() if v.lower() in ["high", "low"]}
    clinical_critera.update(filtered_pdl1_status_dict)

    mmr_ms_status_dict = map_mmr_ms_status(trial_data)
    filtered_mmr_ms_status_dict = {}    
    
    if 'mmr_status' in mmr_ms_status_dict:
        mmr_value = mmr_ms_status_dict['mmr_status']
        if mmr_value in ['MMR-Proficient', 'MMR-Deficient']:
            filtered_mmr_ms_status_dict['mmr_status'] = mmr_value
        
    if 'ms_status' in mmr_ms_status_dict:
        ms_value = mmr_ms_status_dict['ms_status']
        if ms_value in ['MSI-H', 'MSI-L', 'MSS']:
            filtered_mmr_ms_status_dict['ms_status'] = ms_value
    
    clinical_critera.update(filtered_mmr_ms_status_dict)
    
    disease_status_dict = map_disease_status(trial_data)
    if disease_status_dict and len(disease_status_dict.get('disease_status', {})) > 0:
        clinical_critera.update(disease_status_dict)

    # map_tmb_numerical(trial_data)

    logger.debug(f"clinical criteria: {clinical_critera}")
    clinical_ctml = mcm.convert_to_ctml_clinical_schema(clinical_critera)
    logger.debug(f"clinical criteria as CTML: {clinical_ctml}")
    return clinical_ctml

def map_ctml_match_genomic_criteria(trial_data: dict, gene_synonym_mapping:Dict[str, List[str]]):
    nct_id = trial_data['protocolSection']['identificationModule']['nctId']
    eligibilityCriteria = tdh.safe_get(trial_data, ['protocolSection','eligibilityModule','eligibilityCriteria'])
    contains_gene_info = mcm.check_if_eligibility_criteria_contains_gene_info(gene_synonym_mapping, eligibilityCriteria)

    if contains_gene_info: #check if eligibility criteria contains any gene before asking AI
        tcg = ctg.TrialCriteriaToGenes(
            trial_criteria=eligibilityCriteria,
            synonym_to_symbol=gene_synonym_mapping,
        )
        gene_symbols = tcg.extract_official_gene_symbols()
        genomic_critera = ai.get_genomic_criteria(nct_id, gene_symbols, eligibilityCriteria)
        genomic_ctml = mcm.convert_to_ctml_genomic_schema(genomic_critera)
        logger.debug(f"genomic criteria as CTML: {genomic_ctml}")
        return genomic_ctml
    else:
        return {}

def map_age_numerical(trial_data: dict) -> str:
    minimum_age = tdh.safe_get(trial_data, ['protocolSection','eligibilityModule','minimumAge'])
    if minimum_age:
        min_age_components = minimum_age.split()
        if len(min_age_components) > 1 and min_age_components[1].lower() == "years":
            min_age = f">={min_age_components[0]}"
            return min_age
    return ""

def map_her2_er_pr_status(trial_data: dict):
    nct_id = trial_data['protocolSection']['identificationModule']['nctId']
    eligibilityCriteria = tdh.safe_get(trial_data, ['protocolSection','eligibilityModule','eligibilityCriteria'])
    keywords = tdh.safe_get(trial_data, ['protocolSection','conditionsModule','keywords'])
    result = ai.get_her2_er_pr_status(nct_id, eligibilityCriteria, keywords)
    return result

def map_pdl1_status(trial_data: dict):
    nct_id = trial_data['protocolSection']['identificationModule']['nctId']
    eligibilityCriteria = tdh.safe_get(trial_data, ['protocolSection','eligibilityModule','eligibilityCriteria'])
    keywords = tdh.safe_get(trial_data, ['protocolSection','conditionsModule','keywords'])
    contains_pdl1_info = mcm.check_if_eligibility_criteria_contains_pdl1_info(keywords, eligibilityCriteria)
    if contains_pdl1_info:
        result = ai.get_pdl1_status(nct_id, eligibilityCriteria, keywords)
        return result
    return {}

def map_mmr_ms_status(trial_data: dict):
    nct_id = trial_data['protocolSection']['identificationModule']['nctId']
    eligibilityCriteria = tdh.safe_get(trial_data, ['protocolSection','eligibilityModule','eligibilityCriteria'])
    keywords = tdh.safe_get(trial_data, ['protocolSection','conditionsModule','keywords'])
    contains_mmr_info = mcm.check_if_eligibility_criteria_contains_mmr_info(keywords, eligibilityCriteria)
    if contains_mmr_info:
        result = ai.get_mmr_status(nct_id, eligibilityCriteria, keywords)
        return result
    return {}

def map_gender(trial_data: dict):
    nct_gender = tdh.safe_get(trial_data, ['protocolSection', 'eligibilityModule', 'sex'])
    gender_mapping = {
        "male": "Male",
        "female": "Female"}
    result = gender_mapping.get(nct_gender.lower(), {})
    return result

def map_disease_status(trial_data: dict):
    nct_id = trial_data['protocolSection']['identificationModule']['nctId']
    eligibilityCriteria = tdh.safe_get(trial_data, ['protocolSection','eligibilityModule','eligibilityCriteria'])
    keywords = tdh.safe_get(trial_data, ['protocolSection','conditionsModule','keywords'])
    result = ai.get_disease_status(nct_id, eligibilityCriteria, keywords)
    return result

def map_oncotree_primary_diagnosis(trial_data: dict) -> list:
    nct_id = trial_data['protocolSection']['identificationModule']['nctId']
    conditions_list = tdh.safe_get(trial_data, ['protocolSection', 'conditionsModule','conditions'])
        
    all_possible_diagnoses = set()

    if tdh.all_tumours(conditions_list):
        all_possible_diagnoses.add("_SOLID_")
        all_possible_diagnoses.add("_LIQUID_")
    else:        
        if tdh.all_solid_tumours(conditions_list):
            all_possible_diagnoses.add("_SOLID_")
        else:
            level_1_diagnosis, l1_l2_mapping = onct.get_l1_l2_oncotree_data()
            # stage 1 - no need to Extract Keywords
            logger.debug(f"NCTID: {nct_id} | Stage 1 - Original Conditions:{conditions_list}")
            # stage 2 - Map original conditions to Level 1 oncotree diagnoses
            level1_oncotree_values_dict = ai.get_level1_diagnosis_from_original_conditions(nct_id, conditions_list, level_1_diagnosis)
            logger.debug(f"NCTID: {nct_id} | Stage 2 - Mapped original conditions to Level 1:{level1_oncotree_values_dict}") 

            for item in level1_oncotree_values_dict["oncotree_diagnoses"]:
                if item['oncotree_value'] == "" or item['oncotree_value'].lower() == "other":
                    logger.debug(f"NCTID: {nct_id} | Skipping condition {item['cancer_condition']} as no oncotree diagnosis was returned")
                    continue
                # stage 3: Get the child values for Level 1 oncotree diagnoses
                l2_oncotree_values = l1_l2_mapping[item['oncotree_value']]
                nct_condition = item['cancer_condition']
                logger.debug(f"NCTID: {nct_id} | Stage 3 - Condition = {nct_condition}. Child values = {l2_oncotree_values}")
                if len(l2_oncotree_values) > 0:
                    # stage 4: Pass the child values to AI and the conditions to map to a child value --> pass only level 2 values
                    oncotree_diagnoses_result = ai.get_child_level_diagnoses_from_condition(nct_id, l2_oncotree_values, nct_condition)
                    if oncotree_diagnoses_result and 'oncotree_diagnoses' in oncotree_diagnoses_result.keys():
                        all_possible_diagnoses.update(oncotree_diagnoses_result['oncotree_diagnoses']) 

            if len(all_possible_diagnoses) == 0:
                logger.info(f"NCTID: {nct_id} | No oncotree diagnosis was found from original conditions, trying from keywords and title")
                # if the could not dianose from conditions, try getting diagnosis from keywords and title
                extra_info = []
                keywords = tdh.safe_get(trial_data, ['protocolSection', 'conditionsModule','keywords'])
                if keywords:
                    extra_info.extend(keywords)
                long_title = tdh.safe_get(trial_data, ['protocolSection', 'identificationModule','officialTitle'])
                brief_title = tdh.safe_get(trial_data, ['protocolSection', 'identificationModule','briefTitle'])
                extra_info.append(long_title)
                extra_info.append(brief_title)

                all_level_oncotree_values = set()

                # stage 3: Get the child values for Level 1 oncotree diagnoses
                level1_oncotree_values_dict = ai.get_level1_diagnosis_from_original_extra_info(nct_id, extra_info, level_1_diagnosis)
                for item in level1_oncotree_values_dict["oncotree_diagnoses"]:
                    if item == "" or item.lower() == "other":
                        continue
                    l2_oncotree_values = l1_l2_mapping[item]
                    all_level_oncotree_values.update(l2_oncotree_values)
                logger.debug(f"NCTID: {nct_id} | Stage 3 - Diagnoses = {level1_oncotree_values_dict["oncotree_diagnoses"]}. Child values = {l2_oncotree_values}")
                # stage 4: Pass the child values to AI and the conditions to map to a child value --> pass only level 2 values
                oncotree_diagnoses_result = ai.get_child_level_diagnoses_from_extra_info(nct_id, all_level_oncotree_values, extra_info)
                if oncotree_diagnoses_result and 'oncotree_diagnoses' in oncotree_diagnoses_result.keys():
                    all_possible_diagnoses.update(oncotree_diagnoses_result['oncotree_diagnoses'])                
    
    logger.debug(f"NCTID: {nct_id} | Stage 4 Oncotree_diagnoses : {all_possible_diagnoses}")
        
    if len(all_possible_diagnoses) == 0:
        raise Exception(f"NCTID: {nct_id} | No oncotree diagnosis was found")
    return list(all_possible_diagnoses)


def map_prior_treatment_requirements(trial_schema, trial_data) -> dict:
    """
    Special logic to map the inclusion and exclusion criteria, along with prefixing the exclusion criteria with 'Exclude -'
    Updates the incoming trial_schema to add 'prior_treatment_requirements' key

    Parameters
    ----------
    trial_schema: dict
        Dictionary containing the keys and values for a trial as per the clinical trial schema for matchminer
    trial_data: dict
        Dictionary containing the response from https://clinicaltrials.gov/ API for a particular trial
    """
    eligibility_criteria = trial_data['protocolSection']['eligibilityModule']['eligibilityCriteria']
    lines = eligibility_criteria.split('\n')
    
    begin_exclude = False
    # Populate prior_treatment_requirements
    for line in lines:
        if "Exclusion Criteria" in line:
            begin_exclude = True
        stripped_line = line.strip()
        if stripped_line:
            # Prefix exclusion criteria lines with "exclude"
            if begin_exclude:
                trial_schema['prior_treatment_requirements'].append(f'Exclude - {stripped_line}')
            else:
                # Add inclusion criteria lines directly
                trial_schema['prior_treatment_requirements'].append(stripped_line)
    return trial_schema
 

