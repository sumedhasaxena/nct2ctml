## Guide for creation of trial documents

This document outlines the rules for manual creation of CTML documents that adhere to MatchMiner schema

The CTML trial documents are YAML files containing trial information.

#### Reference Schema
The schema for a trial document is located at [matchminer_schema](http://https://github.com/sumedhasaxena/matchminer-api/blob/5b97c71e3f9f7b29c77a84ddbc5ad6b02e8e124b/matchminer/data_model.py "matchminer_schema").
Please refer to following fields in the link above:
- parent_schema
- yaml_genomic_schema
- yaml_clinical_schema

------------


#### Directory Structure

nct2ctml/

├── ctml/

│   ├── json/

│   ├── pending/

│   └── reviewed/

The CTML directory on root level contains the trial CTML files. The sub-directories and their purpose is as follows:

**pending**: Newly curated CTML trial files go here.

**reviewed**: Once the trials under 'pending' folder are reviewed, they are moved to this folder

**json**: When trial files are ready to be picked up by [matchminer-admin](http://https://github.com/sumedhasaxena/matchminer-admin "matchminer-admin"), they are converted to JSON format and moved here. matchminer-admin repo will remove files from here, once it finishes processing them.

------------
#### Rules for assigning values to various CTML fields

1. Oncotree diagnosis - *todo*
2. Genes list- *todo*
3. General fields- *todo*
4. protocol_id and protocol_number- *todo*
5. Defining match criteria- *todo*
   a. Clinical criteria- *todo*
   b. Genomic Criteria- *todo*

------------

#### Manual curation of trial a file (CTML):

Please follow the 'Manual workflow' section in doc/clinical_trial_management_workflow.pdf to understand if a trial needs to be created manually.
Essentially, a trial file needs to be prepared manually only if it cannot be created via automated workflow or if its not present on clinical_trials.gov.

In such case, as presented in the workflow, one needs to do the following:

1. Prepare a CTML file for the trial manually, using the CTML schema mentioned in the section above.
Make sure to set the following fields as:

- nct_id: Set as 'NA'
- protocol_ids: Append the local protocol id to the protocol_ids list.

2. Make an entry for the manually curated trial file in local_trial_info.csv and push the the updated content to git.


