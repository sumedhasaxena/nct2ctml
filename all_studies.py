"""
This script contains method to get NCT_IDS of all studies from clinicaltrials.gov
and write the result in a CSV file
Designed to also run as a standalone script
"""

import clinical_trials_gov
import csv

def main():
    nct_data = clinical_trials_gov.get_all_studies()

    with open('results/nct_data.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['NCT ID', 'Conditions', 'Last Updated Date'])
        writer.writerows(nct_data)


if __name__ == "__main__":
    main()