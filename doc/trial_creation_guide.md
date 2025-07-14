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
The CTML directory on root level contains the trial CTML files. The sub-directories and their purpose is as follows:

**pending**: Newly curated CTML trial files go here.

**closed**: Trial files for trials that are no loger recruiting go here.

**reviewed**: Once the trials under 'pending' folder are reviewed, they are moved to this folder

**json**: When trial files are ready to be picked up my [matchminer-admin](http://https://github.com/sumedhasaxena/matchminer-admin "matchminer-admin"), they are moved here. matchminer-admin repo will remove files from here, once it finishes processing them.

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

Steps for trial file management:

1. Find a clinical trial from a source that needs to be added to the system
   
2. Check if the same trial is present at https://clinicaltrials.gov/
   
3.  If present, check the status of the trial
   
	a. If closed, follow the steps below:

		i. Create a CTML file with necessary fields.

		ii. Set the 'status' as 'Closed'

		iii. Set the local protocol numbers in the 'protocol_ids' field

	b. If recruiting, check if the trial is alreday present in the matchminer system.

	If not present in the system:

		i. Create a CTML file capturing as much information as possible.

		ii. Upload the file to 'pending' folder.



TODO:
Plans needed for:

Preventing duplicate entries

Update CTML from ClinicalTrials.gov with information from duplicate local trial (i.e. local recruiting site). Most important information to add is the name of the local investigator.

Updating trial status

Merge manually added CTML and auto-generated CTML from ClinicalTrials.gov

