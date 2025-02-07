import json
import yaml

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
    trial_data["protocolSection"].pop("statusModule", None)
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
        
def read_from_file(path: str, file_name :str, format:str) -> dict:    
    if format == "json":
        with open(f'{path}/{file_name}.json', 'r') as json_file:
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


