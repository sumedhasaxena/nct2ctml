"""
This script contains method to get NCT_IDS of all studies from clinicaltrials.gov
and write the result in a CSV file
Designed to also run as a standalone script
"""

import src.clinical_trials_gov as ctg
import csv

def main():
    nct_data = ctg.get_all_studies()

    with open('../cache/nct/nct_data.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['NCT ID', 'Conditions', 'Last Updated Date'])
        writer.writerows(nct_data)


if __name__ == "__main__":
    main()