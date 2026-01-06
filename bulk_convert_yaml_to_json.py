import yaml
import json
import os

yaml_files_path = "ctml/reviewed"
json_files_path = "ctml/json"

# Optionally specify a list of NCT IDs to process
# If None or empty, all YAML files in yaml_files_path will be processed
nct_ids = [
"NCT03486873",
"NCT06252649",
"NCT07005128",
"NCT06136559",
"NCT06997497",
"NCT06151574",
"NCT05920356",
"NCT05961410",
"NCT05183984",
"NCT06632717",
"NCT06249854",
"NCT04725994",
"NCT06234397",
"NCT06235437",
"NCT05620628",
"NCT06035757",
"NCT06545526",
"NCT05245656",
"NCT04807257",
"NCT05771584",
"NCT06495463",
"NCT05880043",
"NCT06490328",
"NCT05048901",
"NCT06186076",
"NCT05532696",
"NCT05948475",
"NCT06095583",
"NCT06466265",
"NCT05720260",
"NCT06436976",
"NCT04227509",
"NCT04373564",
"NCT05957822",
"NCT02934568",
"NCT05528458",
"NCT04298008",
"NCT04371224",
"NCT06327269",
"NCT06344715",
"NCT05477264",
"NCT05048524",
"NCT06326502",
"NCT05998447",
"NCT06265025",
"NCT05661643",
"NCT04903873",
"NCT05783570",
"NCT05798026",
"NCT05438420",
"NCT05872867",
"NCT05905887",
"NCT05226169",
"NCT01935778",
"NCT04309578",
"NCT05184803",
"NCT01917552",
"NCT06075849",
"NCT05949333",
"NCT06262386",
"NCT04984668",
"NCT05358379",
"NCT05743504",
"NCT04983810",
"NCT06217848",
"NCT05629429",
"NCT03944304",
"NCT06162650",
"NCT06156527",
"NCT03664895",
"NCT05876806",
"NCT04564521",
"NCT04338763",
"NCT05376423",
"NCT04999332",
"NCT05141877",
"NCT05230680",
"NCT04938583",
"NCT04817540",
"NCT03616782",
"NCT03697356",
"NCT05926336",
"NCT05525247",
"NCT03447951",
"NCT06034977",
"NCT05338619",
"NCT05841472",
"NCT05767684",
"NCT05904457",
"NCT05892146",
"NCT05606692",
"NCT05663242",
"NCT03544099",
"NCT05204862",
"NCT05280457",
"NCT05766410",
"NCT05768282",
"NCT03183115",
"NCT05750290",
"NCT05727410",
"NCT05210907",
"NCT05331911",
"NCT05429697",
"NCT02859402",
"NCT05497102",
"NCT05469022",
"NCT05455918",
"NCT05439993",
"NCT05338931",
"NCT04894188",
"NCT05292573",
"NCT04835584",
"NCT04787354",
"NCT04969731",
"NCT04763616",
"NCT04943653",
"NCT04836507",
"NCT03176199",
"NCT04278469",
"NCT04063527",
"NCT01970748",
"NCT04046159",
"NCT01926821",
"NCT04077099",
"NCT06712355"
]


if nct_ids:
    # Process only specified NCT IDs
    for nct_id in nct_ids:
        yaml_file_name = f"{nct_id}.yaml"
        yaml_file_path = os.path.join(yaml_files_path, yaml_file_name)
        
        if not os.path.exists(yaml_file_path):
            print(f"Warning: File not found: {yaml_file_path}")
            continue
        
        json_file_name = f"{nct_id}.json"
        json_file_path = os.path.join(json_files_path, json_file_name)

        with open(yaml_file_path, 'r', encoding='utf-8') as yaml_file:
            yaml_content = yaml.safe_load(yaml_file)

        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(yaml_content, json_file, indent=4)

        print(f"Converted {yaml_file_path} to {json_file_path}")
else:
    # Process all YAML files in the directory
    for file in os.listdir(yaml_files_path):
        if file.endswith(".yaml") or file.endswith(".yml"):
            yaml_file_path = os.path.join(yaml_files_path, file)
            json_file_name = os.path.splitext(file)[0] + ".json"
            json_file_path = os.path.join(json_files_path, json_file_name)

            with open(yaml_file_path, 'r', encoding='utf-8') as yaml_file:
                yaml_content = yaml.safe_load(yaml_file)

            with open(json_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(yaml_content, json_file, indent=4)

            print(f"Converted {yaml_file_path} to {json_file_path}")


