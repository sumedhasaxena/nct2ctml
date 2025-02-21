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
    result = {"or": []}
    
    # Extract the diagnosis list
    diagnoses = clinical_critera.pop("oncotree_primary_diagnosis")
    
    for diagnosis in diagnoses:
        clinical_entry = {
            "clinical": {
                **clinical_critera,  # Duplicate all other keys
                "oncotree_primary_diagnosis": diagnosis  # Add the current diagnosis
            }
        }
        result["or"].append(clinical_entry)    
    return result