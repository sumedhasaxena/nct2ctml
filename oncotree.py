import csv
from collections import defaultdict
import config

def get_oncotree_data():
    ONCOTREE_TXT_FILE_PATH = config.ONCOTREE_TXT_FILE_PATH
    level_1_list = set()
    maintype_list = set()
    mapping = defaultdict(set)
    with open(ONCOTREE_TXT_FILE_PATH) as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = [row for row in reader]
    
    for row in rows:        
        maintype = row['metamaintype']
        maintype_list.add(maintype)

        level_1 = row['level_1'].split('(')[0].strip()
        level_2 = row['level_2'].split('(')[0].strip()
        level_3 = row['level_3'].split('(')[0].strip()
        level_4 = row['level_4'].split('(')[0].strip()
        level_5 = row['level_5'].split('(')[0].strip()
        level_6 = row['level_6'].split('(')[0].strip()
        level_7 = row['level_7'].split('(')[0].strip()
        
        level_1_list.add(level_1)

        mapping[level_1].update({level_2, level_3, level_4, level_5, level_6, level_7})        
    
    for s in mapping.values():
        if '' in s:
            s.remove('')

    return level_1_list, maintype_list, mapping

level_1_list, maintype_list,level1_mapping = get_oncotree_data()
