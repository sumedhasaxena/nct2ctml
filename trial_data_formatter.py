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
    del trial_data["protocolSection"]["statusModule"]
    del trial_data["protocolSection"]["oversightModule"]
    del trial_data["protocolSection"]["contactsLocationsModule"]["locations"]
    del trial_data["protocolSection"]["ipdSharingStatementModule"]
    del trial_data["derivedSection"]
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

def save_to_file(mapped_data, format):
    nct_id = mapped_data["nct_id"]
    if format == "yaml":
        yaml_data = yaml.dump(mapped_data, sort_keys=False)
        print(yaml_data)

        with open(f'results/{nct_id}.yaml', 'w') as yaml_file:
            yaml_file.write(yaml_data)
    elif format == "json":
        with open(f'results/{nct_id}.json', "w") as json_file: 
            json.dump(mapped_data, json_file)

