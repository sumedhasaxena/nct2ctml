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
import trial_data.all_studies as ast
import trial_data.clinical_trials_gov as ctg
import trial_data.trial_data_helper as tdh
from loguru import logger

def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ['pull','map']:
        print("Usage: python main.py [pull all | pull {nct_id} | map all | map {nct_id}]")
        return
    
    arg1 = sys.argv[1]
    if arg1 == 'pull':
        arg2 = sys.argv[2]
        if arg2 == 'all':
            ast.all_studies.main()
        else:
            nct_id = arg2
            ctg.get_nct_study(nct_id)
            
    elif arg1 == 'map':
        arg2 = sys.argv[2]
        nct_files_path = 'results/nct'
        ctml_files_path = "results/ctml/"
        if arg2 == 'all':            
            # read all nct files from /results/nct and map to ctml
            genes = get_gene_list()
            for file_name in os.listdir(nct_files_path):
                if os.path.isfile(os.path.join(nct_files_path, file_name)):
                    file_components = file_name.split('.')
                    if file_components[1] == "json":
                        nct_id = file_name.split('.')[0]
                        trial_data = tdh.read_from_file(nct_files_path, nct_id, 'json')

                        try:
                            logger.info(f"Mapping NCT ID: {nct_id}")   
                            logger.info(f"-----------------------")                   
                            mapped_ctml = ctg.map_nct_to_ctml(trial_data, genes)
                            tdh.save_to_file(mapped_ctml, ctml_files_path, nct_id, 'yaml')
                            tdh.save_to_file(mapped_ctml, ctml_files_path, nct_id, 'json')
                        except Exception as ex:
                            logger.error(f"nct_id: {nct_id} | Unexpected {ex=}, {type(ex)=}")

            return
        else:
            nct_id = arg2
            try:
                # read specific nct file and map to ctml  
                logger.info(f"Mapping NCT ID: {nct_id}")   
                logger.info(f"-----------------------")                 
                trial_data = tdh.read_from_file(nct_files_path, nct_id, 'json')
            except FileNotFoundError:
                print(f'File {nct_id}.json not found at {nct_files_path}')
                return
            except json.JSONDecodeError:
                print(f'File {nct_id}.json is not a valid json file')
                return
            
            genes = get_gene_list()

            try:
                mapped_ctml = ctg.map_nct_to_ctml(trial_data, genes)

                file_name = nct_id
                tdh.save_to_file(mapped_ctml, ctml_files_path, file_name, 'yaml')
                tdh.save_to_file(mapped_ctml, ctml_files_path, file_name, 'json')
            except Exception as ex:
                logger.error(f"nct_id: {nct_id} | Unexpected {ex=}, {type(ex)=}")

def get_gene_list() -> list:
    genes = []
    with open('ref/genes.txt', 'r') as file:     
        genes = [line.strip() for line in file.readlines()]
    return genes

if __name__ == "__main__":
    logger.add('logs/nct2ctml.log', rotation = '1 MB', encoding="utf-8", format="{time} {level} - Line: {line} - {message}")
    main()