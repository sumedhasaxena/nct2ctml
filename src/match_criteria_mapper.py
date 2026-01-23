import config
import utils.aho_corasick as ac
import src.trial_data_helper as tdh

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
        
        result = {"and":[]}
        diagnosis_result = {"or": []}
        for diagnosis in diagnoses:
            diagnosis_ctml = {
                "clinical": {                    
                    "oncotree_primary_diagnosis": diagnosis
                }
            }
            diagnosis_result["or"].append(diagnosis_ctml)        
        
        other_clinical_ctml = {
                "clinical": {
                    **clinical_critera
                }
            }
        result["and"].append(diagnosis_result)
        result["and"].append(other_clinical_ctml)
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

# Checks that the genomic crietria returned by AI model is not empty and has "hugo_symbol", "variant_category" keys
def convert_to_ctml_genomic_schema(inclusion_genomic_criteria: list, exclusion_genomic_criteria: list) -> dict: 
    inclusions = []
    exclusions = []
    print(tdh.get_all_keys(inclusion_genomic_criteria))
    print(tdh.get_all_keys(exclusion_genomic_criteria))
    if inclusion_genomic_criteria and all(key in tdh.get_all_keys(inclusion_genomic_criteria) for key in ["hugo_symbol", "variant_category"]):
        #post processing
        inclusion_genomic_criteria = tdh.update_hugo_symbol(inclusion_genomic_criteria)
        for alteration in inclusion_genomic_criteria:
            variant_category = alteration["genomic"]["variant_category"]
            # if variant_category begins with !, add alteration to exclusions, without removing !
            if variant_category.startswith('!'):
                exclusions.append(alteration)
            else:
                inclusions.append(alteration)
    
    if exclusion_genomic_criteria and all(key in tdh.get_all_keys(exclusion_genomic_criteria) for key in ["hugo_symbol", "variant_category"]):
        #post processing
        exclusion_genomic_criteria = tdh.update_hugo_symbol(exclusion_genomic_criteria)
        for alteration in exclusion_genomic_criteria:
            exclusions.append(alteration)

    print(f'Inclusions: {inclusions}')
    print(f'Exclusions: {exclusions}')

    #combine inclusions with a top level 'or' and exclusions with a top level 'and'
    if inclusions:
        if len(inclusions) == 1:
            inclusion_genomic_criteria_ctml = inclusions
        else:
            inclusion_genomic_criteria_ctml = {"or": inclusions}
    else:
        inclusion_genomic_criteria_ctml = {}

    print(f'inclusion_genomic_criteria_ctml: {inclusion_genomic_criteria_ctml}')

    if exclusions:
        if len(exclusions) == 1:
            exclusion_genomic_criteria_ctml = exclusions
        else:
            exclusion_genomic_criteria_ctml = {"and": exclusions}
    else:
        exclusion_genomic_criteria_ctml = {}

    print(f'exclusion_genomic_criteria_ctml: {exclusion_genomic_criteria_ctml}')

    #combine both inclusion and exclusion criteria under a top level 'and'
    if inclusion_genomic_criteria_ctml and exclusion_genomic_criteria_ctml:
        inclusion_exclusion_genomic_criteria_ctml = {"and": [inclusion_genomic_criteria_ctml, exclusion_genomic_criteria_ctml]}
        return inclusion_exclusion_genomic_criteria_ctml
    elif inclusion_genomic_criteria_ctml:
        return inclusion_genomic_criteria_ctml
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

def check_if_eligibility_criteria_contains_gene_info(genes:list, eligibility):
    print("looking for gene keywords")
    contains = ac.search_keywords_in_text(genes, eligibility)
    return contains

def check_if_eligibility_criteria_contains_pdl1_info(nct_keywords:list, eligibility):
    pdl1_keywords_to_check = ['pdl1', 'pd-l1']
    nct_keywords_string = ', '.join(nct_keywords)
    print("looking for PDL1 keywords")
    contains = ac.search_keywords_in_text(pdl1_keywords_to_check, nct_keywords_string)
    if contains:
        return True
    else:
        contains = ac.search_keywords_in_text(pdl1_keywords_to_check, eligibility)
        return contains
    
def check_if_eligibility_criteria_contains_mmr_info(nct_keywords:list, eligibility):
    mmr_keywords_to_check = ['mmr', 'Mismatch Repair', 'msi', 'msi-h','dMMR','msi-l','MSI-high','MSI-low']
    nct_keywords_string = ', '.join(nct_keywords)
    print("looking for MMR keywords")
    contains = ac.search_keywords_in_text(mmr_keywords_to_check, nct_keywords_string)
    if contains:
        return True
    else:
        contains = ac.search_keywords_in_text(mmr_keywords_to_check, eligibility)
        return contains