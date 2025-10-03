from loguru import logger
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="NCT to CTML: Pull and map clinical trial data from ClinicalTrials.gov to CTML format.",
        epilog="""
Examples:
  # Pull all updated trials from ClinicalTrials.gov, update trial_status.csv and save trial files to cache/nct
  python main.py pull --all
  
  # Pull a specific trial
  python main.py pull --nct_id NCT03997435
  
  # Map all trials updated within cutoff period (uses config default)
  python main.py map --all
  
  # Map all trials updated in last 14 days
  python main.py map --all --cutoff-days 14
  
  # Map a specific trial
  python main.py map --nct_id NCT03997435
  
  # For continuous automation, use sync_trials.sh
  ./sync_trials.sh
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', required=True, metavar='COMMAND')

    # Subparser for 'pull'
    pull_parser = subparsers.add_parser(
        'pull', 
        help='Pull NCT study data from ClinicalTrials.gov',
        description='Download clinical trial data from ClinicalTrials.gov API and cache locally.',
        epilog="""
Examples:
  python main.py pull --all                    # Pull all eligible trials
  python main.py pull --nct_id NCT03997435    # Pull specific trial  
        """
    )
    pull_group = pull_parser.add_mutually_exclusive_group(required=True)
    
    pull_group.add_argument(
        '--all', 
        action='store_true', 
        help='Pull all eligible trials after comparing status and last updated date as stored in trial_status.csv'
    )    
    pull_group.add_argument(
        '--nct_id', 
        type=str, 
        metavar='NCT_ID',
        help='Pull study data for a specific NCT ID (e.g., NCT03997435)'
    )

    # Subparser for 'map'
    map_parser = subparsers.add_parser(
        'map', 
        help='Map NCT trial data to CTML schema format, including local trial infomation, if any',
        description='Convert downloaded NCT trial data to Clinical Trial Markup Language (CTML) format for MatchMiner.',
        epilog="""
Examples:
  python main.py map --all                           # Map all eligible trials (uses config default)
  python main.py map --all --cutoff-days 14          # Map trials updated in last 14 days
  python main.py map --nct_id NCT03997435            # Map specific trial
        """
    )
    map_group = map_parser.add_mutually_exclusive_group(required=True)
    
    map_group.add_argument(
        '--all', 
        action='store_true', 
        help='Map all eligible NCT files based on last update date in trial_status.csv'
    )
    map_group.add_argument(
        '--nct_id', 
        type=str, 
        metavar='NCT_ID',
        help='Map a specific NCT ID to CTML format'
    )
    
    # Add cutoff days option for map --all
    map_parser.add_argument(
        '--cutoff-days', 
        type=int, 
        metavar='DAYS',
        help='Only with --all. Map trials updated in the last DAYS; overrides MAPPING_CUTOFF_DAYS in the config.'
    )

    args = parser.parse_args()

    nct_files_path = 'cache/nct'
    ctml_files_path = "cache/ctml/"

    if args.command == 'pull':
        if args.all:
            pull_all()
        else:
            pull_nct(args.nct_id)

    elif args.command == 'map':
        if args.all:
            map_all(nct_files_path, ctml_files_path, args)
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
    from src.trial_pull_manager import TrialPullManager
    sync = TrialPullManager()
    sync.pull_single_trial(nct_id)

def map_all(nct_files_path, ctml_files_path, args):
    """Map all NCT files to CTML format"""
    from src.trial_map_manager import TrialMapManager
    
    try:
        manager = TrialMapManager()
        # Get cutoff_days from command line args if provided
        cutoff_days = getattr(args, 'cutoff_days', None)
        results = manager.map_all_trials(nct_files_path, ctml_files_path, cutoff_days)
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
    logger.add('logs/nct2ctml.log', rotation = '1 MB', encoding="utf-8", format="{time} {level} - Line: {line} - {message}", level="INFO")
    main()