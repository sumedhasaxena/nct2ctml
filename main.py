from clinical_trials_gov import get_nct_data
from trial_data_formatter import format_trial_data, check_if_recruiting_in_HK

def main():
    nct_id = "NCT06225765"
    res = get_nct_data(nct_id)

    #check if recruiting in HK
    is_recruiting = check_if_recruiting_in_HK(res)
    if is_recruiting is False:
        print(f"Trial {nct_id} is not actively recuiting in Hong Kong")
        return
    
    #shorten trial data dictionary
    trial_data = format_trial_data(res)
    print(trial_data)

    #map json fields to yaml schema

if __name__ == "__main__":
    main()