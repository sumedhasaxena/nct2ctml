import csv

ONCOTREE_TXT_FILE_PATH = "ref\oncotree_file.txt"

def get_oncotree_data():
    level_1_list = set()
    maintype_list = set()
    with open(ONCOTREE_TXT_FILE_PATH) as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = [row for row in reader]
    
    for row in rows:
        level_1 = row['level_1'].split('(')[0].strip()
        level_1_list.add(level_1)
        maintype = row['metamaintype']
        maintype_list.add(maintype)
    return level_1_list, maintype_list


item1, item2 = get_oncotree_data()
print(item1)
print(item2)