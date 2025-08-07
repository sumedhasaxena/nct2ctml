"""
Trial Synchronization Manager

This module provides a manager for trial synchronization, handling the core logic for fetching, caching, and updating trial data.
"""

import csv
import os
import requests
import urllib.parse
from datetime import datetime
from typing import List, Dict, Set
from loguru import logger
import src.trial_config as config
import src.trial_data_helper as tdh


class TrialSyncManager:
    """Manager for trial synchronization"""
    
    def __init__(self):
        self.api_base_url = "https://clinicaltrials.gov/api/v2/"
        self.trial_status_file = "cache/nct/trial_status.csv"
        self.local_trial_file = "ref/local_trial_info.csv"
        self.cache_nct_dir = "cache/nct"
        self.cache_ctml_dir = "cache/ctml"
        
        # Ensure directories exist
        os.makedirs(self.cache_nct_dir, exist_ok=True)
        self._ensure_trial_status_file()
    
    def _ensure_trial_status_file(self):
        """Create trial_status.csv if it doesn't exist"""
        if not os.path.exists(self.trial_status_file):
            with open(self.trial_status_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['nct_id', 'local_protocol_ids', 'status', 'trial_last_updated_date', 'entry_last_updated_date'])
            logger.info(f"Created new trial_status.csv file")
    
    def get_existing_nct_ids(self) -> Set[str]:
        """Get all NCT IDs from trial_status.csv"""
        nct_ids = set()
        if os.path.exists(self.trial_status_file):
            with open(self.trial_status_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['nct_id'] is not None and row['nct_id'] != 'NA':
                        nct_ids.add(row['nct_id'])
        return nct_ids
    
    def get_local_trial_nct_ids(self) -> Set[str]:
        """Get all NCT IDs from local_trial_info.csv"""
        nct_ids = set()
        if os.path.exists(self.local_trial_file):
            with open(self.local_trial_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['nct_id'] is not None and row['nct_id'] != 'NA':
                        nct_ids.add(row['nct_id'])
        return nct_ids
    
    def get_trial_status(self, nct_id: str) -> Dict:
        """Get current status of a trial from trial_status.csv"""
        if not os.path.exists(self.trial_status_file):
            return None
            
        with open(self.trial_status_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['nct_id'] == nct_id:
                    return row
        return None
    
    def get_nct_local_status(self, trial: dict) -> str:
        overall_status = trial['status']
        if overall_status.lower() != 'recruiting':
            return 'closed'
        else:
            is_recruiting_in_hk = tdh.check_if_recruiting_in_HK(trial['full_data'])
            if is_recruiting_in_hk:
                return 'open'
            else:
                return 'closed'


    def fetch_trials_from_api(self) -> List[Dict]:
        """Fetch trial summaries from clinicaltrials.gov API"""
        endpoint = "studies"
        
        # Default filters
        params = {
            'query.cond': 'cancer',
            'query.locn': 'Hong Kong',
            #'filter.overallStatus': 'RECRUITING',
            'query.term': 'AREA[StudyType]INTERVENTIONAL',
            'pageSize': 50,
            'sort': 'LastUpdatePostDate',
            'fields': 'NCTId|OverallStatus|LastUpdatePostDate|InterventionType|Location'
        }
        
        trials = []
        
        while True:
            endpoint_url = f'{urllib.parse.urljoin(self.api_base_url, endpoint)}?{urllib.parse.urlencode(params)}'
            logger.info(f"Fetching trials from: {endpoint_url}")
            
            try:
                response = requests.get(endpoint_url)
                response.raise_for_status()
                json_response = response.json()
                
                for study in json_response['studies']:
                    nct_id = study['protocolSection']['identificationModule']['nctId']
                    status = study['protocolSection']['statusModule']['overallStatus']
                    last_update_date = study['protocolSection']['statusModule']['lastUpdatePostDateStruct']['date']
                    
                    # Check if trial meets criteria
                    if self._meets_criteria(study):
                        trials.append({
                            'nct_id': nct_id,
                            'status': status,
                            'last_update_date': last_update_date,
                            'full_data': study
                        })
                        logger.info(f"Found trial: {nct_id} - {status}")
                    else:
                        logger.debug(f"Trial {nct_id} does not meet criteria, skipping")
                
                # Check for next page
                if 'nextPageToken' not in json_response or not json_response['nextPageToken']:
                    break
                    
                params['pageToken'] = json_response['nextPageToken']
                
            except requests.RequestException as e:
                logger.error(f"Error fetching trials: {e}")
                break
        
        return trials
    
    def _meets_criteria(self, study: Dict) -> bool:
        """Check if trial meets our filtering criteria"""
        try:
            # Check if recruiting in Hong Kong
            # if not tdh.check_if_recruiting_in_HK(study):
            #     return False
            
            # Check if has correct intervention types
            if not tdh.has_correct_intervention(study, config.intervention_types):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking trial criteria: {e}")
            return False
    
    def fetch_and_cache_trial(self, nct_id: str) -> bool:
        """Fetch individual trial data and cache it"""
        try:        
            
            NCT_STUDY_ENDPOINT = "studies/{0}".format(nct_id)
            endpoint_url = urllib.parse.urljoin(self.api_base_url, NCT_STUDY_ENDPOINT)
            
            response = requests.get(endpoint_url)
            response.raise_for_status()
            study = response.json()
            
            if study:
                # Remove unused keys to save space
                tdh.remove_unused_keys(study)
                # Save to cache
                tdh.save_to_file(study, self.cache_nct_dir, nct_id, 'json')
                logger.info(f"Successfully cached trial {nct_id}")
                return True
            else:
                logger.warning(f"No trial found for NCT ID: {nct_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error fetching trial {nct_id}: {e}")
            return False
    
    def modify_trial_status_file(self, nct_id: str, local_protocol_ids:str, status: str, last_update_date: str, action: str):
        """Update trial_status.csv with new information"""
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        if action == 'insert':
            # Add new row
            with open(self.trial_status_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([nct_id, local_protocol_ids, status, last_update_date, current_date])
            logger.info(f"Inserted trial {nct_id} with status {status}")
            
        elif action == 'update':
            # Update existing row - each NCT ID should be unique
            records = []
            updated = False
            with open(self.trial_status_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['nct_id'] == nct_id:
                        if local_protocol_ids != '':                            
                            # Only set if the caller has a local_protocol_ids value to set, else preserve existing value
                            row['local_protocol_ids'] = local_protocol_ids
                        if status != '':
                            row['status'] = status
                        if last_update_date != '':
                            row['trial_last_updated_date'] = last_update_date
                        row['entry_last_updated_date'] = current_date
                        updated = True
                    records.append(row)
            
            if updated:
                with open(self.trial_status_file, 'w', newline='', encoding='utf-8') as file:
                    fieldnames = ['nct_id', 'local_protocol_ids', 'status', 'trial_last_updated_date', 'entry_last_updated_date']
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(records)
                logger.info(f"Updated trial {nct_id} with status {status}")
            else:
                logger.warning(f"Trial {nct_id} not found in trial_status.csv for update")
            
        elif action == 'close':
            # Close trial (set status to 'closed')
            self.modify_trial_status_file(nct_id, 'closed', last_update_date, 'update')
            logger.info(f"Closed trial {nct_id}")
    
    def sync_trials(self):
        """Main synchronization method"""
        logger.info("Starting trial synchronization")
        
        # Step 1: Get existing and local NCT IDs
        existing_nct_ids = self.get_existing_nct_ids()
        local_trial_nct_ids = self.get_local_trial_nct_ids()
        
        logger.info(f"Found {len(existing_nct_ids)} existing trials and {len(local_trial_nct_ids)} local trials")
        
        # Step 2: Fetch trials from API
        nct_trials = self.fetch_trials_from_api()
        logger.info(f"Retrieved {len(nct_trials)} trials from API")
        
        # Step 3: Classify and process trials
        to_be_inserted = []
        to_be_updated = []
        to_be_closed = []
        
        for trial in nct_trials:
            nct_id = trial['nct_id']
            nct_last_update_date = trial['last_update_date']
            nct_local_status = self.get_nct_local_status(trial)
            trial['status'] = nct_local_status
            if nct_id not in existing_nct_ids:
                # New trial
                if trial['status'].lower() == "open" or nct_id in local_trial_nct_ids:
                # Either its a new open trial, or a closed trial for which we have a local PI.
                # In latter case, we still record local PI info and insert in the system with status as closed
                    to_be_inserted.append(trial)
                else:
                    logger.info(f"Skipping closed trial {nct_id} (not in local trials)")
            else:
                # Existing trial
                existing_trial = self.get_trial_status(nct_id)
                if existing_trial:
                    if existing_trial['status'].lower() != 'closed' and trial['status'].lower() == 'closed':
                        to_be_closed.append(trial)
                    elif nct_last_update_date > existing_trial['trial_last_updated_date']:
                        to_be_updated.append(trial)
                    else:
                        logger.debug(f"Trial {nct_id} - no action needed")
        
        # Step 4: Process insertions
        logger.info(f"Processing {len(to_be_inserted)} insertions")
        for trial in to_be_inserted:
            if self.fetch_and_cache_trial(trial['nct_id']):
                self.modify_trial_status_file(
                    trial['nct_id'], 
                    '',
                    trial['status'], 
                    trial['last_update_date'], 
                    'insert'
                )
        
        # Step 5: Process updates
        logger.info(f"Processing {len(to_be_updated)} updates")
        for trial in to_be_updated:
            if self.fetch_and_cache_trial(trial['nct_id']):
                self.modify_trial_status_file(
                    trial['nct_id'], 
                    '',
                    trial['status'], 
                    trial['last_update_date'], 
                    'update'
                )
        
        # Step 6: Process closures
        logger.info(f"Processing {len(to_be_closed)} closures")
        for trial in to_be_closed:
            self.modify_trial_status_file(
                trial['nct_id'], 
                '',
                trial['status'], 
                trial['last_update_date'], 
                'close'
            )
        
        # Step 7: Merge local trial info in trial_status.csv
        logger.info("Merging local trial info into trial_status.csv")
        local_trials_merged = 0
        with open(self.local_trial_file, 'r', newline='', encoding='utf-8') as local_trials_file:
            local_trial_file_reader = csv.DictReader(local_trials_file)
            for local_trial_file_row in local_trial_file_reader:
                local_protocol_ids = local_trial_file_row['local_protocol_ids'].strip()
                if local_trial_file_row['nct_id'] == 'NA':                    
                    with open(self.trial_status_file, 'r', newline='', encoding='utf-8') as trial_status_file:
                        trial_status_file_reader = csv.DictReader(trial_status_file)
                        local_protocol_record_found = False
                        for trial_status_file_row in trial_status_file_reader:
                            if trial_status_file_row['local_protocol_ids'] == local_protocol_ids:
                                local_protocol_record_found = True #already exists, no need to make any updates
                                break
                        if not local_protocol_record_found:
                            self.modify_trial_status_file(
                                'NA',
                                local_protocol_ids, 
                                'open', 
                                datetime.now().strftime('%Y-%m-%d'), 
                                'insert'
                            )
                            local_trials_merged = local_trials_merged + 1
                else: #try to update existing NCT entry in trial_status.csv, assuming it is present. 
                    #If not, the trial should be pulled from clinicaltrials.gov in next run.
                    self.modify_trial_status_file(
                                local_trial_file_row['nct_id'],
                                local_protocol_ids, 
                                '', #don't change status, just update local_protocol_ids
                                datetime.now().strftime('%Y-%m-%d'), 
                                'update'
                            )
                    local_trials_merged = local_trials_merged + 1
              
        logger.info("Trial synchronization completed!")
        
        return {
            'api_trials_processed': len(nct_trials),
            'insertions': len(to_be_inserted),
            'updates': len(to_be_updated),
            'closures': len(to_be_closed),
            'local_trials_merged': local_trials_merged
        }


def main():
    """Simple entry point"""
    sync = TrialSyncManager()
    results = sync.sync_trials()
    
    print(f"\nSync Results:")
    print(f"API Trials Processed: {results['api_trials_processed']}")
    print(f"Insertions: {results['insertions']}")
    print(f"Updates: {results['updates']}")
    print(f"Closures: {results['closures']}")
    print(f"Local Trials Merged: {results['local_trials_merged']}")


if __name__ == "__main__":
    main() 