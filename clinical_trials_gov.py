"""
This script contains methods that deal with extraction and manpipulation
of data from clinicaltrials.gov
"""

import requests
import urllib.parse
import ctml_schema
import trial_data_formatter as tdf
import config

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

    trial_schema['nct_id'] = trial_data['protocolSection']['identificationModule']['nctId']
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

    officials = trial_data['protocolSection']['contactsLocationsModule']['overallOfficials']
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
                'arm_description': trial_data_arm['description'],
                'arm_suspended': 'N',
                'dose_level': []            
            }

        trial_schema['treatment_list']['step'][0]['arm'].append(schema_arm)
        dose_level_code = 0
        for intervention in trial_data_arm['interventionNames']:
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


    map_prior_treatment_requirements(trial_schema, trial_data)

    return trial_schema

def map_nct_to_ctml_AI(trial_data: dict) -> dict:
    conditions_list = tdf.safe_get(trial_data, ['protocolSection', 'conditionsModule','conditions'])
    # Split the sentence into a list of keywords
    all_keywords = set()
    for cond in conditions_list:
        keywords = [keyword.strip() for keyword in cond.split(',')]
        # Filter out unwanted entries
        filtered_keywords = [keyword for keyword in keywords if not any(word.lower() in keyword.lower() for word in config.keywords_to_remove)]
        all_keywords.add(filtered_keywords)
    
    # TODO
    
    # get level1 list from maintype list from oncotree.py
    # serach for entries with any word from 'all_keywords'
    # The resulting entries and subenties will be passed to AI for further getting the accurate oncotree condition


    return

def map_prior_treatment_requirements(trial_schema, trial_data):
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


    

