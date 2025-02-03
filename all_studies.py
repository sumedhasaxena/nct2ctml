"""
This script contains method to get NCT_IDS of all studies from clinicaltrials.gov
and write the result in a CSV file
Designed to also run as a standalone script
"""

import clinical_trials_gov
import csv

def main():
    all_nctIds = clinical_trials_gov.get_all_studies()

    with open('results/nct_ids.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        for nct_id in all_nctIds:
            writer.writerow([nct_id])


if __name__ == "__main__":
    main()