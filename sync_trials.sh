#!/bin/bash

# Sync trials from clinicaltrials.gov to CTML
# Runs 'pull all' and 'map all' commands continuously

# Configuration - Edit this to change interval
SLEEP_HOURS=24

echo "Starting trial sync (every $SLEEP_HOURS hours)"
echo "Press Ctrl+C to stop"
echo ""

# Convert hours to seconds
SLEEP_SECONDS=$((SLEEP_HOURS * 3600))

while true; do
    echo "[$(date)] Running trial sync..."
    
    # Run pull all
    echo "Running: python main.py pull --all"
    python main.py pull --all
    
    # Run map all
    # Uses MAPPING_CUTOFF_DAYS days from config.py.
    # Maps the trials for which last_updated_date is within MAPPING_CUTOFF_DAYS days.
    echo "Running: python main.py map --all"
    python main.py map --all
    
    echo "[$(date)] Trial sync completed"
    echo "Next sync in $SLEEP_HOURS hours at $(date -d "+$SLEEP_HOURS hours")"
    echo "----------------------------------------"
    
    # Sleep until next cycle
    sleep $SLEEP_SECONDS
done
