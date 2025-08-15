import json
import yaml
from loguru import logger

def remove_unused_keys(trial_data: dict):
    """
    Removes keys that will not be used for mapping data to matchminer trial schema
    The shortened dictionary can be passed to an AI API for mapping
    
    Parameters
    ----------
    trial_data : dict
        Dictionary containing the response from https://clinicaltrials.gov/ API for a particular trial

    Returns
    -------
    trial_data: dict
        Shortened dictionary 
    """
    # Handle statusModule - preserve specific date structures, remove others
    if "statusModule" in trial_data["protocolSection"]:
        status_module = trial_data["protocolSection"]["statusModule"]
        # Keep only the required date structures
        preserved_keys = ["studyFirstPostDateStruct", "lastUpdatePostDateStruct"]
        keys_to_remove = [key for key in status_module.keys() if key not in preserved_keys]
        
        for key in keys_to_remove:
            status_module.pop(key, None)
    
    trial_data["protocolSection"].pop("oversightModule", None)
    trial_data["protocolSection"]["contactsLocationsModule"].pop("locations", None)
    trial_data["protocolSection"].pop("outcomesModule", None)
    trial_data["protocolSection"].pop("ipdSharingStatementModule", None)
    trial_data.pop("derivedSection", None)
    return trial_data

def check_if_recruiting_in_HK(trial_data: dict) -> bool:
    locations = trial_data["protocolSection"]["contactsLocationsModule"]["locations"]
    recruiting_in_hk = any(
        location["country"].lower() == "hong kong" and
        location["status"].lower() == "recruiting"
        for location in locations
    )
    if recruiting_in_hk:
        return True
    else:
        return False
    
def is_study_interventional(trial_data: dict) -> bool:
    studyType = trial_data["protocolSection"]["designModule"]["studyType"]    
    if studyType.lower() == "interventional":
        return True
    else:
        return False
    
def has_correct_intervention(trial_data: dict, intervention_types:list) -> bool:
    interventions = trial_data['protocolSection']['armsInterventionsModule']['interventions']
    return any(intervention["type"] in intervention_types for intervention in interventions)
        
def read_from_file(path: str, file_name :str, format:str) -> dict:    
    if format == "json":
        with open(f'{path}/{file_name}.json', 'r') as json_file:
            data = json.load(json_file)
            return data
    else:
        print('No implementation for formats other than json')

def read_from_file_path(path: str, format:str) -> dict:    
    if format == "json":
        with open(path, 'r') as json_file:
            data = json.load(json_file)
            return data
    else:
        print('No implementation for formats other than json')


def save_to_file(data: dict, path: str, file_name :str, format:str):
    
    if format == "yaml":
        yaml_data = yaml.dump(data, sort_keys=False)
        print(yaml_data)

        with open(f'{path}/{file_name}.yaml', 'w') as yaml_file:
            yaml_file.write(yaml_data)
    elif format == "json":
        with open(f'{path}/{file_name}.json', "w") as json_file: 
            json.dump(data, json_file)

def safe_get(trial_data, keys):
    for key in keys:
        trial_data = trial_data.get(key, {})
    return trial_data

def all_solid_tumours(conditions_list):
    all_solid_tumors = any(
            "solid tumors" in cond.lower() or
            "solid malignancies" in cond.lower()
            for cond in conditions_list)
        
    return all_solid_tumors

def all_tumours(conditions_list):
    all_tumors = any(
    cond.lower() in ["cancer","oncology"] 
    for cond in conditions_list)
    
    return all_tumors


def get_all_keys(d: dict, keys=None):
    if keys is None:
        keys = set()        
    for key, value in d.items():
        keys.add(key) 
        if isinstance(value, dict):  # If the value is a dictionary, recurse into it
            get_all_keys(value, keys)
        elif isinstance(value, list):  # If the value is a list, iterate through each item
            for item in value:
                if isinstance(item, dict):
                    get_all_keys(item, keys)
    return keys

##Post-processing##
def update_hugo_symbol(genomic_crit:dict):
    # Check each key-value pair in the dictionary
    for key, value in genomic_crit.items():
        if key == "hugo_symbol" and value == "HER2":            
            genomic_crit[key] = "ERBB2"  # Update the value
            logger.info(f"Changed HER2 to ERBB2")
        elif isinstance(value, dict):
            update_hugo_symbol(value)  # Recurse into the dictionary
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    update_hugo_symbol(item)  # Recurse into each item in the list
    
    return genomic_crit


def convert_protocol_ids_to_list(protocol_ids_str: str) -> list:
    """
    Convert protocol IDs string to a list of strings.
    Handles cases where the input might already be pipe-separated.
    
    Parameters
    ----------
    protocol_ids_str : str
        Protocol IDs string that might contain pipe-separated values
        
    Returns
    -------
    list
        List of protocol ID strings
    """
    if not protocol_ids_str or protocol_ids_str.strip() == '':
        return []
    
    # Split by pipe and clean up each ID
    protocol_ids_list = [pid.strip() for pid in protocol_ids_str.split('|') if pid.strip()]
    return protocol_ids_list
    


