"""
This script contains methods that deal with extraction and manpipulation
of data from clinicaltrials.gov
"""

import json
import requests
import urllib.parse
import ctml_schema
import ai_helper as ai
import trial_data_formatter as tdf
import oncotree
import match_criteria_mapper as mcm
from loguru import logger


API_BASE_URL = "https://clinicaltrials.gov/api/v2/"


def get_all_studies():
    """
    Queries https://clinicaltrials.gov/api to get all studies filtered by params specified below.
    Extracts certain fields from each study and adds to a list
    Saves each study in a json file

    Returns
    -------
    nctIds: list
        list of NCT_IDS
    """

    ALL_STUDIES_ENDPOINT = "studies"

    # filters
    condition = "cancer"
    location = "Hong Kong"
    status = "RECRUITING"
    study_type = "AREA[StudyType]INTERVENTIONAL"

    sortBy = "LastUpdatePostDate"

    params = {'query.cond': condition,
              'query.locn': location,
              'filter.overallStatus' : status,
              'query.term': study_type,
              'pageSize': 50,
              'sort': sortBy}    
    nct_data = []
    while True:        
        endpoint_url = f'{urllib.parse.urljoin(API_BASE_URL, ALL_STUDIES_ENDPOINT)}?{urllib.parse.urlencode(params)}'
        print(endpoint_url)
        response = requests.get(endpoint_url)
        response.raise_for_status()

        json_response = response.json()
        for study in json_response['studies']:
            nct_id = study['protocolSection']['identificationModule']['nctId']
            is_recruiting_in_hk = tdf.check_if_recruiting_in_HK(study)
            if is_recruiting_in_hk == True:                
                # consolidate info to be saved in a CSV file
                conditions = ','.join(study['protocolSection']['conditionsModule']['conditions'])
                lastUpdatedDate = study['protocolSection']['statusModule']['lastUpdatePostDateStruct']['date']
                nct_data.append((nct_id, conditions, lastUpdatedDate))

                # save each study as a separate json file after removing unnecessary sections
                tdf.remove_unused_keys(study)
                tdf.save_to_file(study, 'results/nct/', nct_id, 'json')
            else:
                print(f"Study {nct_id} is not recruiting actively in HK. Skipping")

        if 'nextPageToken' not in json_response:
            break
        nextPageToken = json_response['nextPageToken']
        if not nextPageToken:
            break
        params['pageToken'] = nextPageToken
    return nct_data

def get_nct_study(nct_id:str):
    """
    Queries a single study with the nct_id param and saves the response to a file
    """

    NCT_STUDY_ENDPOINT = "studies/{0}".format(nct_id)
    endpoint_url = urllib.parse.urljoin(API_BASE_URL, NCT_STUDY_ENDPOINT)
    response = requests.get(endpoint_url)
    response.raise_for_status()
    study = response.json()
    is_recruiting_in_hk =tdf.check_if_recruiting_in_HK(study)
    if is_recruiting_in_hk == True:
        tdf.remove_unused_keys(study)
        tdf.save_to_file(study, 'results/nct/', nct_id, 'json')
        print(f"Study {nct_id} saved at results/nct/{nct_id}.json")
    else:
        print(f"Study {nct_id} is not recruiting actively in HK. Skipping")

def map_nct_to_ctml(trial_data: dict) -> dict:
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

    trial_schema = ctml_schema.get_ctml_schema()

    trial_schema = map_ctml_general_fields(trial_schema, trial_data)   

    trial_schema = map_prior_treatment_requirements(trial_schema, trial_data)

    # clinical_ctml = map_ctml_match_clinical_criteria(trial_data)
    # genomic_ctml = map_ctml_match_genomic_criteria(trial_data)
    # match_result = mcm.combine_clinical_and_genomic_ctml(clinical_ctml, genomic_ctml)
    # trial_schema['treatment_list']['step'][0]['match'] = match_result
    # logger.debug(f"CTML: After mapping clinical and genomic match criteria | {trial_schema}")

    return trial_schema

def map_ctml_general_fields(trial_schema, trial_data) -> dict:

    nct_id = trial_data['protocolSection']['identificationModule']['nctId']

    try:    
        trial_schema['nct_id'] = nct_id
        trial_schema['long_title'] = trial_data['protocolSection']['identificationModule']['officialTitle']
        trial_schema['principal_investigator_institution'] = trial_data['protocolSection']['identificationModule']['organization']['fullName']

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

        officials = tdf.safe_get(trial_data, ['protocolSection','contactsLocationsModule','overallOfficials'])
        if officials:
            for official in officials:
                if official['role'] == 'STUDY_DIRECTOR':
                    trial_schema['principal_investigator'] = official['name']
                    trial_schema['principal_investigator_institution'] = official['affiliation']
                    break

        # Populate arms and drug_list
        drug_list = set()
        arm_internal_id = 0
        for trial_data_arm in trial_data['protocolSection']['armsInterventionsModule']['armGroups']:
            schema_arm = {
                    'arm_code': trial_data_arm['label'],
                    'arm_internal_id': arm_internal_id,
                    'arm_description': tdf.safe_get(trial_data_arm, ['description']),
                    'arm_suspended': 'N',
                    'dose_level': []            
                }

            trial_schema['treatment_list']['step'][0]['arm'].append(schema_arm)
            dose_level_code = 0
            for intervention in tdf.safe_get(trial_data_arm, ['interventionNames']):
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
    filtered_her2_er_pr_dict = {k:v for k,v in her2_er_pr_dict.items() if v.lower() in ["positive", "negative"]}
    clinical_critera.update(filtered_her2_er_pr_dict)
    
    pdl1_status_dict = map_pdl1_status(trial_data)
    filtered_pdl1_status_dict = {k:v for k,v in pdl1_status_dict.items() if v.lower() in ["high", "low"]}
    clinical_critera.update(filtered_pdl1_status_dict)
    
    disease_status_dict = map_disease_status(trial_data)
    if disease_status_dict and len(disease_status_dict.get('disease_status', {})) > 0:
        clinical_critera.update(disease_status_dict)

    # map_muscle_invasion(trial_data)
    # map_tmb_numerical(trial_data)

    logger.debug(f"clinical criteria: {clinical_critera}")
    clinical_ctml = mcm.convert_to_ctml_clinical_schema(clinical_critera)
    logger.debug(f"clinical criteria as CTML: {clinical_ctml}")
    return

def map_ctml_match_genomic_criteria(trial_data: dict):
    genomic_critera = {}
    genomic_ctml = mcm.convert_to_ctml_genomic_schema(genomic_critera)
    logger.debug(f"genomic criteria as CTML: {genomic_ctml}")
    return {}

def map_age_numerical(trial_data: dict) -> str:
    minimum_age = tdf.safe_get(trial_data, ['protocolSection','eligibilityModule','minimumAge'])
    min_age_components = minimum_age.split()
    if len(min_age_components) > 1 and min_age_components[1].lower() == "years":
        min_age = f">={min_age_components[0]}"
        return min_age
    return ""

def map_her2_er_pr_status(trial_data: dict):
    nct_id = trial_data['protocolSection']['identificationModule']['nctId']
    eligibilityCriteria = tdf.safe_get(trial_data, ['protocolSection','eligibilityModule','eligibilityCriteria'])
    keywords = tdf.safe_get(trial_data, ['protocolSection','conditionsModule','keywords'])
    result = ai.get_her2_er_pr_status(nct_id, eligibilityCriteria, keywords)
    return result

def map_pdl1_status(trial_data: dict):
    nct_id = trial_data['protocolSection']['identificationModule']['nctId']
    eligibilityCriteria = tdf.safe_get(trial_data, ['protocolSection','eligibilityModule','eligibilityCriteria'])
    keywords = tdf.safe_get(trial_data, ['protocolSection','conditionsModule','keywords'])
    result = ai.get_pdl1_status(nct_id, eligibilityCriteria, keywords)
    return result

def map_gender(trial_data: dict):
    nct_gender = tdf.safe_get(trial_data, ['protocolSection', 'eligibilityModule', 'sex'])
    gender_mapping = {
        "male": "Male",
        "female": "Female"}
    result = gender_mapping.get(nct_gender.lower(), {})
    return result

def map_disease_status(trial_data: dict):
    nct_id = trial_data['protocolSection']['identificationModule']['nctId']
    eligibilityCriteria = tdf.safe_get(trial_data, ['protocolSection','eligibilityModule','eligibilityCriteria'])
    keywords = tdf.safe_get(trial_data, ['protocolSection','conditionsModule','keywords'])
    result = ai.get_disease_status(nct_id, eligibilityCriteria, keywords)
    return result

def map_oncotree_primary_diagnosis(trial_data: dict) -> list:
    nct_id = trial_data['protocolSection']['identificationModule']['nctId']
    conditions_list = tdf.safe_get(trial_data, ['protocolSection', 'conditionsModule','conditions'])
        
    all_possible_diagnoses = []

    all_solid_tumors = any(
    cond.lower() in ["solid tumors", "cancer"]    
    for cond in conditions_list)
    if all_solid_tumors:
        all_possible_diagnoses.append("_SOLID_")
    else:
        level_1_diagnosis, main_type_list, level1_mapping = oncotree.get_oncotree_data()
        
        # stage 1 - Extract Keywords
        keywords = mcm.get_keywords_from_conditions(conditions_list)
        logger.debug(f"NCTID: {nct_id} | Stage 1 - Condition keywords:{keywords}")    

        # stage 2 - Map keywords to Level 1 oncotree diagnoses
        level1_oncotree_values_dict = ai.get_level1_diagnosis_from_condition_keywords(nct_id, keywords, level_1_diagnosis)
        logger.debug(f"NCTID: {nct_id} | Stage 2 - Mapped keywords to Level 1:{level1_oncotree_values_dict}") 
        # create a dictionary to map level1 diagnoses back to original condition (not keywords)
        level1_oncotree_value_to_nct_condition = {}

        for item in level1_oncotree_values_dict["oncotree_diagnoses"]:        
            cancer_condition_keyword = item['cancer_condition_keyword']
            oncotree_value = item['oncotree_value']
            for condition in conditions_list:
                if cancer_condition_keyword in condition:                
                    level1_oncotree_value_to_nct_condition[oncotree_value] = condition
                    continue
        
        logger.debug(f"NCTID: {nct_id} | Level1 to nct_condition map: {level1_oncotree_value_to_nct_condition}") 

        for item in level1_oncotree_values_dict["oncotree_diagnoses"]:
            # stage 3: Get the child values for Level 1 oncotree diagnoses
            child_values = level1_mapping[item['oncotree_value']]
            nct_condition = level1_oncotree_value_to_nct_condition[item['oncotree_value']]
            logger.debug(f"NCTID: {nct_id} | Stage 3 - Condition = {nct_condition}. Child values = {child_values}")
            if len(child_values) > 0:
                # stage 4: Pass the child values to AI and the conditions to map to a child value
                oncotree_diagnoses_result = ai.get_child_level_diagnoses_from_condition(nct_id, child_values, nct_condition)
                if oncotree_diagnoses_result and 'oncotree_diagnoses' in oncotree_diagnoses_result.keys():
                    all_possible_diagnoses.extend(oncotree_diagnoses_result['oncotree_diagnoses'])
    logger.debug(f"NCTID: {nct_id} | Stage 4 Oncotree_diagnoses : {all_possible_diagnoses}")
            
    return all_possible_diagnoses

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
    
    #logger.debug(f"CTML: After mapping prior_treatment_requirements | {trial_schema}")
    return trial_schema
 

