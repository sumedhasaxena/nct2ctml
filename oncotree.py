import csv
from collections import defaultdict
import config

def get_all_oncotree_data():
    ONCOTREE_TXT_FILE_PATH = config.ONCOTREE_TXT_FILE_PATH
    level_1_list = set()
    mapping_l1_all = defaultdict(set)

    with open(ONCOTREE_TXT_FILE_PATH) as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = [row for row in reader]
    
    for row in rows:
        level_1 = row['level_1'].split('(')[0].strip()
        level_2 = row['level_2'].split('(')[0].strip()
        level_3 = row['level_3'].split('(')[0].strip()
        level_4 = row['level_4'].split('(')[0].strip()
        level_5 = row['level_5'].split('(')[0].strip()
        level_6 = row['level_6'].split('(')[0].strip()
        level_7 = row['level_7'].split('(')[0].strip()
        
        level_1_list.add(level_1)
        mapping_l1_all[level_1].update({level_2, level_3, level_4, level_5, level_6, level_7}) 
    
    for s in mapping_l1_all.values():
        if '' in s:
            s.remove('')
    return level_1_list, mapping_l1_all

def get_l1_l2_oncotree_data():
    ONCOTREE_TXT_FILE_PATH = config.ONCOTREE_TXT_FILE_PATH
    level_1_list = set()
    mapping_11_l2 = defaultdict(set)

    with open(ONCOTREE_TXT_FILE_PATH) as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = [row for row in reader]
    
    for row in rows:
        level_1 = row['level_1'].split('(')[0].strip()
        level_2 = row['level_2'].split('(')[0].strip()
        level_1_list.add(level_1)
        mapping_11_l2[level_1].update({level_2})   

    for s in mapping_11_l2.values():
        if '' in s:
            s.remove('')

    return level_1_list, mapping_11_l2

#Code to test the file
level_1_list, mapping = get_l1_l2_oncotree_data()
print(level_1_list)
print("-------------------------------")
print(mapping)
