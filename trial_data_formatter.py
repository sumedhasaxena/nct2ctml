import json
import yaml

def format_trial_data(trial_data: dict):
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

def convert_to_yaml(mapped_data):
    yaml_data = yaml.dump(mapped_data, sort_keys=False)
    print(yaml_data)
    print(type(mapped_data))

    with open('output.yaml', 'w') as file:
        file.write(yaml_data)
