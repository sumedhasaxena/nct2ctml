import os

nct_files_path = '../results/nct'
import trial_data_helper as tdf

intervention_types = set()

for file_name in os.listdir(nct_files_path):
    if os.path.isfile(os.path.join(nct_files_path, file_name)):
        file_components = file_name.split('.')
        if file_components[1] == "json":
            nct_id = file_name.split('.')[0]
            trial_data = tdf.read_from_file(nct_files_path, nct_id, 'json')

            for intervention in trial_data['protocolSection']['armsInterventionsModule']['interventions']:
                intervention_types.add((intervention['type'], nct_id))

print(intervention_types)
print(len(intervention_types))


