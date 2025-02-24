import config

def get_keywords_from_conditions(conditions_list):
    all_keywords = set()
    for cond in conditions_list:
        cond_keywords = [word for part in cond.split(',') for word in part.split() if word]
        for cond_keyword in cond_keywords:
            if cond_keyword.lower() not in config.keywords_to_remove:
                all_keywords.add(cond_keyword)
    return all_keywords

def convert_to_ctml_clinical_schema(clinical_critera) -> dict:    
    # Extract the diagnosis list
    diagnoses = clinical_critera.pop("oncotree_primary_diagnosis")

    if diagnoses and len(diagnoses) > 1: #incase of multiple diagnoses, put the result under 'or' operator
        result = {"or": []}    
        for diagnosis in diagnoses:
            clinical_ctml = {
                "clinical": {
                    **clinical_critera,  # Duplicate all other keys
                    "oncotree_primary_diagnosis": diagnosis  # Add the current diagnosis
                }
            }
            result["or"].append(clinical_ctml)
        return result
    else:         
        clinical_ctml = {
                "clinical": {
                    **clinical_critera,  # Add all other keys
                    "oncotree_primary_diagnosis": diagnoses[0]  # Add the only diagnosis
                }
            }
        result = clinical_ctml
        return result
    
def convert_to_ctml_genomic_schema(genomic_critera) -> dict:      
    return {}

def combine_clinical_and_genomic_ctml(clinical_ctml, genomic_ctml):
    if genomic_ctml and len(genomic_ctml) > 0:
        match_result = {"and": []} 
        match_result["and"].append(clinical_ctml)
        match_result["and"].append(genomic_ctml)
        return match_result
    else:
        match_result = clinical_ctml
        return match_result
