"""
Based on the input argument, this script gets either the NCT_IDS for all studies or 
gets the data for a single study, maps it to matchminer schema format 
and saves the result in both YAML and JSON formats.

Argument:
--------
pull all -> get and save all studies, based on certain filers
pull {nct_id} -> get and save specific study based on {nct_id)}, based on certain filers
map all -> read all pre-saved nct data files and map to ctml schema files
map {nct_id} -> read pre-saved nct data file for specific id and map to ctml schema

"""

import json
import sys
import os
import all_studies
import clinical_trials_gov as ctg
import trial_data_formatter as tdf

def main():
    if len(sys.argv) < 3:
        print("Usage: python main.py [pull all | pull {nct_id} | map all | map {nct_id}]")
        return
    
    arg1 = sys.argv[1]
    if arg1 == 'pull':
        arg2 = sys.argv[2]
        if arg2 == 'all':
            all_studies.main()
        else:
            nct_id = arg2
            ctg.get_nct_study(nct_id)
            
    elif arg1 == 'map':
        arg2 = sys.argv[2]
        nct_files_path = 'results/nct'
        ctml_files_path = "results/ctml/"
        if arg2 == 'all':            
            # read all nct files from /results/nct and map to ctml
            for file_name in os.listdir(nct_files_path):
                if os.path.isfile(os.path.join(nct_files_path, file_name)):
                    file_components = file_name.split('.')
                    if file_components[1] == "json":
                        nct_id = file_name.split('.')[0]
                        trial_data = tdf.read_from_file(nct_files_path, nct_id, 'json')
                    
                        mapped_ctml = ctg.map_nct_to_ctml(trial_data)
                        tdf.save_to_file(mapped_ctml, ctml_files_path, nct_id, 'yaml')
                        tdf.save_to_file(mapped_ctml, ctml_files_path, nct_id, 'json')

            return
        else:
            nct_id = arg2
            try:
                # read specific nct file and map to ctml                
                trial_data = tdf.read_from_file(nct_files_path, nct_id, 'json')
            except FileNotFoundError:
                print(f'File {nct_id}.json not found at {nct_files_path}')
                return
            except json.JSONDecodeError:
                print(f'File {nct_id}.json is not a valid json file')
                return
            
            mapped_ctml = ctg.map_nct_to_ctml(trial_data)

            file_name = nct_id
            tdf.save_to_file(mapped_ctml, ctml_files_path, file_name, 'yaml')
            tdf.save_to_file(mapped_ctml, ctml_files_path, file_name, 'json')

if __name__ == "__main__":
    main()