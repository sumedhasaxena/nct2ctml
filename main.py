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
import src.all_studies as ast
import src.clinical_trials_gov as ctg
import src.trial_data_helper as tdh
from loguru import logger
import argparse
import csv

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
    
    map_group.add_argument('--all', action='store_true', help='Map all eligible NCT files, based on last update date in trial_status.csv')
    map_group.add_argument('--nct_id', type=str, help='Map a specific NCT ID')

    args = parser.parse_args()

    nct_files_path = 'cache/nct'
    ctml_files_path = "cache/ctml/"

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
    """Trial synchronization implementation"""
    from src.trial_pull_manager import TrialPullManager
    
    try:
        sync = TrialPullManager()
        results = sync.sync_trials()
        print("Trial synchronization completed successfully!")
        print(f"Processed {results['api_trials_processed']} trials from API")
        print(f"Inserted {results['insertions']} new trials")
        print(f"Updated {results['updates']} existing trials")
        print(f"Closed {results['closures']} trials")
        print(f"Merged {results['local_trials_merged']} local trials")
    except Exception as e:
        logger.error(f"Error in pull_all: {e}")
        raise

def pull_nct(nct_id):
    ctg.get_nct_study(nct_id)

def pull_existing():
    """Legacy method - kept for backward compatibility"""
    ctg.get_status_of_existing_studies()

def map_all(nct_files_path, ctml_files_path):
    """Map all NCT files to CTML format"""
    from src.trial_map_manager import TrialMapManager
    
    try:
        manager = TrialMapManager()
        results = manager.map_all_trials(nct_files_path, ctml_files_path)
        logger.info(f"Mapping completed. Processed: {results['processed']}, Skipped: {results['skipped']}")
    except Exception as e:
        logger.error(f"Error in map_all: {e}")
        raise

def map_nct(nct_id, nct_files_path, ctml_files_path):
    """Map a specific NCT ID to CTML format"""
    from src.trial_map_manager import TrialMapManager
    
    try:
        manager = TrialMapManager()
        success = manager.map_single_trial(nct_id, nct_files_path, ctml_files_path)
        if success:
            logger.info(f"Successfully mapped {nct_id}")
        else:
            logger.error(f"Failed to map {nct_id}")
    except Exception as e:
        logger.error(f"Error in map_nct: {e}")
        raise

if __name__ == "__main__":
    logger.add('logs/nct2ctml.log', rotation = '1 MB', encoding="utf-8", format="{time} {level} - Line: {line} - {message}")
    main()