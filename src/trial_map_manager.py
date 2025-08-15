"""
Trial Map Manager

This module handles the mapping of NCT trial data to CTML format.
"""

import csv
import os
from datetime import datetime
from typing import Dict, List
from loguru import logger
import src.clinical_trials_gov as ctg
import src.trial_data_helper as tdh


class TrialMapManager:
    """Manager for trial data mapping to CTML format"""
    
    def __init__(self):
        self.local_trial_file = 'ref/local_trial_info.csv'
        self.trial_status_file = 'cache/nct/trial_status.csv'
    
    def get_gene_list(self) -> List[str]:
        """Load gene list from reference file"""
        genes = []
        try:
            with open('ref/genes.txt', 'r') as file:     
                genes = [line.strip() for line in file.readlines()]
        except FileNotFoundError:
            logger.warning("Gene list file not found: ref/genes.txt")
        return genes
    
    def load_trial_status_dict(self) -> Dict[str, Dict]:
        """Load trial status information into a dictionary"""
        trial_status_dict = {}
        if os.path.exists(self.trial_status_file):
            with open(self.trial_status_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    trial_status_dict[row['nct_id']] = row
        return trial_status_dict
    
    def load_local_trial_dict(self) -> Dict[str, Dict]:
        """Load local trial info into a consolidated dictionary with key as nct_id"""
        local_trial_dict = {}
        if os.path.exists(self.local_trial_file):
            with open(self.local_trial_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    nct_id = row['nct_id']
                    local_protocol_id = row['local_protocol_ids'].strip()
                    pi_name = row['pi_name'].strip()
                    pi_institution = row['pi_institution'].strip()
                    
                    # Only process trials with valid NCT IDs (skip 'NA' entries)
                    if nct_id != 'NA':
                        if nct_id not in local_trial_dict:
                            local_trial_dict[nct_id] = {
                                'nct_id': nct_id,
                                'local_protocol_ids': local_protocol_id,
                                'pi_names': pi_name,
                                'pi_institutions': pi_institution
                            }
                        else:
                            # Append multiple local_protocol_ids with pipe separator
                            existing_protocols = local_trial_dict[nct_id]['local_protocol_ids']
                            if local_protocol_id not in existing_protocols:
                                local_trial_dict[nct_id]['local_protocol_ids'] = f"{existing_protocols}|{local_protocol_id}"
                            
                            # Append multiple pi_names with pipe separator
                            existing_pi_names = local_trial_dict[nct_id]['pi_names']
                            if pi_name not in existing_pi_names:
                                local_trial_dict[nct_id]['pi_names'] = f"{existing_pi_names}|{pi_name}"
                            
                            # Append multiple pi_institutions with pipe separator
                            existing_pi_institutions = local_trial_dict[nct_id]['pi_institutions']
                            if pi_institution not in existing_pi_institutions:
                                local_trial_dict[nct_id]['pi_institutions'] = f"{existing_pi_institutions}|{pi_institution}"
        
        return local_trial_dict
    
    def _add_local_trial_info(self, mapped_ctml: dict, nct_id: str) -> None:
        """
        Add local trial information to the mapped CTML data.
        This method handles the common logic for both map_all_trials and map_single_trial.
        
        Parameters
        ----------
        mapped_ctml : dict
            The CTML data to be updated with local trial info
        nct_id : str
            The NCT ID to look up in local trial info
        """
        if os.path.exists(self.local_trial_file):
            with open(self.local_trial_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                local_protocol_ids_list = []
                local_pi_names_list = []
                local_pi_institutions_list = []
                
                for row in reader:
                    if row['nct_id'] == nct_id:
                        local_protocol_ids_list.append(row['local_protocol_ids'].strip())
                        local_pi_names_list.append(row['pi_name'].strip())
                        local_pi_institutions_list.append(row['pi_institution'].strip())
                
                if local_protocol_ids_list:
                    # Convert protocol IDs to list (handle any existing pipe separators)
                    local_protocol_ids_str = '|'.join(local_protocol_ids_list)
                    local_protocol_ids_list_final = tdh.convert_protocol_ids_to_list(local_protocol_ids_str)
                    mapped_ctml['protocol_ids'] = local_protocol_ids_list_final
                    logger.info(f"Added local protocol IDs: {local_protocol_ids_list_final}")
                    
                    # Handle PI names - convert pipe to comma and append to existing if present
                    local_pi_names = ', '.join(local_pi_names_list)
                    if mapped_ctml['principal_investigator']:
                        mapped_ctml['principal_investigator'] = f"{mapped_ctml['principal_investigator']}, {local_pi_names}"
                    else:
                        mapped_ctml['principal_investigator'] = local_pi_names
                    logger.info(f"Added local PI names: {local_pi_names}")
                    
                    # Handle PI institutions - convert pipe to comma and append to existing if present
                    local_pi_institutions = ', '.join(local_pi_institutions_list)
                    if mapped_ctml['principal_investigator_institution']:
                        mapped_ctml['principal_investigator_institution'] = f"{mapped_ctml['principal_investigator_institution']}, {local_pi_institutions}"
                    else:
                        mapped_ctml['principal_investigator_institution'] = local_pi_institutions
                    logger.info(f"Added local PI institutions: {local_pi_institutions}")
                    
                else:
                    mapped_ctml['protocol_ids'] = []
                    logger.info("No local trial info found")
        else:
            mapped_ctml['protocol_ids'] = []
            logger.info("Local trial info file not found")
    
    def map_all_trials(self, nct_files_path: str, ctml_files_path: str) -> Dict[str, int]:
        """Map all NCT files to CTML format with local trial info integration"""
        current_date = datetime.now().strftime('%Y-%m-%d')
        genes = self.get_gene_list()
        
        # Load data dictionaries
        trial_status_dict = self.load_trial_status_dict()
        local_trial_dict = self.load_local_trial_dict()
        
        logger.info(f"Loaded {len(trial_status_dict)} trial status records")
        logger.info(f"Loaded {len(local_trial_dict)} local trial records")
        
        processed_count = 0
        skipped_count = 0
        
        for file_name in os.listdir(nct_files_path):
            if os.path.isfile(os.path.join(nct_files_path, file_name)) and file_name.endswith('.json'):
                nct_id = file_name.split('.')[0]
                
                # Check if this trial was updated today in trial_status.csv
                if nct_id in trial_status_dict:
                    entry_last_updated_date = trial_status_dict[nct_id]['entry_last_updated_date']
                    if entry_last_updated_date != current_date:
                        logger.info(f"Skipping NCT ID: {nct_id} - not updated today (last updated: {entry_last_updated_date})")
                        skipped_count += 1
                        continue
                else:
                    logger.info(f"Skipping NCT ID: {nct_id} - not found in trial_status.csv")
                    skipped_count += 1
                    continue
                
                try:
                    logger.info(f"Mapping NCT ID: {nct_id}")   
                    logger.info("-----------------------")
                    
                    trial_data = tdh.read_from_file(nct_files_path, nct_id, 'json')
                    
                    # Map to CTML format
                    mapped_ctml = ctg.map_nct_to_ctml(trial_data, genes)
                    
                    # Add local trial info if available
                    if nct_id in local_trial_dict:
                        local_info = local_trial_dict[nct_id]
                        
                        # Add local protocol IDs - convert to list
                        local_protocol_ids_str = local_info['local_protocol_ids']
                        local_protocol_ids_list = tdh.convert_protocol_ids_to_list(local_protocol_ids_str)
                        mapped_ctml['protocol_ids'] = local_protocol_ids_list
                        logger.info(f"Added local protocol IDs: {local_protocol_ids_list}")
                        
                        # Handle PI names - convert pipe to comma and append to existing if present
                        local_pi_names = local_info['pi_names'].replace('|', ', ')
                        if mapped_ctml['principal_investigator']:
                            mapped_ctml['principal_investigator'] = f"{mapped_ctml['principal_investigator']}, {local_pi_names}"
                        else:
                            mapped_ctml['principal_investigator'] = local_pi_names
                        logger.info(f"Added local PI names: {local_pi_names}")
                        
                        # Handle PI institutions - convert pipe to comma and append to existing if present
                        local_pi_institutions = local_info['pi_institutions'].replace('|', ', ')
                        if mapped_ctml['principal_investigator_institution']:
                            mapped_ctml['principal_investigator_institution'] = f"{mapped_ctml['principal_investigator_institution']}, {local_pi_institutions}"
                        else:
                            mapped_ctml['principal_investigator_institution'] = local_pi_institutions
                        logger.info(f"Added local PI institutions: {local_pi_institutions}")
                        
                    else:
                        # Fall back to reading from file for this specific trial
                        self._add_local_trial_info(mapped_ctml, nct_id)
                    
                    # Save CTML files
                    tdh.save_to_file(mapped_ctml, ctml_files_path, nct_id, 'yaml')
                    #tdh.save_to_file(mapped_ctml, ctml_files_path, nct_id, 'json')
                    
                    processed_count += 1
                    logger.info(f"Successfully mapped and saved {nct_id}")
                    
                except Exception as ex:
                    logger.error(f"nct_id: {nct_id} | Unexpected {ex=}, {type(ex)=}")
        
        logger.info(f"Mapping completed. Processed: {processed_count}, Skipped: {skipped_count}")
        
        return {
            'processed': processed_count,
            'skipped': skipped_count
        }
    
    def map_single_trial(self, nct_id: str, nct_files_path: str, ctml_files_path: str) -> bool:
        """Map a specific NCT ID to CTML format with local trial info integration"""
        try:
            logger.info(f"Mapping NCT ID: {nct_id}")   
            logger.info("-----------------------")                 
            trial_data = tdh.read_from_file(nct_files_path, nct_id, 'json')
        except FileNotFoundError:
            print(f'File {nct_id}.json not found at {nct_files_path}')
            return False
        except Exception as e:
            print(f'Error reading file {nct_id}.json: {e}')
            return False
        
        genes = self.get_gene_list()

        try:
            # Map to CTML format
            mapped_ctml = ctg.map_nct_to_ctml(trial_data, genes)
            
            # Add local trial info if available
            self._add_local_trial_info(mapped_ctml, nct_id)
            
            # Save CTML file
            tdh.save_to_file(mapped_ctml, ctml_files_path, nct_id, 'yaml')
            
            logger.info(f"Successfully mapped and saved {nct_id}")
            return True
            
        except Exception as ex:
            logger.error(f"nct_id: {nct_id} | Unexpected {ex=}, {type(ex)=}")
            return False


def main():
    """Simple entry point for testing"""
    manager = TrialMapManager()
    
    # Test mapping all trials
    nct_files_path = 'cache/nct'
    ctml_files_path = 'cache/ctml/'
    
    if os.path.exists(nct_files_path):
        results = manager.map_all_trials(nct_files_path, ctml_files_path)
        print(f"Mapping completed. Processed: {results['processed']}, Skipped: {results['skipped']}")
    else:
        print(f"NCT files directory not found: {nct_files_path}")


if __name__ == "__main__":
    main()

