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
import argparse

# def main():
#     if len(sys.argv) < 3 or sys.argv[1] not in ['pull','map']:
#         print("Usage: python main.py [pull all | pull existing | pull {nct_id} | map all | map {nct_id}]")
#         return
    
#     arg1 = sys.argv[1]
#     if arg1 == 'pull':
#         arg2 = sys.argv[2]
#         if arg2 == 'all':
#             ast.all_studies.main()
#         elif arg2 == 'existing':
#             ctg.get_status_of_existing_studies()
#         else:
#             nct_id = arg2
#             ctg.get_nct_study(nct_id)
            
#     elif arg1 == 'map':
#         arg2 = sys.argv[2]
#         nct_files_path = 'results/nct'
#         ctml_files_path = "results/ctml/"
#         if arg2 == 'all':            
#             # read all nct files from /results/nct and map to ctml
#             genes = get_gene_list()
#             for file_name in os.listdir(nct_files_path):
#                 if os.path.isfile(os.path.join(nct_files_path, file_name)):
#                     file_components = file_name.split('.')
#                     if file_components[1] == "json":
#                         nct_id = file_name.split('.')[0]
#                         trial_data = tdh.read_from_file(nct_files_path, nct_id, 'json')

#                         try:
#                             logger.info(f"Mapping NCT ID: {nct_id}")   
#                             logger.info(f"-----------------------")                   
#                             mapped_ctml = ctg.map_nct_to_ctml(trial_data, genes)
#                             tdh.save_to_file(mapped_ctml, ctml_files_path, nct_id, 'yaml')
#                             tdh.save_to_file(mapped_ctml, ctml_files_path, nct_id, 'json')
#                         except Exception as ex:
#                             logger.error(f"nct_id: {nct_id} | Unexpected {ex=}, {type(ex)=}")

#             return
#         else:
#             nct_id = arg2
#             try:
#                 # read specific nct file and map to ctml  
#                 logger.info(f"Mapping NCT ID: {nct_id}")   
#                 logger.info(f"-----------------------")                 
#                 trial_data = tdh.read_from_file(nct_files_path, nct_id, 'json')
#             except FileNotFoundError:
#                 print(f'File {nct_id}.json not found at {nct_files_path}')
#                 return
#             except json.JSONDecodeError:
#                 print(f'File {nct_id}.json is not a valid json file')
#                 return
            
#             genes = get_gene_list()

#             try:
#                 mapped_ctml = ctg.map_nct_to_ctml(trial_data, genes)

#                 file_name = nct_id
#                 tdh.save_to_file(mapped_ctml, ctml_files_path, file_name, 'yaml')
#                 tdh.save_to_file(mapped_ctml, ctml_files_path, file_name, 'json')
#             except Exception as ex:
#                 logger.error(f"nct_id: {nct_id} | Unexpected {ex=}, {type(ex)=}")


def main():
    parser = argparse.ArgumentParser(description="Process NCT trial data into CTML.")
    
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Subparser for 'pull'
    pull_parser = subparsers.add_parser('pull', help='Pull NCT study data.')
    pull_group = pull_parser.add_mutually_exclusive_group(required=True)
    
    pull_group.add_argument('--all', action='store_true', help='Pull all studies')
    pull_group.add_argument('--existing', action='store_true', help='Pull existing studies')
    pull_group.add_argument('--nct_id', type=str, help='Pull study data for a specific NCT ID')

    # Subparser for 'map'
    map_parser = subparsers.add_parser('map', help='Map NCT IDs to CTML.')
    map_group = map_parser.add_mutually_exclusive_group(required=True)
    
    map_group.add_argument('--all', action='store_true', help='Map all NCT files')
    map_group.add_argument('--nct_id', type=str, help='Map a specific NCT ID')

    args = parser.parse_args()

    nct_files_path = 'results/nct'
    ctml_files_path = "results/ctml/"

    if args.command == 'pull':
        if args.all:
            pull_all()
        elif args.existing:
            pull_existing()
        else:
            pull_nct(args.nct_id)

    elif args.command == 'map':
        if args.all:
            map_all(nct_files_path, ctml_files_path)
        else:
            map_nct(args.nct_id, nct_files_path, ctml_files_path)

def pull_all():
    ast.all_studies.main()

def pull_nct(nct_id):
    ctg.get_nct_study(nct_id)

def pull_existing():
    ctg.get_status_of_existing_studies()

def map_all(nct_files_path, ctml_files_path):
    genes = get_gene_list()
    for file_name in os.listdir(nct_files_path):
        if os.path.isfile(os.path.join(nct_files_path, file_name)) and file_name.endswith('.json'):
            nct_id = file_name.split('.')[0]
            trial_data = tdh.read_from_file(nct_files_path, nct_id, 'json')

            try:
                logger.info(f"Mapping NCT ID: {nct_id}")   
                logger.info("-----------------------")                   
                mapped_ctml = ctg.map_nct_to_ctml(trial_data, genes)
                tdh.save_to_file(mapped_ctml, ctml_files_path, nct_id, 'yaml')
                tdh.save_to_file(mapped_ctml, ctml_files_path, nct_id, 'json')
            except Exception as ex:
                logger.error(f"nct_id: {nct_id} | Unexpected {ex=}, {type(ex)=}")

def map_nct(nct_id, nct_files_path, ctml_files_path):
    try:
        logger.info(f"Mapping NCT ID: {nct_id}")   
        logger.info("-----------------------")                 
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
        tdh.save_to_file(mapped_ctml, ctml_files_path, nct_id, 'yaml')
        tdh.save_to_file(mapped_ctml, ctml_files_path, nct_id, 'json')
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