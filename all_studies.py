import clinical_trials_gov
import csv

def main():
    all_nctIds = clinical_trials_gov.get_all_studies()

    with open('nct_ids.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        for nct_id in all_nctIds:
            writer.writerow([nct_id])


if __name__ == "__main__":
    main()