"""
This script contains methods that deal with extraction and manpipulation
of data from clinicaltrials.gov
"""

import config
import requests
import urllib.parse
import ctml_schema
import ai_helper as ai
import trial_data_helper as tdh
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
            is_recruiting_in_hk = tdh.check_if_recruiting_in_HK(study)
            if is_recruiting_in_hk == True:
                if tdh.has_correct_intervention(study, config.intervention_types):
                    # consolidate info to be saved in a CSV file
                    conditions = ','.join(study['protocolSection']['conditionsModule']['conditions'])
                    lastUpdatedDate = study['protocolSection']['statusModule']['lastUpdatePostDateStruct']['date']
                    nct_data.append((nct_id, conditions, lastUpdatedDate))

                    # save each study as a separate json file after removing unnecessary sections
                    tdh.remove_unused_keys(study)
                    tdh.save_to_file(study, 'results/nct/', nct_id, 'json')
                else:
                    print(f"Study {nct_id} does not have relevant intervention types. Skipping")
                    logger.info(f"Study {nct_id} does not have relevant intervention types. Skipping")
            else:
                print(f"Study {nct_id} is not recruiting actively in HK. Skipping")
                logger.info(f"Study {nct_id} is not recruiting actively in HK. Skipping")

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
    is_recruiting_in_hk =tdh.check_if_recruiting_in_HK(study)
    if is_recruiting_in_hk == True:
        if tdh.has_correct_intervention(study, config.intervention_types):
            tdh.remove_unused_keys(study)
            tdh.save_to_file(study, 'results/nct/', nct_id, 'json')
            print(f"Study {nct_id} saved at results/nct/{nct_id}.json")
        else:
            print(f"Study {nct_id} does not have relevant intervention types. Skipping")
            logger.info(f"Study {nct_id} does not have relevant intervention types. Skipping")
    else:
        print(f"Study {nct_id} is not recruiting actively in HK. Skipping")
        logger.info(f"Study {nct_id} is not recruiting actively in HK. Skipping")

def map_nct_to_ctml(trial_data: dict, genes:list) -> dict:
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

    clinical_ctml = map_ctml_match_clinical_criteria(trial_data)
    genomic_ctml = map_ctml_match_genomic_criteria(trial_data, genes)
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

        officials = tdh.safe_get(trial_data, ['protocolSection','contactsLocationsModule','overallOfficials'])
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
    filtered_her2_er_pr_dict = {k:v for k,v in her2_er_pr_dict.items() if v.lower() in ["positive", "negative"]}
    clinical_critera.update(filtered_her2_er_pr_dict)
    
    pdl1_status_dict = map_pdl1_status(trial_data)
    filtered_pdl1_status_dict = {k:v for k,v in pdl1_status_dict.items() if v.lower() in ["high", "low"]}
    clinical_critera.update(filtered_pdl1_status_dict)
    
    disease_status_dict = map_disease_status(trial_data)
    if disease_status_dict and len(disease_status_dict.get('disease_status', {})) > 0:
        clinical_critera.update(disease_status_dict)

    # map_tmb_numerical(trial_data)

    logger.debug(f"clinical criteria: {clinical_critera}")
    clinical_ctml = mcm.convert_to_ctml_clinical_schema(clinical_critera)
    logger.debug(f"clinical criteria as CTML: {clinical_ctml}")
    return clinical_ctml

def map_ctml_match_genomic_criteria(trial_data: dict, genes:list):
    nct_id = trial_data['protocolSection']['identificationModule']['nctId']
    eligibilityCriteria = tdh.safe_get(trial_data, ['protocolSection','eligibilityModule','eligibilityCriteria'])
    contains_gene_info = mcm.check_if_eligibility_criteria_contains_gene_info(genes, eligibilityCriteria)
    if contains_gene_info: #check if eligibility criteria contains any gene before asking AI
        genomic_critera = ai.get_genomic_criteria(nct_id, genes, eligibilityCriteria)
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
            level_1_diagnosis, l1_l2_mapping = oncotree.get_l1_l2_oncotree_data()
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
 

