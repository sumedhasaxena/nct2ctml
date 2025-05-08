
import sys
import os
import json 
sys.path.append(os.path.abspath('../'))

import utils.ai_helper as ai
import argparse

def get_patent_genomic_data(genomic_text:str):
   response = ai.get_patient_genomic_criteria('case1', genomic_text)
   return response

def main(text_file: str):
    current_dir = os.path.dirname(__file__)
    
    # Construct the full path to the TXT file
    TXT_FILE_PATH = os.path.join(current_dir, '../extracted_text', text_file)
    with open(TXT_FILE_PATH, 'r') as file:
        content = file.read()
        response = get_patent_genomic_data(content)
        output_path = os.path.join(current_dir, '../genomic_json')
        with open(f'{output_path}/{os.path.splitext(text_file)[0]}.json', "w") as json_file: 
            json.dump(response, json_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert plan text genomic data to matchminer compliant form.")
    parser.add_argument("text_file", type=str, help="Name of text file containing genomic criteria")
    args = parser.parse_args()

    main(args.text_file)

