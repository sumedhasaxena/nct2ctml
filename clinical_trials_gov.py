import requests
import urllib.parse
import clinical_trial_schema

API_BASE_URL = "https://clinicaltrials.gov/api/v2/"

def get_nct_data(nct_id:str):
    NCT_STUDY_ENDPOINT = "studies/{0}".format(nct_id)
    endpoint_url = urllib.parse.urljoin(API_BASE_URL, NCT_STUDY_ENDPOINT)
    response = requests.get(endpoint_url)
    response.raise_for_status()
    return response.json()

def map_clinical_trial_data(trial_data) -> dict:
    trial_schema = clinical_trial_schema.get_trial_schema()

    trial_schema['nct_id'] = trial_data['protocolSection']['identificationModule']['nctId']
    trial_schema['long_title'] = trial_data['protocolSection']['identificationModule']['officialTitle']
    trial_schema['principal_investigator_institution'] = trial_data['protocolSection']['identificationModule']['organization']['fullName']
    #trial_schema['protocol_id'] = trial_data['protocolSection']['identificationModule']['orgStudyIdInfo']['id']
    #trial_schema['prior_treatment_requirements'].append(trial_data['protocolSection']['eligibilityModule']['eligibilityCriteria'])
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

    # Populate arms and drug_list
    for intervention in trial_data['protocolSection']['armsInterventionsModule']['interventions']:
        trial_schema['drug_list']['drug'].append(
            {'drug_name': intervention['name']}
        )
        for label in intervention['armGroupLabels']:
            trial_schema['treatment_list']['step'][0]['arm'].append({
                'arm_code': label,
                'arm_internal_id': 1111,  # You might want to adjust this
                'arm_description': f"Participants will receive {intervention['name']}",
                'arm_suspended': 'N',
                'dose_level': [{
                    'level_code': '1',
                    'level_description': f'Drug: {intervention["name"]}',
                    'level_internal_id': 1,
                    'level_suspended': 'N'
                }]
            })
    
    map_prior_treatment_requirements(trial_schema, trial_data)

    return trial_schema

def map_prior_treatment_requirements(trial_schema, trial_data):
    eligibility_criteria = trial_data['protocolSection']['eligibilityModule']['eligibilityCriteria']
    lines = eligibility_criteria.split('\n')
    
    begin_exclude = False
    # Populate prior_treatment_requirements
    for line in lines:
        if "Exclusion Criteria" in line:
            begin_exclude = True
            # Prefix exclusion criteria lines with "exclude"
        if begin_exclude:
            trial_schema['prior_treatment_requirements'].append(f'Exclude - {line.strip()}')
        else:
            # Add inclusion criteria lines directly
            trial_schema['prior_treatment_requirements'].append(line.strip())


    

