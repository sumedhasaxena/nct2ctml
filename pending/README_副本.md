# nct2ctml

The **nct2ctml** repository is a specialized ETL (Extract, Transform, Load) application for trial and patient data. It provides a CLI interface for various operations. Below is the description of various operations for both trial data and patient data.

#### Trial Data:
- Pulls trial data from [ClinicalTrials.gov](https://clinicaltrials.gov/data-api/api#extapi "ClinicalTrials.gov")
- Converts it to Clinical Trial Markup Language ([CTML](https://matchminer.gitbook.io/matchminer/deployment/ctml-and-trial-curation "CTML")) schema format
- Saves the converted trial files locally.

#### Patient Data:

The repository contains scripts to handle the extraction and load of 2 kinds of patient data:
1. Clinical & demographic data
2. Genomic data

#####  Clinical data:
 - Converts plain text data to matchminer compliant JSON structure for clinical data.

#####  Genomic data:
 - Extract text from image(s) using OCR (surya-OCR)
 - Convert the text to matchminer compliant JSON structure for genomic data

For detailed information about the system architecture and component relationships, see -

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/sumedhasaxena/nct2ctml)
------------
### Overview of Trial Data component

#### Pre-requisites
The trial data component of nct2ctml has been developed using Python 3.12

#### Usage

python main.py [-h] {pull,map} ...

**positional arguments:**
  {pull,map}
  
    pull     Pull NCT study data.
    map      Map NCT IDs to CTML.

Arguments for 'pull' operation:

    --all            Pull all studies
    --existing       Pull existing studies
    --nct_id NCT_ID  Pull study data for a specific NCT ID

Arguments for 'map' operation:

    --all            Map all NCT files
    --nct_id NCT_ID  Map a specific NCT ID

##### Detailed explanation of CLI options:
###### python main.py pull --all
Pulls all NCT trial studies based on locally defined filters. Saves the files locally in JSON format.

###### python main.py pull --nct_id {nct_id}
Pulls the specified NCT trial study. Saves the file locally in JSON format.

###### python main.py pull --existing
Looks up a list of existing NCT Ids that are in matcjminer platform. Pull the overall status of trial as well as the sttaus of trial in HK.

###### python main.py map --all
Assumes that the NCT trial studies are already pulled and stored locally in JSON format. It reads the files and converts them to CTML compliant schema, ready-to-be uploaded to matchminer platform.

###### python main.py map --nct_id {nct_id}

Assumes that the mentioned NCT trial study is already pulled and stored locally in JSON format. It reads the file and converts it to CTML compliant schema, ready-to-be uploaded to matchminer platform.

#### Reference data used:

The trial data component refers to following data:
1.  **Oncotree data:**
 Oncotree is a hierarchical classification system for cancer types that enables precise categorization of trial eligibility based on cancer diagnoses.
 The oncotree data (version: oncotree_2021_11_02) has been pre-downloaded in a text file and used as a referenec for categorizing diagnosis. Location: `ref\oncotree_file.txt`

2. **Genes list:**
The list of genes has been downloaded from cosmic database (https://cancer.sanger.ac.uk/census), and used as reference for defining genomic criteria in CTML. Location: `ref\genes.txt`

------------


### Overview of Patient Data component

#### Pre-requisites
The patient data component of nct2ctml uses following packages:
- python >=3.10
- pyTorch
- surya-ocr
- biopython

#### Description

Unlike trial data, the patient data component uses a pipeline of multiple scripts for extraction/conversion of patient's clinical and genomic data.

**Patient's Genomic Data:**
The conversion of patient's genomic data comprises of following steps:

 **Step1**: Extract the genomic profile of the patient from image(s).
This step uses surya-ocr to extract text from the image.

**Script**: surya_ocr_text_extract.py

**Input**: Name of the image file containing genomic data. The application will look for image in `nct2ctml\patient_data\images` folder.

**Output**: Text file containing extracted data. The file will be stored with same name as image name in the folder: `nct2ctml\patient_data\extracted_text`.

**Usage**:
`python patient_data/surya_ocr_text_extract.py {image.txt}`

>  By default, the code will automatically check the current device and select the GPU with smallest index to run, which is GPU:0. To override this behavior, we can set the TORCH_DEVICE parameter defined in settings.py via environment variable.
> For example, on Linux, run the following command to select GPU:02, before running the script.
   ` export TORCH_DEVICE='cuda:2'`


**Step2**: Conversion of extracted text to matchminer compitable JSON format
This step needs an AI server running that will serve the incoming request to convert extracted text into JSON format that is matchminer compliant.
The details of AI server are present in `config.py`

**Script**: get_patient_genomic_data.py

**Input**: Name of the text file containing genomic data that was extracted from previous step. The application will look for the file in `nct2ctml\patient_data\extracted_text` folder.

**Output**: JSON file containing matchminer compliant genomic data. The file will be stored with same name as text file name in the folder: `nct2ctml\patient_data\genomic_json` .

**Usage**:
`python patient_data/get_patient_genomic_data.py {text_file.txt}`

**Patient's Clinical Data:**

The conversion of patient's clinical data follows following steps:
**Step1**: Convert text based clinicla data to matchminer compitable JSON format
The application expects that the patient's clinical dtaa will already be present in text format. 

**Script**: get_patient_clinical_data.py

**Input**: Name of the text file containing clinical data. The application will look for text file in `nct2ctml\patient_data\clinical_data` folder.

**Output**: JSON file containing matchminer compliant clinical data. The JSON file will be stored with same name as input text file name in the folder: `nct2ctml\patient_data\clinical_json` .

**Usage**:
`python patient_data/get_patient_clinical_data.py {clinical_data.txt}`

To be able to convert it to matchminer-compliant schema, the text file should have following keys (represented with sample values):

	###### mandatory fields	
	GENDER : Female	
	SAMPLE_ID : 2025040901-1	
	AGE: 72	
	DIAGNOSIS : Lung Adenoid Cystic Carcinoma	
	REPORT_DATE: 2025-04-20	
	###### optional fields	
	TUMOR_MUTATIONAL_BURDEN_PER_MEGABASE: 10	
	PDL1_STATUS: High/Low	
	HER2_STATUS: Positive/Negative	
	PR_STATUS: Positive/Negative	
	ER_STATUS: Positive/Negative	
	MGMT_PROMOTER_STATUS: Methylated/Unmethylated
------------

#### Running tests:

**Running All Tests**
python -m unittest discover -s tests -v

**Running Individual Tests**
python -m unittest tests.test_your_module.TestGetGeneInfo.test_get_gene_info -v
