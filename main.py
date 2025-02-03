"""
Based on the input argument, this script gets either the NCT_IDS for all studies or 
gets the data for a single study, maps it to matchminer schema format 
and saves the result in both YAML and JSON formats.

Argument:
--------
all -> calls the script to get all studies
{NCTID} -> calls the fucntion to get and convert the data for a specific trial based on NCT_ID

"""

import sys
import all_studies

from clinical_trials_gov import get_nct_data, map_clinical_trial_data
from trial_data_formatter import remove_unused_keys, check_if_recruiting_in_HK, save_to_file

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py [all | <NCTID>]")
        return
    
    arg = sys.argv[1]
    if arg == 'all':
        all_studies.main()
    else:
        nct_id = arg
        res = get_nct_data(nct_id)

        #check if recruiting in HK
        is_recruiting = check_if_recruiting_in_HK(res)
        if is_recruiting is False:
            print(f"Trial {nct_id} is not actively recruiting in Hong Kong")
            return
        
        #shorten trial data dictionary
        trial_data = remove_unused_keys(res)

        mapped_data = map_clinical_trial_data(trial_data)

        save_to_file(mapped_data, 'yaml')
        save_to_file(mapped_data, 'json')

if __name__ == "__main__":
    main()